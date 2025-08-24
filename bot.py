from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات روشنه ✅")

# هندل کردن پیام‌های عادی
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"پیام شما: {update.message.text}")

def main():
    # توکن رو از محیط می‌خونه (Render → Environment Variables)
    import os
    TOKEN = os.getenv("BOT_TOKEN")

    # ساخت اپلیکیشن
    app = ApplicationBuilder().token(TOKEN).build()

    # دستور /start
    app.add_handler(CommandHandler("start", start))

    # هندل پیام‌ها
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # اجرا
    app.run_polling()

if __name__ == "__main__":
    main()
