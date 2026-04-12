import telebot
import yt_dlp
import os
import time
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

user_data = {}

# ---------- WELCOME ----------
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    text = "👋 Welcome to Video Downloader Bot!\n\n📥 Send me any video link\n🎥 YouTube / TikTok / Facebook / Instagram"

    bot.send_message(chat_id, "⏳ Loading bot...")
    time.sleep(1)
    bot.send_message(chat_id, text)

# ---------- GET URL ----------
@bot.message_handler(func=lambda message: True)
def get_url(message):
    chat_id = message.chat.id
    url = message.text.strip()

    if "http" not in url:
        bot.reply_to(message, "😂 এটা link না ভাই! সঠিক link দাও")
        return

    user_data[chat_id] = url

    # FUN MESSAGE
    bot.send_message(chat_id, "😎 Wow! Hacker mode activated...\n🔍 Link scanning...")

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✔ Start Download", callback_data="start"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="no")
    )

    bot.send_message(chat_id, "👇 Confirm download?", reply_markup=markup)

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "no":
        bot.send_message(chat_id, "❌ Cancelled by user")
        return

    url = user_data.get(chat_id)

    if not url:
        bot.send_message(chat_id, "❌ No URL found")
        return

    file_name = f"video_{chat_id}.mp4"

    # PROGRESS STYLE UI
    status = bot.send_message(chat_id, "📡 Connecting to server...")

    time.sleep(1)
    bot.edit_message_text("🔍 Detecting platform...", chat_id, status.message_id)

    time.sleep(1)
    bot.edit_message_text("📥 Downloading video... 10%", chat_id, status.message_id)

    ydl_opts = {
        'format': 'best',
        'outtmpl': file_name,
        'noplaylist': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.edit_message_text("📤 Uploading to Telegram... 90%", chat_id, status.message_id)

        with open(file_name, "rb") as video:
            bot.send_video(chat_id, video)

        os.remove(file_name)

        bot.send_message(chat_id, "✅ Done! Enjoy 🎉")

    except:
        bot.send_message(chat_id, "❌ Download failed")

bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
