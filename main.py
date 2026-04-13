import telebot
import requests
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# ⚠️ এখানে তোমাকে working terabox extractor API বসাতে হবে
API_BASE = "https://your-terabox-api.com"

def is_terabox(url):
    return "terabox" in url.lower()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "📥 Terabox link পাঠান")

@bot.message_handler(func=lambda message: True)
def handle_link(message):
    chat_id = message.chat.id
    url = message.text.strip()

    if not is_terabox(url):
        bot.send_message(chat_id, "❌ Valid Terabox link দিন")
        return

    bot.send_message(chat_id, "🔄 Folder পড়া হচ্ছে...")

    try:
        # 🔥 Folder list API call
        res = requests.get(f"{API_BASE}/list?url={url}").json()
        files = res.get("files", [])

        if not files:
            bot.send_message(chat_id, "❌ কোনো ফাইল পাওয়া যায়নি")
            return

        markup = InlineKeyboardMarkup()

        for file in files:
            btn = InlineKeyboardButton(
                text=file["name"],
                callback_data=file["download_url"]
            )
            markup.add(btn)

        bot.send_message(chat_id, "📂 ফাইল সিলেক্ট করুন:", reply_markup=markup)

    except:
        bot.send_message(chat_id, "❌ Error হয়েছে")

@bot.callback_query_handler(func=lambda call: True)
def send_download(call):
    bot.send_message(
        call.message.chat.id,
        f"📥 Download Link:\n{call.data}"
    )

bot.infinity_polling()
