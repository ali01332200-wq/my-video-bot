import telebot
import yt_dlp
import os
from telebot import types

TOKEN = os.getenv("8675679641:AAGvnIc2t767rcS7Cj6m49MmVDgTWSJVfC0")
bot = telebot.TeleBot(TOKEN)

user_data = {}

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📥 Send any video link (YouTube / TikTok / Facebook / Instagram)")

# ---------- URL ----------
@bot.message_handler(func=lambda message: True)
def get_url(message):
    chat_id = message.chat.id
    url = message.text.strip()

    user_data[chat_id] = {"url": url}

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✔ Download", callback_data="dl"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="no")
    )

    bot.send_message(chat_id, f"🔗 Link received:\n{url}\n\nConfirm download?", reply_markup=markup)

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
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

    bot.send_message(chat_id, "🎥 Select quality:", reply_markup=markup)

# ---------- DOWNLOAD ----------
@bot.callback_query_handler(func=lambda call: call.data in ["360", "720", "1080"])
def download(call):
    chat_id = call.message.chat.id
    quality = call.data

    url = user_data.get(chat_id, {}).get("url")

    if not url:
        bot.send_message(chat_id, "❌ No URL found")
        return

    status = bot.send_message(chat_id, "⚡ Detecting platform...")

    file_name = f"video_{chat_id}.mp4"

    # SMART FAST SETTINGS
    ydl_opts = {
        'format': f'best[height<={quality}]',
        'outtmpl': file_name,
        'noplaylist': True,
        'quiet': True,
    }

    try:
        bot.edit_message_text("📥 Starting download...", chat_id, status.message_id)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.edit_message_text("📤 Uploading to Telegram...", chat_id, status.message_id)

        with open(file_name, "rb") as video:
            bot.send_video(chat_id, video)

        os.remove(file_name)

        bot.send_message(chat_id, "✅ Done!")

    except Exception as e:
        bot.send_message(chat_id, "❌ Download failed")

bot.infinity_polling(timeout=60, long_polling_timeout=60)
