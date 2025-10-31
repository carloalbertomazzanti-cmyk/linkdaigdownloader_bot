# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 17:30:49 2025

@author: MACA
"""

# bot.py
# Telegram Instagram relay bot — no-cost version using GitHub Actions
# Downloads public Instagram posts and relays them to a Telegram channel with author & caption.
import os
import base64
import requests
import instaloader
import shutil

# -------------------
# Configuration
# -------------------
USERNAME = os.environ.get("INSTAGRAM_USERNAME")
SESSION_FILE_LOCAL = "session.txt"  # Optional local file in repo
SESSION_SECRET_ENV = "INSTA_SESSION_B64"  # GitHub secret name

TG_TOKEN = os.environ["TELEGRAM_TOKEN"]
TARGET_CHANNEL = os.environ["TARGET_CHANNEL"]

DOWNLOAD_DIR = "downloads"

# -------------------
# Instagram setup
# -------------------
L = instaloader.Instaloader(dirname_pattern=DOWNLOAD_DIR, download_comments=False, save_metadata=False)

# Try loading local session file first
if os.path.exists(SESSION_FILE_LOCAL):
    try:
        L.load_session_from_file(USERNAME, SESSION_FILE_LOCAL)
        print("✅ Logged in using local session file.")
    except Exception as e:
        print(f"⚠️ Failed to load local session: {e}")

# Otherwise, try GitHub Base64 secret
elif os.environ.get(SESSION_SECRET_ENV):
    try:
        session_data = base64.b64decode(os.environ[SESSION_SECRET_ENV])
        with open("session_from_secret", "wb") as f:
            f.write(session_data)
        L.load_session_from_file(USERNAME, "session_from_secret")
        print("✅ Logged in using Base64 session secret.")
    except Exception as e:
        print(f"⚠️ Failed to load session from secret: {e}")

# If both fail, try username/password login (optional)
elif USERNAME and os.environ.get("INSTAGRAM_PASSWORD"):
    try:
        L.login(USERNAME, os.environ["INSTAGRAM_PASSWORD"])
        print("✅ Logged in using username/password.")
    except Exception as e:
        print(f"⚠️ Login failed: {e}")
else:
    print("⚠️ No valid Instagram login method found. Exiting.")
    exit(1)

# -------------------
# Telegram helper functions
# -------------------
def send_text(chat_id, text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": chat_id, "text": text})
    r.raise_for_status()


def send_document(chat_id, path, caption=None):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendDocument"
    with open(path, "rb") as f:
        files = {"document": f}
        data = {"chat_id": chat_id, "caption": caption} if caption else {"chat_id": chat_id}
        r = requests.post(url, files=files, data=data)
        r.raise_for_status()


# -------------------
# Download Instagram post
# -------------------
def download_post(url):
    try:
        shortcode = url.rstrip("/").split("/")[-1].split("?")[0]
        post = instaloader.Post.from_shortcode(L.context, shortcode)
    except Exception as e:
        print(f"❌ Error fetching post metadata: {e}")
        return None

    outdir = os.path.join(DOWNLOAD_DIR, f"post_{shortcode}")
    os.makedirs(outdir, exist_ok=True)

    media_files = []

    # Download images/videos
    for i, node in enumerate(post.get_sidecar_nodes() if post.typename == "GraphSidecar" else [post]):
        filename = f"{i}_{node.shortcode}.mp4" if node.is_video else f"{i}_{node.shortcode}.jpg"
        path = os.path.join(outdir, filename)
        try:
            L.download_pic(path, node.url, node.date_utc)
            media_files.append(path)
        except Exception as e:
            print(f"⚠️ Failed to download media: {e}")

    if not media_files:
        print("⚠️ No media downloaded.")
        return None

    return {
        "media": media_files,
        "caption": post.caption or "",
        "author": post.owner_username,
        "url": url,
    }


# -------------------
# Process message
# -------------------
def process_message(url):
    data = download_post(url)
    if not data:
        try:
            send_text(TARGET_CHANNEL, f"❗Could not download media for:\n{url}")
        except Exception as e:
            print(f"⚠️ Telegram error sending failure message: {e}")
        return

    caption_text = f"📸 {data['author']}\n\n{data['caption']}\n\n🔗 {data['url']}"
    for file_path in data["media"]:
        try:
            send_document(TARGET_CHANNEL, file_path, caption_text)
        except Exception as e:
            print(f"⚠️ Error sending media to Telegram: {e}")


# -------------------
# Main loop (for testing)
# -------------------
if __name__ == "__main__":
    while True:
        text = input("Enter Instagram link: ").strip()
        if text.lower() in ["exit", "quit"]:
            break
        process_message(text)
        print("✅ Done processing.\n")




