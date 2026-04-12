import telebot
import yt_dlp
import os
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

user_data = {}

# progress store
progress_msg = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send a video link 🎥")

@bot.message_handler(func=lambda message: True)
def get_url(message):
    chat_id = message.chat.id
    url = message.text.strip()

    user_data[chat_id] = url

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✔ Yes", callback_data="yes"),
        types.InlineKeyboardButton("❌ No", callback_data="no")
    )

    bot.send_message(chat_id, f"Confirm download?\n{url}", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    if call.data == "no":
        bot.send_message(chat_id, "Cancelled ❌")
        return

    url = user_data.get(chat_id)
    if not url:
        bot.send_message(chat_id, "No URL found ❌")
        return

    file_name = f"video_{chat_id}.mp4"

    msg = bot.send_message(chat_id, "Starting download... ⏳")
    progress_msg[chat_id] = msg.message_id

    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', '')
            text = f"Downloading...\n{percent}\n{speed}"

            try:
                bot.edit_message_text(
                    text,
                    chat_id,
                    progress_msg[chat_id]
                )
            except:
                pass

        elif d['status'] == 'finished':
            try:
                bot.edit_message_text(
                    "Download finished ✔️\nUploading...",
                    chat_id,
                    progress_msg[chat_id]
                )
            except:
                pass

    ydl_opts = {
        'format': 'best',
        'outtmpl': file_name,
        'noplaylist': True,
        'quiet': True,
        'progress_hooks': [progress_hook]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open(file_name, "rb") as video:
            bot.send_video(chat_id, video)

        os.remove(file_name)

        bot.edit_message_text(
            "Done ✅ Uploaded!",
            chat_id,
            progress_msg[chat_id]
        )

    except Exception as e:
        bot.edit_message_text(
            "Download failed ❌",
            chat_id,
            progress_msg[chat_id]
        )

bot.infinity_polling()
