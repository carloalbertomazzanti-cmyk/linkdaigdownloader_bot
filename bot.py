# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 17:30:49 2025

@author: MACA
"""

import os
import re
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = os.getenv("API_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
CHANNEL_ID = "@YourChannelUsername"   # or numeric ID like -1001234567890

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

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)


