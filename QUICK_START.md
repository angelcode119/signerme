# 🚀 راهنمای سریع - Suzi License System

## کنترل سریع برنامه

### 🟢 فعال کردن برنامه
```bash
# در ریپوی signerverify این فایل رو بذار:
{
  "allowed": true,
  "message": "برنامه فعال است - Suzi Brand ✅"
}
```

### 🔴 غیرفعال کردن برنامه
```bash
# در ریپوی signerverify:
{
  "allowed": false,
  "message": "این نسخه غیرفعال شده است ❌"
}
```

---

## 📍 آدرس License فعلی

**Repository:** `angelcode119/signerverify`  
**File:** `license.json`  
**Raw URL:** 
```
https://raw.githubusercontent.com/angelcode119/signerverify/main/license.json
```

---

## 📱 استفاده در برنامه Android

### قدم 1: کپی کردن فایل
```bash
cp LicenseChecker.java /path/to/your/android/app/src/main/java/com/suzi/license/
```

### قدم 2: افزودن Permission به AndroidManifest.xml
```xml
<uses-permission android:name="android.permission.INTERNET" />
```

### قدم 3: استفاده در MainActivity
```java
import com.suzi.license.LicenseChecker;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // فقط یک خط! 🎯
        LicenseChecker.checkLicense(this);
        
        setContentView(R.layout.activity_main);
    }
}
```

**تمام! 🎉**

---

## ⚡ تست سریع

### تست 1: چک کردن وضعیت فعلی
```bash
curl https://raw.githubusercontent.com/angelcode119/signerverify/main/license.json
```

### تست 2: غیرفعال کردن
در ریپوی `signerverify`:
```bash
echo '{"allowed": false, "message": "تست غیرفعال سازی"}' > license.json
git add license.json
git commit -m "Test: disable app"
git push
```

### تست 3: فعال کردن مجدد
```bash
echo '{"allowed": true, "message": "برنامه فعال است"}' > license.json
git push
```

---

## 🎯 سناریوهای رایج

### 🚫 مسدود کردن نسخه قدیمی
```json
{
  "allowed": false,
  "message": "⚠️ این نسخه منقضی شده است\n\nلطفا نسخه جدید را دانلود کنید",
  "update_url": "https://example.com/download"
}
```

### 💎 فعال کردن Premium
```json
{
  "allowed": true,
  "premium": true,
  "features": {
    "remove_ads": true,
    "unlimited": true
  }
}
```

### 🔧 نگهداری
```json
{
  "allowed": false,
  "message": "🔧 سرور در حال نگهداری است\n\nلطفا بعد از 30 دقیقه مجددا تلاش کنید"
}
```

### ⚠️ Kill Switch اضطراری
```json
{
  "allowed": false,
  "message": "🚨 این نسخه به دلیل مشکل امنیتی غیرفعال شده\n\nبه سرعت آپدیت کنید!"
}
```

---

## 📊 مانیتورینگ

### دیدن درخواست‌ها
- به صفحه Insights > Traffic در GitHub برید
- تعداد views فایل license.json = تعداد چک‌ها

### لاگ‌ها در برنامه
در LogCat فیلتر کنید:
```
tag:SuziLicense
```

---

## 🔐 امنیت

✅ **HTTPS** - GitHub همیشه SSL داره  
✅ **Rate Limit** - GitHub: 5000 request/hour (کافیه!)  
✅ **Backup** - تاریخچه Git همه تغییرات رو داره  
✅ **Fast** - CDN GitHub خیلی سریعه  

### توصیه‌های امنیتی:
1. **ProGuard فعال باشه** تا کد obfuscate بشه
2. **در چند جا check کنید** نه فقط onCreate
3. **Cache کنید** برای کاهش request
4. **SSL Pinning** برای امنیت بیشتر

---

## ❓ مشکلات رایج

### ❌ Error: Unable to resolve host
**علت:** برنامه اجازه INTERNET نداره  
**راه حل:** `<uses-permission android:name="android.permission.INTERNET" />` اضافه کن

### ❌ 404 Not Found
**علت:** آدرس اشتباهه یا فایل license.json در ریپو نیست  
**راه حل:** مطمئن شو فایل در branch `main` هست

### ❌ JSONException
**علت:** فرمت JSON نامعتبره  
**راه حل:** از JSON validator استفاده کن: https://jsonlint.com/

### ⚠️ برنامه باز میشه ولی check نمی‌کنه
**علت:** شاید AsyncTask نتیجه رو برنگردونده  
**راه حل:** لاگ‌ها رو چک کن یا timeout رو زیاد کن

---

## 🎓 لینک‌های مفید

📖 [راهنمای کامل](README_LICENSE.md)  
💡 [مثال‌های عملی](example_usage.md)  
🔧 [Injection Script](inject_license.py)  
📦 [APK Signer](m.py)  

---

## 💬 پشتیبانی

ساخته شده با ❤️ توسط **Suzi Brand**

Repository: https://github.com/angelcode119/signerverify

---

**یادت باشه:** هر تغییری در `license.json` فوری روی همه برنامه‌ها اثر می‌ذاره! 🔥
