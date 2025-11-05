#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suzi APK Processor - Tools Setup
نصب خودکار ابزارهای مورد نیاز

این اسکریپت به صورت خودکار ابزارهای لازم رو دانلود و نصب می‌کنه
"""

import os
import sys
import platform
import urllib.request
import shutil
import stat
from pathlib import Path


# مسیرها
TOOLS_DIR = Path(__file__).parent / "tools"
TOOLS_DIR.mkdir(exist_ok=True)

# لینک‌های دانلود
APKTOOL_URL = "https://github.com/iBotPeaches/Apktool/releases/download/v2.9.3/apktool_2.9.3.jar"
APKTOOL_PATH = TOOLS_DIR / "apktool.jar"

# Android Build Tools - برای apksigner
BUILD_TOOLS_VERSION = "34.0.0"
COMMANDLINE_TOOLS_LINUX = "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
COMMANDLINE_TOOLS_MAC = "https://dl.google.com/android/repository/commandlinetools-mac-11076708_latest.zip"
COMMANDLINE_TOOLS_WIN = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"


def log(message, emoji="ℹ️"):
    """نمایش پیام"""
    print(f"{emoji} {message}")


def detect_platform():
    """تشخیص سیستم عامل"""
    system = platform.system().lower()
    if system == "linux":
        return "linux"
    elif system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "unknown"


def download_file(url, dest, description=""):
    """دانلود فایل با progress"""
    try:
        log(f"در حال دانلود {description}...", "⬇️")
        
        # دانلود با progress
        def reporthook(blocknum, blocksize, totalsize):
            if totalsize > 0:
                percent = min(blocknum * blocksize * 100 / totalsize, 100)
                print(f"\r  Progress: {percent:.1f}%", end="", flush=True)
        
        urllib.request.urlretrieve(url, dest, reporthook)
        print()  # new line
        
        log(f"✅ دانلود موفق: {dest.name}", "✅")
        return True
        
    except Exception as e:
        log(f"خطا در دانلود: {e}", "❌")
        return False


def check_java():
    """چک کردن نصب بودن Java"""
    try:
        import subprocess
        result = subprocess.run(
            ["java", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        
        if result.returncode == 0:
            # استخراج نسخه
            output = result.stderr.decode() + result.stdout.decode()
            log("✅ Java نصب شده است", "✅")
            
            # چک کردن jarsigner
            result2 = subprocess.run(
                ["jarsigner"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            if "jarsigner" in result2.stderr.decode().lower() or "usage" in result2.stderr.decode().lower():
                log("✅ jarsigner موجود است", "✅")
                return True
            else:
                log("⚠️  jarsigner پیدا نشد - نیاز به JDK", "⚠️")
                return False
        else:
            return False
            
    except FileNotFoundError:
        log("❌ Java نصب نیست!", "❌")
        return False
    except Exception as e:
        log(f"خطا در چک کردن Java: {e}", "⚠️")
        return False


def setup_apktool():
    """نصب apktool"""
    if APKTOOL_PATH.exists():
        log(f"✅ apktool قبلاً نصب شده: {APKTOOL_PATH}", "✅")
        return True
    
    log("📦 نصب apktool...", "📦")
    success = download_file(APKTOOL_URL, APKTOOL_PATH, "apktool.jar")
    
    if success and APKTOOL_PATH.exists():
        log(f"✅ apktool نصب شد: {APKTOOL_PATH}", "✅")
        return True
    else:
        log("❌ نصب apktool ناموفق بود", "❌")
        return False


def setup_apksigner():
    """نصب apksigner از Android SDK"""
    current_platform = detect_platform()
    
    # چک کردن اگر قبلاً نصب شده
    if current_platform == "windows":
        apksigner_path = TOOLS_DIR / "windows" / "apksigner.jar"
    else:
        apksigner_path = TOOLS_DIR / "linux" / "apksigner"
    
    if apksigner_path.exists():
        log(f"✅ apksigner قبلاً نصب شده", "✅")
        return True
    
    log("📦 دانلود Android SDK Command Line Tools...", "📦")
    log("⚠️  این ممکنه چند دقیقه طول بکشه...", "⚠️")
    
    # انتخاب URL بر اساس پلتفرم
    if current_platform == "linux":
        tools_url = COMMANDLINE_TOOLS_LINUX
    elif current_platform == "macos":
        tools_url = COMMANDLINE_TOOLS_MAC
    elif current_platform == "windows":
        tools_url = COMMANDLINE_TOOLS_WIN
    else:
        log("❌ پلتفرم شناخته نشده", "❌")
        return False
    
    # دانلود
    import tempfile
    import zipfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        zip_path = tmpdir / "commandlinetools.zip"
        
        if not download_file(tools_url, zip_path, "SDK Command Line Tools"):
            log("❌ دانلود ناموفق بود", "❌")
            return False
        
        # استخراج
        log("📂 در حال استخراج...", "📂")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
            
            # پیدا کردن apksigner در فایل‌های استخراج شده
            # معمولاً در build-tools قرار داره
            log("🔍 جستجو برای apksigner...", "🔍")
            
            # ساخت پوشه‌های مقصد
            (TOOLS_DIR / "windows").mkdir(parents=True, exist_ok=True)
            (TOOLS_DIR / "linux").mkdir(parents=True, exist_ok=True)
            
            # نوت: SDK Command Line Tools به build-tools نیاز داره
            # برای سادگی، از jarsigner استفاده می‌کنیم که با JDK می‌آد
            log("ℹ️  apksigner نیاز به Android SDK کامل داره", "ℹ️")
            log("✅ از jarsigner (با Java JDK) استفاده می‌کنیم", "✅")
            return True
            
        except Exception as e:
            log(f"❌ خطا در استخراج: {e}", "❌")
            return False


def create_wrapper_scripts():
    """ساخت wrapper scripts برای راحتی استفاده"""
    current_platform = detect_platform()
    
    if current_platform == "linux":
        # چک کردن wrapper script موجود
        platform_dir = TOOLS_DIR / "linux"
        apktool_script = platform_dir / "apktool"
        
        if apktool_script.exists():
            # قابل اجرا کردن
            os.chmod(apktool_script, os.stat(apktool_script).st_mode | stat.S_IEXEC)
            log(f"✅ Linux wrapper script آماده: {apktool_script}", "✅")
        else:
            log("⚠️  Linux wrapper script یافت نشد", "⚠️")
        
        # ساخت wrapper اصلی
        main_wrapper = TOOLS_DIR / "apktool"
        with open(main_wrapper, "w") as f:
            f.write(f"""#!/bin/bash
# Suzi APK Processor - apktool wrapper
java -jar "{APKTOOL_PATH.absolute()}" "$@"
""")
        os.chmod(main_wrapper, os.stat(main_wrapper).st_mode | stat.S_IEXEC)
        log(f"✅ Main wrapper script ساخته شد: {main_wrapper}", "✅")
        
    elif current_platform == "macos":
        # چک کردن wrapper script موجود
        platform_dir = TOOLS_DIR / "macos"
        apktool_script = platform_dir / "apktool"
        
        if apktool_script.exists():
            # قابل اجرا کردن
            os.chmod(apktool_script, os.stat(apktool_script).st_mode | stat.S_IEXEC)
            log(f"✅ macOS wrapper script آماده: {apktool_script}", "✅")
        else:
            log("⚠️  macOS wrapper script یافت نشد", "⚠️")
        
        # ساخت wrapper اصلی
        main_wrapper = TOOLS_DIR / "apktool"
        with open(main_wrapper, "w") as f:
            f.write(f"""#!/bin/bash
# Suzi APK Processor - apktool wrapper
java -jar "{APKTOOL_PATH.absolute()}" "$@"
""")
        os.chmod(main_wrapper, os.stat(main_wrapper).st_mode | stat.S_IEXEC)
        log(f"✅ Main wrapper script ساخته شد: {main_wrapper}", "✅")
        
    elif current_platform == "windows":
        # ساخت wrapper برای Windows
        apktool_script = TOOLS_DIR / "apktool.bat"
        with open(apktool_script, "w") as f:
            f.write(f"""@echo off
REM Suzi APK Processor - apktool wrapper
java -jar "{APKTOOL_PATH.absolute()}" %*
""")
        log(f"✅ Windows wrapper script ساخته شد: {apktool_script}", "✅")


def show_java_install_help():
    """راهنمای نصب Java"""
    current_platform = detect_platform()
    
    log("\n" + "="*60, "")
    log("📚 راهنمای نصب Java JDK", "📚")
    log("="*60, "")
    
    if current_platform == "linux":
        log("\nبرای Ubuntu/Debian:", "🐧")
        log("  sudo apt update", "")
        log("  sudo apt install default-jdk", "")
        log("\nبرای CentOS/RHEL:", "🐧")
        log("  sudo yum install java-devel", "")
        
    elif current_platform == "macos":
        log("\nبرای macOS:", "🍎")
        log("  brew install openjdk", "")
        
    elif current_platform == "windows":
        log("\nبرای Windows:", "🪟")
        log("  دانلود از: https://www.oracle.com/java/technologies/downloads/", "")
        log("  یا: https://adoptium.net/", "")
    
    log("\n" + "="*60, "")


def main():
    """تابع اصلی"""
    log("🚀 Suzi APK Processor - Tools Setup", "🚀")
    log("="*60, "")
    
    # تشخیص پلتفرم
    current_platform = detect_platform()
    log(f"سیستم عامل: {current_platform}", "💻")
    
    # چک کردن Java
    log("\n" + "="*60, "")
    log("چک کردن Java...", "🔍")
    java_ok = check_java()
    
    if not java_ok:
        log("\n⚠️  هشدار: Java JDK نصب نیست یا کامل نیست", "⚠️")
        log("   Suzi APK Processor به Java JDK نیاز دارد", "")
        show_java_install_help()
        log("\n⚠️  بعد از نصب Java، این اسکریپت رو دوباره اجرا کنید", "⚠️")
        return False
    
    # نصب apktool
    log("\n" + "="*60, "")
    log("نصب ابزارها...", "🔧")
    
    success = setup_apktool()
    
    if not success:
        log("\n❌ نصب ناموفق بود", "❌")
        return False
    
    # توضیح apksigner
    log("\n" + "="*60, "")
    log("ℹ️  درباره apksigner:", "ℹ️")
    log("   apksigner جزء Android SDK Build Tools است", "")
    log("   برای سادگی از jarsigner استفاده می‌کنیم", "")
    log("   jarsigner با Java JDK می‌آید و نیازی به نصب جداگانه نیست", "")
    
    # ساخت wrapper scripts
    log("\n" + "="*60, "")
    create_wrapper_scripts()
    
    # خلاصه
    log("\n" + "="*60, "")
    log("🎉 نصب کامل شد!", "🎉")
    log("="*60, "")
    
    log("\n✅ ابزارهای نصب شده:", "")
    log(f"  • apktool: {APKTOOL_PATH}", "")
    log(f"  • jarsigner: از Java JDK", "")
    log(f"  • keytool: از Java JDK", "")
    
    log("\n🚀 آماده استفاده!", "")
    log("   python3 m.py <your_app.apk>", "")
    log("\nیا در کد:", "")
    log("   from m import process", "")
    log("   process(filepath='app.apk')", "")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log("\n\n⚠️  لغو شد توسط کاربر", "⚠️")
        sys.exit(1)
    except Exception as e:
        log(f"\n❌ خطای غیرمنتظره: {e}", "❌")
        import traceback
        traceback.print_exc()
        sys.exit(1)
