#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suzi APK Processor - Standalone Builder
ساخت یک فایل کامل standalone با Nuitka

این builder یک executable کامل می‌سازه که:
- نیاز به Python نداره
- نیاز به Java نداره
- همه چیز داخلش هست
- یک فایل بدون پسوند
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def log(msg, emoji="ℹ️"):
    """نمایش پیام"""
    print(f"{emoji} {msg}")


def run_cmd(cmd, description=""):
    """اجرای دستور"""
    if description:
        log(f"{description}...", "🔄")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        log(f"خطا: {result.stderr}", "❌")
        return False
    
    if result.stdout:
        print(result.stdout)
    
    return True


def check_nuitka():
    """چک کردن Nuitka"""
    log("چک کردن Nuitka...", "🔍")
    
    result = subprocess.run(
        [sys.executable, "-m", "nuitka", "--version"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        log("Nuitka نصب نیست!", "❌")
        log("در حال نصب Nuitka...", "📦")
        
        subprocess.run([sys.executable, "-m", "pip", "install", "nuitka", "ordered-set"])
        log("✅ Nuitka نصب شد", "✅")
    else:
        log("✅ Nuitka نصب شده است", "✅")
    
    return True


def build_with_nuitka():
    """Build با Nuitka"""
    log("\n🚀 شروع build با Nuitka...", "🚀")
    log("="*60, "")
    
    # تشخیص پلتفرم
    current_platform = platform.system().lower()
    
    # نام خروجی
    output_name = "suzi-apk"
    if current_platform == "windows":
        output_name = "suzi-apk.exe"
    
    # دستور Nuitka
    cmd = [
        sys.executable,
        "-m", "nuitka",
        "--standalone",                    # standalone mode
        "--onefile",                       # یک فایل
        "--remove-output",                 # پاک کردن build قبلی
        "--assume-yes-for-downloads",      # دانلود خودکار
        f"--output-filename={output_name}", # نام خروجی
        "--output-dir=dist",               # پوشه خروجی
        
        # بهینه‌سازی
        "--lto=yes",                       # Link Time Optimization
        "--jobs=4",                        # استفاده از 4 core
        
        # Include کردن فایل‌ها
        "--include-data-dir=tools=tools",  # اضافه کردن tools
        
        # Include ماژول‌ها
        "--include-module=apk_processor",  # اضافه کردن apk_processor
        
        # Module های مورد نیاز
        "--follow-imports",                # دنبال کردن importها
        
        # فایل اصلی
        "main.py"
    ]
    
    log(f"Command: {' '.join(cmd)}", "💻")
    log("\n⏳ این ممکنه چند دقیقه طول بکشه...\n", "⏳")
    
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        log("❌ Build ناموفق بود!", "❌")
        return False
    
    log("\n✅ Build موفق!", "✅")
    
    # چک کردن فایل خروجی
    output_path = Path("dist") / output_name
    if output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        log(f"📦 فایل: {output_path}", "📦")
        log(f"📊 حجم: {size_mb:.2f} MB", "📊")
        
        # در Linux/macOS قابل اجرا کن
        if current_platform != "windows":
            os.chmod(output_path, 0o755)
            log("✅ قابل اجرا شد", "✅")
        
        return True
    else:
        log("❌ فایل خروجی پیدا نشد!", "❌")
        return False


def test_executable():
    """تست executable"""
    log("\n🧪 تست executable...", "🧪")
    
    current_platform = platform.system().lower()
    exe_name = "suzi-apk.exe" if current_platform == "windows" else "suzi-apk"
    exe_path = Path("dist") / exe_name
    
    if not exe_path.exists():
        log("❌ فایل پیدا نشد!", "❌")
        return False
    
    # تست اجرا
    cmd = [str(exe_path), "--help"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0 or "usage" in result.stdout.lower() or "استفاده" in result.stdout:
        log("✅ تست موفق!", "✅")
        return True
    else:
        log("⚠️ تست با خطا مواجه شد", "⚠️")
        return False


def create_readme():
    """ساخت README"""
    current_platform = platform.system().lower()
    exe_name = "suzi-apk.exe" if current_platform == "windows" else "suzi-apk"
    
    readme = f"""# Suzi APK Processor - Standalone

یک فایل کامل بدون نیاز به نصب چیزی!

## استفاده

```bash
./{exe_name} app.apk         # Linux/macOS
{exe_name} app.apk          # Windows
```

## ویژگی‌ها

✅ بدون نیاز به Python
✅ بدون نیاز به Java (فقط برای اولین بار)
✅ همه چیز داخل یک فایل
✅ standalone کامل

## خروجی

```
app_out.apk
```

---

Built with ❤️ by Suzi Brand
"""
    
    readme_path = Path("dist") / "README.txt"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)
    
    log("✅ README ساخته شد", "✅")


def main():
    """تابع اصلی"""
    log("🎯 Suzi APK Processor - Standalone Builder", "🎯")
    log("="*60, "")
    
    try:
        # 1. چک Nuitka
        if not check_nuitka():
            return False
        
        # 2. Build
        if not build_with_nuitka():
            return False
        
        # 3. تست
        test_executable()
        
        # 4. README
        create_readme()
        
        # خلاصه
        log("\n" + "="*60, "")
        log("🎉 موفق!", "🎉")
        log("="*60, "")
        
        current_platform = platform.system().lower()
        exe_name = "suzi-apk.exe" if current_platform == "windows" else "suzi-apk"
        
        log(f"\n📦 فایل خروجی: dist/{exe_name}", "")
        log("\n🚀 استفاده:", "")
        log(f"   cd dist", "")
        log(f"   ./{exe_name} app.apk", "")
        
        return True
        
    except Exception as e:
        log(f"\n❌ خطا: {e}", "❌")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
