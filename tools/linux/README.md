# 🐧 Linux Tools - Suzi APK Processor

ابزارهای مخصوص Linux

## 📦 محتویات

### apktool
Wrapper script برای اجرای apktool.jar روی Linux

**استفاده:**
```bash
chmod +x tools/linux/apktool
./tools/linux/apktool d app.apk
```

## ✅ نیازمندی‌ها

### Java JDK
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install default-jdk

# Fedora/CentOS/RHEL
sudo dnf install java-devel
# یا
sudo yum install java-devel

# Arch Linux
sudo pacman -S jdk-openjdk

# چک کردن نصب
java -version
javac -version
keytool
jarsigner
```

## 🔧 نصب خودکار

```bash
python3 setup_tools.py
```

این اسکریپت:
- ✅ Java رو چک می‌کنه
- ✅ apktool.jar رو دانلود می‌کنه
- ✅ wrapper scripts رو قابل اجرا می‌کنه
- ✅ همه چیز رو تست می‌کنه

## 🎯 استفاده در Suzi

شما نیازی به استفاده مستقیم از این فایل‌ها ندارید!

فقط:
```python
from m import process
process(filepath="app.apk")
```

همه چیز خودکار انجام میشه! ✨

## 📝 نکات

1. **jarsigner** از Java JDK می‌آد و نیازی به نصب جداگانه نداره
2. **keytool** هم جزء Java JDK هست
3. فقط مطمئن شو Java JDK (نه فقط JRE) نصب باشه

## 🔍 عیب‌یابی

### خطا: java command not found
```bash
# نصب Java
sudo apt install default-jdk

# اضافه کردن به PATH (اگر لازم بود)
echo 'export JAVA_HOME=/usr/lib/jvm/default-java' >> ~/.bashrc
echo 'export PATH=$PATH:$JAVA_HOME/bin' >> ~/.bashrc
source ~/.bashrc
```

### خطا: jarsigner not found
```bash
# باید JDK نصب کنی (نه فقط JRE)
sudo apt install default-jdk

# یا دانلود از Oracle
# https://www.oracle.com/java/technologies/downloads/
```

### خطا: Permission denied
```bash
chmod +x tools/linux/apktool
```

## 💡 مثال استفاده

```bash
# decompile
./tools/linux/apktool d app.apk -o output_dir

# recompile
./tools/linux/apktool b output_dir -o new_app.apk

# ولی توصیه می‌کنیم از Python API استفاده کنی:
python3 -c "from m import process; process(filepath='app.apk')"
```

## 🚀 سریع‌ترین راه

```bash
# 1. نصب Java
sudo apt install default-jdk

# 2. نصب ابزارها
python3 setup_tools.py

# 3. استفاده
python3 m.py app.apk
```

یا در کد:
```python
from m import process
process(filepath="app.apk")
```

همین! 🎉
