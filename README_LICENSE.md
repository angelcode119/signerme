# 🔐 Suzi Brand - License System

سیستم مدیریت مجوز برنامه‌های اندروید با برند Suzi

## 📋 فایل‌های پروژه

- `license.json` - فایل کنترل مجوز روی GitHub
- `LicenseChecker.java` - کد چک کردن مجوز در برنامه اندروید
- `inject_license.py` - اسکریپت اضافه کردن license به APK
- `m.py` - اسکریپت اصلی پردازش و sign کردن APK

## 🚀 نحوه استفاده

### مرحله 1: فعال/غیرفعال کردن مجوز

فایل `license.json` رو ویرایش کنید:

```json
{
  "allowed": true,  // true = برنامه کار می‌کنه | false = برنامه بسته میشه
  "message": "برنامه فعال است - Suzi Brand",
  "version": "1.0",
  "last_update": "2025-11-05"
}
```

بعد commit و push کنید:
```bash
git add license.json
git commit -m "تغییر وضعیت license"
git push
```

### مرحله 2: اضافه کردن License Check به برنامه

#### روش A: اضافه کردن دستی به کد برنامه (توصیه می‌شه)

در `MainActivity.java` یا اولین Activity:

```java
import com.suzi.license.LicenseChecker;

@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    
    // چک کردن مجوز Suzi
    LicenseChecker.checkLicense(this);
    
    setContentView(R.layout.activity_main);
    // بقیه کد شما...
}
```

#### روش B: Injection به APK موجود (پیشرفته)

```bash
python3 inject_license.py app.apk
```

**نکته:** این روش نیاز به تبدیل Java به Smali داره و پیچیده‌تر هست.

### مرحله 3: Sign کردن APK

```bash
python3 m.py your_app.apk
```

خروجی: `your_app_out.apk` با امضای Suzi

## 🔧 تنظیمات پیشرفته

### تغییر URL سرور License

در `LicenseChecker.java` خط 15:

```java
private static final String LICENSE_URL = "https://raw.githubusercontent.com/angelcode119/signerverify/main/license.json";
```

**آدرس فعلی:** `https://raw.githubusercontent.com/angelcode119/signerverify/main/license.json`

**نکته:** از raw.githubusercontent.com استفاده می‌شه، نه github.com/blob/

### افزودن فیلدهای بیشتر به License

می‌تونید فیلدهای دلخواه اضافه کنید:

```json
{
  "allowed": true,
  "message": "نسخه پریمیوم",
  "expiry_date": "2026-01-01",
  "features": {
    "premium": true,
    "ads_free": true
  }
}
```

و در کد Java:

```java
JSONObject json = new JSONObject(response.toString());
boolean premium = json.optJSONObject("features").optBoolean("premium", false);
```

## 📊 نحوه کار

```
برنامه Android (APK)
    ↓
درخواست GET به license.json
    ↓
GitHub Raw File (license.json)
    ↓
دریافت پاسخ {"allowed": true/false}
    ↓
اگر true → برنامه ادامه میده
اگر false → Alert و بستن برنامه
```

## 🔒 امنیت

**نکات امنیتی:**
- این یک license check ساده است، برای امنیت بیشتر:
  - از ProGuard/R8 برای obfuscate کردن کد استفاده کنید
  - SSL Pinning اضافه کنید
  - Server-side verification اضافه کنید
  - کد check رو در چند جا تکرار کنید

## 📝 مثال کامل

### 1. ساخت برنامه با License Check

```java
// در build.gradle اضافه کنید
android {
    ...
    packagingOptions {
        exclude 'META-INF/NOTICE'
        exclude 'META-INF/LICENSE'
    }
}

dependencies {
    implementation 'org.json:json:20210307'
}
```

### 2. غیرفعال کردن برنامه

```bash
# ویرایش license.json
echo '{"allowed": false, "message": "این نسخه منقضی شده است"}' > license.json
git add license.json
git commit -m "غیرفعال کردن برنامه"
git push
```

حالا تمام کاربران که برنامه رو باز کنن، پیام "این نسخه منقضی شده است" رو می‌بینن و برنامه بسته میشه! 🔒

### 3. فعال کردن مجدد

```bash
echo '{"allowed": true, "message": "برنامه فعال است"}' > license.json
git push
```

## 🎯 Use Cases

- ✅ غیرفعال کردن نسخه‌های قدیمی
- ✅ کنترل دسترسی به ویژگی‌های خاص
- ✅ مدیریت نسخه‌های آزمایشی (Beta)
- ✅ Kill switch برای مواقع اضطراری
- ✅ A/B Testing

## 🤝 پشتیبانی

ساخته شده با ❤️ توسط Suzi Brand

برای سوالات و مشکلات، Issue باز کنید.
