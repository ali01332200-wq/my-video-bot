import telebot
import os
import re

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

def normalize_link(url):
    url = url.strip()

    # 1024tera → terabox convert
    url = url.replace("1024tera.com", "terabox.com")

    return url

def is_valid_format(url):
    return "tera" in url

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "📥 Terabox link পাঠান")

@bot.message_handler(func=lambda m: True)
def handle(m):
    url = normalize_link(m.text)

    if not is_valid_format(url):
        bot.send_message(m.chat.id, "❌ Invalid link format")
        return

    # 🔥 Here API call should go
    bot.send_message(
        m.chat.id,
        "🔄 Link process করা হচ্ছে...\n\n"
        "⚠️ যদি file না পাওয়া যায় তাহলে link expired বা private হতে পারে"
    )

    # simulate response (real API লাগবে)
    bot.send_message(m.chat.id, f"📎 Processed link:\n{url}")

bot.infinity_polling()
