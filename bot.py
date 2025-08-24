import os
import io
import pandas as pd
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode

TOKEN = os.getenv("BOT_TOKEN")

# حافظه ساده برای هر کاربر
USER_STATE = {}  # chat_id -> {"csv_path": str, "spot": float}

HELP_TEXT = (
    "سلام! 👋\n\n"
    "این ربات نسخه‌ی آزمایشیِ تحلیل اختیار معاملهٔ بورس ایران است.\n\n"
    "دستورات:\n"
    "/start – شروع\n"
    "/help – راهنما\n"
    "/setspot <price> – تنظیم قیمت دارایی پایه (اختیاری)\n"
    "/analysis – اجرای تحلیل روی آخرین فایل CSV که فرستادی\n\n"
    "نحوهٔ استفاده:\n"
    "1) از سایت مورد نظرت (مثلاً TSETMC یا هر منبع دیگری) زنجیره‌ی اختیار معامله را به **CSV** خروجی بگیر.\n"
    "2) فایل **CSV** را همین‌جا برای ربات ارسال کن.\n"
    "3) دستور /analysis را بزن تا خلاصهٔ تحلیل برگردانده شود.\n\n"
    "ستون‌های پیشنهادی CSV (نام‌ها بهتره انگلیسی باشند):\n"
    "symbol,type,strike,last,bid,ask,volume,open_interest,expiry,underlying\n"
    "type = C یا P\n"
)

def start(update, context):
    update.message.reply_text(
        "✅ ربات روشنه.\n"
        "برای راهنما: /help\n"
        "برای تحلیل: فایل CSV آپلود کن و بعد /analysis بزن."
    )

def help_cmd(update, context):
    update.message.reply_text(HELP_TEXT)

def setspot(update, context):
    chat_id = update.message.chat_id
    if len(context.args) != 1:
        update.message.reply_text("مثال: /setspot 123456")
        return
    try:
        spot = float(context.args[0])
    except Exception:
        update.message.reply_text("عدد معتبر وارد کن. مثال: /setspot 123456")
        return
    st = USER_STATE.get(chat_id, {})
    st["spot"] = spot
    USER_STATE[chat_id] = st
    update.message.reply_text(f"✅ قیمت دارایی پایه تنظیم شد: {spot}")

def save_csv_file(update, context):
    """دریافت فایل CSV و ذخیره در /tmp"""
    chat_id = update.message.chat_id
    doc = update.message.document

    if not doc:
        update.message.reply_text("فقط فایل ارسال کن لطفاً.")
        return

    # فقط CSV
    filename = doc.file_name or "options.csv"
    if not filename.lower().endswith(".csv"):
        update.message.reply_text("⚠️ لطفاً فایل با پسوند CSV بفرست.")
        return

    file_obj = doc.get_file()
    file_bytes = file_obj.download_as_bytearray()

    path = f"/tmp/options_{chat_id}.csv"
    with open(path, "wb") as f:
        f.write(file_bytes)

    st = USER_STATE.get(chat_id, {})
    st["csv_path"] = path
    USER_STATE[chat_id] = st

    update.message.reply_text("✅ فایل CSV ذخیره شد. حالا دستور /analysis رو بزن.")

def _normalize_columns(df):
    """ستون‌ها را به اسامی استاندارد نگاشت می‌کند تا انعطاف داشته باشیم."""
    mapping = {
        "symbol": ["symbol", "نماد", "contract", "contract_symbol"],
        "type": ["type", "نوع", "option_type", "call_put", "cp"],
        "strike": ["strike", "قیمت اعمال", "strike_price"],
        "last": ["last", "آخرین", "last_price"],
        "bid": ["bid", "خرید"],
        "ask": ["ask", "فروش"],
        "volume": ["volume", "حجم", "vol"],
        "open_interest": ["open_interest", "oi", "سود باز", "openinterest"],
        "expiry": ["expiry", "سررسید", "exp", "maturity"],
        "underlying": ["underlying", "spot", "base", "قیمت پایه"],
    }

    cols = {c.lower().strip(): c for c in df.columns}
    out = {}
    for std_name, aliases in mapping.items():
        for ali in aliases:
            if ali.lower() in cols:
                out[std_name] = cols[ali.lower()]
                break
    # فقط ستون‌های موجود را نگه می‌داریم
    picked = {k: v for k, v in out.items()}
    return df.rename(columns=picked)

def analyze(update, context):
    chat_id = update.message.chat_id
    st = USER_STATE.get(chat_id, {})
    csv_path = st.get("csv_path")

    if not csv_path or not os.path.exists(csv_path):
        update.message.reply_text("اول یک فایل CSV بفرست، بعد /analysis بزن.")
        return

    try:
        # خواندن CSV با حدس Encoding
        try:
            df = pd.read_csv(csv_path)
        except UnicodeDecodeError:
            df = pd.read_csv(csv_path, encoding="utf-8-sig")
    except Exception as e:
        update.message.reply_text(f"خواندن CSV ناموفق بود: {e}")
        return

    if df.empty:
        update.message.reply_text("فایل CSV خالیه.")
        return

    df = _normalize_columns(df)

    # پاکسازی پایه
    for col in ["type", "symbol"]:
        if col in df.columns:
            df[col] = df[col].astype(str)

    for col in ["strike", "last", "bid", "ask", "volume", "open_interest", "underlying"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # تفکیک کال/پوت
    def _is_call(x):
        x = str(x).strip().lower()
        return x in ["c", "call", "کال", "خرید"]

    def _is_put(x):
        x = str(x).strip().lower()
        return x in ["p", "put", "پوت", "فروش"]

    df["is_call"] = df["type"].apply(_is_call) if "type" in df.columns else False
    df["is_put"] = df["type"].apply(_is_put) if "type" in df.columns else False

    # محاسبات ساده
    total_vol = df["volume"].sum() if "volume" in df.columns else None
    total_oi = df["open_interest"].sum() if "open_interest" in df.columns else None

    vol_call = df.loc[df["is_call"], "volume"].sum() if "volume" in df.columns else None
    vol_put = df.loc[df["is_put"], "volume"].sum() if "volume" in df.columns else None

    oi_call = df.loc[df["is_call"], "open_interest"].sum() if "open_interest" in df.columns else None
    oi_put = df.loc[df["is_put"], "open_interest"].sum() if "open_interest" in df.columns else None

    pcr_vol = (vol_put / vol_call) if vol_call and vol_call > 0 else None
    pcr_oi = (oi_put / oi_call) if oi_call and oi_call > 0 else None

    # تاپ‌ها
    def top_table(by_col, n=5):
        if by_col in df.columns:
            tmp = df.sort_values(by_col, ascending=False).head(n)
            cols = [c for c in ["symbol", "type", "strike", by_col, "last"] if c in tmp.columns]
            return tmp[cols]
        return None

    top_vol = top_table("volume", 5)
    top_oi = top_table("open_interest", 5)

    # قیمت پایه (اختیاری)
    spot = st.get("spot")
    if not spot and "underlying" in df.columns:
        # اگر ستون underlying وجود داشته باشد، میانگین می‌گیریم
        spot_guess = df["underlying"].dropna()
        if len(spot_guess) > 0:
            spot = float(spot_guess.mean())
            st["spot"] = spot
            USER_STATE[chat_id] = st

    # ساخت خروجی متنی
    lines = []
    lines.append("🧾 *خلاصهٔ تحلیل آپشن – بورس ایران*")
    if spot:
        lines.append(f"• قیمت دارایی پایه (spot): `{spot:,.0f}`")

    if total_vol is not None:
        lines.append(f"• حجم کل معاملات (Volume): `{int(total_vol):,}`")
    if total_oi is not None:
        lines.append(f"• مجموع موقعیت‌های باز (Open Interest): `{int(total_oi):,}`")

    if vol_call is not None and vol_put is not None:
        lines.append(f"• حجم Call: `{int(vol_call):,}` | حجم Put: `{int(vol_put):,}`")
    if pcr_vol is not None:
        lines.append(f"• Put/Call Ratio (Volume): `{pcr_vol:.2f}`")

    if oi_call is not None and oi_put is not None:
        lines.append(f"• OI Call: `{int(oi_call):,}` | OI Put: `{int(oi_put):,}`")
    if pcr_oi is not None:
        lines.append(f"• Put/Call Ratio (OI): `{pcr_oi:.2f}`")

    msg = "\n".join(lines)
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    # ارسال تاپ‌ها به‌صورت متن جمع‌وجور
    def table_to_text(df_, title):
        if df_ is None or df_.empty:
            return f"*{title}:* اطلاعات موجود نیست."
        rows = []
        rows.append(f"*{title}:*")
        for _, r in df_.iterrows():
            sym = r.get("symbol", "")
            typ = r.get("type", "")
            strike = r.get("strike", "")
            last = r.get("last", "")
            byv = r.get("volume", r.get("open_interest", ""))
            label = "Vol" if "volume" in df_.columns else "OI"
            rows.append(f"• `{sym}` ({typ})  |  K={strike}  |  {label}={byv}  |  Last={last}")
        return "\n".join(rows)

    update.message.reply_text(
        table_to_text(top_vol, "Top 5 بر اساس Volume"),
        parse_mode=ParseMode.MARKDOWN
    )
    update.message.reply_text(
        table_to_text(top_oi, "Top 5 بر اساس Open Interest"),
        parse_mode=ParseMode.MARKDOWN
    )

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("setspot", setspot))
    dp.add_handler(CommandHandler("analysis", analyze))

    # دریافت فایل CSV
    dp.add_handler(MessageHandler(Filters.document, save_csv_file))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
