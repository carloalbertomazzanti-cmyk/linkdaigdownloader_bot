# Telegram Instagram Relay Bot (Free Hosting via GitHub Actions)

A lightweight Telegram bot that receives **Instagram post or reel links** via message, downloads the **images/videos** along with **author name** and **caption**, and automatically posts them to a **Telegram channel**.

✅ **Completely free** — runs on GitHub Actions (no servers or subscriptions).  
✅ Handles photos, carousels, and short videos (public posts).  
✅ Captions and author handle included automatically.

---

## 📦 Features

- Downloads public Instagram post media using [Instaloader](https://instaloader.github.io/).
- Extracts author handle and caption.
- Posts all media to your target Telegram channel.
- Supports photo albums (up to 10 media per post).
- Runs every 5 minutes automatically (via GitHub Actions).

---

## ⚙️ Setup

### 1. Create your Telegram Bot
1. Open Telegram and search for **@BotFather**.
2. Use `/newbot` → give it a name and username.
3. Copy the **bot token** (you’ll need it below).

### 2. Create a Telegram Channel
- Create a new channel (public or private).
- Add your bot as **Administrator** (must be able to post).

### 3. Create GitHub Repository
1. Create a **public** repository.
2. Add these files:
   - `bot.py` (from this project)
   - `.github/workflows/poll.yml`
   - `offset.txt` (empty, containing just `0`)
3. Commit and push.

### 4. Add Secrets in GitHub
Go to your repository → **Settings → Secrets → Actions → New repository secret**:

| Name | Example value |
|------|----------------|
| `TELEGRAM_TOKEN` | `123456789:ABCxyz...` |
| `TARGET_CHANNEL` | `@mychannel` or `-1001234567890` |

### 5. Enable Actions
- Go to the **Actions** tab.
- Approve the first workflow run if prompted.
- It will run every 5 minutes automatically.

---

## 💬 How to Use

1. Send an **Instagram post link** to your bot in Telegram (e.g., `https://www.instagram.com/p/XYZ123/`).
2. Within ~5 minutes, the bot will:
   - Download the media,
   - Post it to your configured channel,
   - Include the author name and caption,
   - Append the original link.

Example output in your channel:

📸 @username

This is the Instagram caption text.

🔗 https://www.instagram.com/p/XYZ123/


---

## ⚠️ Notes & Limitations

- **Public posts only** — private posts can’t be accessed without login credentials.
- **Large videos (>50 MB)** may fail to upload; the bot will instead post the link.
- **Rate limits:** Suitable for personal/small use. Avoid spamming Instagram or Telegram.
- **Delay:** GitHub Actions runs every 5 minutes (minimum allowed). Instant responses are not possible on the free plan.

---

## 🧰 Technologies

- **Python 3.10**
- [Instaloader](https://instaloader.github.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- **GitHub Actions** (free for public repos)

---

## 🕵️‍♂️ Privacy

No data is stored beyond the minimal `offset.txt` (which records the last Telegram update ID).  
Instagram media and captions are fetched on-demand and not retained.

---

## 🚀 Free Hosting Explained

GitHub Actions allows scheduled workflows every 5 minutes on **public repositories** without cost.  
Each run polls Telegram for new messages and processes any Instagram links found.  
Because this job only runs briefly each cycle, it remains **completely free** and within usage limits.

---

## 🧩 License

MIT License — you can modify and use freely.
