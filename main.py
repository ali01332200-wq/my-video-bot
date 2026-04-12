import telebot
import yt_dlp
import os
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("BOT_TOKEN missing")
    exit()

bot = telebot.TeleBot(TOKEN)

user_data = {}

# START
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📥 Send a valid video link")

# GET URL
@bot.message_handler(func=lambda message: True)
def get_url(message):
    chat_id = message.chat.id
    url = message.text.strip()

    # basic validation (CRASH FIX)
    if "http" not in url:
        bot.reply_to(message, "❌ Please send a valid link")
        return

    user_data[chat_id] = url

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✔ Download", callback_data="yes"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="no")
    )

    bot.send_message(chat_id, f"🔗 Link received:\n{url}", reply_markup=markup)

# CALLBACK
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "no":
        bot.send_message(chat_id, "❌ Cancelled")
        return

    url = user_data.get(chat_id)

    if not url:
        bot.send_message(chat_id, "❌ No URL found")
        return

    file_name = f"video_{chat_id}.mp4"

    bot.send_message(chat_id, "⚡ Downloading...")

    ydl_opts = {
        'format': 'best',
        'outtmpl': file_name,
        'noplaylist': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.send_message(chat_id, "📤 Sending video...")

        with open(file_name, "rb") as video:
            bot.send_video(chat_id, video)

        os.remove(file_name)

        bot.send_message(chat_id, "✅ Done")

    except Exception as e:
        bot.send_message(chat_id, "❌ Failed to download")

bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
