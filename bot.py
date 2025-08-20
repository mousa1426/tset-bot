from telegram.ext import Application, CommandHandler

# توکن رباتی که از BotFather گرفتی
TOKEN = "8255406778:AAGM-juXZ8HfnzkbYhJy_6Hoemrs1nOkupE"

async def start(update, context):
    await update.message.reply_text("سلام ✌️ ربات آپشن روشن شد.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.run_polling()

if __name__ == "__main__":
    main()
