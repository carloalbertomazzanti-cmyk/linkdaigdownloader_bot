# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 17:30:49 2025

@author: MACA
"""

# bot.py
# Telegram Instagram relay bot — no-cost version using GitHub Actions
# Downloads public Instagram posts and relays them to a Telegram channel with author & caption.
import os
import requests
import instaloader
import time
import json
import shutil

# === CONFIG ===
TG_TOKEN = os.environ["TELEGRAM_TOKEN"]
TARGET_CHANNEL = os.environ["TARGET_CHANNEL"]

DOWNLOAD_DIR = "downloads"
OFFSET_FILE = "offset.txt"

# Optional Instagram login (recommended)
IG_USERNAME = os.environ.get("INSTAGRAM_USERNAME")
IG_PASSWORD = os.environ.get("INSTAGRAM_PASSWORD")

# === TELEGRAM HELPERS ===
def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()

def send_text(chat_id, text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    r = requests.post(url, data=data)
    r.raise_for_status()
    return r.json()

def send_document(chat_id, path, caption=None):
    if not os.path.exists(path):
        print(f"⚠️ File not found, skipping: {path}")
        return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendDocument"
    with open(path, "rb") as f:
        files = {"document": f}
        data = {"chat_id": chat_id, "caption": caption or ""}
        r = requests.post(url, data=data, files=files)
        r.raise_for_status()
    print(f"✅ Sent {os.path.basename(path)} to {chat_id}")

# === INSTAGRAM DOWNLOADER ===
def download_instagram(url):
    """Download media, caption, and author info from a public IG post."""
    shortcode = url.rstrip("/").split("/")[-1]
    outdir = os.path.join(DOWNLOAD_DIR, f"post_{shortcode}")
    os.makedirs(outdir, exist_ok=True)

    L = instaloader.Instaloader(
        dirname_pattern=outdir,
        filename_pattern="{shortcode}_{index}",
        download_comments=False,
        save_metadata=False,
        download_video_thumbnails=False
    )

    if IG_USERNAME and IG_PASSWORD:
        try:
            L.login(IG_USERNAME, IG_PASSWORD)
            print("✅ Logged into Instagram successfully.")
        except Exception as e:
            print(f"⚠️ Login failed: {e}")

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=outdir)
    except Exception as e:
        print(f"❌ Error downloading Instagram post: {e}")
        return None

    media = []
    for f in os.listdir(outdir):
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".mp4")):
            media.append({"path": os.path.join(outdir, f)})

    if not media:
        print("⚠️ No media files found — likely 403 or private post.")
        return None

    caption = post.caption or ""
    author = post.owner_username or "unknown"
    return {"media": media, "caption": caption, "author": author, "url": url}

# === MESSAGE HANDLER ===
def process_message(text):
    if "instagram.com" not in text:
        return

    data = download_instagram(text)
    if not data:
        send_text(TARGET_CHANNEL, f"❗Could not download media.\n{text}")
        return

    caption_text = f"📸 {data['author']}\n\n{data['caption']}\n\n🔗 {data['url']}"
    for m in data["media"]:
        if not os.path.exists(m["path"]):
            print(f"⚠️ Missing file, skipping: {m['path']}")
            continue
        try:
            send_document(TARGET_CHANNEL, m["path"], caption_text)
        except Exception as e:
            print(f"❌ Error sending {m['path']}: {e}")

    shutil.rmtree(os.path.dirname(data["media"][0]["path"]), ignore_errors=True)
    print("✅ Post complete.")

# === MAIN LOOP ===
def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    offset = 0

    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, "r") as f:
            try:
                offset = int(f.read().strip())
            except ValueError:
                offset = 0

    try:
        updates = get_updates(offset + 1)
        for u in updates.get("result", []):
            update_id = u["update_id"]
            message = u.get("message", {})
            text = message.get("text")

            if text:
                print(f"📩 Received: {text}")
                process_message(text)

            offset = update_id

        with open(OFFSET_FILE, "w") as f:
            f.write(str(offset))
        print("Cycle complete.")

    except Exception as e:
        print(f"❌ Error in main loop: {e}")

if __name__ == "__main__":
    main()



