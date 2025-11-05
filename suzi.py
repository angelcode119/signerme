#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suzi APK Processor - API ساده
استفاده فوق‌ساده از نسخه محافظت شده یا عادی

مثال استفاده:
    import suzi
    
    # استفاده ساده
    result = suzi.process("app.apk")
    print(result)  # app_out.apk
"""

import os
import sys
import subprocess
from pathlib import Path


class SuziAPK:
    """کلاس اصلی برای کار با APK"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.dist_dir = self.root_dir / "dist"
        
        # تشخیص executable
        self.executable = self._find_executable()
        
    def _find_executable(self):
        """پیدا کردن نسخه محافظت شده"""
        # چک کردن dist
        if self.dist_dir.exists():
            # Windows
            exe_win = self.dist_dir / "suzi-apk.exe"
            if exe_win.exists():
                return exe_win
            
            # Linux/macOS
            exe_unix = self.dist_dir / "suzi-apk"
            if exe_unix.exists():
                return exe_unix
        
        # اگر executable نبود، از نسخه عادی استفاده کن
        return None
    
    def process(self, filepath, output=None, verbose=False):
        """
        پردازش APK - خیلی ساده!
        
        Args:
            filepath: مسیر فایل APK
            output: نام خروجی (اختیاری)
            verbose: نمایش جزئیات (اختیاری)
        
        Returns:
            مسیر فایل خروجی
        
        مثال:
            import suzi
            result = suzi.process("app.apk")
            print(result)
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"فایل پیدا نشد: {filepath}")
        
        # اگر executable داریم
        if self.executable:
            return self._process_with_executable(filepath, output, verbose)
        
        # اگر نه، از نسخه عادی استفاده کن
        return self._process_with_python(filepath, output, verbose)
    
    def _process_with_executable(self, filepath, output, verbose):
        """استفاده از نسخه محافظت شده (executable)"""
        cmd = [str(self.executable), filepath]
        
        if output:
            cmd.extend(["--output", output])
        
        if verbose:
            print(f"🚀 استفاده از نسخه محافظت شده: {self.executable.name}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"خطا در پردازش: {result.stderr}")
        
        # استخراج نام فایل خروجی
        if output:
            return output
        else:
            base = os.path.splitext(os.path.basename(filepath))[0]
            return f"{base}_out.apk"
    
    def _process_with_python(self, filepath, output, verbose):
        """استفاده از نسخه عادی Python"""
        if verbose:
            print("📝 استفاده از نسخه Python")
        
        # Import نسخه عادی
        from m import process
        return process(filepath=filepath, output=output, verbose=verbose)


# Instance سراسری
_suzi = SuziAPK()


def process(filepath, output=None, verbose=False):
    """
    تابع ساده برای پردازش APK
    
    این تابع خودکار نسخه محافظت شده رو انتخاب می‌کنه
    اگر نبود، از نسخه عادی استفاده می‌کنه
    
    Args:
        filepath: مسیر فایل APK
        output: نام خروجی (اختیاری)
        verbose: نمایش جزئیات (اختیاری)
    
    Returns:
        مسیر فایل خروجی
    
    مثال ساده:
        import suzi
        result = suzi.process("app.apk")
        print(result)  # app_out.apk
    
    مثال با نام خروجی:
        import suzi
        result = suzi.process("app.apk", output="my_app.apk")
    
    مثال با جزئیات:
        import suzi
        result = suzi.process("app.apk", verbose=True)
    """
    return _suzi.process(filepath, output, verbose)


def has_protected_version():
    """چک می‌کنه که آیا نسخه محافظت شده موجوده"""
    return _suzi.executable is not None


def get_version_info():
    """نمایش اطلاعات نسخه"""
    info = {
        "protected": has_protected_version(),
        "executable": str(_suzi.executable) if _suzi.executable else None,
        "python_fallback": True,
    }
    return info


if __name__ == "__main__":
    # تست
    print("🔍 Suzi APK Processor - اطلاعات نسخه")
    print("="*50)
    
    info = get_version_info()
    
    if info["protected"]:
        print("✅ نسخه محافظت شده موجود است")
        print(f"📍 مسیر: {info['executable']}")
    else:
        print("⚠️  نسخه محافظت شده یافت نشد")
        print("📝 استفاده از نسخه Python")
    
    print("\n💡 استفاده:")
    print("    import suzi")
    print("    result = suzi.process('app.apk')")
    print("    print(result)")
