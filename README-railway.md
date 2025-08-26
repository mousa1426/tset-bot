# استقرار روی Railway

1. ریپوی گیتهاب بساز و فایل‌های bot.py و requirements.txt و این README را بذار.
2. در Railway: New Project → Deploy from GitHub.
3. Service Type را روی Worker بذار.
4. Variables:
   - BOT_TOKEN = توکن ربات
   - CHAT_ID = آیدی عددی یا به‌جاش TARGET_USERNAME = @YourUserName
   - SYMBOLS = اهرم
   - NIXPACKS_PYTHON_VERSION = 3.12
   - TZ = Asia/Tehran
5. Start Command: python bot.py
