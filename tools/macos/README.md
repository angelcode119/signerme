# 🍎 macOS Tools - Suzi APK Processor

ابزارهای مخصوص macOS

## 📦 محتویات

### apktool
Wrapper script برای اجرای apktool.jar روی macOS

**استفاده:**
```bash
chmod +x tools/macos/apktool
./tools/macos/apktool d app.apk
```

## ✅ نیازمندی‌ها

### Java JDK

```bash
# نصب با Homebrew (توصیه می‌شه)
brew install openjdk

# لینک کردن
sudo ln -sfn $(brew --prefix)/opt/openjdk/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk.jdk

# یا دانلود از Oracle
# https://www.oracle.com/java/technologies/downloads/

# چک کردن
java -version
javac -version
```

## 🔧 نصب خودکار

```bash
python3 setup_tools.py
```

## 🎯 استفاده در Suzi

شما نیازی به استفاده مستقیم ندارید!

```python
from m import process
process(filepath="app.apk")
```

همه چیز خودکار! ✨

## 🚀 سریع‌ترین راه

```bash
# 1. نصب Homebrew (اگر نداری)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. نصب Java
brew install openjdk

# 3. نصب ابزارها
python3 setup_tools.py

# 4. استفاده
python3 m.py app.apk
```

یا در کد:
```python
from m import process
process(filepath="app.apk")
```

همین! 🎉
