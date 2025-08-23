import os
from telegram.ext import Application, CommandHandler

TOKEN = os.getenv("TOKEN")

app = Application.builder().token(TOKEN).build()

async def start(update, context):
    await update.message.reply_text("سلام! ربات روشنه ✅")

app.add_handler(CommandHandler("start", start))

app.run_polling()
