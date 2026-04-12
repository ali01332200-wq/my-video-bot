import telebot
import yt_dlp
import os
import time
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("BOT_TOKEN missing")
    exit()

bot = telebot.TeleBot(TOKEN)
user_data = {}

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    bot.send_message(
        message.chat.id,
        f"👋 Hello {name}!\n\nSend any video link:\nYouTube / Instagram / Facebook / TikTok"
    )

# ---------------- GET URL ----------------
@bot.message_handler(func=lambda message: True)
def get_url(message):
    chat_id = message.chat.id
    url = message.text.strip()

    if "http" not in url:
        bot.reply_to(message, "❌ Valid link পাঠাও")
        return

    user_data[chat_id] = url

    # YouTube হলে quality option দেখাবে
    if "youtube.com" in url or "youtu.be" in url:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("360p", callback_data="360"),
            types.InlineKeyboardButton("720p", callback_data="720"),
            types.InlineKeyboardButton("Best", callback_data="best")
        )
        bot.send_message(chat_id, "🎥 Select Quality:", reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✔ Download", callback_data="download"))
        bot.send_message(chat_id, "✔ Download শুরু করবো?", reply_markup=markup)

# ---------------- CALLBACK ----------------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    url = user_data.get(chat_id)

    if not url:
        bot.send_message(chat_id, "❌ URL missing")
        return

    quality = call.data

    # format setup
    if quality == "360":
        format_option = "best[height<=360]"
    elif quality == "720":
        format_option = "best[height<=720]"
    else:
        format_option = "best"

    file_name = f"video_{chat_id}.mp4"

    status = bot.send_message(chat_id, "📥 Download শুরু হচ্ছে...")

    try:
        # Fake smooth progress effect
        for i in range(1, 6):
            time.sleep(0.5)
            bot.edit_message_text(
                f"📥 Downloading... {i*20}%",
                chat_id,
                status.message_id
            )

        ydl_opts = {
            'format': format_option,
            'outtmpl': file_name,
            'noplaylist': True,
            'quiet': True,
            'socket_timeout': 25,
            'retries': 3
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # 50MB limit protection
        if os.path.getsize(file_name) > 49 * 1024 * 1024:
            os.remove(file_name)
            bot.send_message(chat_id, "❌ Video 50MB এর বেশি")
            return

        bot.edit_message_text("📤 Upload হচ্ছে...", chat_id, status.message_id)

        with open(file_name, "rb") as video:
            bot.send_video(chat_id, video)

        os.remove(file_name)

        bot.send_message(chat_id, "✅ Done! Enjoy 🎉")

    except Exception as e:
        print(e)
        bot.send_message(chat_id, "❌ Download failed (private / blocked / large file)")

# ---------------- RUN ----------------
bot.infinity_polling(timeout=60, long_polling_timeout=60, skip_pending=True)
