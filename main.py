import telebot
import yt_dlp
import os

TOKEN = os.getenv("8675679641:AAGvnIc2t767rcS7Cj6m49MmVDgTWSJVfC0")

if not TOKEN:
    print("BOT_TOKEN not found!")
    exit()

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send me a video link 🎥")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text.strip()

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
            bot.send_video(message.chat.id, video)

        os.remove("video.mp4")

    except Exception as e:
        bot.reply_to(message, "Download failed ❌")

bot.infinity_polling()
