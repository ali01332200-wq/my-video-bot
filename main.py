import telebot
import yt_dlp
import os
import random
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")

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

# ---------- URL ----------
@bot.message_handler(func=lambda message: True)
def get_url(message):
    chat_id = message.chat.id
    url = message.text.strip()

    if "http" not in url:
        bot.reply_to(message, "😂 এটা valid link না ভাই!")
        return

    # clean url
    url = url.split("&")[0]

    user_data[chat_id] = url

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✔ Download শুরু করো", callback_data="yes"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="no")
    )

    bot.send_message(chat_id, f"🔗 Link পাওয়া গেছে:\n{url}\n\nConfirm করো:", reply_markup=markup)

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "no":
        bot.send_message(chat_id, "❌ Cancel করা হয়েছে")
        return

    url = user_data.get(chat_id)

    if not url:
        bot.send_message(chat_id, "❌ No URL found")
        return

    file_name = f"video_{chat_id}.mp4"

    bot.send_message(chat_id, "📥 Download শুরু হচ্ছে... ⏳")

    try:
        ydl_opts = {
                   'format': 'best',
                   'outtmpl': file_name,
                   'noplaylist': True,
                   'quiet': True,
                   'socket_timeout': 30,
                   'retries': 3
                   }
        }

        bot.send_message(chat_id, "⚡ Processing...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.send_message(chat_id, "📤 Upload হচ্ছে...")

        with open(file_name, "rb") as video:
            bot.send_video(chat_id, video)

        os.remove(file_name)

        bot.send_message(chat_id, "✅ Done! Enjoy 🎉")

    except Exception as e:
        print(e)
        bot.send_message(chat_id, "❌ Download failed (link বা server issue)")

# ---------- RUN ----------
bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
