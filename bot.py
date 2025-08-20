import logging
from telegram.ext import Updater, CommandHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update, context):
    update.message.reply_text("سلام! رباتت روی Render فعال شد 🚀")

def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("⚠️ BOT_TOKEN تنظیم نشده!")
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
