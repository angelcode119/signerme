# 🚀 Multi-Bot Runner

راهنمای اجرای همزمان دو ربات

## 📋 روش‌های اجرا

### 1️⃣ **Python Runner (توصیه شده - همه سیستم‌ها)**

```bash
python run_bots.py
```

**ویژگی‌ها:**
- ✅ کار می‌کند روی Windows, Linux, Mac
- ✅ رنگ‌بندی زیبا در Terminal
- ✅ مانیتور کردن خودکار
- ✅ Ctrl+C برای توقف همزمان

---

### 2️⃣ **Windows Batch File**

```bash
run_bots.bat
```

**ویژگی‌ها:**
- ✅ باز شدن در پنجره‌های جداگانه
- ✅ راحت برای دیباگ
- ✅ دابل کلیک برای اجرا

---

### 3️⃣ **Linux/Mac Shell Script**

```bash
chmod +x run_bots.sh
./run_bots.sh
```

**ویژگی‌ها:**
- ✅ اجرا در background
- ✅ لاگ در فایل‌های جداگانه
- ✅ رنگ‌بندی Terminal

---

## 🎯 ربات‌ها

### ✨ **Bot 1 - APK Generator Studio**
- فایل: `m.py`
- لاگ: `bot.log`
- قابلیت: ساخت APK با شخصی‌سازی

### 🔍 **Bot 2 - APK Analyzer Studio**
- فایل: `bot2.py`
- لاگ: `bot2.log`
- قابلیت: تحلیل و استخراج اطلاعات APK

---

## 🛑 توقف ربات‌ها

### Python Runner:
```
Ctrl + C
```

### Windows Batch:
```
بستن پنجره‌ها یا Ctrl + C در هر پنجره
```

### Linux/Mac Shell:
```
Ctrl + C
```

---

## 📊 مانیتور کردن

### دیدن لاگ‌ها (Linux/Mac):

**Bot 1:**
```bash
tail -f bot1.log
```

**Bot 2:**
```bash
tail -f bot2.log
```

### دیدن لاگ‌ها (همه سیستم‌ها):

**Bot 1:**
```bash
python -c "import time; f=open('bot.log'); f.seek(0,2); 
while True: 
    line=f.readline(); 
    if line: print(line.strip()); 
    time.sleep(0.1)"
```

---

## ⚡ Quick Start

### یک خط (Python):
```bash
python run_bots.py
```

### یک خط (Windows):
```bash
run_bots.bat
```

### یک خط (Linux/Mac):
```bash
chmod +x run_bots.sh && ./run_bots.sh
```

---

## 🔧 نیازمندی‌ها

```bash
pip install -r requirements.txt
```

**محتوای requirements.txt:**
```
telethon
aiohttp
```

---

## 📝 نکات

1. **پورت‌ها:** هر ربات از session جداگانه استفاده می‌کند
2. **Database:** فایل‌های users جداگانه دارند
3. **توکن:** هر ربات باید توکن مخصوص خودش را داشته باشد
4. **لاگ:** لاگ‌های جداگانه برای debug آسان‌تر

---

## 🐛 عیب‌یابی

### ربات شروع نمی‌شود:
```bash
# بررسی فایل‌ها
ls -la m.py bot2.py

# بررسی مجوزها (Linux/Mac)
chmod +x m.py bot2.py

# بررسی Python
python --version
```

### خطای Import:
```bash
pip install -r requirements.txt --upgrade
```

### خطای Session:
```bash
rm -f *.session*
```

---

## 💡 توصیه‌ها

✅ **برای Development:** استفاده از Python Runner
✅ **برای Production:** استفاده از systemd/pm2
✅ **برای Debug:** اجرای manual هر ربات
✅ **برای Monitor:** استفاده از tmux/screen

---

## 🎨 Output مثال

```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║  🚀  Multi-Bot Runner - Professional Edition 🚀          ║
║                                                           ║
║  ✨ APK Generator Studio                                 ║
║  🔍 APK Analyzer Studio                                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

✅ All bot files found

Starting bots...

[Bot 1 - Generator] Starting...
[Bot 1 - Generator] Started! PID: 12345

[Bot 2 - Analyzer] Starting...
[Bot 2 - Analyzer] Started! PID: 12346

✅ All bots started successfully!
Press Ctrl+C to stop all bots
```
