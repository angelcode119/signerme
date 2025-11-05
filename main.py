#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suzi APK Processor - Main Entry Point
نقطه ورود اصلی برای standalone executable

این فایل همه چیز رو داخل خودش داره
"""

import sys
import os

# اضافه کردن مسیر فعلی به sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import مستقیم از apk_processor
from apk_processor import SuziAPKProcessor


def main():
    """تابع اصلی"""
    if len(sys.argv) != 2:
        print("❌ استفاده نادرست!")
        print("✅ استفاده صحیح:")
        print("    suzi-apk app.apk")
        print("\nمثال:")
        print("    suzi-apk myapp.apk")
        print("\nخروجی:")
        print("    myapp_out.apk")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    # تبدیل به مسیر absolute
    # استفاده از realpath برای حل کردن symlink ها
    if not os.path.isabs(filepath):
        # اگه مسیر نسبی هست، نسبت به working directory فعلی resolve کن
        # نه نسبت به مسیر executable!
        import subprocess
        # گرفتن working directory واقعی
        current_dir = os.environ.get('PWD') or os.environ.get('CD')
        if not current_dir:
            # fallback
            current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            # اگه sys.argv[0] خود executable هست، parent directory رو بگیر
            if current_dir.endswith('.exe') or os.path.isfile(current_dir):
                current_dir = os.path.dirname(current_dir)
        
        filepath = os.path.join(current_dir, filepath)
    
    filepath = os.path.abspath(filepath)
    
    if not os.path.exists(filepath):
        print(f"❌ فایل پیدا نشد: {filepath}")
        sys.exit(1)
    
    # تعیین نام خروجی در همون پوشه فایل ورودی
    input_dir = os.path.dirname(filepath)
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    output = os.path.join(input_dir, f"{base_name}_out.apk")
    
    try:
        print(f"🔄 در حال پردازش: {filepath}")
        
        # استفاده از processor
        processor = SuziAPKProcessor(verbose=False)
        result = processor.process_apk(filepath, output)
        
        print(f"✅ تمام! خروجی: {result}")
        
    except FileNotFoundError as e:
        print(f"❌ فایل پیدا نشد: {e}")
        sys.exit(1)
        
    except RuntimeError as e:
        print(f"❌ خطا در پردازش: {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ خطای غیرمنتظره: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
