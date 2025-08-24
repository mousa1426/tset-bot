import asyncio
import requests
from telegram.ext import Application, CommandHandler

# توکن رباتت رو اینجا بذار
TOKEN = "8255406778:AAHY4dInzMMPrEeDdMlssKFX_56RiB-buJg"

# آیدی عددی چت (خودت یا گروهت) رو اینجا بذار
CHAT_ID =   132429595

# دستور /start
async def start(update, context):
    await update.message.reply_text("سلام 👋 ربات روشنه ✅")

# تابع گرفتن داده واقعی (مثال: قیمت دلار از API رایگان)
def get_real_data():
    try:
        response = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=IRR")
        data = response.json()
        return f"📊 نرخ دلار: {data['rates']['IRR']} ریال"
    except:
        return "❌ خطا در دریافت داده"

# گزارش روزانه
async def send_daily_report(application):
    text = get_real_data()
    await application.bot.send_message(chat_id=CHAT_ID, text=text)

def main():
    # ساخت اپلیکیشن
    application = Application.builder().token(TOKEN).build()

    # هندلر برای /start
    application.add_handler(CommandHandler("start", start))

    # فعال‌سازی job_queue
    job_queue = application.job_queue
    job_queue.run_repeating(
        lambda ctx: asyncio.create_task(send_daily_report(application)),
        interval=3600,  # هر ۱ ساعت یک بار
        first=10        # اولین بار بعد از ۱۰ ثانیه
    )

    # اجرای ربات
    application.run_polling()

if __name__ == "__main__":
    main()
