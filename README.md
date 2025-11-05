# 🔐 Suzi APK Processor

پردازش و امضای APK با محافظت کامل از سورس کد

---

## 🚀 استفاده سریع

### در کد Python:
```python
import suzi

# فقط یک خط!
result = suzi.process("app.apk")
print(result)  # app_out.apk
```

### Push خودکار:
```bash
python auto_push.py "تغییرات جدید"
```

بعد از 5-10 دقیقه به **GitHub Actions** برو و executable دانلود کن.

### استفاده از executable:
```bash
./suzi-apk app.apk         # Linux/macOS
suzi-apk.exe app.apk       # Windows
```

---

## 📦 نصب

```bash
# نیاز به Java JDK
sudo apt install default-jdk  # Ubuntu/Debian
# یا
brew install openjdk          # macOS

# نصب dependencies
pip install -r requirements.txt
```

**ساینر:** استفاده از `uber-apk-signer` (standalone - داخل پروژه) ✨

---

## 🔧 Build نسخه محافظت شده

### خودکار (توصیه می‌شه):
```bash
git push origin main
```
بعد به **Actions** برو و دانلود کن.

### محلی:
```bash
pip install -r requirements.txt
python build_protected.py
```

---

## ✨ ویژگی‌ها

- ✅ API یک خطی: `suzi.process("app.apk")`
- ✅ **uber-apk-signer:** ساینر قدرتمند standalone (بدون نیاز به Android SDK!)
- ✅ نسخه محافظت شده: کد به C کامپایل شده
- ✅ کراس‌پلتفرم: Linux, Windows, macOS
- ✅ بدون پسوند Python
- ✅ Standalone executable (یک فایل)
- ✅ سیستم License از راه دور
- ✅ Build خودکار با GitHub Actions
- ✅ Encryption + Signing: اول رمزگذاری، بعد امضا

---

## 📁 فایل‌های مهم

```
suzi.py              # API اصلی
auto_push.py         # Push خودکار
m.py                 # نسخه عادی
apk_processor.py     # منطق اصلی
build_protected.py   # Build executable
setup_tools.py       # نصب ابزارها
```

---

## 🔐 License System

کنترل برنامه از راه دور:

**فایل:** `license.json` در ریپوی `angelcode119/signerverify`

```json
{
  "allowed": true,
  "message": "برنامه فعال است"
}
```

**در برنامه Android:**
```java
import com.suzi.license.LicenseChecker;

@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    LicenseChecker.checkLicense(this);
    setContentView(R.layout.activity_main);
}
```

---

## 🤝 پشتیبانی

ساخته شده با ❤️ توسط **Suzi Brand**

Repository: https://github.com/angelcode119/signerme
