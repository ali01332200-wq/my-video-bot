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

    # FIX: clean youtube url
    url = url.split("&")[0]

    if "http" not in url:
        bot.reply_to(message, "😂 এটা valid link না ভাই!")
        return

    user_data[chat_id] = url

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✔ Download শুরু করো", callback_data="download"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    )

    bot.send_message(chat_id, f"🔗 Link পাওয়া গেছে:\n{url}", reply_markup=markup)

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "cancel":
        bot.send_message(chat_id, "❌ Cancel করা হয়েছে")
        return

    url = user_data.get(chat_id)

    if not url:
        bot.send_message(chat_id, "❌ Link পাওয়া যায়নি")
        return

    file_name = f"video_{chat_id}.mp4"

    status = bot.send_message(chat_id, "📡 Download শুরু হচ্ছে...")

    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': file_name,
            'noplaylist': True,
            'quiet': True,
            'merge_output_format': 'mp4',
            'socket_timeout': 30,
            'retries': 3,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0'
            }
        }

        bot.edit_message_text("📥 Download হচ্ছে...", chat_id, status.message_id)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.edit_message_text("📤 Upload হচ্ছে...", chat_id, status.message_id)

        with open(file_name, "rb") as video:
            bot.send_video(chat_id, video)

        os.remove(file_name)

        bot.send_message(chat_id, "✅ Done! Enjoy 🎉")

    except Exception as e:
        print(e)
        bot.send_message(chat_id, "❌ ভিডিও ডাউনলোড করা যাচ্ছে না। অন্য লিংক চেষ্টা করো।")

# ---------- RUN ----------
bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
