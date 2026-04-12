import telebot
import yt_dlp
import os

TOKEN = "BOT_TOKEN"
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

    if call.data == "no":
        bot.edit_message_text("Cancelled ❌", chat_id, call.message.message_id)
        return

    url = user_data.get(chat_id)

    if not url:
        bot.edit_message_text("No URL found ❌", chat_id, call.message.message_id)
        return

    bot.edit_message_text("Downloading... ⏳", chat_id, call.message.message_id)

    file_name = f"video_{chat_id}.%(ext)s"

    ydl_opts = {
        'format': 'best',
        'outtmpl': file_name,
        'noplaylist': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_file = ydl.prepare_filename(info)

        bot.edit_message_text("Uploading... 📤", chat_id, call.message.message_id)

        with open(final_file, "rb") as video:
            bot.send_document(chat_id, video)

        os.remove(final_file)

        bot.edit_message_text("Done ✅", chat_id, call.message.message_id)

    except Exception as e:
        bot.send_message(chat_id, f"Error ❌\n{e}")

bot.infinity_polling(skip_pending=True)
