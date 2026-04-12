import telebot
import yt_dlp
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🎥 Send me a video link and I will download it automatically!")

@bot.message_handler(func=lambda message: True)
def get_url(message):
    chat_id = message.chat.id
    url = message.text.strip()

    if not url.startswith("http"):
        bot.send_message(chat_id, "❌ Please send a valid video URL")
        return

    user_data[chat_id] = url

    bot.send_message(chat_id, "🎥 Link received ✔️\nDownloading started... ⏳")

    file_name = f"video_{chat_id}.mp4"

    ydl_opts = {
        'format': 'best',
        'outtmpl': file_name,
        'noplaylist': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.send_message(chat_id, "📤 Uploading video...")

        with open(file_name, "rb") as video:
            bot.send_video(chat_id, video)

        os.remove(file_name)

        bot.send_message(chat_id, "✅ Done!")

    except Exception as e:
        bot.send_message(chat_id, "❌ Download failed")

bot.infinity_polling(timeout=60, long_polling_timeout=60)
