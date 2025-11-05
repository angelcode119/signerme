# 🔧 Suzi APK Processor - Tools

این پوشه شامل ابزارهای لازم برای پردازش APK است

## 📦 محتویات

```
tools/
├── apktool.jar          # ✅ ابزار decompile/recompile APK
├── linux/               # ✅ ابزارهای مخصوص Linux
│   ├── apktool          # ✅ wrapper script
│   └── README.md        # ✅ راهنما
├── macos/               # ✅ ابزارهای مخصوص macOS
│   ├── apktool          # ✅ wrapper script
│   └── README.md        # ✅ راهنما
├── windows/             # ✅ ابزارهای مخصوص Windows
│   ├── apksigner.bat    # ✅ موجود
│   └── README.md        # (قرار داره اضافه بشه)
└── README.md            # این فایل
```

## 🚀 نصب خودکار

فایل‌های گم‌شده به صورت خودکار دانلود می‌شوند:

```bash
python3 setup_tools.py
```

یا اولین بار که برنامه رو اجرا کنید، خودکار نصب میشه!

## 📥 دانلود دستی (اختیاری)

اگر خواستید خودتون دانلود کنید:

### apktool.jar
```bash
wget https://github.com/iBotPeaches/Apktool/releases/download/v2.9.3/apktool_2.9.3.jar -O tools/apktool.jar
```

### Android Build Tools (برای apksigner)
از Android SDK دانلود کنید:
- https://developer.android.com/studio/releases/build-tools

یا از command line tools:
```bash
# Linux
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip commandlinetools-linux-*.zip
./cmdline-tools/bin/sdkmanager "build-tools;34.0.0"

# Windows
# دانلود از: https://developer.android.com/studio#command-tools
```

## ✅ چک کردن

بعد از نصب:

```bash
java -jar tools/apktool.jar --version
ls tools/windows/apksigner.bat
ls tools/linux/apksigner
```

## 🔐 امضا (Signing)

برای امضای APK از jarsigner استفاده می‌کنیم که با Java JDK می‌آید:

```bash
jarsigner -version
keytool
```

اگر نصب نیستن:

### Ubuntu/Debian:
```bash
sudo apt install default-jdk
```

### CentOS/RHEL:
```bash
sudo yum install java-devel
```

### Windows:
دانلود JDK از: https://www.oracle.com/java/technologies/downloads/

### macOS:
```bash
brew install openjdk
```

## 💡 نکته

سیستم Suzi به طور پیش‌فرض از **jarsigner** استفاده می‌کنه که با JDK می‌آد و نیاز به دانلود ندارید!

فقط مطمئن شوید Java JDK نصب باشه:
```bash
java -version
javac -version
```

## 🎯 سیستم خودکار

کد به صورت خودکار:
1. پلتفرم رو تشخیص میده (Windows/Linux/Mac)
2. فایل‌های مورد نیاز رو چک می‌کنه
3. اگر نبود، دانلود می‌کنه
4. از jarsigner به عنوان fallback استفاده می‌کنه

شما فقط باید Java JDK داشته باشید، بقیه خودکاره! ✨
