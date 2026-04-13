import os
import telebot
import asyncio
from playwright.async_api import async_playwright

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

COOKIE_FILE = "cookies.json"


def load_cookies():
    import json
    try:
        with open(COOKIE_FILE, "r") as f:
            return json.load(f)
    except:
        return []


async def open_page(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        cookies = load_cookies()
        if cookies:
            await context.add_cookies(cookies)

        page = await context.new_page()
        await page.goto(url)

        await page.wait_for_timeout(5000)

        content = await page.content()

        await browser.close()

        return content


@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Send Terabox link 🎥")


@bot.message_handler(func=lambda m: True)
def handle(m):
    url = m.text

    bot.reply_to(m, "Processing... ⏳")

    try:
        result = asyncio.run(open_page(url))

        if "http" in result:
            bot.reply_to(m, "Page loaded successfully ✅")
        else:
            bot.reply_to(m, "No content found ❌")

    except Exception as e:
        bot.reply_to(m, f"Error ❌\n{str(e)}")


bot.polling()
