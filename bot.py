# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 17:30:49 2025

@author: MACA
"""

# bot.py
# Telegram Instagram relay bot — no-cost version using GitHub Actions
# Downloads public Instagram posts and relays them to a Telegram channel with author & caption.

import os
import re
import json
import requests
import time
from pathlib import Path
from instaloader import Instaloader, Post

TG_TOKEN = os.environ[8419360224:AAFhhmY7rUloLc25I87649iF9jE_0PDEbPY]
TARGET_CHANNEL = os.environ[@linkdaig]  # e.g. "@mychannel" or "-1001234567890"
OFFSET_FILE = "offset.txt"
WORKDIR = Path("downloads")
WORKDIR.mkdir(exist_ok=True)

TELEGRAM_API = f"https://api.telegram.org/bot{TG_TOKEN}"

INSTAGRAM_URL_RE = re.compile(r"(https?://(www\.)?instagram\.com/(p|reel)/[A-Za-z0-9_\-]+)/?")

def read_offset():
    try:
        return int(Path(OFFSET_FILE).read_text().strip())
    except:
        return 0

def write_offset(o):
    Path(OFFSET_FILE).write_text(str(o))

def get_updates(offset):
    params = {"offset": offset, "timeout": 20}
    r = requests.get(f"{TELEGRAM_API}/getUpdates", params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("result", [])

def send_text(chat_id, text):
    r = requests.post(f"{TELEGRAM_API}/sendMessage", data={
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": False
    })
    r.raise_for_status()

def send_media_group(chat_id, media):
    url = f"{TELEGRAM_API}/sendMediaGroup"
    files = {}
    payload_media = []
    for i, item in enumerate(media):
        fname = f"file{i}"
        payload_media.append({
            "type": item["type"],
            "media": f"attach://{fname}",
            **({"caption": item["caption"]} if "caption" in item and item["caption"] else {})
        })
        files[fname] = open(item["path"], "rb")
    data = {"chat_id": chat_id, "media": json.dumps(payload_media)}
    r = requests.post(url, data=data, files=files, timeout=120)
    for f in files.values():
        f.close()
    r.raise_for_status()

def send_document(chat_id, path, caption=None):
    url = f"{TELEGRAM_API}/sendDocument"
    files = {"document": open(path, "rb")}
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption
    r = requests.post(url, data=data, files=files, timeout=120)
    files["document"].close()
    r.raise_for_status()

def download_instagram(url, outdir):
    shortcode = url.rstrip("/").split("/")[-1]
    L = Instaloader(dirname_pattern=str(outdir), filename_pattern="{shortcode}_{index}")
    try:
        post = Post.from_shortcode(L.context, shortcode)
        author = post.owner_username
        caption = post.caption or ""
        paths = []
        for idx, node in enumerate(post.get_sidecar_nodes() if post.typename == "GraphSidecar" else [post]):
            filename = f"{shortcode}_{idx}.jpg" if node.is_video is False else f"{shortcode}_{idx}.mp4"
            target = outdir / filename
            if node.is_video:
                L.download_pic(str(target), node.video_url, post.date_utc)
            else:
                L.download_pic(str(target), node.display_url, post.date_utc)
            paths.append(str(target))
        return {
            "author": author,
            "caption": caption,
            "shortcode": shortcode,
            "files": paths
        }
    except Exception as e:
        print("Error downloading Instagram post:", e)
        return None

def process_message(text):
    m = INSTAGRAM_URL_RE.search(text)
    if not m:
        return False
    url = m.group(1)
    outdir = WORKDIR / f"post_{int(time.time())}"
    outdir.mkdir(parents=True, exist_ok=True)
    data = download_instagram(url, outdir)
    if not data:
        send_text(TARGET_CHANNEL, f"⚠️ Could not download media.\n{url}")
        return True
    caption_text = f"📸 <b>@{data['author']}</b>\n\n{data['caption'] or ''}\n\n🔗 {url}"
    # prepare media
    media = []
    for p in data["files"]:
        ext = p.lower().split(".")[-1]
        if ext in ("jpg", "jpeg", "png", "webp"):
            media.append({"type": "photo", "path": p})
        elif ext in ("mp4", "mov", "mkv", "webm"):
            media.append({"type": "video", "path": p})
        else:
            media.append({"type": "document", "path": p})
    # Send media
    try:
        if 1 < len(media) <= 10:
            # add caption only to first item
            media[0]["caption"] = caption_text
            send_media_group(TARGET_CHANNEL, media)
        elif len(media) == 1:
            if media[0]["type"] in ("photo", "video"):
                send_document(TARGET_CHANNEL, media[0]["path"], caption_text)
            else:
                send_document(TARGET_CHANNEL, media[0]["path"], caption_text)
        else:
            send_text(TARGET_CHANNEL, caption_text)
        return True
    except Exception as e:
        print("Error sending media:", e)
        send_text(TARGET_CHANNEL, f"❗Error sending media.\n{url}")
        return True

def main():
    offset = read_offset()
    updates = get_updates(offset + 1)
    max_offset = offset
    for u in updates:
        upd_id = u["update_id"]
        if upd_id <= offset:
            continue
        max_offset = max(max_offset, upd_id)
        msg = u.get("message") or u.get("channel_post") or u.get("edited_message")
        if not msg:
            continue
        text = msg.get("text") or msg.get("caption") or ""
        if text:
            process_message(text)
    if max_offset > offset:
        write_offset(max_offset + 1)
    print("Cycle complete.")

if __name__ == "__main__":
    main()






