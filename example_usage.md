# 📱 مثال استفاده از License System

## مثال 1: اضافه کردن به یک پروژه Android Studio

### قدم 1: کپی کردن فایل LicenseChecker

```bash
# کپی کردن به پروژه اندروید
cp LicenseChecker.java /path/to/your/android/project/app/src/main/java/com/suzi/license/
```

### قدم 2: افزودن Permission به AndroidManifest.xml

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.yourapp">
    
    <!-- اجازه دسترسی به اینترنت -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    
    <application
        ...>
        ...
    </application>
</manifest>
```

### قدم 3: استفاده در MainActivity

```java
package com.yourapp;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;
import com.suzi.license.LicenseChecker;

public class MainActivity extends AppCompatActivity {
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // ✨ چک کردن License - اولین خط بعد از super.onCreate
        LicenseChecker.checkLicense(this);
        
        setContentView(R.layout.activity_main);
        
        // بقیه کد برنامه شما...
    }
}
```

---

## مثال 2: کنترل ویژگی‌های خاص

### سناریو: فقط کاربران Premium دسترسی داشته باشن

**license.json:**
```json
{
  "allowed": true,
  "premium": true,
  "features": {
    "remove_ads": true,
    "unlimited_usage": true,
    "cloud_sync": true
  }
}
```

**Enhanced LicenseChecker.java:**
```java
public interface LicenseCallback {
    void onLicenseChecked(boolean allowed, JSONObject features);
}

public static void checkLicense(final Activity activity, final LicenseCallback callback) {
    new AsyncTask<Void, Void, JSONObject>() {
        @Override
        protected JSONObject doInBackground(Void... voids) {
            try {
                URL url = new URL(LICENSE_URL);
                // ... کد دریافت ...
                return new JSONObject(response.toString());
            } catch (Exception e) {
                return null;
            }
        }
        
        @Override
        protected void onPostExecute(JSONObject json) {
            if (json == null || !json.optBoolean("allowed", false)) {
                // بستن برنامه
                activity.finishAffinity();
            } else {
                // ارسال features به callback
                if (callback != null) {
                    callback.onLicenseChecked(true, json.optJSONObject("features"));
                }
            }
        }
    }.execute();
}
```

**استفاده در MainActivity:**
```java
LicenseChecker.checkLicense(this, (allowed, features) -> {
    if (features != null) {
        boolean isPremium = features.optBoolean("remove_ads", false);
        if (isPremium) {
            // مخفی کردن تبلیغات
            hideAds();
        }
        
        boolean hasCloudSync = features.optBoolean("cloud_sync", false);
        if (hasCloudSync) {
            // فعال کردن sync
            enableCloudSync();
        }
    }
});
```

---

## مثال 3: کنترل نسخه (Version Control)

### سناریو: فورس کردن آپدیت برای نسخه‌های قدیمی

**license.json:**
```json
{
  "allowed": true,
  "min_version": 15,
  "latest_version": 20,
  "update_url": "https://example.com/download",
  "message": "لطفا به نسخه جدید آپدیت کنید"
}
```

**در برنامه:**
```java
// در build.gradle
android {
    defaultConfig {
        versionCode 14  // نسخه فعلی
        versionName "1.4"
    }
}
```

```java
// چک کردن نسخه
int currentVersion = BuildConfig.VERSION_CODE;
int minVersion = json.optInt("min_version", 0);

if (currentVersion < minVersion) {
    // نمایش دیالوگ آپدیت اجباری
    new AlertDialog.Builder(activity)
        .setTitle("آپدیت الزامی")
        .setMessage(json.optString("message"))
        .setPositiveButton("دانلود", (dialog, which) -> {
            String url = json.optString("update_url");
            Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
            activity.startActivity(intent);
            activity.finish();
        })
        .setCancelable(false)
        .show();
}
```

---

## مثال 4: Kill Switch برای موارد اضطراری

### سناریو: یک باگ خطرناک پیدا شده، باید همه برنامه‌ها رو متوقف کنیم

```bash
# سریع license رو غیرفعال کن
cat > license.json << EOF
{
  "allowed": false,
  "message": "⚠️ این نسخه به دلیل یک مشکل امنیتی غیرفعال شده است.\n\nلطفا نسخه جدید را از وب‌سایت دانلود کنید.",
  "update_url": "https://suzi.com/download"
}
EOF

git add license.json
git commit -m "Emergency kill switch activated"
git push
```

همین! تمام کاربران که برنامه رو باز کنن، پیام رو می‌بینن و برنامه بسته میشه 🛑

---

## مثال 5: A/B Testing

### سناریو: نمایش ویژگی جدید فقط برای 50% کاربران

**license.json:**
```json
{
  "allowed": true,
  "ab_test": {
    "new_feature_enabled": true,
    "percentage": 50
  }
}
```

**در برنامه:**
```java
JSONObject abTest = json.optJSONObject("ab_test");
if (abTest != null && abTest.optBoolean("new_feature_enabled")) {
    int percentage = abTest.optInt("percentage", 0);
    
    // تولید عدد رندوم 0-100
    int userGroup = new Random().nextInt(100);
    
    if (userGroup < percentage) {
        // نمایش ویژگی جدید
        showNewFeature();
    }
}
```

---

## 🧪 تست سیستم License

### تست 1: برنامه فعال است
```json
{"allowed": true, "message": "همه چیز اوکیه"}
```
✅ برنامه باز میشه و کار می‌کنه

### تست 2: برنامه غیرفعال است
```json
{"allowed": false, "message": "برنامه غیرفعال شده"}
```
❌ Alert نمایش داده میشه و برنامه بسته میشه

### تست 3: سرور در دسترس نیست
- اینترنت رو قطع کنید
- برنامه رو باز کنید
- Default behavior: برنامه بسته میشه (امن‌تر)

### تست 4: پاسخ نامعتبر
```json
{"این": "جیسون نامعتبره"}
```
❌ برنامه بسته میشه

---

## 🎨 سفارشی‌سازی UI

### دیالوگ زیباتر:

```java
new AlertDialog.Builder(activity, R.style.CustomAlertDialog)
    .setTitle("🔒 دسترسی محدود")
    .setMessage(message)
    .setIcon(R.drawable.ic_lock)
    .setPositiveButton("متوجه شدم", (dialog, which) -> {
        activity.finishAffinity();
    })
    .show();
```

### نمایش ProgressDialog:

```java
ProgressDialog dialog = new ProgressDialog(activity);
dialog.setMessage("در حال بررسی مجوز...");
dialog.show();

LicenseChecker.checkLicense(activity, (allowed, features) -> {
    dialog.dismiss();
    // ...
});
```

---

## 📊 آمارگیری

می‌تونید تعداد درخواست‌ها رو در GitHub Actions ببینید یا از سرویس‌های آماری مثل Google Analytics استفاده کنید.

```java
// ارسال event به Analytics
FirebaseAnalytics.getInstance(activity)
    .logEvent("license_check", bundle);
```

---

## 🔐 نکات امنیتی

1. **همیشه HTTPS استفاده کنید** (GitHub Raw همیشه HTTPS هست ✅)
2. **کد check رو obfuscate کنید** با ProGuard/R8
3. **در چند جا check کنید** نه فقط onCreate
4. **از هاردکد کردن URL خودداری کنید** یا رمزش کنید
5. **Cache کردن** نتیجه برای کاهش درخواست‌ها

```java
SharedPreferences prefs = activity.getSharedPreferences("license", MODE_PRIVATE);
long lastCheck = prefs.getLong("last_check", 0);
boolean cachedAllowed = prefs.getBoolean("allowed", false);

// چک هر 1 ساعت
if (System.currentTimeMillis() - lastCheck < 3600000) {
    return cachedAllowed;
}
```
