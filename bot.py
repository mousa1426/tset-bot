import os
from telegram.ext import Application, CommandHandler

# اینجا BOT_TOKEN رو از Environment Variable می‌خونه
TOKEN = os.getenv("BOT_TOKEN")

app = Application.builder().token(TOKEN).build()

async def start(update, context):
    await update.message.reply_text("سلام! ربات روشنه ✅")

app.add_handler(CommandHandler("start", start))

if __name__ == "__main__":
    app.run_polling()
