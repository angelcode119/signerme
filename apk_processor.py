#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suzi Brand - APK Processor
منطق اصلی پردازش و امضای APK

این ماژول شامل کلاس‌ها و توابع اصلی برای:
- تغییر Bit Flag در APK (بدون باز کردن فایل‌ها)
- ساخت Keystore با برند Suzi
- امضای APK با jarsigner یا apksigner
"""

import os
import sys
import struct
import subprocess
import random
import string
import hashlib
import tempfile
import shutil
import platform
from pathlib import Path
from typing import Tuple, Optional

# Try to import pure Python signer
try:
    from python_signer import sign_apk_pure_python
    HAS_PYTHON_SIGNER = True
except ImportError:
    HAS_PYTHON_SIGNER = False


# مسیر پوشه tools
SCRIPT_DIR = Path(__file__).parent
TOOLS_DIR = SCRIPT_DIR / "tools"


def check_and_setup_tools():
    """چک و نصب خودکار ابزارهای لازم"""
    # اگر tools وجود نداره، نصب کن
    if not TOOLS_DIR.exists() or not (TOOLS_DIR / "apktool.jar").exists():
        print("⚠️  ابزارهای لازم یافت نشد. نصب خودکار...")
        try:
            import setup_tools
            setup_tools.main()
        except Exception as e:
            print(f"⚠️  لطفاً setup_tools.py را اجرا کنید: python3 setup_tools.py")
            print(f"   خطا: {e}")
    
    return TOOLS_DIR


class SuziAPKProcessor:
    """
    کلاس اصلی پردازش APK با برند Suzi
    """
    
    def __init__(self, use_jarsigner: bool = False, verbose: bool = False, auto_setup: bool = True):
        """
        مقداردهی اولیه
        
        Args:
            use_jarsigner: استفاده از jarsigner (پیش‌فرض: False - از uber-apk-signer استفاده می‌شود)
            verbose: نمایش پیام‌های جزئیات (پیش‌فرض: False)
            auto_setup: نصب خودکار ابزارها در صورت نیاز (پیش‌فرض: True)
        """
        self.use_jarsigner = use_jarsigner
        self.use_python_signer = False
        
        self.verbose = verbose
        self.temp_files = []  # لیست فایل‌های موقت برای پاکسازی
        
        # Setup ابزارها
        if auto_setup:
            self.tools_dir = check_and_setup_tools()
        else:
            self.tools_dir = TOOLS_DIR
        
        # مسیرهای ابزارها
        self.apktool_jar = self.tools_dir / "apktool.jar"
        self.uber_apk_signer = self.tools_dir / "uber-apk-signer.jar"
        
        # تشخیص پلتفرم
        self.platform = platform.system().lower()
        
        # لاگ نوع signer
        if self.use_jarsigner:
            self.log("استفاده از jarsigner")
        elif self.uber_apk_signer.exists():
            self.log("استفاده از uber-apk-signer (standalone - بدون نیاز به Android SDK!)")
        else:
            self.log("استفاده از jarsigner (fallback)")
    
    def log(self, message: str):
        """نمایش پیام اگر verbose فعال باشه"""
        if self.verbose:
            print(f"[Suzi APK] {message}")
    
    def generate_random_string(self, length: int = 10) -> str:
        """
        تولید رشته تصادفی
        
        Args:
            length: طول رشته (پیش‌فرض: 10)
            
        Returns:
            رشته تصادفی شامل حروف و اعداد
        """
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    
    def generate_password(self, length: int = 16) -> str:
        """
        تولید پسورد تصادفی
        
        Args:
            length: طول پسورد (پیش‌فرض: 16)
            
        Returns:
            پسورد تصادفی قوی
        """
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_keystore(self) -> Tuple[str, str, str]:
        """
        ساخت keystore با برند Suzi
        
        Returns:
            Tuple[keystore_path, password, alias]
        """
        # ساخت نام فایل keystore با prefix suzi
        ks_name = f"suzi_{hashlib.md5(str(random.getrandbits(128)).encode()).hexdigest()[:8]}.keystore"
        keystore_path = os.path.join(tempfile.gettempdir(), ks_name)
        
        # تولید پسورد و alias
        password = self.generate_password()
        alias = "suzi_" + self.generate_random_string()
        
        self.log(f"Creating keystore: {keystore_path}")
        self.log(f"Alias: {alias}")
        
        # اگر keystore از قبل نداریم، بسازش
        if not os.path.exists(keystore_path):
            cmd = [
                "keytool", "-genkey", "-v",
                "-keystore", keystore_path,
                "-alias", alias,
                "-keyalg", "RSA",
                "-keysize", "2048",
                "-validity", "10000",
                "-storepass", password,
                "-keypass", password,
                "-dname", "CN=suzi, O=Suzi Brand, C=IR"
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL if not self.verbose else None,
                stderr=subprocess.DEVNULL if not self.verbose else None
            )
            
            if result.returncode != 0:
                raise RuntimeError("Failed to create keystore")
            
            self.log("✅ Keystore created successfully")
            self.temp_files.append(keystore_path)
        
        return keystore_path, password, alias
    
    def modify_bit_flags(self, input_apk: str, output_apk: str) -> str:
        """
        تغییر Bit Flag در APK (بدون باز کردن فایل‌ها)
        این تغییر باعث میشه APK به عنوان encrypted شناخته بشه
        
        Args:
            input_apk: مسیر فایل APK ورودی
            output_apk: مسیر فایل APK خروجی
            
        Returns:
            مسیر فایل APK خروجی
            
        Raises:
            FileNotFoundError: اگر فایل ورودی پیدا نشد
            RuntimeError: اگر ساختار APK نامعتبر بود
        """
        # تبدیل به مسیر absolute
        input_apk = os.path.abspath(input_apk)
        output_apk = os.path.abspath(output_apk)
        
        if not os.path.exists(input_apk):
            raise FileNotFoundError(f"Input APK not found: {input_apk}")
        
        self.log(f"Modifying bit flags: {input_apk} -> {output_apk}")
        
        # خواندن فایل APK
        with open(input_apk, 'rb') as f:
            data = f.read()
        
        # پیدا کردن End of Central Directory record
        eocd_offset = data.rfind(b'\x50\x4B\x05\x06')
        if eocd_offset == -1:
            raise RuntimeError("Invalid APK structure: EOCD not found")
        
        # خواندن اطلاعات Central Directory
        cd_size = struct.unpack_from('<I', data, eocd_offset + 12)[0]
        cd_offset = struct.unpack_from('<I', data, eocd_offset + 16)[0]
        
        # ایجاد نسخه قابل تغییر
        modified_data = bytearray(data)
        
        # پیمایش Central Directory و تغییر flag ها
        position = cd_offset
        modified_count = 0
        
        while position < cd_offset + cd_size:
            # چک کردن Central Directory File Header signature
            if data[position:position+4] != b'\x50\x4B\x01\x02':
                break
            
            # آدرس bit flag
            flag_offset = position + 8
            current_flag = struct.unpack_from('<H', data, flag_offset)[0]
            
            # اگر bit 0 (encryption) فعال نیست، فعالش کن
            if not (current_flag & 0x0001):
                new_flag = current_flag | 0x0001
                struct.pack_into('<H', modified_data, flag_offset, new_flag)
                modified_count += 1
            
            # حرکت به file header بعدی
            filename_length = struct.unpack_from('<H', data, position + 28)[0]
            extra_length = struct.unpack_from('<H', data, position + 30)[0]
            comment_length = struct.unpack_from('<H', data, position + 32)[0]
            position += 46 + filename_length + extra_length + comment_length
        
        self.log(f"Modified {modified_count} file entries")
        
        # نوشتن فایل خروجی
        with open(output_apk, 'wb') as f:
            f.write(modified_data)
        
        self.log(f"✅ Bit flags modified successfully")
        self.temp_files.append(output_apk)
        
        return output_apk
    
    def sign_apk(self, input_apk: str, keystore: str, password: str, 
                 alias: str, output_apk: Optional[str] = None) -> str:
        """
        امضای APK با keystore
        
        Args:
            input_apk: مسیر فایل APK ورودی
            keystore: مسیر فایل keystore
            password: پسورد keystore
            alias: alias کلید در keystore
            output_apk: مسیر فایل APK خروجی (اختیاری)
            
        Returns:
            مسیر فایل APK امضا شده
            
        Raises:
            FileNotFoundError: اگر فایل ورودی پیدا نشد
            RuntimeError: اگر امضا ناموفق بود
        """
        # تبدیل به مسیر absolute
        input_apk = os.path.abspath(input_apk)
        
        if not os.path.exists(input_apk):
            raise FileNotFoundError(f"Input APK not found: {input_apk}")
        
        if output_apk is None:
            # ساخت output در همون پوشه input
            base_dir = os.path.dirname(input_apk)
            base_name = os.path.splitext(os.path.basename(input_apk))[0]
            output_apk = os.path.join(base_dir, f"{base_name}_signed.apk")
        else:
            output_apk = os.path.abspath(output_apk)
        
        self.log(f"Signing APK: {input_apk} -> {output_apk}")
        
        if self.use_python_signer:
            # استفاده از Pure Python Signer (بدون نیاز به Java!)
            self.log("استفاده از Pure Python Signer...")
            
            try:
                result = sign_apk_pure_python(input_apk, output_apk, verbose=self.verbose)
                self.log("✅ APK signed with Python signer")
                self.temp_files.append(output_apk)
                return output_apk
            except Exception as e:
                raise RuntimeError(f"Python signer failed: {e}")
        
        elif self.uber_apk_signer.exists() and not self.use_jarsigner:
            # استفاده از uber-apk-signer (standalone, می‌تونه با encrypted files کار کنه!)
            self.log("استفاده از uber-apk-signer...")
            
            cmd = [
                "java", "-jar", str(self.uber_apk_signer),
                "-a", input_apk,
                "--ks", keystore,
                "--ksPass", password,
                "--ksAlias", alias,
                "--ksKeyPass", password,
                "-o", os.path.dirname(output_apk)
            ]
            
            if self.verbose:
                cmd.append("-v")
            
            # اجرا
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                error_msg = f"Failed to sign APK with uber-apk-signer (exit code: {result.returncode})\n"
                error_msg += f"Command: {' '.join(cmd)}\n"
                if result.stdout:
                    error_msg += f"STDOUT: {result.stdout}\n"
                if result.stderr:
                    error_msg += f"STDERR: {result.stderr}\n"
                raise RuntimeError(error_msg)
            
            # uber-apk-signer فایل رو با پسوند -aligned-signed.apk ذخیره می‌کنه
            base_name = os.path.splitext(os.path.basename(input_apk))[0]
            signed_file = os.path.join(os.path.dirname(output_apk), f"{base_name}-aligned-signed.apk")
            
            if os.path.exists(signed_file):
                # جابجایی به output_apk
                shutil.move(signed_file, output_apk)
                self.log("✅ APK signed successfully with uber-apk-signer")
                self.temp_files.append(output_apk)
                return output_apk
            else:
                raise RuntimeError(f"Signed APK not found: {signed_file}")
            
        else:
            # استفاده از jarsigner (fallback)
            # کپی کردن فایل
            try:
                shutil.copy2(input_apk, output_apk)
                self.log(f"Copied to: {output_apk}")
            except Exception as e:
                raise RuntimeError(f"Failed to copy APK: {e}")
            
            # چک کردن فایل کپی شده
            if not os.path.exists(output_apk):
                raise RuntimeError(f"Output APK not created: {output_apk}")
            
            cmd = [
                "jarsigner",
                "-verbose" if self.verbose else "-sigalg", 
                "SHA256withRSA" if not self.verbose else "",
                "-digestalg", "SHA-256",
                "-keystore", keystore,
                "-storepass", password,
                "-keypass", password,
                output_apk,
                alias
            ]
            # حذف المنت‌های خالی
            cmd = [c for c in cmd if c]
            
            if self.verbose:
                cmd.insert(1, "-verbose")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            error_msg = f"Failed to sign APK (exit code: {result.returncode})\n"
            error_msg += f"Command: {' '.join(cmd)}\n"
            if result.stdout:
                error_msg += f"STDOUT: {result.stdout}\n"
            if result.stderr:
                error_msg += f"STDERR: {result.stderr}\n"
            raise RuntimeError(error_msg)
        
        self.log("✅ APK signed successfully")
        self.temp_files.append(output_apk)
        
        return output_apk
    
    def process_apk(self, input_apk: str, output_apk: Optional[str] = None,
                   clean_temp: bool = True) -> str:
        """
        پردازش کامل APK: تغییر bit flag + امضا
        
        Args:
            input_apk: مسیر فایل APK ورودی
            output_apk: مسیر فایل APK خروجی (اختیاری)
            clean_temp: پاکسازی فایل‌های موقت (پیش‌فرض: True)
            
        Returns:
            مسیر فایل APK نهایی
        """
        # تبدیل به مسیر absolute
        input_apk = os.path.abspath(input_apk)
        
        if not os.path.exists(input_apk):
            raise FileNotFoundError(f"Input APK not found: {input_apk}")
        
        input_dir = os.path.dirname(input_apk)
        base_name = os.path.splitext(os.path.basename(input_apk))[0]
        
        if output_apk is None:
            output_apk = os.path.join(input_dir, f"{base_name}_out.apk")
        else:
            output_apk = os.path.abspath(output_apk)
        
        self.log(f"Processing APK: {input_apk}")
        self.log(f"Output: {output_apk}")
        
        # ترتیب صحیح: اول Encrypt بعد Sign
        
        # مرحله 1: تغییر Bit Flag (Encryption)
        temp_modified = os.path.join(input_dir, f"{base_name}_modified.apk")
        self.log("مرحله 1: تغییر Bit Flags (Encryption)")
        self.modify_bit_flags(input_apk, temp_modified)
        
        # مرحله 2: ساخت keystore
        self.log("مرحله 2: ساخت Keystore")
        keystore, password, alias = self.create_keystore()
        
        # مرحله 3: امضای APK (بعد از encryption)
        # jarsigner می‌تونه با encrypted files کار کنه
        temp_signed = os.path.join(input_dir, f"{base_name}_signed.apk")
        self.log("مرحله 3: امضای APK")
        self.sign_apk(temp_modified, keystore, password, alias, temp_signed)
        
        # جابجایی فایل نهایی
        if os.path.exists(output_apk):
            os.remove(output_apk)
        shutil.move(temp_signed, output_apk)
        
        # پاکسازی temp_modified
        if os.path.exists(temp_modified):
            os.remove(temp_modified)
        
        # پاکسازی فایل‌های موقت
        if clean_temp:
            self.cleanup()
        
        self.log(f"✅ APK processing completed: {output_apk}")
        
        return output_apk
    
    def cleanup(self):
        """پاکسازی فایل‌های موقت"""
        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    self.log(f"Cleaned up: {temp_file}")
                except Exception as e:
                    self.log(f"Failed to clean up {temp_file}: {e}")
        self.temp_files.clear()
    
    def __del__(self):
        """Destructor - پاکسازی خودکار"""
        self.cleanup()


# توابع helper برای استفاده ساده‌تر
def process_apk(input_apk: str, output_apk: Optional[str] = None, 
                verbose: bool = False) -> str:
    """
    تابع helper برای پردازش سریع APK
    
    Args:
        input_apk: مسیر فایل APK ورودی
        output_apk: مسیر فایل APK خروجی (اختیاری)
        verbose: نمایش پیام‌های جزئیات
        
    Returns:
        مسیر فایل APK پردازش شده
    """
    processor = SuziAPKProcessor(verbose=verbose)
    return processor.process_apk(input_apk, output_apk)


if __name__ == "__main__":
    # مثال استفاده
    if len(sys.argv) < 2:
        print("Usage: python3 apk_processor.py <input.apk> [output.apk]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = process_apk(input_file, output_file, verbose=True)
        print(f"\n✅ Success! Output: {result}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
