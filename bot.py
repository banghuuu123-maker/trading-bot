import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Kalkulator Position Size Siap!\n\n"
        "Cara pakai:\n"
        "/hitung modal risk% harga_entry harga_sl\n"
        "atau dengan TP:\n"
        "/hitung modal risk% harga_entry harga_tp harga_sl\n\n"
        "Contoh:\n"
        "/hitung 1000 1 50000 49000\n"
        "/hitung 54 2.5 0.7943 0.9642 0.7383"
    )

async def hitung(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if len(args) < 4:
            await update.message.reply_text(
                "❌ Format salah!\n"
                "Gunakan: /hitung modal risk% entry sl\n"
                "Contoh: /hitung 1000 1 50000 49000\n"
                "Atau: /hitung 1000 1 50000 52000 49000 (dengan TP)"
            )
            return

        modal = float(args[0])
        risk_percent = float(args[1])

        if len(args) == 4:
            entry = float(args[2])
            sl = float(args[3])
            tp = None
        else:
            entry = float(args[2])
            tp = float(args[3])
            sl = float(args[4])

        risk_usd = modal * risk_percent / 100.0
        is_long = sl < entry if tp is None else (tp > entry and sl < entry)
        if tp is not None and not (tp > entry and sl < entry) and not (tp < entry and sl > entry):
            is_long = sl < entry

        jarak_sl = abs(entry - sl)
        qty = risk_usd / jarak_sl
        position_size = qty * entry

        rr_text = ""
        profit_text = ""
        if tp is not None:
            jarak_tp = abs(tp - entry)
            rr = jarak_tp / jarak_sl
            profit_usd = qty * jarak_tp
            profit_percent = (profit_usd / modal * 100)
            rr_status = "✅ RR Bagus!" if rr >= 1.5 else "⚠️ RR Cukup" if rr >= 1 else "❌ RR Kecil, hati-hati"
            rr_text = f"-> Risk/Reward: 1 : {rr:.2f}\n{rr_status}\n"
            profit_text = f"-> Profit jika TP kena: ${profit_usd:.2f} ({profit_percent:.2f}%)\n"

        tipe = "LONG 🟢" if is_long else "SHORT 🔴"
        
        def fmt(x):
            if abs(x) >= 1000: return f"{x:.2f}"
            elif abs(x) >= 1: return f"{x:.4f}"
            else: return f"{x:.6f}".rstrip('0').rstrip('.')

        msg = f"📊 HASIL HITUNG - {tipe}\nModal: ${modal}\nRisk: {risk_percent}% = ${risk_usd:.2f}\nEntry: {fmt(entry)} | SL: {fmt(sl)}"
        if tp is not None: msg += f" | TP: {fmt(tp)}"
        msg += f"\nJarak SL: {fmt(jarak_sl)}\n\n-> Qty / Koin yang boleh dibeli: {fmt(qty)}\n-> Position Size ($): ${position_size:.2f}\n\n"
        if profit_text: msg += profit_text
        if rr_text: msg += rr_text + "\n"
        msg += f"Jika kena SL, kamu rugi tepat ${risk_usd:.2f}"
        await update.message.reply_text(msg)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hitung", hitung))
    print("Bot ON!")
    app.run_polling()

if __name__ == "__main__":
    main()
