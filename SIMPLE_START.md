# 🚀 راهنمای فوق‌ساده - Suzi APK Processor

## یک دقیقه! فقط این رو بخون 👇

---

## 🎯 میخوای چیکار کنی؟

### 1️⃣ الان میخوام از برنامه استفاده کنم

```python
import suzi

# همین! فقط یک خط!
result = suzi.process("app.apk")
print(result)  # app_out.apk
```

**تمام!** 🎉

---

### 2️⃣ میخوام کدم رو آپدیت کنم و بفرستم

```bash
# کدت رو بنویس...
# بعد:

python auto_push.py "تغییرات جدید"
```

**همین!** بعد منتظر بمون 5-10 دقیقه، build میشه! 🚀

---

### 3️⃣ میخوام executable دانلود کنم

1. برو به: `https://github.com/YOUR_REPO/actions`
2. آخرین workflow موفق رو باز کن
3. دانلود Artifacts:
   - `suzi-apk-linux-x64` (Linux)
   - `suzi-apk-windows-x64.exe` (Windows)
   - `suzi-apk-macos-x64` (macOS)

**استفاده:**
```bash
./suzi-apk app.apk         # Linux/macOS
suzi-apk.exe app.apk       # Windows
```

---

## 📖 مثال‌های واقعی

### مثال 1: ساده‌ترین حالت
```python
import suzi

result = suzi.process("my_app.apk")
print(f"✅ نتیجه: {result}")
```

### مثال 2: چند APK
```python
import suzi
import os

for apk in os.listdir("."):
    if apk.endswith(".apk"):
        result = suzi.process(apk)
        print(f"✅ {apk} → {result}")
```

### مثال 3: با نام دلخواه
```python
import suzi

result = suzi.process(
    filepath="app.apk",
    output="my_custom_name.apk"
)
```

### مثال 4: با جزئیات
```python
import suzi

result = suzi.process(
    filepath="app.apk",
    verbose=True  # نمایش تمام مراحل
)
```

---

## 🔄 Workflow من

### هر روز کاری:

```bash
# 1. کدت رو بنویس
nano my_script.py

# 2. تست کن
python my_script.py

# 3. بفرست
python auto_push.py "ویژگی X اضافه شد"

# 4. منتظر بمون (5-10 دقیقه)

# 5. برو به GitHub Actions و دانلود کن
```

---

## 🆘 مشکل دارم!

### مشکل: نسخه محافظت شده نیست
```python
import suzi

# چک کن
info = suzi.get_version_info()
print(info)

# اگر protected: False بود:
# 1. یکبار git push کن
# 2. منتظر build بمون
# 3. دانلود از Actions
```

### مشکل: خطای Import
```bash
# مطمئن شو در پوشه پروژه هستی
cd /path/to/project
python -c "import suzi; print('OK')"
```

### مشکل: auto_push کار نمی‌کنه
```bash
# دستی انجام بده:
git add -A
git commit -m "update"
git push origin main
```

---

## 💡 نکات مهم

### ✅ استفاده از نسخه عادی:
```python
# حالت 1: خودکار (توصیه می‌شه)
import suzi
suzi.process("app.apk")

# حالت 2: مستقیم
from m import process
process(filepath="app.apk")
```

### ✅ استفاده از نسخه محافظت شده:
```bash
# بعد از دانلود از Actions
chmod +x suzi-apk          # Linux/macOS
./suzi-apk app.apk
```

### ✅ ترکیبی (suzi.py):
```python
import suzi

# اگر نسخه محافظت شده داشته باشی، ازش استفاده می‌کنه
# اگر نه، از نسخه عادی استفاده می‌کنه
result = suzi.process("app.apk")
```

---

## 🎓 مثال کامل یک پروژه

```python
#!/usr/bin/env python3
"""
پروژه من - پردازش APKها
"""

import suzi
import os
import sys

def main():
    # پیدا کردن همه APKها
    apks = [f for f in os.listdir(".") if f.endswith(".apk")]
    
    if not apks:
        print("❌ هیچ APK پیدا نشد!")
        return
    
    print(f"📦 {len(apks)} APK پیدا شد")
    
    # پردازش
    for apk in apks:
        print(f"\n🔄 در حال پردازش: {apk}")
        try:
            result = suzi.process(apk, verbose=True)
            print(f"✅ موفق: {result}")
        except Exception as e:
            print(f"❌ خطا: {e}")

if __name__ == "__main__":
    main()
```

**اجرا:**
```bash
python my_project.py
```

**بعد از تست:**
```bash
python auto_push.py "پروژه کامل شد"
```

---

## 🎯 چک لیست

قبل از استفاده:
- [ ] Python 3.6+ نصب شده؟
- [ ] Java JDK نصب شده؟ (`java -version`)
- [ ] در پوشه پروژه هستی؟

برای build:
- [ ] یکبار `git push` کردی؟
- [ ] به Actions رفتی؟
- [ ] منتظر build موندی؟
- [ ] Artifact دانلود کردی؟

---

## 📚 فایل‌های مهم

```
📁 پروژه/
├── suzi.py           # 👈 این رو import کن!
├── auto_push.py      # 👈 این رو اجرا کن!
├── m.py              # نسخه عادی
├── apk_processor.py  # منطق اصلی
└── dist/             # نسخه محافظت شده (بعد از build)
    └── suzi-apk
```

---

## 🔥 خلاصه خلاصه

### استفاده:
```python
import suzi
suzi.process("app.apk")
```

### آپدیت:
```bash
python auto_push.py "تغییرات"
```

### دانلود:
```
GitHub → Actions → Artifacts
```

**همین! 🎉**

---

## 🤝 کمک

مشکل داری؟ Issue باز کن!

ساخته شده با ❤️ توسط **Suzi Brand**
