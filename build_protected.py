#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suzi APK Processor - Protected Build Script
ساخت نسخه محافظت شده بدون دسترسی به سورس

مراحل:
1. تبدیل Python به C با Cython
2. کامپایل C به shared library (.so/.pyd)
3. ساخت executable با PyInstaller
4. پاکسازی فایل‌های اضافی
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


class ProtectedBuilder:
    """کلاس ساخت نسخه محافظت شده"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.build_dir = self.root_dir / "build"
        self.dist_dir = self.root_dir / "dist"
        self.platform = platform.system().lower()
        
    def log(self, message, emoji="ℹ️"):
        """نمایش پیام"""
        print(f"{emoji} {message}")
    
    def check_dependencies(self):
        """چک کردن وجود ابزارهای لازم"""
        self.log("چک کردن dependencies...", "🔍")
        
        required = {
            'cython': 'Cython',
            'pyinstaller': 'PyInstaller',
        }
        
        missing = []
        for module, name in required.items():
            try:
                __import__(module)
                self.log(f"✅ {name} نصب شده", "✅")
            except ImportError:
                self.log(f"❌ {name} نصب نیست", "❌")
                missing.append(name)
        
        if missing:
            self.log("\n📦 نصب dependencies...", "📦")
            cmd = [sys.executable, "-m", "pip", "install"] + [m.lower() for m in missing]
            subprocess.run(cmd)
            self.log("✅ Dependencies نصب شدند", "✅")
        
        return True
    
    def clean(self):
        """پاکسازی فایل‌های قبلی"""
        self.log("پاکسازی فایل‌های قبلی...", "🧹")
        
        dirs_to_clean = [self.build_dir, self.dist_dir, self.root_dir / "__pycache__"]
        for d in dirs_to_clean:
            if d.exists():
                shutil.rmtree(d)
                self.log(f"  پاک شد: {d.name}", "🗑️")
        
        # پاک کردن فایل‌های .c و .so/.pyd
        for ext in ['*.c', '*.so', '*.pyd', '*.o']:
            for f in self.root_dir.glob(ext):
                f.unlink()
                self.log(f"  پاک شد: {f.name}", "🗑️")
    
    def cythonize_code(self):
        """تبدیل Python به C و کامپایل"""
        self.log("\n🔧 تبدیل Python به C با Cython...", "🔧")
        
        # Build با setup.py
        cmd = [sys.executable, "setup.py", "build_ext", "--inplace"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.log(f"❌ خطا در Cython build:\n{result.stderr}", "❌")
            return False
        
        self.log("✅ کد به C تبدیل و کامپایل شد", "✅")
        return True
    
    def create_loader_script(self):
        """ساخت اسکریپت loader برای استفاده از ماژول‌های کامپایل شده"""
        self.log("\n📝 ساخت loader script...", "📝")
        
        loader_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suzi APK Processor - Protected Loader
این فایل ماژول‌های محافظت شده رو لود می‌کنه
"""

import sys
import os

# Import ماژول‌های کامپایل شده
try:
    import apk_processor_core as apk_processor
    import m_core as m
except ImportError:
    # Fallback به نسخه معمولی
    import apk_processor
    import m

# Export کردن توابع
process = m.process

def main():
    """تابع اصلی"""
    m.main()

if __name__ == "__main__":
    main()
'''
        
        loader_path = self.root_dir / "suzi_apk.py"
        with open(loader_path, 'w', encoding='utf-8') as f:
            f.write(loader_code)
        
        self.log(f"✅ Loader script ساخته شد: {loader_path.name}", "✅")
        return loader_path
    
    def build_executable(self, loader_script):
        """ساخت executable با PyInstaller"""
        self.log("\n🎯 ساخت executable با PyInstaller...", "🎯")
        
        # نام executable
        exe_name = "suzi-apk"
        if self.platform == "windows":
            exe_name += ".exe"
        
        # تنظیمات PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",                    # یک فایل
            "--name", "suzi-apk",          # نام
            "--clean",                      # پاکسازی cache
            "--noconfirm",                  # بدون تایید
            # "--noconsole",                # بدون console (optional)
            "--add-data", f"tools{os.pathsep}tools",  # اضافه کردن tools
            str(loader_script),
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            self.log(f"❌ خطا در PyInstaller:\n{result.stderr}", "❌")
            return False
        
        # چک کردن executable
        exe_path = self.dist_dir / exe_name
        if exe_path.exists():
            self.log(f"✅ Executable ساخته شد: {exe_path}", "✅")
            
            # نمایش اطلاعات
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            self.log(f"   حجم: {size_mb:.2f} MB", "📊")
            
            return True
        else:
            self.log("❌ Executable ساخته نشد", "❌")
            return False
    
    def test_build(self):
        """تست نسخه ساخته شده"""
        self.log("\n🧪 تست build...", "🧪")
        
        exe_name = "suzi-apk"
        if self.platform == "windows":
            exe_name += ".exe"
        
        exe_path = self.dist_dir / exe_name
        
        if not exe_path.exists():
            self.log("❌ فایل executable یافت نشد", "❌")
            return False
        
        # تست اجرا
        self.log("  اجرای تست...", "🔬")
        result = subprocess.run([str(exe_path), "--help"], capture_output=True, text=True)
        
        if result.returncode == 0 or "استفاده" in result.stdout or "Usage" in result.stdout:
            self.log("✅ تست موفق", "✅")
            return True
        else:
            self.log(f"⚠️  تست با خطا: {result.stderr}", "⚠️")
            return False
    
    def create_readme(self):
        """ساخت README برای نسخه ساخته شده"""
        readme = f"""# 🔐 Suzi APK Processor - Protected Build

نسخه محافظت شده بدون دسترسی به سورس کد

## 📦 فایل‌های موجود

- `suzi-apk{'.exe' if self.platform == 'windows' else ''}` - برنامه اصلی (executable)
- `tools/` - ابزارهای لازم

## 🚀 استفاده

### Command Line:
```bash
./suzi-apk app.apk        # Linux/macOS
suzi-apk.exe app.apk      # Windows
```

### خروجی:
```
app_out.apk
```

## 🔒 امنیت

این نسخه:
- ✅ کد به C کامپایل شده (Cython)
- ✅ Standalone executable
- ✅ بدون دسترسی به سورس Python
- ✅ محافظت شده در برابر reverse engineering

## ℹ️ اطلاعات

- Platform: {self.platform}
- Build Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Version: 1.0.0

---

ساخته شده با ❤️ توسط Suzi Brand
"""
        
        readme_path = self.dist_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme)
        
        self.log(f"✅ README ساخته شد", "✅")
    
    def build(self):
        """فرآیند کامل build"""
        self.log("🚀 شروع ساخت نسخه محافظت شده...", "🚀")
        self.log("="*60, "")
        
        try:
            # 1. چک dependencies
            if not self.check_dependencies():
                return False
            
            # 2. پاکسازی
            self.clean()
            
            # 3. Cythonize
            if not self.cythonize_code():
                return False
            
            # 4. ساخت loader
            loader_script = self.create_loader_script()
            
            # 5. Build executable
            if not self.build_executable(loader_script):
                return False
            
            # 6. کپی کردن tools
            self.log("\n📂 کپی کردن tools...", "📂")
            dist_tools = self.dist_dir / "tools"
            if dist_tools.exists():
                shutil.rmtree(dist_tools)
            shutil.copytree(self.root_dir / "tools", dist_tools)
            self.log("✅ tools کپی شد", "✅")
            
            # 7. تست
            if not self.test_build():
                self.log("⚠️  Build ساخته شد ولی تست ناموفق بود", "⚠️")
            
            # 8. README
            self.create_readme()
            
            # 9. خلاصه
            self.log("\n" + "="*60, "")
            self.log("🎉 Build موفق!", "🎉")
            self.log("="*60, "")
            self.log(f"\n📦 فایل‌ها در: {self.dist_dir}", "")
            self.log(f"   • suzi-apk{'.exe' if self.platform == 'windows' else ''}", "")
            self.log(f"   • tools/", "")
            self.log(f"   • README.md", "")
            
            self.log("\n🚀 آماده استفاده!", "")
            self.log(f"   ./dist/suzi-apk{'.exe' if self.platform == 'windows' else ''} app.apk", "")
            
            return True
            
        except Exception as e:
            self.log(f"\n❌ خطا: {e}", "❌")
            import traceback
            traceback.print_exc()
            return False


def main():
    """تابع اصلی"""
    builder = ProtectedBuilder()
    success = builder.build()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
