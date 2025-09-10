# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 17:30:49 2025

@author: MACA
"""

import os
import re
import requests
import asyncio
from aiogram import Bot, Dispatcher, types
from aiohttp import web

API_TOKEN = os.getenv("API_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
CHANNEL_ID = "@YourChannelUsername"   # or -1001234567890

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_instagram_links(message: types.Message):
    insta_pattern = r"(https?://(www\.)?instagram\.com/[^\s]+)"
    match = re.search(insta_pattern, message.text or "")

    if match:
        url = match.group(1)
        api_url = "https://instagram-downloader-download-instagram-videos-stories.p.rapidapi.com/index"
        headers = {"X-RapidAPI-Key": RAPIDAPI_KEY}
        params = {"url": url}

        try:
            response = requests.get(api_url, headers=headers, params=params).json()
            if "media" in response:
                for media_url in response["media"]:
                    if media_url.endswith(".mp4"):
                        await bot.send_video(CHANNEL_ID, media_url)
                    else:
                        await bot.send_photo(CHANNEL_ID, media_url)
            else:
                await message.reply("⚠️ Could not fetch media.")
        except Exception as e:
            await message.reply(f"❌ Error: {e}")

# --- Web server handler ---
async def handle(request):
    return web.Response(text="Bot is running on Koyeb!")

async def on_startup(app):
    loop = asyncio.get_event_loop()
    loop.create_task(dp.start_polling(bot))

async def on_cleanup(app):
    await bot.session.close()

def main():
    app = web.Application()
    app.router.add_get("/", handle)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)
    web.run_app(app, port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()




