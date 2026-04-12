import telebot
import yt_dlp
import os

TOKEN = "BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

user_data = {}
status_msg = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send a video link 🎥")

@bot.message_handler(func=lambda message: True)
def get_url(message):
    chat_id = message.chat.id
    url = message.text.strip()

    user_data[chat_id] = url

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
        bot.edit_message_text(
            "Cancelled ❌",
            chat_id,
            call.message.message_id
        )
        return

    if not url:
        bot.edit_message_text(
            "No URL found ❌",
            chat_id,
            call.message.message_id
        )
        return

    # ⭐ প্রথমে message edit করে status দেখাবে
    msg = bot.edit_message_text(
        "Downloading... ⏳",
        chat_id,
        call.message.message_id
    )

    status_msg[chat_id] = msg.message_id

    file_name = f"video_{chat_id}.mp4"

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': file_name,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.edit_message_text(
            "Uploading... 📤",
            chat_id,
            status_msg[chat_id]
        )

        with open(file_name, "rb") as video:
            bot.send_document(chat_id, video)

        bot.edit_message_text(
            "Done ✅",
            chat_id,
            status_msg[chat_id]
        )

        os.remove(file_name)

    except Exception as e:
        bot.edit_message_text(
            f"Failed ❌\n{e}",
            chat_id,
            call.message.message_id
        )

bot.infinity_polling()
