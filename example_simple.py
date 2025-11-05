#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مثال ساده استفاده از Suzi APK Processor

این فایل نشون میده چطور خیلی ساده از suzi استفاده کنی
"""

import suzi


def example_1_simple():
    """مثال 1: ساده‌ترین حالت"""
    print("=" * 50)
    print("مثال 1: استفاده ساده")
    print("=" * 50)
    
    # فقط یک خط!
    result = suzi.process("a.apk")
    print(f"✅ نتیجه: {result}\n")


def example_2_custom_name():
    """مثال 2: با نام دلخواه"""
    print("=" * 50)
    print("مثال 2: نام خروجی سفارشی")
    print("=" * 50)
    
    result = suzi.process(
        filepath="a.apk",
        output="my_custom_app.apk"
    )
    print(f"✅ نتیجه: {result}\n")


def example_3_with_details():
    """مثال 3: با نمایش جزئیات"""
    print("=" * 50)
    print("مثال 3: با جزئیات")
    print("=" * 50)
    
    result = suzi.process(
        filepath="a.apk",
        verbose=True  # نمایش تمام مراحل
    )
    print(f"✅ نتیجه: {result}\n")


def example_4_multiple_apks():
    """مثال 4: پردازش چند APK"""
    print("=" * 50)
    print("مثال 4: پردازش چندین APK")
    print("=" * 50)
    
    import os
    
    # پیدا کردن همه APKها
    apks = [f for f in os.listdir(".") if f.endswith(".apk")]
    print(f"📦 {len(apks)} APK پیدا شد\n")
    
    for apk in apks:
        print(f"🔄 در حال پردازش: {apk}")
        try:
            result = suzi.process(apk)
            print(f"   ✅ موفق: {result}")
        except Exception as e:
            print(f"   ❌ خطا: {e}")
    
    print()


def example_5_check_version():
    """مثال 5: چک کردن نسخه"""
    print("=" * 50)
    print("مثال 5: اطلاعات نسخه")
    print("=" * 50)
    
    # چک کردن نسخه محافظت شده
    if suzi.has_protected_version():
        print("✅ نسخه محافظت شده موجود است")
    else:
        print("⚠️  نسخه محافظت شده موجود نیست")
        print("📝 استفاده از نسخه Python")
    
    # نمایش اطلاعات کامل
    info = suzi.get_version_info()
    print(f"\n📊 جزئیات:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    print()


def example_6_error_handling():
    """مثال 6: مدیریت خطا"""
    print("=" * 50)
    print("مثال 6: مدیریت خطا")
    print("=" * 50)
    
    try:
        # فایل موجود
        result = suzi.process("a.apk")
        print(f"✅ موفق: {result}")
        
    except FileNotFoundError as e:
        print(f"❌ فایل پیدا نشد: {e}")
        
    except Exception as e:
        print(f"❌ خطا: {e}")
    
    print()


def main():
    """اجرای همه مثال‌ها"""
    print("\n" + "🎯 " * 20)
    print("Suzi APK Processor - مثال‌های ساده")
    print("🎯 " * 20 + "\n")
    
    # انتخاب مثال
    print("کدوم مثال رو میخوای ببینی؟")
    print("1. ساده‌ترین حالت")
    print("2. با نام دلخواه")
    print("3. با جزئیات")
    print("4. چندین APK")
    print("5. چک نسخه")
    print("6. مدیریت خطا")
    print("7. همه")
    print()
    
    choice = input("انتخاب (1-7): ").strip()
    
    print()
    
    examples = {
        "1": example_1_simple,
        "2": example_2_custom_name,
        "3": example_3_with_details,
        "4": example_4_multiple_apks,
        "5": example_5_check_version,
        "6": example_6_error_handling,
    }
    
    if choice in examples:
        examples[choice]()
    elif choice == "7":
        for example_func in examples.values():
            example_func()
    else:
        print("❌ انتخاب نامعتبر!")
    
    print("✅ تمام!")


if __name__ == "__main__":
    # اگر از command line اجرا بشه
    main()
