import os, asyncio, logging
from typing import List
import httpx
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("options-bot")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()
TARGET_USERNAME = os.getenv("TARGET_USERNAME", "").strip()
SYMBOLS = [s.strip() for s in os.getenv("SYMBOLS", "اهرم").split(",") if s.strip()]
SEND_ON_STARTUP = os.getenv("SEND_ON_STARTUP", "1") == "1"
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", "3600"))

if not BOT_TOKEN:
    raise SystemExit("❌ BOT_TOKEN را در متغیرهای محیطی تنظیم کن.")

async def search_candidates_from_tsetmc(keyword: str) -> List[dict]:
    url = f"https://tsetmc.com/InstSearch/{keyword}"
    out = []
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return out
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                text = (a.get_text() or "").strip()
                href = a["href"]
                if not text:
                    continue
                if ("اختيار" in text) or text.startswith("ض"):
                    out.append({"name": text, "href": href})
            return out[:30]
    except Exception as e:
        log.exception("search failed: %s", e)
        return out

async def get_option_chain_snapshot(base_symbol_fa: str) -> str:
    cands = await search_candidates_from_tsetmc(base_symbol_fa)
    if not cands:
        return f"🔎 برای «{base_symbol_fa}» موردی پیدا نشد."
    lines = [f"🧾 چند قرارداد «اختیار» مرتبط با «{base_symbol_fa}» پیدا شد:"]
    for i, c in enumerate(cands, 1):
        name = c["name"]
        lines.append(f"{i:02d}. {name}")
    lines.append("⚠️ این لیست ممکن است کامل نباشد.")
    return "\n".join(lines)

async def _resolve_target_chat_id(app: Application) -> int:
    if CHAT_ID:
        try:
            return int(CHAT_ID)
        except:
            log.warning("CHAT_ID عددی نبود؛ تلاش با TARGET_USERNAME")
    if TARGET_USERNAME:
        chat = await app.bot.get_chat(TARGET_USERNAME)
        return chat.id
    raise RuntimeError("نه CHAT_ID و نه TARGET_USERNAME تنظیم نشده‌اند.")

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! دستور نمونه: /chain اهرم")

async def cmd_chain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("نماد پایه را بده: مثلا /chain اهرم")
        return
    base = " ".join(context.args).strip()
    msg = await get_option_chain_snapshot(base)
    await update.message.reply_text(msg)

async def periodic_worker(app: Application, target_chat_id: int):
    while True:
        try:
            for base in SYMBOLS:
                txt = await get_option_chain_snapshot(base)
                await app.bot.send_message(chat_id=target_chat_id, text=txt)
                await asyncio.sleep(2)
        except Exception as e:
            log.exception("periodic_worker error: %s", e)
        await asyncio.sleep(INTERVAL_SECONDS)

async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("chain", cmd_chain))

    async with application:
        target_id = await _resolve_target_chat_id(application)
        log.info("Target chat id: %s", target_id)
        if SEND_ON_STARTUP:
            await application.bot.send_message(chat_id=target_id, text="✅ ربات روی Railway بالا آمد.")
        asyncio.create_task(periodic_worker(application, target_id))
        await application.run_polling(close_loop=False)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
