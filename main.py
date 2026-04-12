import telebot
import yt_dlp
import os

TOKEN = os.environ.get("8675679641:AAGvnIc2t767rcS7Cj6m49MmVDgTWSJVfC0")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        video = open("video.mp4", "rb")
        bot.send_video(message.chat.id, video)

        os.remove("video.mp4")

    except Exception as e:
        bot.reply_to(message, "Error: Link check করো!")

bot.polling()
