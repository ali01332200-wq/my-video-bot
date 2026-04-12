import telebot
import yt_dlp
import os
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📥 Send YouTube link")

@bot.message_handler(func=lambda message: True)
def get_url(message):
    chat_id = message.chat.id
    url = message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:
        bot.reply_to(message, "❌ শুধু YouTube link দাও")
        return

    user_data[chat_id] = url

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✔ Download", callback_data="yes"))

    bot.send_message(chat_id, "Download শুরু করবো?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "yes")
def download(call):
    chat_id = call.message.chat.id
    url = user_data.get(chat_id)

    if not url:
        bot.send_message(chat_id, "❌ URL missing")
        return

    file_name = f"video_{chat_id}.mp4"

    bot.send_message(chat_id, "📥 Download হচ্ছে...")

    try:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': file_name,
            'noplaylist': True,
            'quiet': True,
            'socket_timeout': 20
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # FILE SIZE CHECK (Telegram limit protection)
        if os.path.getsize(file_name) > 49 * 1024 * 1024:
            os.remove(file_name)
            bot.send_message(chat_id, "❌ ভিডিও ৫০MB এর বেশি। ছোট ভিডিও চেষ্টা করো।")
            return

        with open(file_name, "rb") as video:
            bot.send_video(chat_id, video)

        os.remove(file_name)

        bot.send_message(chat_id, "✅ Done!")

    except Exception as e:
        print(e)
        bot.send_message(chat_id, "❌ YouTube blocked / link invalid")

bot.infinity_polling(timeout=60, long_polling_timeout=60)
