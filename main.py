import telebot
import yt_dlp
import os
from telebot import types

TOKEN = os.getenv("75679641:AAGvnIc2t767rcS7Cj6m49MmVDgTWSJVfC0")
bot = telebot.TeleBot(TOKEN)

user_url = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send me a video link 🎥")

# URL receive
@bot.message_handler(func=lambda message: True)
def get_url(message):
    url = message.text.strip()

    user_url[message.chat.id] = url

    # Confirm buttons
    markup = types.InlineKeyboardMarkup()
    yes = types.InlineKeyboardButton("✔ Download", callback_data="yes")
    no = types.InlineKeyboardButton("❌ Cancel", callback_data="no")

    markup.add(yes, no)

    bot.send_message(
        message.chat.id,
        f"🔗 URL received:\n{url}\n\nDo you want to download?",
        reply_markup=markup
    )

# Button click handler
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "no":
        bot.send_message(chat_id, "❌ Cancelled")
        return

    if call.data == "yes":
        url = user_url.get(chat_id)

        if not url:
            bot.send_message(chat_id, "No URL found ❌")
            return

        bot.send_message(chat_id, "Downloading... ⏳")

        ydl_opts = {
            'format': 'best',
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
