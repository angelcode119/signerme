#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suzi Brand - APK Processor Runner
اسکریپت اجرایی ساده برای پردازش APK

این فایل فقط یک wrapper ساده برای apk_processor است
منطق اصلی در apk_processor.py قرار داره
"""

import sys
import os

# Import کردن منطق اصلی
from apk_processor import process_apk


def main():
    """تابع اصلی runner"""
    # چک کردن آرگومان‌ها
    if len(sys.argv) != 2:
        print("❌ استفاده نادرست!")
        print("✅ استفاده صحیح: python3 m.py <input.apk>")
        print("\nمثال:")
        print("  python3 m.py app.apk")
        sys.exit(1)
    
    input_apk = sys.argv[1]
    
    # چک کردن وجود فایل
    if not os.path.exists(input_apk):
        print(f"❌ فایل پیدا نشد: {input_apk}")
        sys.exit(1)
    
    # تعیین نام فایل خروجی
    base_name = os.path.splitext(os.path.basename(input_apk))[0]
    output_apk = f"{base_name}_out.apk"
    
    try:
        # پردازش APK با استفاده از منطق اصلی
        print(f"🔄 در حال پردازش: {input_apk}")
        result = process_apk(input_apk, output_apk, verbose=False)
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
