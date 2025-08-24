import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# توکن ربات از محیط
BOT_TOKEN = "8255406778:AAFb3QdVHVQdzhVa0roFfOMpN6u5YzwKkVk"

# نمادهای ثبت شده
watchlist = []

# تنظیمات لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# گرفتن داده از TSETMC
def fetch_data(inscode):
    try:
        url = f"https://cdn.tsetmc.com/api/Instrument/GetInstrumentInfo/{inscode}"
        r = requests.get(url, timeout=10)
        data = r.json().get("instrumentInfo", {}).get("lVal18AFC", "Unknown")

        url2 = f"https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceInfo/{inscode}"
        r2 = requests.get(url2, timeout=10)
        last_price = r2.json().get("closingPriceInfo", {}).get("pClosing", 0)

        return f"{data}: {last_price:,}"
    except Exception as e:
        return f"خطا در دریافت داده برای {inscode}: {e}"

# دستورات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ربات روشن است. از /help برای راهنما استفاده کنید.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/add <inscode> ➡️ اضافه کردن نماد\n"
        "/list ➡️ لیست نمادها\n"
        "/report ➡️ گزارش فوری\n"
        "/start_reports ➡️ شروع گزارش‌گیری دوره‌ای\n"
        "/stop_reports ➡️ توقف گزارش‌گیری"
    )

async def add_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ کد نماد (inscode) را وارد کنید.")
        return
    ins = context.args[0]
    if ins not in watchlist:
        watchlist.append(ins)
        await update.message.reply_text(f"➕ نماد {ins} اضافه شد.")
    else:
        await update.message.reply_text("این نماد قبلاً ثبت شده است.")

async def list_symbols(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not watchlist:
        await update.message.reply_text("هیچ نمادی ثبت نشده.")
    else:
        await update.message.reply_text("📌 لیست نمادها:\n" + "\n".join(watchlist))

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not watchlist:
        await update.message.reply_text("⚠️ هیچ نمادی ثبت نشده.")
        return
    msgs = [fetch_data(ins) for ins in watchlist]
    await update.message.reply_text("\n".join(msgs))

# گزارش دوره‌ای
async def scheduled_report(context: ContextTypes.DEFAULT_TYPE):
    if not watchlist:
        return
    msgs = [fetch_data(ins) for ins in watchlist]
    await context.bot.send_message(chat_id=context.job.chat_id, text="\n".join(msgs))

async def start_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    job_queue = context.application.job_queue
    job_queue.run_repeating(scheduled_report, interval=900, first=10, chat_id=chat_id)
    await update.message.reply_text("📢 گزارش‌دهی دوره‌ای شروع شد (هر ۱۵ دقیقه).")

async def stop_reports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.application.job_queue.stop()
    await update.message.reply_text("⛔ گزارش‌دهی متوقف شد.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("add", add_symbol))
    app.add_handler(CommandHandler("list", list_symbols))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(CommandHandler("start_reports", start_reports))
    app.add_handler(CommandHandler("stop_reports", stop_reports))

    app.run_polling()

if __name__ == "__main__":
    main()
