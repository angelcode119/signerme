# 🚀 راهنمای فوق‌العاده ساده - Suzi APK Processor

## نصب یکباره (فقط بار اول)

```bash
python3 setup_tools.py
```

این دستور:
✅ Java رو چک می‌کنه  
✅ ابزارهای لازم رو دانلود می‌کنه  
✅ همه چیز رو آماده می‌کنه  

---

## استفاده (خیلی ساده!)

### روش 1: از Command Line

```bash
python3 m.py app.apk
```

همین! خروجی: `app_out.apk` ✅

---

### روش 2: در کد Python (یک خط!)

```python
from m import process

result = process(filepath="app.apk")
print(result)  # app_out.apk
```

---

### روش 3: با نام خروجی دلخواه

```python
from m import process

result = process(filepath="app.apk", output="my_app.apk")
```

---

### روش 4: با جزئیات

```python
from m import process

result = process(filepath="app.apk", verbose=True)
# نمایش تمام مراحل پردازش
```

---

## مثال‌های واقعی

### مثال 1: پردازش ساده
```python
from m import process

# فقط همین!
process(filepath="my_app.apk")
```

### مثال 2: پردازش چندین APK
```python
from m import process
import os

for apk in os.listdir("."):
    if apk.endswith(".apk"):
        result = process(filepath=apk)
        print(f"✅ {apk} → {result}")
```

### مثال 3: در یک تابع
```python
from m import process

def process_user_apk(apk_path):
    try:
        result = process(filepath=apk_path)
        return {"status": "success", "file": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# استفاده
result = process_user_apk("uploaded.apk")
print(result)
```

### مثال 4: با مدیریت خطا
```python
from m import process

try:
    result = process(filepath="app.apk")
    print(f"✅ موفق: {result}")
except FileNotFoundError:
    print("❌ فایل پیدا نشد")
except Exception as e:
    print(f"❌ خطا: {e}")
```

---

## چیزهایی که نیاز داری

### نیازمندی اصلی: فقط Java!
```bash
# چک کردن
java -version

# اگر نبود، نصب کن:

# Ubuntu/Debian
sudo apt install default-jdk

# macOS
brew install openjdk

# Windows
# دانلود از: https://www.oracle.com/java/technologies/downloads/
```

### همین! بقیه خودکار نصب میشه ✨

---

## سوالات متداول

### ❓ اولین بار چیکار کنم؟
```bash
python3 setup_tools.py
```

### ❓ چطوری استفاده کنم؟
```python
from m import process
process(filepath="app.apk")
```

### ❓ خروجی کجاست؟
در همون پوشه، با نام `app_out.apk`

### ❓ میخوام نام خروجی رو خودم مشخص کنم
```python
process(filepath="app.apk", output="my_name.apk")
```

### ❓ خطا میده
1. مطمئن شو Java نصب شده: `java -version`
2. اجرا کن: `python3 setup_tools.py`
3. دوباره امتحان کن

### ❓ میخوام ببینم چیکار می‌کنه
```python
process(filepath="app.apk", verbose=True)
```

---

## ساختار فایل‌ها

```
/workspace/
├── m.py                # 👈 فقط این رو صدا بزن!
├── apk_processor.py    # منطق (خودکار استفاده میشه)
├── setup_tools.py      # نصب ابزارها (فقط بار اول)
└── tools/              # ابزارها (خودکار دانلود میشه)
    ├── apktool.jar
    └── ...
```

---

## نمونه کد کامل

```python
#!/usr/bin/env python3
"""
مثال کامل استفاده از Suzi APK Processor
"""

from m import process
import os

def main():
    # لیست APKها
    apks = ["app1.apk", "app2.apk", "game.apk"]
    
    for apk in apks:
        if os.path.exists(apk):
            print(f"🔄 در حال پردازش: {apk}")
            try:
                result = process(filepath=apk)
                print(f"   ✅ موفق: {result}")
            except Exception as e:
                print(f"   ❌ خطا: {e}")
        else:
            print(f"   ⚠️  فایل موجود نیست: {apk}")

if __name__ == "__main__":
    main()
```

---

## یادت باشه

### ✅ فقط یک بار نصب:
```bash
python3 setup_tools.py
```

### ✅ بعدش همیشه همین:
```python
from m import process
process(filepath="app.apk")
```

### همین! 🎉

---

## پشتیبانی

ساخته شده با ❤️ توسط **Suzi Brand**

مشکلی پیش اومد؟ Issue باز کن!

---

**خلاصه:** فقط `process(filepath="app.apk")` 🚀
