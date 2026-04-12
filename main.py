import telebot
import yt_dlp
import os
from telebot import types

TOKEN = os.getenv("8675679641:AAGvnIc2t767rcS7Cj6m49MmVDgTWSJVfC0")
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send a video link 🎥")

# Step 1: Get URL
@bot.message_handler(func=lambda message: True)
def get_url(message):
    chat_id = message.chat.id
    url = message.text.strip()

    user_data[chat_id] = {"url": url}

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✔ Yes", callback_data="yes"),
        types.InlineKeyboardButton("❌ No", callback_data="no")
    )

    bot.send_message(chat_id, f"URL received:\n{url}\n\nConfirm download?", reply_markup=markup)

# Step 2: Confirm
@bot.callback_query_handler(func=lambda call: call.data in ["yes", "no"])
def confirm(call):
    chat_id = call.message.chat.id

    if call.data == "no":
        bot.send_message(chat_id, "❌ Cancelled")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("360p", callback_data="360"),
        types.InlineKeyboardButton("720p", callback_data="720"),
        types.InlineKeyboardButton("1080p", callback_data="1080")
    )

    bot.send_message(chat_id, "Choose quality 🎥", reply_markup=markup)

# Step 3: Download with quality
@bot.callback_query_handler(func=lambda call: call.data in ["360", "720", "1080"])
def download(call):
    chat_id = call.message.chat.id
    quality = call.data

    url = user_data.get(chat_id, {}).get("url")

    if not url:
        bot.send_message(chat_id, "No URL found ❌")
        return

    bot.send_message(chat_id, f"Downloading {quality}p... ⏳")

    ydl_opts = {
        'format': f'best[height<={quality}]',
        'outtmpl': 'video.mp4',
        'noplaylist': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open("video.mp4", "rb") as video:
            bot.send_video(chat_id, video)

        os.remove("video.mp4")

    except Exception as e:
        bot.send_message(chat_id, "Download failed ❌")

bot.infinity_polling()
