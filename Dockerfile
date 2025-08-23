# استفاده از نسخه پایدار پایتون
FROM python:3.10-slim

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی کردن فایل‌های موردنیاز
COPY requirements.txt .

# نصب وابستگی‌ها
RUN pip install --no-cache-dir -r requirements.txt

# کپی کل پروژه
COPY . .

# اجرای بات
CMD ["python", "bot.py"]
