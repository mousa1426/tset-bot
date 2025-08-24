import logging
import requests
import pandas as pd
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import datetime

# ----------------------------
# 🔑 توکن ربات تلگرام
TOKEN = "PUT-YOUR-BOT-TOKEN-HERE"
CHAT_ID = "PUT-YOUR-CHAT-ID-HERE"   # چت آی‌دی خودت برای ارسال خودکار
# ----------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------------------------
# 📊 گرفتن داده واقعی از TSETMC
def get_option_data():
    try:
        url = "http://www.tsetmc.com/tsev2/data/MarketWatchPlus.aspx"
        response = requests.get(url)
        response.encoding = "utf-8"

        rows = response.text.split(";")

        # فقط نمادهایی که "اختیار" هستن رو می‌گیریم
        option_rows = [r.split(",") for r in rows if "اختيار" in r]

        if not option_rows:
            return "❌ دیتایی از معاملات آپشن پیدا نشد."

        df = pd.DataFrame(option_rows)
        # ستون‌ها ممکنه تغییر کنن، ولی معمولاً اینجوریه:
        df = df[[0, 2, 3, 6, 7]]  # نماد، آخرین قیمت، تعداد معاملات، حجم، ارزش
        df.columns = ["نماد", "آخرین", "تعداد", "حجم", "ارزش"]

        # فقط 10 نماد اول برای خلاصه
        df = df.head(10)

        report = "📊 گزارش معاملات آپشن (TSETMC):\n\n"
        for idx, row in df.iterrows():
            report += f"🔹 {row['نماد']} | آخرین: {row['آخرین']} | حجم: {row['حجم']} | ارزش: {row['ارزش']}\n"

        return report

    except Exception as e:
        return f"⚠️ خطا در دریافت داده: {e}"

# ----------------------------
# ✅ دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات روشنه ✅\nبرای دریافت گزارش آپشن بزن /option")

# ✅ دستور /option
async def option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    report = get_option_data()
    await update.message.reply_text(report)

# ----------------------------
# ⏰ ارسال خودکار هر روز
async def send_daily_report(application: Application):
    while True:
        now = datetime.datetime.now()
        if now.hour == 10 and now.minute == 0:  # هر روز ساعت ۱۰:۰۰ صبح
            report = get_option_data()
            await application.bot.send_message(chat_id=CHAT_ID, text=report)
            await asyncio.sleep(60)
        await asyncio.sleep(20)

# ----------------------------
# 🚀 اجرای ربات
def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("option", option))

    # راه‌اندازی تسک پس‌زمینه
    application.job_queue.run_once(lambda ctx: asyncio.create_task(send_daily_report(application)), 1)

    application.run_polling()

if __name__ == "__main__":
    main()
