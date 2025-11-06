# 🖥️ توصیه سرور برای Production

## 🎯 مشخصات توصیه شده:

### **حداقل (Minimum):**
```
CPU: 2 vCPU / Cores
RAM: 4 GB
Storage: 20 GB SSD
Bandwidth: 1 TB/month
OS: Windows Server 2019/2022 یا Ubuntu 20.04/22.04
```

### **توصیه شده (Recommended):**
```
CPU: 4 vCPU / Cores
RAM: 8 GB
Storage: 40 GB SSD
Bandwidth: 3 TB/month
OS: Windows Server 2022 یا Ubuntu 22.04
```

### **برای تعداد کاربر بالا (High Load):**
```
CPU: 8 vCPU / Cores
RAM: 16 GB
Storage: 80 GB SSD
Bandwidth: 5 TB/month
OS: Windows Server 2022 یا Ubuntu 22.04
```

---

## 💰 پیشنهادات قیمتی:

### **🇮🇷 سرورهای ایرانی:**

#### **1. پارس پک (Parspack)**
- CPU: 4 Core
- RAM: 8 GB
- Storage: 40 GB SSD
- قیمت: ~500,000 تومان/ماه
- Link: https://parspack.com

#### **2. ابر آروان (Arvan Cloud)**
- CPU: 4 vCPU
- RAM: 8 GB
- Storage: 40 GB
- قیمت: ~400,000 تومان/ماه
- Link: https://arvancloud.ir

#### **3. فندق (Fandogh)**
- CPU: 4 Core
- RAM: 8 GB
- Storage: 40 GB
- قیمت: ~450,000 تومان/ماه
- Link: https://fandogh.cloud

---

### **🌍 سرورهای خارجی (سریع‌تر ولی گرون‌تر):**

#### **1. Hetzner (آلمان) - 💯 توصیه می‌شه!**
```
VPS: CX32
CPU: 4 vCPU (AMD)
RAM: 8 GB
Storage: 80 GB SSD
Bandwidth: 20 TB
قیمت: €10.58/month (~$11)
Link: https://www.hetzner.com/cloud
```

#### **2. DigitalOcean**
```
Droplet: Basic 8GB
CPU: 4 vCPU
RAM: 8 GB
Storage: 160 GB SSD
Bandwidth: 5 TB
قیمت: $48/month
Link: https://www.digitalocean.com
```

#### **3. Vultr**
```
Cloud Compute
CPU: 4 vCPU
RAM: 8 GB
Storage: 180 GB SSD
Bandwidth: 4 TB
قیمت: $24/month
Link: https://www.vultr.com
```

#### **4. Contabo (ارزان!)**
```
VPS M
CPU: 6 vCPU
RAM: 16 GB
Storage: 400 GB SSD
Bandwidth: 32 TB
قیمت: €8.99/month (~$9.5)
Link: https://contabo.com
```

---

## 🏆 توصیه نهایی من:

### **برای شروع:**
```
🥇 Hetzner CX32
   - سریع
   - ارزان (€10/month)
   - Reliable
   - SSD سریع
   - Bandwidth زیاد
```

### **اگه بودجه کمه:**
```
🥈 Contabo VPS M
   - خیلی ارزان (€9/month)
   - RAM و Storage زیاد
   - مناسب شروع
```

### **اگه ایران باشه:**
```
🥉 ابر آروان
   - قیمت مناسب
   - پشتیبانی فارسی
   - بدون مشکل تحریم
```

---

## 📊 مقایسه Performance:

| سرور | CPU | RAM | Storage | قیمت/ماه | سرعت | پایداری |
|------|-----|-----|---------|----------|------|----------|
| Hetzner CX32 | 4 | 8GB | 80GB | $11 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Contabo VPS M | 6 | 16GB | 400GB | $9.5 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Arvan Cloud | 4 | 8GB | 40GB | 400k تومان | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Vultr | 4 | 8GB | 180GB | $24 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🔧 تنظیمات بعد از خرید:

```bash
# 1. نصب Python
apt install python3 python3-pip  # Linux
# یا دانلود از python.org  # Windows

# 2. نصب Java
apt install openjdk-11-jre  # Linux
# یا از adoptium.net  # Windows

# 3. Clone پروژه
git clone https://github.com/angelcode119/signerme.git
cd signerme

# 4. نصب packages
pip install telethon requests aiohttp

# 5. تنظیم config
nano modules/config.py
# BOT2_TOKEN رو بزار
# LOG_CHANNEL_ID (اختیاری)

# 6. اجرا
python run.py
```

---

## 💡 نکات مهم:

✅ **SSD حتماً** - HDD خیلی کنده  
✅ **Bandwidth زیاد** - APK ها حجم دارن  
✅ **Location:** هر چی نزدیک‌تر، سریع‌تر  
✅ **Uptime:** حداقل 99.9%  

---

**من Hetzner رو توصیه می‌کنم! ارزان، سریع، قابل اعتماد! 🚀**

بگو بردارم محدودیت‌ها رو؟