import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from binance.client import Client
from binance.enums import *
import asyncio

# API
TELEGRAM_TOKEN = "7300093292:AAFn0XkEppHk9I__y5MN9Vvz4ZtBrPJbf9Y"
BINANCE_API_KEY = "l5Dg6lUTdxuDLPottXxZxCkF2Et2lgzAQT1JrfmUZN3PwTVZhmcFdrvVyAugDoTO"
BINANCE_API_SECRET = "ypcUtklgDnITB13XE09PRTrMUEPkcCiz2QKxsKs1WAy3B5rNw8zg0XffHTBMpvdR"

client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

symbol = "SOLUSDT"
leverage = 40
usdt_amount = 30
sl_percent = 0.5
tp_percent = 1.0

logging.basicConfig(level=logging.INFO)

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

def calculate_qty(price):
    position_size = usdt_amount * leverage
    qty = round(position_size / price, 3)
    return qty

async def long_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(client.get_symbol_ticker(symbol=symbol)["price"])
        quantity = calculate_qty(price)
        sl = round(price * (1 - sl_percent / 100), 2)
        tp = round(price * (1 + tp_percent / 100), 2)

        client.futures_change_leverage(symbol=symbol, leverage=leverage)
        client.futures_create_order(symbol=symbol, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=quantity)
        client.futures_create_order(symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_STOP_MARKET, stopPrice=sl, closePosition=True)
        client.futures_create_order(symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_TAKE_PROFIT_MARKET, stopPrice=tp, closePosition=True)

        await update.message.reply_text(f"✅ ЛОНГ очилди:\nНарх: {price}\nҲажм: {quantity} SOL\nSL: {sl}\nTP: {tp}")
    except Exception as e:
        await update.message.reply_text(f"❌ Хатолик: {str(e)}")

async def short_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(client.get_symbol_ticker(symbol=symbol)["price"])
        quantity = calculate_qty(price)
        sl = round(price * (1 + sl_percent / 100), 2)
        tp = round(price * (1 - tp_percent / 100), 2)

        client.futures_change_leverage(symbol=symbol, leverage=leverage)
        client.futures_create_order(symbol=symbol, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=quantity)
        client.futures_create_order(symbol=symbol, side=SIDE_BUY, type=ORDER_TYPE_STOP_MARKET, stopPrice=sl, closePosition=True)
        client.futures_create_order(symbol=symbol, side=SIDE_BUY, type=ORDER_TYPE_TAKE_PROFIT_MARKET, stopPrice=tp, closePosition=True)

        await update.message.reply_text(f"✅ ШОРТ очилди:\nНарх: {price}\nҲажм: {quantity} SOL\nSL: {sl}\nTP: {tp}")
    except Exception as e:
        await update.message.reply_text(f"❌ Хатолик: {str(e)}")

# Bot setup
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("stop", stop))
app.add_handler(CommandHandler("long", long_order))
app.add_handler(CommandHandler("short", short_order))

print("Бот тайёр. Telegram буйруқ кутаяпти...")
app.run_polling()
