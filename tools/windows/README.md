# 🪟 Windows Tools - Suzi APK Processor

ابزارهای مخصوص Windows

## 📦 محتویات

### apksigner.bat
فایل batch برای apksigner (موجود)

## ✅ نیازمندی‌ها

### Java JDK

**دانلود و نصب:**
- Oracle JDK: https://www.oracle.com/java/technologies/downloads/
- OpenJDK (Adoptium): https://adoptium.net/

**چک کردن نصب:**
```cmd
java -version
javac -version
keytool
jarsigner
```

### اضافه کردن به PATH (در صورت نیاز)

1. باز کردن "Environment Variables"
2. پیدا کردن متغیر "Path" در System Variables
3. اضافه کردن مسیر Java:
   ```
   C:\Program Files\Java\jdk-21\bin
   ```

## 🔧 نصب خودکار

```cmd
python setup_tools.py
```

یا:
```powershell
python3 setup_tools.py
```

این اسکریپت:
- ✅ Java رو چک می‌کنه
- ✅ apktool.jar رو دانلود می‌کنه
- ✅ wrapper scripts رو می‌سازه
- ✅ همه چیز رو تست می‌کنه

## 🎯 استفاده در Suzi

شما نیازی به استفاده مستقیم ندارید!

```cmd
python m.py app.apk
```

یا در کد:
```python
from m import process
process(filepath="app.apk")
```

همه چیز خودکار! ✨

## 📝 نکات

1. **JDK vs JRE**: مطمئن شو JDK نصب کردی (نه فقط JRE)
2. **PATH**: اگر `java` رو تشخیص نمیده، به PATH اضافه کن
3. **PowerShell**: اگر از PowerShell استفاده می‌کنی، ممکنه نیاز به `python3` باشه

## 🔍 عیب‌یابی

### خطا: 'java' is not recognized
```cmd
# چک کردن نصب Java
where java

# اگر خروجی نداد، Java رو نصب کن و به PATH اضافه کن
```

### خطا: 'jarsigner' is not recognized
```cmd
# باید JDK نصب کنی (نه فقط JRE)
# بعد از نصب، Path رو چک کن:
where jarsigner
```

### خطا: Python not found
```cmd
# نصب Python از python.org
# یا از Microsoft Store

# چک کردن
python --version
# یا
python3 --version
```

## 🚀 نصب سریع

### مرحله 1: نصب Java JDK
1. دانلود از https://adoptium.net/ (توصیه می‌شه)
2. اجرای installer
3. انتخاب گزینه "Add to PATH"

### مرحله 2: نصب ابزارهای Suzi
```cmd
python setup_tools.py
```

### مرحله 3: استفاده
```cmd
python m.py your_app.apk
```

یا در کد:
```python
from m import process
process(filepath="your_app.apk")
```

## 💡 مثال استفاده

### Command Line
```cmd
REM پردازش APK
python m.py app.apk

REM خروجی: app_out.apk
```

### Python Script
```python
# simple_usage.py
from m import process

# پردازش APK
result = process(filepath="app.apk")
print(f"Done: {result}")

# اجرا
# python simple_usage.py
```

### Batch Processing
```python
# process_multiple.py
from m import process
import os

# پردازش همه APKها در پوشه
for filename in os.listdir("."):
    if filename.endswith(".apk"):
        print(f"Processing {filename}...")
        result = process(filepath=filename)
        print(f"  -> {result}")
```

## 🎨 ادغام با PowerShell

```powershell
# process.ps1
$apks = Get-ChildItem -Filter *.apk

foreach ($apk in $apks) {
    Write-Host "Processing $($apk.Name)..." -ForegroundColor Green
    python m.py $apk.FullName
}
```

## 📊 مقایسه ابزارها

| ابزار | نصب | استفاده در Suzi |
|------|-----|------------------|
| Java JDK | ✅ لازم (دستی) | ✅ خودکار |
| apktool.jar | ✅ خودکار | ✅ خودکار |
| jarsigner | ✅ با JDK | ✅ خودکار |
| keytool | ✅ با JDK | ✅ خودکار |

فقط Java JDK رو نصب کن، بقیه خودکار! 🎉

## 🤝 پشتیبانی

ساخته شده با ❤️ توسط **Suzi Brand**

مشکلی پیش اومد؟ Issue باز کن!
