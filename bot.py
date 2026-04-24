import telebot
from rembg import remove
from PIL import Image
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Send a photo 🖼️")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id

    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    input_path = "input.png"
    output_path = "output.png"

    with open(input_path, "wb") as f:
        f.write(downloaded_file)

    bot.send_message(chat_id, "Removing background... ⏳")

    try:
        img = Image.open(input_path)
        result = remove(img)
        result.save(output_path)

        with open(output_path, "rb") as f:
            bot.send_document(chat_id, f)

        os.remove(input_path)
        os.remove(output_path)

    except Exception as e:
        bot.send_message(chat_id, f"Error ❌ {e}")

bot.infinity_polling()
