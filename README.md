# 🚀 APK Studio - Professional Edition

Two powerful Telegram bots for APK processing

## 🤖 ربات‌ها

### ✨ Bot 1: APK Generator Studio
- ساخت APK با شخصی‌سازی کامل
- انتخاب از چندین برنامه
- تم‌های سفارشی
- رمزنگاری و امضای حرفه‌ای

### 🔍 Bot 2: APK Analyzer Studio  
- تحلیل فایل‌های APK
- استخراج آیکون و اطلاعات
- نمایش اطلاعات کامل برنامه

---

## 📦 نصب

### 1️⃣ دانلود:
```bash
git clone https://github.com/angelcode119/signerme.git
cd signerme
```

### 2️⃣ نصب کتابخانه‌ها:
```bash
pip install -r requirements.txt
```

### 3️⃣ تنظیم توکن‌ها:
فایل `modules/config.py` را باز کنید:

```python
BOT_TOKEN = 'توکن_ربات_اول'    # ✅ از قبل تنظیم شده
BOT2_TOKEN = 'توکن_ربات_دوم'   # ⚠️ باید تنظیم کنید
```

**نحوه دریافت توکن دوم:**
1. به `@BotFather` بروید
2. `/newbot` بفرستید
3. نام و username دلخواه
4. توکن را کپی کنید

---

## 🚀 اجرا

### اجرای هر دو ربات:
```bash
python run.py
```

### اجرای جداگانه:
```bash
python bots/bot1_generator.py  # ربات 1
python bots/bot2_analyzer.py   # ربات 2
```

---

## 📁 ساختار

```
signerme/
├── bots/          # ربات‌ها
├── modules/       # ماژول‌های اصلی
├── data/          # Session ها و کاربران
├── logs/          # لاگ‌ها
├── apks/          # APK های پایه
└── docs/          # مستندات
```

---

## 📖 مستندات

- [نصب و راه‌اندازی](docs/INSTALLATION.md)
- [تنظیم توکن‌ها](docs/SETUP_TOKENS.md)
- [ساختار پروژه](docs/PROJECT_STRUCTURE.md)

---

## 🎯 استفاده

### ربات 1 (Generator):
1. `/start` → انتخاب برنامه
2. Quick یا Custom → ساخت APK

### ربات 2 (Analyzer):
1. `/start` → احراز هویت
2. ارسال فایل APK → دریافت اطلاعات

---

## ⚡ Quick Start

```bash
git clone https://github.com/angelcode119/signerme.git
cd signerme
pip install telethon aiohttp
python run.py
```

---

## 🔐 امنیت

- احراز هویت OTP
- Session های جداگانه
- محدودیت همزمانی
- پاک‌سازی خودکار

---

## 📝 نیازمندی‌ها

- Python 3.8+
- Java (برای apktool و apksigner)
- Telethon
- aiohttp

---

Made with ❤️ by APK Studio
