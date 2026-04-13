import os
import asyncio
import telebot
from playwright.async_api import async_playwright

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

COOKIE_FILE = "cookies.json"


def load_cookies():
    # simple JSON cookie loader
    import json
    try:
        with open(COOKIE_FILE, "r") as f:
            return json.load(f)
    except:
        return []


async def terabox_download(url):
    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # 🍪 load cookies
        cookies = load_cookies()
        if cookies:
            await context.add_cookies(cookies)

        page = await context.new_page()

        # 1️⃣ open user link
        await page.goto(url)
        await page.wait_for_timeout(5000)

        # 2️⃣ try find download button
        try:
            await page.click("text=Download")
            await page.wait_for_timeout(5000)
        except:
            pass

        # 3️⃣ extract possible download links
        content = await page.content()

        await browser.close()

        return content


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send Terabox link 🎥")


@bot.message_handler(func=lambda m: True)
def handle(message):
    url = message.text

    bot.reply_to(message, "Login + searching file... ⏳")

    try:
        result = asyncio.run(terabox_download(url))

        if "http" in result:
            bot.reply_to(message, "File detected ✅ (download started internally)")
        else:
            bot.reply_to(message, "Download failed ❌ (button not found)")

    except Exception as e:
        bot.reply_to(message, f"Error ❌\n{str(e)}")


bot.polling()
