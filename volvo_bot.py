
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from binance.client import Client
import asyncio

# API Keys
TELEGRAM_TOKEN = "7300093292:AAFn0XkEppHk9I__y5MN9Vvz4ZtBrPJbf9Y"
BINANCE_API_KEY = "l5Dg6lUTdxuDLPottXxZxCkF2Et2IgzAQT1JrfmUZN3PwTVZhmcFdrvVyAugDoT0"
BINANCE_API_SECRET = "ypcUtkIgDnlTB13XE09PRTrMUEPkcCiz2QKxsKs1WAy3B5rNw8zg0XffHTBMpvdR"

# Binance client
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

# Logging
logging.basicConfig(level=logging.INFO)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Умний бот ишга тушди!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        balance = client.futures_account_balance()
        usdt_balance = next((b['balance'] for b in balance if b['asset'] == 'USDT'), "0")
        await update.message.reply_text(f"USDT Баланс: {usdt_balance}")
    except Exception as e:
        await update.message.reply_text(f"Хатолик: {str(e)}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот тўхтатилди.")
    asyncio.get_event_loop().stop()

# Application
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("stop", stop))

# Run bot
print("Бот тайёр. Telegram буйруқ кутаяпти...")
app.run_polling()
