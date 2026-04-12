import telebot
import yt_dlp
import os
import random
from telebot import types

TOKEN = os.getenv("8675679641:AAGvnIc2t767rcS7Cj6m49MmVDgTWSJVfC0")

if not TOKEN:
    print("BOT_TOKEN missing")
    exit()

bot = telebot.TeleBot(TOKEN)

user_data = {}

# ---------- START ----------
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name

    greetings = [
        f"👋 হ্যালো {name}! ভিডিও ডাউনলোড করতে ready তো? 🎥",
        f"😂 ওহে {name}! আমি এখন তোমার জন্য অনলাইন হয়ে গেছি!",
        f"🔥 {name}, তুমি এখন downloader power unlock করছো!",
        f"😎 কি খবর {name}! একটা link দাও দেখি!",
        f"🚀 Welcome {name}! চল ভিডিও নামানো শুরু করি!"
    ]

    bot.send_message(message.chat.id, "⏳ সিস্টেম চালু হচ্ছে...")
    bot.send_message(message.chat.id, random.choice(greetings))

# ---------- URL HANDLER ----------
@bot.message_handler(func=lambda message: True)
def get_url(message):
    chat_id = message.chat.id
    url = message.text.strip()

    if "http" not in url:
        bot.reply_to(message, "😂 এটা valid link না ভাই!")
        return

    user_data[chat_id] = url

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✔ Download শুরু করো", callback_data="start"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="no")
    )

    bot.send_message(chat_id, f"🔗 Link পাওয়া গেছে:\n{url}\n\nকি করতে চাও?", reply_markup=markup)

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "no":
        bot.send_message(chat_id, "❌ Cancel করা হয়েছে")
        return

    url = user_data.get(chat_id)

    if not url:
        bot.send_message(chat_id, "❌ কোনো link পাওয়া যায়নি")
        return

    # QUALITY SELECT
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("360p", callback_data="360"),
        types.InlineKeyboardButton("720p", callback_data="720"),
        types.InlineKeyboardButton("1080p", callback_data="1080")
    )

    bot.send_message(chat_id, "🎥 Quality select করো:", reply_markup=markup)

# ---------- DOWNLOAD ----------
@bot.callback_query_handler(func=lambda call: call.data in ["360", "720", "1080"])
def download(call):
    chat_id = call.message.chat.id
    quality = call.data

    url = user_data.get(chat_id)

    if not url:
        bot.send_message(chat_id, "❌ Link missing")
        return

    file_name = f"video_{chat_id}.mp4"

    status = bot.send_message(chat_id, "📡 Server connect করা হচ্ছে...")

    try:
        bot.edit_message_text("🔍 Link detect করা হচ্ছে...", chat_id, status.message_id)

        ydl_opts = {
            'format': f'best[height<={quality}]',
            'outtmpl': file_name,
            'noplaylist': True,
            'quiet': True
        }

        bot.edit_message_text("📥 Download হচ্ছে...", chat_id, status.message_id)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.edit_message_text("📤 Telegram এ পাঠানো হচ্ছে...", chat_id, status.message_id)

        with open(file_name, "rb") as video:
            bot.send_video(chat_id, video)

        os.remove(file_name)

        bot.send_message(chat_id, "✅ Done! Enjoy 🎉")

    except:
        bot.send_message(chat_id, "❌ Download failed")

# ---------- RUN ----------
bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
