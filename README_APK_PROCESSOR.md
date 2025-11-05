# 📦 Suzi APK Processor

سیستم پردازش و امضای APK با معماری modular و قابل استفاده مجدد

---

## 📂 ساختار پروژه

```
/workspace/
├── apk_processor.py      # ⭐ منطق اصلی (کلاس‌ها و توابع)
├── m.py                  # 🏃 Runner ساده
├── example_usage.py      # 💡 7 مثال کاربردی
└── README_APK_PROCESSOR.md
```

---

## 🎯 معماری جدید

### قبل (منسوخ شده):
```python
# همه چی توی یک فایل
m.py → منطق + runner همه توی هم
```

### بعد (جدید و بهتر):
```python
# جداسازی منطق و اجرا
apk_processor.py → منطق اصلی (قابل استفاده مجدد)
m.py → فقط runner ساده
```

---

## 🚀 استفاده سریع

### روش 1: استفاده از Runner (m.py)

```bash
python3 m.py input.apk
```

خروجی: `input_out.apk`

### روش 2: استفاده مستقیم در کد

```python
from apk_processor import process_apk

# یک خط کد!
result = process_apk("app.apk", "output.apk", verbose=True)
print(f"Done: {result}")
```

### روش 3: استفاده پیشرفته

```python
from apk_processor import SuziAPKProcessor

# ساخت processor
processor = SuziAPKProcessor(verbose=True)

# پردازش کامل
result = processor.process_apk("app.apk", "output.apk")

# یا مرحله به مرحله:
modified = processor.modify_bit_flags("app.apk", "app_modified.apk")
keystore, pw, alias = processor.create_keystore()
signed = processor.sign_apk(modified, keystore, pw, alias)
```

---

## 📚 API Reference

### `SuziAPKProcessor` Class

#### Constructor
```python
processor = SuziAPKProcessor(
    use_jarsigner=True,  # استفاده از jarsigner (پیشنهادی)
    verbose=False        # نمایش لاگ‌ها
)
```

#### Methods

##### `process_apk()`
پردازش کامل: تغییر bit flag + امضا
```python
result = processor.process_apk(
    input_apk="app.apk",
    output_apk="output.apk",  # اختیاری
    clean_temp=True            # پاکسازی فایل‌های موقت
)
```

##### `modify_bit_flags()`
تغییر bit flag بدون باز کردن فایل‌ها
```python
modified = processor.modify_bit_flags(
    input_apk="app.apk",
    output_apk="app_modified.apk"
)
```

##### `create_keystore()`
ساخت keystore با برند Suzi
```python
keystore, password, alias = processor.create_keystore()
# keystore: مسیر فایل keystore
# password: پسورد تصادفی
# alias: alias با prefix suzi_
```

##### `sign_apk()`
امضای APK با keystore
```python
signed = processor.sign_apk(
    input_apk="app.apk",
    keystore="/path/to/keystore",
    password="pass123",
    alias="suzi_abc",
    output_apk="signed.apk"  # اختیاری
)
```

##### `cleanup()`
پاکسازی فایل‌های موقت
```python
processor.cleanup()
```

---

### `process_apk()` Helper Function

تابع helper برای استفاده سریع:

```python
from apk_processor import process_apk

result = process_apk(
    input_apk="app.apk",
    output_apk="output.apk",  # اختیاری
    verbose=False
)
```

---

## 💡 مثال‌های کاربردی

### مثال 1: پردازش ساده
```python
from apk_processor import process_apk

result = process_apk("app.apk")
print(f"✅ {result}")
```

### مثال 2: پردازش دسته‌ای
```python
from apk_processor import process_apk
import os

for filename in os.listdir("./apks/"):
    if filename.endswith(".apk"):
        try:
            result = process_apk(f"./apks/{filename}")
            print(f"✅ {filename} → {result}")
        except Exception as e:
            print(f"❌ {filename}: {e}")
```

### مثال 3: ادغام در سیستم خودتون
```python
from apk_processor import SuziAPKProcessor

class MyAppProcessor:
    def __init__(self):
        self.apk_processor = SuziAPKProcessor(verbose=True)
    
    def process_uploaded_apk(self, apk_path, user_id):
        # پردازش APK آپلود شده توسط کاربر
        output = f"processed_{user_id}.apk"
        result = self.apk_processor.process_apk(apk_path, output)
        
        # ذخیره در دیتابیس
        self.save_to_database(user_id, result)
        
        return result
```

### مثال 4: مدیریت خطا
```python
from apk_processor import process_apk

try:
    result = process_apk("app.apk", verbose=True)
    print(f"✅ Success: {result}")
    
except FileNotFoundError:
    print("❌ فایل پیدا نشد")
    
except RuntimeError as e:
    print(f"❌ خطا در پردازش: {e}")
    
except Exception as e:
    print(f"❌ خطای غیرمنتظره: {e}")
```

### مثال 5: استفاده با Config
```python
from apk_processor import SuziAPKProcessor
import json

# خواندن config
with open("config.json") as f:
    config = json.load(f)

# استفاده از config
processor = SuziAPKProcessor(
    use_jarsigner=config.get("use_jarsigner", True),
    verbose=config.get("verbose", False)
)

result = processor.process_apk(
    input_apk=config["input"],
    output_apk=config["output"]
)
```

برای مثال‌های بیشتر، فایل `example_usage.py` رو ببینید!

---

## 🔧 نیازمندی‌ها

- **Python 3.6+**
- **Java JDK** (برای keytool و jarsigner)
  ```bash
  java -version
  keytool
  jarsigner
  ```

---

## 📖 چگونه کار می‌کند؟

### مرحله 1: تغییر Bit Flag
APK فایل ZIP هست که ساختار خاصی داره:
- فایل‌های فشرده
- Central Directory (لیست فایل‌ها)
- EOCD (End of Central Directory)

Processor وارد Central Directory میشه و bit flag هر فایل رو تغییر میده (encryption flag رو فعال می‌کنه) **بدون باز کردن فایل‌ها**.

### مرحله 2: ساخت Keystore
یک keystore موقت با مشخصات زیر می‌سازه:
- نام: `suzi_XXXXXXXX.keystore`
- Alias: `suzi_YYYYYYYYYY`
- DN: `CN=suzi, O=Suzi Brand, C=IR`
- Algorithm: RSA 2048-bit
- Validity: 10000 روز

### مرحله 3: امضای APK
با استفاده از jarsigner یا apksigner، APK رو امضا می‌کنه.

---

## 🎨 مزایای معماری جدید

✅ **Reusable** - می‌تونی در پروژه‌های دیگه استفاده کنی  
✅ **Modular** - منطق جدا از اجراست  
✅ **Testable** - راحت‌تر می‌تونی تست بنویسی  
✅ **Clean Code** - خواناتر و قابل نگهداری‌تر  
✅ **Flexible** - می‌تونی مرحله به مرحله استفاده کنی  
✅ **Professional** - معماری استاندارد  

---

## 🔄 مقایسه قبل و بعد

### قبل:
```python
# فقط از command line قابل استفاده
python3 m.py app.apk
```

### بعد:
```python
# 1. از command line
python3 m.py app.apk

# 2. به عنوان library
from apk_processor import process_apk
process_apk("app.apk")

# 3. استفاده پیشرفته
from apk_processor import SuziAPKProcessor
processor = SuziAPKProcessor()
processor.process_apk("app.apk")

# 4. مرحله به مرحله
processor.modify_bit_flags(...)
processor.create_keystore()
processor.sign_apk(...)
```

---

## 🧪 تست کردن

### تست Import
```bash
python3 -c "from apk_processor import SuziAPKProcessor; print('✅ OK')"
```

### تست Runner
```bash
python3 m.py a.apk
```

### تست مستقیم
```bash
python3 apk_processor.py a.apk output.apk
```

### تست مثال‌ها
```bash
python3 example_usage.py
```

---

## 📝 نکات مهم

1. **Cleanup**: کلاس خودکار فایل‌های موقت رو پاک می‌کنه
2. **Verbose Mode**: برای debugging فعالش کن
3. **Custom Output**: می‌تونی نام دلخواه برای خروجی تعیین کنی
4. **Error Handling**: همه توابع exception پرتاب می‌کنن
5. **Thread Safe**: هر instance مستقل هست

---

## 🎓 یادگیری بیشتر

- 📖 کد کامل: `apk_processor.py`
- 💡 مثال‌ها: `example_usage.py`
- 🏃 Runner: `m.py`
- 🔐 License System: `README_LICENSE.md`

---

## 🤝 مشارکت

ساخته شده با ❤️ توسط **Suzi Brand**

برای سوالات و پیشنهادات، Issue باز کنید.

---

## 📜 License

این کد برای استفاده شخصی و تجاری آزاد است.
