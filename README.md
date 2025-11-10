# 🎨 APK Studio

Professional Telegram bot system for building and analyzing custom Android APKs.

## 📋 Overview

APK Studio is a dual-bot system that provides:
- **Bot 1 (Generator):** Build custom APKs with personalized themes
- **Bot 2 (Analyzer):** Analyze APK files for detailed information

## ✨ Features

### For Users
- 🔨 Quick & Custom APK builds
- 🎨 Custom theme support
- 📊 Personal statistics tracking
- 📜 Build history
- 🔐 Secure authentication
- 📱 Single session security

### For Admins
- 👥 User management (ban/unban)
- 📱 APK management (upload/delete)
- 📊 System statistics
- 📋 Queue monitoring
- 📢 Broadcast messaging
- 🔍 Detailed analytics

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd workspace
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure the bot:**

Edit `modules/config.py`:
```python
# Telegram API credentials
API_ID = 'your_api_id'
API_HASH = 'your_api_hash'
BOT_TOKEN = 'your_bot_token'

# Admin User IDs
ADMIN_USER_IDS = [
    123456789,  # Your Telegram ID
]

# API Configuration
API_BASE_URL = 'your_api_url'
BOT_IDENTIFIER = 'your_bot_identifier'
```

4. **Prepare APK files:**
```bash
# Place your base APKs in data/ folder
cp your_app.apk data/
```

5. **Start the bots:**
```bash
python3 run.py
```

## 📁 Project Structure

```
workspace/
├── bots/
│   ├── bot1_generator.py      # APK Generator bot
│   └── bot2_analyzer.py       # APK Analyzer bot
├── modules/
│   ├── config.py              # Configuration
│   ├── auth.py                # Authentication
│   ├── apk_builder.py         # APK building logic
│   ├── apk_analyzer.py        # APK analysis
│   ├── stats_manager.py       # Statistics tracking
│   ├── apk_manager.py         # APK database
│   ├── admin_panel.py         # Admin interface
│   ├── queue_manager.py       # Build queue
│   ├── theme_manager.py       # Theme customization
│   └── ...
├── data/                      # APK files & databases
├── logs/                      # Build logs
├── builds/                    # Temporary builds
├── run.py                     # Main runner
├── requirements.txt           # Dependencies
├── README.md                  # This file
├── USER_GUIDE.md             # User documentation
└── ADMIN_GUIDE.md            # Admin documentation
```

## 📖 Documentation

- **[User Guide](USER_GUIDE.md)** - Complete guide for end users
- **[Admin Guide](ADMIN_GUIDE.md)** - Admin panel and management

## 🔧 Requirements

- Python 3.8+
- Java JDK 8+ (for APK tools)
- 2GB+ free disk space
- Internet connection

### Python Dependencies
```
telethon
aiohttp
requests
FastTelethonhelper
```

### System Tools
- `apktool.jar` - APK decompiler
- `apksigner.bat` - APK signer
- `zipalign.exe` - APK optimizer

## 🎯 Commands

### User Commands
- `/start` - Start bot and login
- `/stats` - View statistics
- `/history` - View build history
- `/logout` - Logout
- `/help` - Show help

### Admin Commands
- `/admin` - Open admin panel
- `/broadcast <msg>` - Send message to all users
- `/help` - Show admin help

## 🔒 Security Features

- Single session per user
- Secure token authentication
- Ban system for abuse prevention
- Automatic session timeout
- Temporary file cleanup

## 📊 Statistics Tracking

The system tracks:
- Total builds per user
- Success/failure rates
- Build duration
- APK usage
- User activity
- Daily/weekly reports

## 🛠️ Build Process

1. User selects APK
2. Chooses Quick or Custom build
3. System queues build request
4. APK is decompiled
5. Payload injected & configured
6. APK recompiled & signed
7. File uploaded to user

**Average build time:** 30-60 seconds

## 📱 APK Management

### Adding APKs

**Method 1: Upload**
```
/admin → APK Management → ➕ Upload APK
```

**Method 2: Folder**
```bash
cp your_app.apk data/
# Then: /admin → APK Management → 🔍 Scan Folder
```

### APK Requirements
- Valid Android APK
- Max size: 100 MB (admin upload)
- Readable package name
- Decompilable with apktool

## 👥 User Management

### Ban System
Admins can ban users for:
- Terms violation
- Service abuse
- Suspicious activity

Banned users:
- Cannot login
- Cannot build APKs
- See ban message

### Single Session
- Only one device per account
- Automatic logout on new login
- Security notifications

## 📢 Broadcasting

Send messages to all users:
```
/broadcast 🎉 New feature available!
```

Features:
- Markdown support
- Progress tracking
- Success/failure count

## 🐛 Troubleshooting

### Common Issues

**Bot not starting:**
- Check config.py
- Verify API credentials
- Check internet connection

**Build failures:**
- Verify apktool.jar present
- Check Java installation
- Review bot.log

**Authentication errors:**
- Check API_BASE_URL
- Verify BOT_IDENTIFIER
- Test API connectivity

### Logs

- **Bot logs:** `bot.log`
- **Build logs:** `logs/builds/YYYY-MM-DD.json`

## 📈 Performance

- Max concurrent builds: 5
- Build timeout: 5 minutes
- Queue system: Fair FIFO
- Auto-cleanup: Enabled

## 🔄 Maintenance

### Daily Tasks
- Monitor statistics
- Check error logs
- Review active builds

### Weekly Tasks
- Clean old logs
- Update APKs
- Review user activity
- Check disk space

### Monthly Tasks
- Generate reports
- Backup databases
- Update documentation

## 📦 Backup

```bash
# Backup command
tar -czf backup-$(date +%Y%m%d).tar.gz data/ logs/

# Restore
tar -xzf backup-YYYYMMDD.tar.gz
```

## 🆘 Support

For issues or questions:
1. Check documentation
2. Review logs
3. Test in isolated environment
4. Contact administrator

## 📄 License

[Your License Here]

## 👏 Credits

Built with:
- [Telethon](https://github.com/LonamiWebs/Telethon)
- [FastTelethonhelper](https://github.com/RaphielGang/FastTelethon)
- [APKTool](https://ibotpeaches.github.io/Apktool/)

## 📝 Changelog

### Version 2.0.0 (2025-11-10)
- ✨ Added user statistics tracking
- ✨ Added build history
- ✨ Implemented single session system
- ✨ Added logout functionality
- ✨ Added /help command
- 🎨 Cleaned all Persian comments
- 📖 Created comprehensive documentation
- 🔨 Admin panel enhancements
- 🐛 Various bug fixes

### Version 1.0.0
- Initial release
- Basic APK building
- Admin panel
- Queue system

---

**Made with ❤️ for APK enthusiasts**

*Last updated: 2025-11-10*
