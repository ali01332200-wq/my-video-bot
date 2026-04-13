import os
import telebot
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

DOWNLOAD_DIR = "downloads"

if not os.path.exists(DOWNLOAD_DIR):
    os.mkdir(DOWNLOAD_DIR)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send any video link 🎥\nI will try to download it...")


@bot.message_handler(func=lambda m: True)
def download_video(message):
    url = message.text
    chat_id = message.chat.id

    bot.send_message(chat_id, "Downloading... ⏳")

    try:
        file_path = f"{DOWNLOAD_DIR}/video.mp4"

        ydl_opts = {
            'outtmpl': file_path,
            'format': 'mp4/best',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.send_message(chat_id, "Uploading to Telegram... 📤")

        video = open(file_path, "rb")
        bot.send_video(chat_id, video)

        video.close()

        os.remove(file_path)

    except Exception as e:
        bot.send_message(chat_id, f"Failed ❌\nReason: {str(e)}")


bot.polling()
