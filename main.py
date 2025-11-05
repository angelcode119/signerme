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
    
    # تبدیل به مسیر absolute بر اساس current working directory
    if not os.path.isabs(filepath):
        filepath = os.path.join(os.getcwd(), filepath)
    
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
