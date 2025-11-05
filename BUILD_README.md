# 🔐 ساخت نسخه محافظت شده - Suzi APK Processor

راهنمای کامل ساخت executable محافظت شده بدون دسترسی به سورس

---

## 🎯 هدف

تبدیل کد Python به:
- ✅ **فایل executable** بدون پسوند Python
- ✅ **محافظت شده** - کد به C کامپایل شده (Cython)
- ✅ **Standalone** - بدون نیاز به Python
- ✅ **کراس‌پلتفرم** - Windows, Linux, macOS
- ✅ **بدون دسترسی به سورس** - غیرقابل استخراج

---

## 📦 روش‌های Build

### روش 1: GitHub Actions (توصیه می‌شه) ⭐

**مزایا:**
- ✅ Build خودکار
- ✅ همزمان برای 3 پلتفرم
- ✅ Release خودکار
- ✅ بدون نیاز به نصب ابزار

**استفاده:**

#### Option A: Push به main/master
```bash
git push origin main
```

بعد از push:
1. به صفحه "Actions" در GitHub برید
2. منتظر بمونید تا build تمام بشه (حدود 5-10 دقیقه)
3. فایل‌های build شده در "Artifacts" دانلود کنید

#### Option B: Manual Trigger
1. به صفحه "Actions" برید
2. "Build Protected Executable" رو انتخاب کنید
3. "Run workflow" بزنید
4. منتظر build بمونید

#### Option C: Release با Tag
```bash
# ساخت tag
git tag v1.0.0
git push origin v1.0.0
```

این روش:
- Build می‌کنه
- Release می‌سازه
- فایل‌ها رو به release اضافه می‌کنه

---

### روش 2: Build محلی

**نیازمندی‌ها:**
```bash
# نصب dependencies
pip install cython pyinstaller setuptools wheel
```

**Build:**
```bash
# اجرای اسکریپت build
python build_protected.py
```

**خروجی:**
```
dist/
├── suzi-apk           # executable (Linux/macOS)
├── suzi-apk.exe       # executable (Windows)
├── tools/             # ابزارهای لازم
└── README.md          # راهنما
```

---

## 🔧 جزئیات فنی

### مرحله 1: Cython
کد Python به C تبدیل و کامپایل میشه:

```
apk_processor.py  →  apk_processor.c  →  apk_processor_core.so/.pyd
m.py              →  m.c              →  m_core.so/.pyd
```

**تنظیمات Cython:**
- `language_level: 3` - Python 3
- `embedsignature: False` - بدون signature
- `boundscheck: False` - بدون چک bounds (سریع‌تر)
- `cdivision: True` - تقسیم C-style
- Optimization: `-O3` (Linux/macOS) یا `/O2` (Windows)

### مرحله 2: PyInstaller
فایل‌های کامپایل شده + Python runtime → یک executable:

```
PyInstaller:
├── suzi_apk.py (loader)
├── apk_processor_core.so/.pyd
├── m_core.so/.pyd
├── Python runtime
└── dependencies
                ↓
         suzi-apk (executable)
```

**تنظیمات PyInstaller:**
- `--onefile` - یک فایل
- `--name suzi-apk` - نام executable
- `--clean` - پاکسازی cache
- `--add-data tools:tools` - اضافه کردن tools

---

## 🛡️ سطح امنیت

### ✅ محافظت‌های اعمال شده:

1. **Cython Compilation**
   - کد Python → C bytecode
   - کامپایل به shared library
   - غیرقابل decompile به Python

2. **PyInstaller Bundling**
   - همه چیز در یک executable
   - رمزنگاری داخلی
   - سخت برای استخراج

3. **No Source Access**
   - فایل‌های `.py` حذف شدن
   - فقط `.so`/`.pyd` موجوده
   - بدون امکان خواندن کد

### ⚠️ نکات امنیتی:

**این روش مقاوم هست در برابر:**
- ✅ خواندن مستقیم کد
- ✅ Decompile ساده
- ✅ استخراج با ابزارهای معمولی

**ولی نمی‌تونه جلوی اینا رو بگیره:**
- ❌ Reverse engineering پیشرفته
- ❌ Debugging در سطح assembly
- ❌ Memory dumping

**توصیه:**
برای امنیت بیشتر:
- اضافه کردن obfuscation
- استفاده از packing
- Anti-debugging techniques
- Server-side validation

---

## 📊 مقایسه روش‌ها

| روش | امنیت | سرعت | سهولت | پلتفرم |
|-----|------|------|-------|--------|
| **Python عادی** | ❌ کم | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | همه |
| **Cython فقط** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | نیاز به Python |
| **PyInstaller فقط** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | Standalone |
| **Cython + PyInstaller** ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Standalone |
| **Nuitka** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | Standalone |

---

## 🚀 استفاده از نسخه محافظت شده

### دانلود:

#### از GitHub Actions:
1. به "Actions" برید
2. آخرین successful workflow
3. دانلود artifact مورد نظر:
   - `suzi-apk-linux-x64`
   - `suzi-apk-windows-x64.exe`
   - `suzi-apk-macos-x64`

#### از Releases:
```bash
# مثال Linux
wget https://github.com/USERNAME/REPO/releases/download/v1.0.0/suzi-apk-linux-x64
chmod +x suzi-apk-linux-x64
```

### اجرا:

#### Linux/macOS:
```bash
./suzi-apk app.apk
```

#### Windows:
```cmd
suzi-apk.exe app.apk
```

### خروجی:
```
app_out.apk
```

---

## 🧪 تست

### تست محلی:
```bash
# بعد از build
cd dist

# Linux/macOS
./suzi-apk --help
./suzi-apk ../a.apk

# Windows
suzi-apk.exe --help
suzi-apk.exe ..\a.apk
```

### تست امنیت:
```bash
# سعی در استخراج (باید ناموفق باشه)
strings suzi-apk | grep "def process"    # نباید چیزی پیدا کنه
file suzi-apk                             # نشون میده executable
```

---

## 📁 ساختار فایل‌های Build

```
build/                  # فایل‌های موقت build
├── temp.*/
└── lib.*/

dist/                   # خروجی نهایی
├── suzi-apk           # executable
├── tools/             # ابزارهای ضروری
│   ├── apktool.jar
│   ├── linux/
│   ├── macos/
│   └── windows/
└── README.md          # راهنما

*.c                     # فایل‌های C تولید شده (موقت)
*.so / *.pyd           # کتابخانه‌های کامپایل شده (موقت)
suzi_apk.py            # Loader script (موقت)
```

---

## ⚙️ تنظیمات پیشرفته

### تغییر نام executable:
در `build_protected.py`:
```python
exe_name = "your-custom-name"
```

### تنظیمات بیشتر PyInstaller:
در `build_protected.py`:
```python
cmd = [
    ...
    "--icon", "icon.ico",      # آیکون
    "--noconsole",             # بدون console
    "--hidden-import", "X",    # import مخفی
]
```

### اضافه کردن فایل‌های دیگه:
```python
cmd = [
    ...
    "--add-data", "config.json:.",
    "--add-data", "assets:assets",
]
```

---

## 🐛 عیب‌یابی

### خطا: Module not found
```bash
# اضافه کردن به PyInstaller
--hidden-import MODULE_NAME
```

### خطا: Cython compilation failed
```bash
# نصب compiler
# Ubuntu
sudo apt install build-essential python3-dev

# macOS
xcode-select --install

# Windows
# دانلود Visual Studio Build Tools
```

### خطا: Executable doesn't run
```bash
# چک dependencies
ldd suzi-apk              # Linux
otool -L suzi-apk         # macOS
# Windows: Dependency Walker
```

---

## 📚 منابع بیشتر

- [Cython Documentation](https://cython.readthedocs.io/)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [Python Packaging Guide](https://packaging.python.org/)

---

## 🎯 خلاصه

### Build سریع:
```bash
# محلی
python build_protected.py

# یا فقط push کن
git push origin main
```

### استفاده:
```bash
./dist/suzi-apk app.apk
```

### نتیجه:
- ✅ Executable محافظت شده
- ✅ بدون دسترسی به سورس
- ✅ Standalone
- ✅ کراس‌پلتفرم

---

## 🤝 پشتیبانی

ساخته شده با ❤️ توسط **Suzi Brand**

برای مشکلات build، Issue باز کنید.
