# 🖥️ راهنمای نصب روی سرور Windows

## ✅ چک‌لیست نیازها:

### 1️⃣ Java Runtime
```cmd
java -version
```
اگه error داد:
- دانلود: https://adoptium.net/
- نصب JRE 11 یا بالاتر

---

### 2️⃣ Python Packages
```cmd
pip install telethon requests aiohttp
```

---

### 3️⃣ Android Build Tools

**گزینه A: کپی از لوکال**
```cmd
# از سیستم لوکالت:
C:\Users\awmeiiir\AppData\Local\Android\Sdk\build-tools\34.0.0\

# کپی کن به سرور:
C:\BuildTools\
```

**گزینه B: دانلود مستقیم**
```
1. برو: https://developer.android.com/studio#command-tools
2. دانلود: Command Line Tools
3. Extract کن
4. تو CMD:
   sdkmanager "build-tools;34.0.0"
```

---

### 4️⃣ تنظیم config.py

باز کن: `modules/config.py`

```python
# Tool paths - تنظیم برای سرور
APKTOOL_JAR = str(PROJECT_ROOT / "apktool.jar")  # ✅ خودکار
APKTOOL_PATH = PROJECT_ROOT / "apktool.jar"       # ✅ خودکار

# این دو تا رو عوض کن:
ZIPALIGN_PATH = r"C:\BuildTools\zipalign.exe"    # ← مسیر سرورت
APKSIGNER_PATH = r"C:\BuildTools\apksigner.bat"  # ← مسیر سرورت
```

---

### 5️⃣ تست Tools

```cmd
# تست Java
java -version

# تست apktool
java -jar apktool.jar

# تست zipalign
C:\BuildTools\zipalign.exe

# تست apksigner
C:\BuildTools\apksigner.bat
```

همه باید بدون error جواب بدن!

---

## 🚀 دستورات نصب کامل:

```cmd
REM 1. نصب Java (اگه نداری)
REM    https://adoptium.net/ → دانلود JRE 11

REM 2. نصب Python packages
pip install telethon requests aiohttp

REM 3. کپی build-tools
REM    از: C:\Users\awmeiiir\AppData\Local\Android\Sdk\build-tools\34.0.0\
REM    به: C:\BuildTools\

REM 4. Clone پروژه
git clone https://github.com/angelcode119/signerme.git
cd signerme

REM 5. ویرایش config.py
notepad modules\config.py

REM    عوض کن:
REM    ZIPALIGN_PATH = r"C:\BuildTools\zipalign.exe"
REM    APKSIGNER_PATH = r"C:\BuildTools\apksigner.bat"
REM    BOT2_TOKEN = "توکن ربات دومت"

REM 6. اجرا
python run.py
```

---

## 🔍 Troubleshooting:

### Error: "The system cannot find the file specified"

**چک کن:**
```cmd
REM 1. apktool.jar وجود داره؟
dir apktool.jar

REM 2. zipalign در مسیر درسته؟
dir C:\BuildTools\zipalign.exe

REM 3. apksigner در مسیر درسته؟
dir C:\BuildTools\apksigner.bat

REM 4. Java نصبه؟
java -version
```

---

## 📁 ساختار نهایی سرور:

```
C:\
├── BuildTools\         ← Android tools
│   ├── zipalign.exe
│   ├── apksigner.bat
│   └── lib\
│
└── signerme\           ← پروژه
    ├── apktool.jar     ✅
    ├── payload.apk     ✅
    ├── bots\
    ├── modules\
    └── ...
```

---

## ✅ چک نهایی:

```cmd
cd C:\signerme
python -c "import sys; print(sys.version)"
java -version
dir apktool.jar
dir C:\BuildTools\zipalign.exe
dir C:\BuildTools\apksigner.bat
```

همه باید OK باشن!
