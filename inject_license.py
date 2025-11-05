#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suzi Brand - License Injector
این اسکریپت کد چک کردن license رو به APK اضافه می‌کنه
"""

import os
import sys
import subprocess
import shutil
import zipfile
import re

APKTOOL_JAR = "apktool.jar"
LICENSE_JAVA = "LicenseChecker.java"

def log(msg):
    print(f"[Suzi] {msg}")

def decompile_apk(apk_path, output_dir):
    """Decompile APK با apktool"""
    log(f"در حال decompile کردن {apk_path}...")
    cmd = ["java", "-jar", APKTOOL_JAR, "d", apk_path, "-o", output_dir, "-f"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"❌ خطا در decompile: {result.stderr}")
        return False
    log("✅ Decompile موفق")
    return True

def find_main_activity_smali(decompiled_dir):
    """پیدا کردن MainActivity.smali"""
    log("در حال جستجوی MainActivity...")
    
    # خواندن AndroidManifest.xml برای پیدا کردن MainActivity
    manifest_path = os.path.join(decompiled_dir, "AndroidManifest.xml")
    if not os.path.exists(manifest_path):
        log("❌ AndroidManifest.xml پیدا نشد")
        return None
    
    # جستجو در فولدر smali
    smali_dir = os.path.join(decompiled_dir, "smali")
    if not os.path.exists(smali_dir):
        smali_dir = os.path.join(decompiled_dir, "smali_classes2")
    
    if not os.path.exists(smali_dir):
        log("❌ پوشه smali پیدا نشد")
        return None
    
    # پیدا کردن MainActivity
    for root, dirs, files in os.walk(smali_dir):
        for file in files:
            if "MainActivity.smali" in file:
                full_path = os.path.join(root, file)
                log(f"✅ MainActivity پیدا شد: {full_path}")
                return full_path
    
    log("⚠️  MainActivity پیدا نشد، از اولین Activity استفاده می‌کنیم")
    # اگر MainActivity نبود، اولین Activity رو پیدا کن
    for root, dirs, files in os.walk(smali_dir):
        for file in files:
            if file.endswith("Activity.smali"):
                full_path = os.path.join(root, file)
                log(f"✅ Activity پیدا شد: {full_path}")
                return full_path
    
    return None

def inject_license_check(smali_file):
    """اضافه کردن کد چک license به smali"""
    log(f"در حال inject کردن license check به {os.path.basename(smali_file)}...")
    
    with open(smali_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # پیدا کردن متد onCreate
    oncreate_pattern = r'(\.method\s+(?:protected\s+)?onCreate\(Landroid/os/Bundle;\)V.*?\.locals\s+\d+)'
    
    match = re.search(oncreate_pattern, content, re.DOTALL)
    if not match:
        log("❌ متد onCreate پیدا نشد")
        return False
    
    # کد smali برای چک کردن license
    license_check_code = """
    # Suzi License Check - شروع
    invoke-static {p0}, Lcom/suzi/license/LicenseChecker;->checkLicense(Landroid/app/Activity;)V
    # Suzi License Check - پایان
    """
    
    # اضافه کردن کد بعد از .locals
    insert_pos = match.end()
    new_content = content[:insert_pos] + license_check_code + content[insert_pos:]
    
    # ذخیره فایل
    with open(smali_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    log("✅ License check به smali اضافه شد")
    return True

def add_license_checker_class(decompiled_dir):
    """اضافه کردن کلاس LicenseChecker به APK"""
    log("در حال اضافه کردن کلاس LicenseChecker...")
    
    # پیدا کردن پوشه smali
    smali_dir = os.path.join(decompiled_dir, "smali")
    if not os.path.exists(smali_dir):
        smali_dir = os.path.join(decompiled_dir, "smali_classes2")
    
    # ساخت پوشه com/suzi/license
    license_dir = os.path.join(smali_dir, "com", "suzi", "license")
    os.makedirs(license_dir, exist_ok=True)
    
    # کپی کردن فایل Java به عنوان مرجع (باید به smali تبدیل بشه)
    # برای سادگی، یک نوت می‌ذاریم که باید manual compile بشه
    note_path = os.path.join(license_dir, "README.txt")
    with open(note_path, 'w', encoding='utf-8') as f:
        f.write("""
این پوشه باید شامل LicenseChecker.smali باشه
فایل Java در پوشه اصلی پروژه موجوده: LicenseChecker.java

برای تبدیل Java به smali:
1. Java رو compile کنید: javac LicenseChecker.java
2. با d8/dx به dex تبدیل کنید
3. با apktool/baksmali به smali تبدیل کنید

یا می‌تونید از ابزار online استفاده کنید.
        """)
    
    log("✅ پوشه LicenseChecker آماده شد")
    return True

def recompile_apk(decompiled_dir, output_apk):
    """Recompile APK با apktool"""
    log(f"در حال recompile کردن به {output_apk}...")
    cmd = ["java", "-jar", APKTOOL_JAR, "b", decompiled_dir, "-o", output_apk]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"❌ خطا در recompile: {result.stderr}")
        return False
    log("✅ Recompile موفق")
    return True

def main():
    if len(sys.argv) != 2:
        print("استفاده: python3 inject_license.py <input.apk>")
        sys.exit(1)
    
    input_apk = sys.argv[1]
    if not os.path.exists(input_apk):
        log(f"❌ فایل {input_apk} پیدا نشد")
        sys.exit(1)
    
    base_name = os.path.splitext(os.path.basename(input_apk))[0]
    decompiled_dir = f"{base_name}_decompiled"
    output_apk = f"{base_name}_with_license.apk"
    
    # پاکسازی پوشه قبلی
    if os.path.exists(decompiled_dir):
        shutil.rmtree(decompiled_dir)
    
    # مراحل injection
    if not decompile_apk(input_apk, decompiled_dir):
        sys.exit(1)
    
    # Note: برای سادگی، فقط structure رو آماده می‌کنیم
    # کاربر باید manual LicenseChecker.smali رو اضافه کنه
    add_license_checker_class(decompiled_dir)
    
    log("""
⚠️  توجه: برای کامل کردن license injection:
1. فایل LicenseChecker.java رو به smali تبدیل کنید
2. فایل .smali رو در {}/smali/com/suzi/license/ قرار بدید
3. سپس این اسکریپت رو دوباره اجرا کنید

یا می‌تونید از m.py برای sign کردن استفاده کنید.
    """.format(decompiled_dir))
    
    log("✅ تمام! پوشه decompiled آماده است.")

if __name__ == "__main__":
    main()
