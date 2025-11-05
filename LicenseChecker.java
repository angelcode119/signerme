package com.suzi.license;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.AsyncTask;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * Suzi Brand License Checker
 * این کلاس مجوز برنامه را از سرور چک می‌کند
 */
public class LicenseChecker {
    
    // آدرس فایل license روی GitHub (باید با آدرس ریپوی خودتون جایگزین بشه)
    private static final String LICENSE_URL = "https://raw.githubusercontent.com/angelcode119/signerme/main/license.json";
    
    /**
     * چک کردن مجوز برنامه
     * @param activity اکتیویتی که باید بسته بشه اگر مجوز نداشته باشیم
     */
    public static void checkLicense(final Activity activity) {
        new AsyncTask<Void, Void, Boolean>() {
            private String message = "";
            
            @Override
            protected Boolean doInBackground(Void... voids) {
                try {
                    URL url = new URL(LICENSE_URL);
                    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                    connection.setRequestMethod("GET");
                    connection.setConnectTimeout(10000);
                    connection.setReadTimeout(10000);
                    
                    int responseCode = connection.getResponseCode();
                    if (responseCode == 200) {
                        BufferedReader reader = new BufferedReader(
                            new InputStreamReader(connection.getInputStream())
                        );
                        StringBuilder response = new StringBuilder();
                        String line;
                        while ((line = reader.readLine()) != null) {
                            response.append(line);
                        }
                        reader.close();
                        
                        JSONObject json = new JSONObject(response.toString());
                        message = json.optString("message", "بدون پیام");
                        return json.optBoolean("allowed", false);
                    }
                    connection.disconnect();
                } catch (Exception e) {
                    e.printStackTrace();
                    message = "خطا در اتصال به سرور";
                }
                return false;
            }
            
            @Override
            protected void onPostExecute(Boolean allowed) {
                if (!allowed) {
                    // اگر مجوز نداریم، برنامه رو ببند
                    new AlertDialog.Builder(activity)
                        .setTitle("🔒 عدم دسترسی")
                        .setMessage("این نسخه از برنامه غیرفعال شده است.\n\n" + message)
                        .setCancelable(false)
                        .setPositiveButton("خروج", (dialog, which) -> {
                            activity.finishAffinity();
                            System.exit(0);
                        })
                        .show();
                } else {
                    // مجوز داریم، میتونیم ادامه بدیم
                    android.util.Log.d("SuziLicense", "✅ License valid: " + message);
                }
            }
        }.execute();
    }
}
