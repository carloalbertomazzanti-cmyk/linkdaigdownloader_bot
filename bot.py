# -*- coding: utf-8 -*-
"""
Created on Tue Sep  9 17:30:49 2025

@author: MACA
"""

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import re
import requests

API_TOKEN = "8419360224:AAFhhmY7rUloLc25I87649iF9jE_0PDEbPY"
RAPIDAPI_KEY = "79c4f11226msh1ee21ab35454578p1a0671jsn86c6b70eaefa"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_instagram_links(message: types.Message):
    insta_pattern = r"(https?://(www\.)?instagram\.com/[^\s]+)"
    match = re.search(insta_pattern, message.text)

    if match:
        url = match.group(1)

        # Call API to get media links
        api_url = "https://instagram-downloader-download-instagram-videos-stories.p.rapidapi.com/index"
        headers = {"X-RapidAPI-Key": RAPIDAPI_KEY}
        params = {"url": url}

        try:
            response = requests.get(api_url, headers=headers, params=params).json()

            if "media" in response:
                for media_url in response["media"]:
                    if media_url.endswith(".mp4"):
                        await message.answer_video(media_url)
                    else:
                        await message.answer_photo(media_url)
            else:
                await message.answer("⚠️ Could not fetch media.")
        except Exception as e:
            await message.answer(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
