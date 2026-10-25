from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest
import os
from flask import Flask
import threading

TOKEN = os.getenv("TOKEN") or "8964751799:AAGERNIrze2zJoVdJHo4T6stomsK_CJcbwg"
def to_float(s):
    return float(s.replace(',', '.'))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot Kalkulator Position Size Siap!\n\n"
        "Cara pakai:\n"
        "/hitung modal risk% harga_entry harga_sl\n\n"
        "Contoh:\n"
        "/hitung 1000 1 50000 49000\n"
        "Artinya: Modal $1000, risk 1%, entry 50000, SL 49000"
    )

async def hitung(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        modal = float(context.args[0])
        risk_persen = float(context.args[1])
        entry = float(context.args[2])
        sl = float(context.args[3])

        risk_uang = modal * (risk_persen / 100)
        jarak_sl = abs(entry - sl)
        if jarak_sl == 0:
            raise ValueError("Entry dan SL tidak boleh sama")
        
        position_size = risk_uang / jarak_sl * entry # untuk futures/crypto
        # Atau kalau mau hitung lot/koin: position_size = risk_uang / jarak_sl
        
        qty = risk_uang / jarak_sl
        
        await update.message.reply_text(
            f"HASIL HITUNG:\n"
            f"Modal: ${modal}\n"
            f"Risk: {risk_persen}% = ${risk_uang}\n"
            f"Entry: {entry} | SL: {sl}\n"
            f"Jarak SL: {jarak_sl}\n\n"
            f"-> Qty / Koin yang boleh dibeli: {qty:.4f}\n"
            f"-> Position Size ($): ${qty * entry:.2f}\n\n"
            f"Jika kena SL, kamu rugi tepat ${risk_uang}"
        )
    except Exception as e:
        await update.message.reply_text(f"Format salah. Contoh: /hitung 1000 1 50000 49000\nError: {e}")
        
from flask import Flask
import threading
app = Flask(__name__)
@app.route('/')
def home(): return "Bot ON!"
def run_web():
    app.run(host='0.0.0.0', port=10000)
threading.Thread(target=run_web).start()
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hitung", hitung))
print("Bot sedang jalan... buka Telegram dan ketik /start")
app.run_polling()
