#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suzi Brand - APK Processor Runner
رانر فوق‌العاده ساده برای پردازش APK

استفاده:
    from m import process
    process(filepath="app.apk")
"""

import sys
import os

# Import منطق اصلی
from apk_processor import SuziAPKProcessor


def process(filepath, output=None, verbose=False):
    """
    تابع ساده برای پردازش APK - فقط filepath بده!
    
    Args:
        filepath: مسیر فایل APK
        output: نام فایل خروجی (اختیاری)
        verbose: نمایش جزئیات (اختیاری)
    
    Returns:
        مسیر فایل پردازش شده
    
    مثال:
        from m import process
        result = process(filepath="app.apk")
        print(result)  # app_out.apk
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"فایل پیدا نشد: {filepath}")
    
    processor = SuziAPKProcessor(verbose=verbose)
    
    if output is None:
        base = os.path.splitext(os.path.basename(filepath))[0]
        output = f"{base}_out.apk"
    
    return processor.process_apk(filepath, output)


def main():
    """تابع اصلی برای استفاده از command line"""
    if len(sys.argv) != 2:
        print("❌ استفاده نادرست!")
        print("✅ استفاده صحیح: python3 m.py <input.apk>")
        print("\nیا در کد Python:")
        print("    from m import process")
        print("    process(filepath='app.apk')")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    try:
        print(f"🔄 در حال پردازش: {filepath}")
        result = process(filepath=filepath, verbose=False)
        print(f"✅ تمام! خروجی: {result}")
    except Exception as e:
        print(f"❌ خطا: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
