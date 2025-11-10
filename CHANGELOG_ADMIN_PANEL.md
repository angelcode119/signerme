# 📝 تغییرات پنل ادمین - Changelog

## 🎉 نسخه 1.0.0 - پنل ادمین کامل

تاریخ: 2024-11-10

---

## ✨ قابلیت‌های جدید

### 1️⃣ پنل ادمین کامل با دسترسی محدود
- سیستم احراز هویت بر اساس User ID
- منوی تعاملی با دکمه‌های inline
- دسترسی فقط برای ادمین‌های تعریف شده

### 2️⃣ سیستم آمار و لاگ حرفه‌ای
- **لاگ تمام build ها** به صورت روزانه
- **آمار کاربران** شامل تعداد build، زمان، نوع build
- **آمار سیستم** شامل uptime، کاربران فعال، build های روزانه
- **نمودار هفتگی** build ها
- **Top users** بر اساس تعداد build

### 3️⃣ مدیریت کاربران
- **لیست کاربران** با وضعیت آنلاین/آفلاین
- **فیلتر کاربران**: Online, New, Most Active
- **وضعیت real-time**: 🟢 Online, 🟡 Recently, 🔴 Offline, ⚪ Inactive
- نمایش تعداد build و آخرین فعالیت

### 4️⃣ مدیریت APK ها
- **لیست APK ها** با جزئیات (سایز، تعداد build)
- **اسکن خودکار** APK های جدید از پوشه data
- **آمار هر APK**: تعداد استفاده، تاریخ اضافه شدن
- نمایش حجم کل storage

### 5️⃣ وضعیت صف (Queue Status)
- نمایش build های فعال
- نمایش build های در انتظار
- زمان سپری شده هر build
- نمایش username و نام APK

### 6️⃣ سیستم Broadcast
- ارسال پیام همگانی به همه کاربران
- نمایش progress در حین ارسال
- آمار موفق/ناموفق در پایان

---

## 📁 فایل‌های جدید

### 1. `modules/stats_manager.py` (جدید) ⭐
**وظایف:**
- مدیریت لاگ build ها
- ذخیره آمار کاربران
- محاسبه آمار کلی سیستم
- دریافت کاربران فعال/جدید
- محاسبه Top Users

**توابع اصلی:**
```python
- log_build()              # ثبت یک build
- get_total_stats()        # آمار کلی
- get_builds_by_day()      # build های 7 روز اخیر
- get_top_users()          # بهترین کاربران
- get_all_users()          # لیست کاربران با فیلتر
- get_user_details()       # جزئیات یک کاربر
- update_user_activity()   # آپدیت فعالیت کاربر
```

### 2. `modules/apk_manager.py` (جدید) ⭐
**وظایف:**
- مدیریت لیست APK ها
- اضافه/ویرایش/حذف APK
- آمار هر APK
- محاسبه حجم storage

**توابع اصلی:**
```python
- add_apk()                # اضافه کردن APK
- update_apk()             # آپدیت اطلاعات
- delete_apk()             # حذف APK
- increment_build_count()  # افزایش شمارنده
- get_all_apks()           # لیست همه
- get_apk_stats()          # آمار یک APK
- get_total_storage()      # حجم کل
```

### 3. `modules/admin_panel.py` (جدید) ⭐
**وظایف:**
- Handler های پنل ادمین
- نمایش منو و زیرمنوها
- مدیریت callback ها
- سیستم broadcast

**توابع اصلی:**
```python
- handle_admin_command()         # دستور /admin
- handle_admin_stats()           # بخش آمار
- handle_admin_users()           # بخش کاربران
- handle_admin_users_filter()   # فیلتر کاربران
- handle_admin_apks()            # بخش APK ها
- handle_admin_apks_scan()       # اسکن APK ها
- handle_admin_queue()           # وضعیت صف
- handle_admin_callback()        # مدیریت callback
- handle_broadcast()             # ارسال همگانی
```

### 4. `ADMIN_PANEL_GUIDE.md` (جدید) 📚
راهنمای کامل استفاده از پنل ادمین

### 5. `CHANGELOG_ADMIN_PANEL.md` (این فایل) 📝
خلاصه تغییرات و قابلیت‌های جدید

---

## 🔧 فایل‌های تغییر یافته

### 1. `modules/config.py` ✏️
**تغییرات:**
```python
# اضافه شده:
ADMIN_USER_IDS = [
    # Add your Telegram User IDs here
]
```

### 2. `bots/bot1_generator.py` ✏️
**تغییرات:**

**Import های جدید:**
```python
from modules.config import ADMIN_USER_IDS
from modules.admin_panel import handle_admin_command, handle_admin_callback, handle_broadcast
from modules.stats_manager import stats_manager
from modules.apk_manager import apk_manager
```

**Handler جدید برای دستورات ادمین:**
```python
# در handler اصلی:
if text == '/admin':
    await handle_admin_command(event, ADMIN_USER_IDS)
    return

if text.startswith('/broadcast '):
    await handle_broadcast(event, ADMIN_USER_IDS, bot)
    return
```

**Handler جدید برای callback های ادمین:**
```python
@bot.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode('utf-8')
    if data.startswith('admin:'):
        await handle_admin_callback(event, ADMIN_USER_IDS)
        return
    raise events.StopPropagation
```

**لاگ کردن build ها:**
```python
# در quick_build_handler:
start_time = time.time()
success, result = await build_apk(...)
build_duration = int(time.time() - start_time)

stats_manager.log_build(
    user_id=user_id,
    username=username or 'Unknown',
    apk_name=apk_name,
    duration=build_duration,
    success=success,
    is_custom=False,
    error=None if success else result
)

if success:
    apk_manager.increment_build_count(selected_apk_filename)
```

**آپدیت فعالیت کاربر:**
```python
# در هر پیام:
username = user_manager.get_username(user_id)
if username:
    stats_manager.update_user_activity(user_id, username)
```

### 3. `modules/custom_build_handler.py` ✏️
**تغییرات:**

**Import های جدید:**
```python
from .stats_manager import stats_manager
from .apk_manager import apk_manager
```

**لاگ کردن custom build:**
```python
start_time = time.time()
success, result = await build_apk(...)
build_duration = int(time.time() - start_time)

stats_manager.log_build(
    user_id=user_id,
    username=username or 'Unknown',
    apk_name=apk_name,
    duration=build_duration,
    success=success,
    is_custom=True,  # custom build
    error=None if success else result
)

if success:
    apk_manager.increment_build_count(selected_apk_filename)
```

---

## 📂 ساختار فولدرها و فایل‌های جدید

```
workspace/
├── modules/
│   ├── stats_manager.py      ⭐ NEW
│   ├── apk_manager.py         ⭐ NEW
│   ├── admin_panel.py         ⭐ NEW
│   ├── config.py              ✏️ MODIFIED
│   └── custom_build_handler.py ✏️ MODIFIED
├── bots/
│   └── bot1_generator.py      ✏️ MODIFIED
├── logs/                      ⭐ NEW (ساخته می‌شود اتوماتیک)
│   └── builds/
│       ├── 2024-11-10.json
│       ├── 2024-11-09.json
│       └── ...
├── data/
│   ├── stats.json             ⭐ NEW (ساخته می‌شود اتوماتیک)
│   ├── user_stats.json        ⭐ NEW (ساخته می‌شود اتوماتیک)
│   └── apks.json              ⭐ NEW (ساخته می‌شود اتوماتیک)
├── ADMIN_PANEL_GUIDE.md       ⭐ NEW
└── CHANGELOG_ADMIN_PANEL.md   ⭐ NEW
```

---

## 🎯 دستورات جدید

### برای کاربران عادی:
❌ هیچ تغییری ندارد - همه چیز مثل قبل کار می‌کند

### برای ادمین‌ها:
✅ `/admin` - باز کردن پنل ادمین
✅ `/broadcast <message>` - ارسال پیام همگانی

---

## 📊 داده‌های لاگ شده

### برای هر build:
- ✅ User ID و Username
- ✅ نام APK
- ✅ زمان build (ثانیه)
- ✅ موفق یا ناموفق
- ✅ نوع build (Quick / Custom)
- ✅ پیام خطا (در صورت وجود)
- ✅ تاریخ و ساعت دقیق

### برای هر کاربر:
- ✅ تعداد کل build ها
- ✅ تعداد Quick builds
- ✅ تعداد Custom builds  
- ✅ تعداد build های ناموفق
- ✅ مجموع زمان build
- ✅ اولین و آخرین build
- ✅ آخرین فعالیت
- ✅ استفاده از هر APK

---

## 🔐 امنیت

- ✅ فقط User ID های مشخص شده در `ADMIN_USER_IDS` دسترسی دارند
- ✅ کاربران عادی هیچ دسترسی به پنل ندارند
- ✅ پیام "Access Denied" برای کاربران غیرمجاز

---

## ⚡ عملکرد

- ✅ لاگ‌ها به صورت خودکار روزانه ذخیره می‌شوند
- ✅ فایل‌های JSON برای سرعت بالا
- ✅ آمار به صورت real-time محاسبه نمی‌شود (باید refresh کنید)
- ✅ Broadcast برای تعداد زیاد کاربر ممکن است کند باشد

---

## 🐛 باگ‌های برطرف شده

- ✅ محاسبه درست build duration
- ✅ Import درست FastTelethonhelper
- ✅ مدیریت صحیح callback ها

---

## 📌 نکات مهم

1. **قبل از استفاده**: User ID خود را در `config.py` اضافه کنید
2. **بعد از تغییرات**: بات را restart کنید
3. **Backup**: از فایل‌های `logs/` و `data/` backup بگیرید
4. **APK Management**: ابتدا APK ها را در `data/` قرار دهید، سپس Scan کنید

---

## 🚀 استفاده اولیه

```bash
# 1. User ID خود را پیدا کنید
ربات @userinfobot را باز کنید

# 2. User ID را در config.py اضافه کنید
ADMIN_USER_IDS = [123456789]

# 3. بات را restart کنید
python run.py

# 4. پنل را باز کنید
/admin
```

---

## 📞 پشتیبانی

در صورت بروز مشکل:
1. فایل `bot.log` را چک کنید
2. راهنمای `ADMIN_PANEL_GUIDE.md` را مطالعه کنید
3. مطمئن شوید User ID درست است

---

## 🎨 توسعه‌دهندگان

**APK Studio Team**
- نسخه: 1.0.0
- تاریخ: 2024-11-10
- زبان: Python 3.12
- Framework: Telethon

---

## 🔮 قابلیت‌های آینده (پیشنهادی)

- [ ] نمودار بیشتر (نمودار ساعتی، هفتگی، ماهانه)
- [ ] Export آمار به Excel/CSV
- [ ] مسدود کردن کاربران (Ban/Unban)
- [ ] حذف کاربر
- [ ] ویرایش APK از داخل پنل
- [ ] آپلود APK جدید از تلگرام
- [ ] تنظیم حداکثر build در روز برای هر کاربر
- [ ] سیستم Subscription (Free/Premium)
- [ ] لاگ‌های دقیق‌تر (IP، Device، etc)
- [ ] Alert های خودکار (صف پر، خطا، etc)

---

**تمام! پنل ادمین آماده استفاده است! 🎉**
