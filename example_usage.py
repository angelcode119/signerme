#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مثال‌های استفاده از Suzi APK Processor

این فایل نشون میده چطور می‌تونی از apk_processor.py در پروژه‌های خودت استفاده کنی
"""

from apk_processor import SuziAPKProcessor, process_apk
import os


def example_1_simple_usage():
    """مثال 1: استفاده ساده - فقط یک خط!"""
    print("=" * 50)
    print("مثال 1: استفاده ساده")
    print("=" * 50)
    
    # فقط یک خط کد!
    result = process_apk("a.apk", "output.apk", verbose=True)
    print(f"\n✅ نتیجه: {result}\n")


def example_2_custom_output():
    """مثال 2: تعیین نام خروجی دلخواه"""
    print("=" * 50)
    print("مثال 2: نام خروجی سفارشی")
    print("=" * 50)
    
    result = process_apk(
        input_apk="a.apk",
        output_apk="my_custom_name.apk",
        verbose=True
    )
    print(f"\n✅ نتیجه: {result}\n")


def example_3_batch_processing():
    """مثال 3: پردازش چندین APK"""
    print("=" * 50)
    print("مثال 3: پردازش دسته‌ای")
    print("=" * 50)
    
    apk_files = ["app1.apk", "app2.apk", "app3.apk"]
    
    for apk in apk_files:
        if os.path.exists(apk):
            print(f"\n📦 در حال پردازش: {apk}")
            try:
                result = process_apk(apk, verbose=False)
                print(f"   ✅ موفق: {result}")
            except Exception as e:
                print(f"   ❌ خطا: {e}")


def example_4_advanced_usage():
    """مثال 4: استفاده پیشرفته با کلاس"""
    print("=" * 50)
    print("مثال 4: استفاده پیشرفته")
    print("=" * 50)
    
    # ساخت instance از processor
    processor = SuziAPKProcessor(
        use_jarsigner=True,
        verbose=True
    )
    
    # مرحله به مرحله
    try:
        # 1. تغییر bit flags
        print("\n📝 مرحله 1: تغییر Bit Flags")
        modified = processor.modify_bit_flags("a.apk", "a_modified.apk")
        
        # 2. ساخت keystore
        print("\n🔑 مرحله 2: ساخت Keystore")
        keystore, password, alias = processor.create_keystore()
        print(f"   Keystore: {keystore}")
        print(f"   Alias: {alias}")
        
        # 3. امضای APK
        print("\n✍️  مرحله 3: امضای APK")
        signed = processor.sign_apk(modified, keystore, password, alias, "a_final.apk")
        
        print(f"\n✅ تمام! فایل نهایی: {signed}")
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
    
    finally:
        # پاکسازی فایل‌های موقت
        processor.cleanup()


def example_5_error_handling():
    """مثال 5: مدیریت خطاها"""
    print("=" * 50)
    print("مثال 5: مدیریت خطاها")
    print("=" * 50)
    
    apk_files = ["existing.apk", "non_existing.apk", "a.apk"]
    
    for apk in apk_files:
        print(f"\n📦 پردازش: {apk}")
        
        try:
            if not os.path.exists(apk):
                raise FileNotFoundError(f"فایل {apk} وجود ندارد")
            
            result = process_apk(apk, verbose=False)
            print(f"   ✅ موفق: {result}")
            
        except FileNotFoundError as e:
            print(f"   ⚠️  فایل پیدا نشد: {e}")
            
        except RuntimeError as e:
            print(f"   ❌ خطا در پردازش: {e}")
            
        except Exception as e:
            print(f"   ❌ خطای غیرمنتظره: {e}")


def example_6_integration():
    """مثال 6: ترکیب با سیستم خودتون"""
    print("=" * 50)
    print("مثال 6: ادغام در سیستم")
    print("=" * 50)
    
    # فرض کنید لیست APKها رو از دیتابیس یا API می‌گیرید
    apks_from_database = [
        {"id": 1, "path": "app1.apk", "name": "MyApp"},
        {"id": 2, "path": "app2.apk", "name": "GameApp"},
    ]
    
    results = []
    
    for apk_info in apks_from_database:
        apk_path = apk_info["path"]
        
        if not os.path.exists(apk_path):
            print(f"⚠️  {apk_info['name']}: فایل موجود نیست")
            continue
        
        try:
            print(f"\n🔄 در حال پردازش: {apk_info['name']}")
            output = f"{apk_info['name']}_processed.apk"
            result = process_apk(apk_path, output, verbose=False)
            
            # ذخیره نتیجه (مثلاً در دیتابیس)
            results.append({
                "id": apk_info["id"],
                "original": apk_path,
                "processed": result,
                "status": "success"
            })
            
            print(f"   ✅ موفق: {result}")
            
        except Exception as e:
            results.append({
                "id": apk_info["id"],
                "original": apk_path,
                "processed": None,
                "status": "failed",
                "error": str(e)
            })
            print(f"   ❌ خطا: {e}")
    
    print("\n📊 خلاصه نتایج:")
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"   {status_icon} ID {result['id']}: {result['status']}")


def example_7_with_config():
    """مثال 7: استفاده با تنظیمات"""
    print("=" * 50)
    print("مثال 7: استفاده با config")
    print("=" * 50)
    
    # تنظیمات پروژه
    config = {
        "input_dir": "input_apks/",
        "output_dir": "output_apks/",
        "use_jarsigner": True,
        "verbose": True,
        "clean_temp": True
    }
    
    # ساخت processor با config
    processor = SuziAPKProcessor(
        use_jarsigner=config["use_jarsigner"],
        verbose=config["verbose"]
    )
    
    # فرض کنید فایل‌ها در پوشه input هستند
    input_dir = config.get("input_dir", "./")
    output_dir = config.get("output_dir", "./")
    
    print(f"📂 Input: {input_dir}")
    print(f"📂 Output: {output_dir}")
    
    # پردازش فایل‌ها
    if os.path.exists(input_dir):
        for filename in os.listdir(input_dir):
            if filename.endswith(".apk"):
                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, f"processed_{filename}")
                
                try:
                    result = processor.process_apk(
                        input_path, 
                        output_path,
                        clean_temp=config["clean_temp"]
                    )
                    print(f"✅ {filename} → {result}")
                except Exception as e:
                    print(f"❌ {filename}: {e}")


if __name__ == "__main__":
    print("\n" + "🎯 " * 20)
    print("Suzi APK Processor - مثال‌های استفاده")
    print("🎯 " * 20 + "\n")
    
    # اجرای مثال‌ها (یکی رو uncomment کنید)
    
    # example_1_simple_usage()
    # example_2_custom_output()
    # example_3_batch_processing()
    # example_4_advanced_usage()
    # example_5_error_handling()
    # example_6_integration()
    # example_7_with_config()
    
    print("\n💡 برای اجرا، یکی از مثال‌ها رو uncomment کنید!")
    print("📖 یا می‌تونید مستقیماً از process_apk استفاده کنید:\n")
    print("    from apk_processor import process_apk")
    print("    process_apk('input.apk', 'output.apk', verbose=True)")
    print()
