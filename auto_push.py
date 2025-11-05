#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suzi APK Processor - Auto Push
کامیت و پوش خودکار بعد از کدنویسی

استفاده:
    python auto_push.py "پیام commit"
    
    یا در کد:
    import auto_push
    auto_push.push("تغییرات جدید")
"""

import subprocess
import sys


def run_command(cmd, description=""):
    """اجرای دستور shell"""
    if description:
        print(f"🔄 {description}...")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ خطا: {result.stderr}")
        return False
    
    if result.stdout:
        print(result.stdout)
    
    return True


def push(message="Update code", branch=None):
    """
    کامیت و پوش خودکار
    
    Args:
        message: پیام commit
        branch: نام branch (اگر None باشه، branch فعلی استفاده میشه)
    
    مثال:
        import auto_push
        auto_push.push("تغییرات جدید")
    """
    print("🚀 شروع Git Push خودکار")
    print("="*50)
    
    # 1. چک وضعیت
    if not run_command("git status", "چک کردن وضعیت"):
        return False
    
    # 2. اضافه کردن فایل‌ها
    if not run_command("git add -A", "اضافه کردن فایل‌ها"):
        return False
    
    # 3. کامیت
    commit_cmd = f'git commit -m "{message}"'
    print(f"💾 کامیت با پیام: {message}")
    result = subprocess.run(commit_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
            print("⚠️  هیچ تغییری برای کامیت وجود ندارد")
            return True
        else:
            print(f"❌ خطا در کامیت: {result.stderr}")
            return False
    
    print(result.stdout)
    
    # 4. تشخیص branch
    if not branch:
        result = subprocess.run(
            "git branch --show-current",
            shell=True,
            capture_output=True,
            text=True
        )
        branch = result.stdout.strip()
    
    # 5. پوش
    if not run_command(f"git push origin {branch}", f"پوش به {branch}"):
        return False
    
    print("\n✅ موفق!")
    print(f"📤 کد به branch '{branch}' پوش شد")
    print("⏳ حالا منتظر بمون تا GitHub Actions build رو انجام بده")
    print("📍 برو به: https://github.com/YOUR_REPO/actions")
    
    return True


def main():
    """تابع اصلی برای استفاده از command line"""
    if len(sys.argv) < 2:
        print("❌ استفاده نادرست!")
        print("✅ استفاده صحیح:")
        print("    python auto_push.py 'پیام commit'")
        print("\nمثال:")
        print("    python auto_push.py 'اضافه کردن ویژگی جدید'")
        sys.exit(1)
    
    message = sys.argv[1]
    branch = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = push(message, branch)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
