# 🚀 Professional APK Builder Bot

A powerful Telegram bot for building and signing Android APK files with enterprise-grade security.

## ✨ Features

- 🔐 **Secure Authentication** - OTP-based user authentication
- 📱 **Multiple APK Support** - Select from multiple applications
- ⚡ **Fast Build System** - Optimized build pipeline
- 🔏 **Digital Signing** - APK signing with v1/v2/v3 signatures
- 🔐 **Encryption** - Built-in BitFlag encryption
- ⚙️ **Alignment** - Automatic APK zipalign optimization
- 🎯 **Per-User Queue** - Concurrent builds for different users

## 📦 Structure

```
.
├── m.py                 # Main bot file
├── n.py                 # Simple builder variant
├── config.py            # Configuration
├── auth.py              # Authentication system
├── apk_builder.py       # APK build logic
├── apk_selector.py      # APK selection system
├── utils.py             # Utility functions
├── queue_manager.py     # Build queue management
├── apks/                # APK files directory
│   └── README.md
└── builds/              # Temporary build files
```

## 🎮 Usage

1. **Add APK Files**: Place your APK files in the `apks/` directory
2. **Start Bot**: Run `python m.py`
3. **Authenticate**: Send `/start` to the bot and authenticate with OTP
4. **Select APK**: Choose an application from the list
5. **Build**: Wait for the build to complete (1-2 minutes)
6. **Download**: Receive your signed and encrypted APK

## 🔧 Requirements

- Python 3.8+
- Java JRE (for apktool and apksigner)
- Telethon
- Android SDK Build Tools (apksigner, zipalign)

## 🎨 UI/UX

The bot features a modern, professional interface with:
- Beautiful emoji-enhanced messages
- Clear status indicators
- Step-by-step build progress
- Secure information handling (no sensitive data shown)

## 🔐 Security

- Device tokens are never displayed to users
- Per-user authentication and session management
- Encrypted APK files
- Digital signature verification
- Secure build isolation

## 📝 License

Proprietary - All rights reserved
