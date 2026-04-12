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

    user_data[chat_id] = url

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✔ Continue", callback_data="continue"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    )

    bot.send_message(chat_id, f"🔗 Link পাওয়া গেছে:\n{url}", reply_markup=markup)

# ---------- CALLBACK ----------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    url = user_data.get(chat_id)

    if call.data == "cancel":
        bot.send_message(chat_id, "❌ Cancel করা হয়েছে")
        return

    if not url:
        bot.send_message(chat_id, "❌ Link পাওয়া যায়নি")
        return

    is_youtube = "youtube.com" in url or "youtu.be" in url

    # ---------- CONTINUE ----------
    if call.data == "continue":

        if is_youtube:
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton("360p", callback_data="q_360"),
                types.InlineKeyboardButton("720p", callback_data="q_720"),
                types.InlineKeyboardButton("1080p", callback_data="q_1080")
            )

            bot.send_message(chat_id, "🎥 YouTube detected!\nQuality select করো:", reply_markup=markup)
        else:
            download(chat_id, url, "best")

    # ---------- QUALITY ----------
    if call.data.startswith("q_"):
        quality = call.data.split("_")[1]
        download(chat_id, url, quality)

# ---------- DOWNLOAD FUNCTION ----------
def download(chat_id, url, quality):
    file_name = f"video_{chat_id}.mp4"

    status = bot.send_message(chat_id, "📡 Processing...")

    # ---------- FORMAT FIX ----------
    if quality == "best":
        format_option = "bestvideo+bestaudio/best"
    elif quality == "360":
        format_option = "bestvideo[height<=360]+bestaudio/best[height<=360]"
    elif quality == "720":
        format_option = "bestvideo[height<=720]+bestaudio/best[height<=720]"
    elif quality == "1080":
        format_option = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    else:
        format_option = "best"

    try:
        ydl_opts = {
            'format': format_option,
            'outtmpl': file_name,
            'noplaylist': True,
            'quiet': True,
            'merge_output_format': 'mp4'
        }

        bot.edit_message_text("📥 Download হচ্ছে...", chat_id, status.message_id)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.edit_message_text("📤 Upload হচ্ছে...", chat_id, status.message_id)

        with open(file_name, "rb") as video:
            bot.send_video(chat_id, video)

        os.remove(file_name)

        bot.send_message(chat_id, "✅ Done! Enjoy 🎉")

    except:
        bot.send_message(chat_id, "❌ Download failed")

# ---------- RUN ----------
bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
