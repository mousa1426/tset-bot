from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "Y8255406778:AAGM-juXZ8HfnzkbYhJy_6Hoemrs1nOkupE"

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات روشنه 🚀")

def main():
    # ساخت اپلیکیشن
    application = Application.builder().token(TOKEN).build()

    # اضافه کردن هندلر
    application.add_handler(CommandHandler("start", start))

    # شروع ربات
    application.run_polling()

if __name__ == "__main__":
    main()
