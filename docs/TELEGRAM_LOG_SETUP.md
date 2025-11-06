# 📊 راهنمای تنظیم Telegram Log Channel

## 🎯 قابلیت‌ها:

✅ دریافت log هر build در کانال  
✅ مشخصات کاربر (user_id, username)  
✅ جزییات build (app name, size, duration)  
✅ وضعیت (start, success, fail)  
✅ چک admin status  

---

## 📋 مراحل تنظیم:

### **1️⃣ ساخت کانال**

```
1. تو تلگرام: New Channel
2. اسم: APK Studio Logs
3. نوع: Private
4. ساخت کانال
```

### **2️⃣ اضافه کردن Bot به کانال**

```
1. تو کانال: Add Members
2. جستجو: @YourBot1 و @YourBot2
3. اضافه کردن هر دو بات
4. Promote to Admin:
   - Bot1: Admin
   - Bot2: Admin
   - Permissions: Post Messages ✅
```

### **3️⃣ گرفتن Channel ID**

**روش A: با Bot**
```python
# Send این message به کانال:
/start

# Bot forward کن به @userinfobot
# نتیجه: Chat ID
```

**روش B: با کد**
```python
from telethon import TelegramClient

client = TelegramClient('session', API_ID, API_HASH)
async with client:
    async for dialog in client.iter_dialogs():
        if dialog.name == 'APK Studio Logs':
            print(f"Channel ID: {dialog.id}")
```

**روش C: Web Telegram**
```
1. باز کن: https://web.telegram.org
2. برو تو کانال
3. URL: https://web.telegram.org/k/#-1001234567890
4. عدد بعد از #: -1001234567890 ← این Channel ID است!
```

### **4️⃣ تنظیم در کد**

فایل: `modules/config.py`

```python
# Telegram Log Channel
LOG_CHANNEL_ID = -1001234567890  # ← Channel ID خودت
```

**یا اگه نمی‌خوای:**
```python
LOG_CHANNEL_ID = None  # Disabled
```

### **5️⃣ Restart بات**

```bash
# Restart کن
python run.py
```

**Log startup:**
```
✅ Telegram logger enabled: -1001234567890
Bot2 (Payload Injector) started and ready!
```

---

## 📱 نمونه Log ها:

### **🚀 Build Start:**
```
🚀 Build Started
━━━━━━━━━━━━━━━━━━━━
👤 User: 7053561971
📝 Username: angel
📱 App: Viral Hub
📦 Package: dApp.binance
💾 Size: 6.0 MB
🤖 Bot: Payload Injector
⏰ Time: 2025-11-06 21:30:15
```

### **✅ Build Success:**
```
✅ Build Successful
━━━━━━━━━━━━━━━━━━━━
👤 User: 7053561971
📝 Username: angel
📱 App: Viral Hub
⏱️ Duration: 125s
📦 Output: 12.8 MB
🤖 Bot: Payload Injector
⏰ Time: 2025-11-06 21:32:20
```

### **❌ Build Fail:**
```
❌ Build Failed
━━━━━━━━━━━━━━━━━━━━
👤 User: 7053561971
📝 Username: angel
📱 App: MyApp
⚠️ Error: Signing failed
🤖 Bot: Payload Injector
⏰ Time: 2025-11-06 21:35:00
```

### **🔐 Authentication:**
```
🔐 New Authentication
━━━━━━━━━━━━━━━━━━━━
👤 User: 7053561971
📝 Username: angel
🤖 Bot: Payload Injector
⏰ Time: 2025-11-06 21:00:00
```

### **⚠️ Admin Disabled:**
```
⚠️ Admin Status Check
━━━━━━━━━━━━━━━━━━━━
📝 Username: angel
🔒 Status: Disabled
⏰ Time: 2025-11-06 22:00:00
```

---

## 🔒 Admin Check:

### **چیکار می‌کنه؟**

```
کاربر APK میفرسته
       ↓
✅ چک admin status
       ↓
    Active?
    ↙️     ↘️
  YES      NO
   ↓        ↓
Process   Deny
```

### **API Endpoint:**
```
GET http://95.134.130.160:8765/bot/check-admin?username=angel

Response:
{
  "is_admin": true/false
}
```

### **اگه Disabled شد:**
```
❌ Access Denied

Account disabled by admin

Please contact support if this is an error.
```

---

## 📊 مزایا:

✅ **نظارت Real-time** - هر build رو ببین
✅ **Debugging** - مشخصات کامل در log
✅ **Security** - Admin check خودکار
✅ **Tracking** - User activity
✅ **Analytics** - Duration, size, success rate

---

## ⚠️ نکات مهم:

1. **Channel باید Private باشه** (برای امنیت)
2. **Bot ها باید Admin باشن** (برای post کردن)
3. **Permission: Post Messages** فعال باشه
4. **Channel ID** منفی است (مثلاً `-1001234567890`)
5. اگه `None` بذاری → Log غیرفعال میشه

---

## 🔧 Troubleshooting:

**Log نمیاد:**
- چک کن bot admin هست؟
- چک کن Channel ID درسته؟
- چک کن permission داره؟

**Error:**
```python
# Log error
Failed to send log to channel: Chat not found
→ Channel ID اشتباهه!
```

---

**الان همه چیز آماده است! فقط Channel ID رو تنظیم کن!** 📊
