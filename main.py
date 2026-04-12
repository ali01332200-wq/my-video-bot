import telebot
import yt_dlp
import os

TOKEN = "YOUR_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send a video link 🎥")

@bot.message_handler(func=lambda message: True)
def get_url(message):
    chat_id = message.chat.id
    user_data[chat_id] = message.text.strip()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton("✔ Yes", callback_data="yes"),
        telebot.types.InlineKeyboardButton("❌ No", callback_data="no")
    )

    bot.send_message(chat_id, "Confirm download?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    url = user_data.get(chat_id)

    if call.data == "no":
        bot.send_message(chat_id, "Cancelled ❌")
        return

    if not url:
        bot.send_message(chat_id, "No URL found ❌")
        return

    bot.send_message(chat_id, "Downloading... ⏳")

    file_name = f"video_{chat_id}.mp4"

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',   # ⭐ better quality
        'outtmpl': file_name,
        'merge_output_format': 'mp4',          # ⭐ force mp4
        'noplaylist': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # ⭐ IMPORTANT: send as document (more stable)
        with open(file_name, "rb") as video:
            bot.send_document(chat_id, video)

        os.remove(file_name)

    except Exception as e:
        bot.send_message(chat_id, f"Error ❌\n{e}")

bot.infinity_polling()
