import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8255406778:AAFb3QdVHVQdzhVa0roFfOMpN6u5YzwKkVk"

# بارگذاری لیست اولیه نمادها
with open("options.json", "r", encoding="utf-8") as f:
    options = json.load(f)

# سهم پایه (مثال: اهرم)
BASE_SHARE = {"inscode": "123456789", "name": "اهرم"}
if BASE_SHARE not in options:
    options.append(BASE_SHARE)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ربات روشن است. از /help برای راهنما استفاده کنید.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "/add <inscode> ➕ اضافه کردن نماد\n"
        "/list 📋 لیست نمادها\n"
        "/report 📊 گزارش فوری\n"
    )
    await update.message.reply_text(text)

async def add_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ لطفاً inscode را وارد کنید.")
        return
    inscode = context.args[0]
    new_item = {"inscode": inscode, "name": f"نماد {inscode}"}
    if new_item not in options:
        options.append(new_item)
        with open("options.json", "w", encoding="utf-8") as f:
            json.dump(options, f, ensure_ascii=False, indent=2)
        await update.message.reply_text(f"✅ نماد {inscode} اضافه شد.")
    else:
        await update.message.reply_text("⚠️ این نماد قبلاً ثبت شده است.")

async def list_symbols(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not options:
        await update.message.reply_text("⚠️ هیچ نمادی ثبت نشده.")
        return
    text = "📋 لیست نمادها:\n" + "\n".join([f"- {opt['name']} ({opt['inscode']})" for opt in options])
    await update.message.reply_text(text)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("add", add_symbol))
    app.add_handler(CommandHandler("list", list_symbols))

    app.run_polling()

if __name__ == "__main__":
    main()
