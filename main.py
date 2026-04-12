import telebot
import yt_dlp
import os
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")  # Render / Railway / VPS এ ENV সেট করবে
bot = telebot.TeleBot(TOKEN)

user_data = {}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        f"👋 Welcome {message.from_user.first_name}!\n\nSend a video link (YouTube / Facebook / Instagram)"
    )

# ================= GET URL =================
@bot.message_handler(func=lambda message: True)
def get_url(message):
    chat_id = message.chat.id
    url = message.text.strip()

    if not url.startswith("http"):
        bot.reply_to(message, "❌ Please send a valid video link.")
        return

    user_data[chat_id] = url

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("⬇ Download", callback_data="download"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    )

    bot.send_message(
        chat_id,
        f"📥 Confirm download?\n\n{url}",
        reply_markup=markup
    )

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == "cancel":
        bot.edit_message_text(
            "❌ Cancelled.",
            chat_id,
            message_id
        )
        return

    url = user_data.get(chat_id)

    if not url:
        bot.edit_message_text(
            "❌ No URL found.",
            chat_id,
            message_id
        )
        return

    file_name = f"video_{chat_id}.mp4"

    # 🔄 Edit message instead of sending new
    bot.edit_message_text(
        "⏳ Downloading...",
        chat_id,
        message_id
    )

    ydl_opts = {
        'format': 'best',
        'outtmpl': file_name,
        'noplaylist': True,
        'quiet': True,
        'cookiefile': 'cookies.txt',  # Optional (if needed)
        'retries': 5
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.edit_message_text(
            "📤 Uploading...",
            chat_id,
            message_id
        )

        with open(file_name, "rb") as video:
            bot.send_video(chat_id, video)

        os.remove(file_name)

        bot.edit_message_text(
            "✅ Completed.",
            chat_id,
            message_id
        )

    except Exception as e:
        bot.edit_message_text(
            "❌ Download failed.",
            chat_id,
            message_id
        )

# ================= RUN =================
bot.infinity_polling(timeout=60, long_polling_timeout=60)
