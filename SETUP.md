# 🚀 Quick Setup Guide

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- telethon
- aiohttp
- requests
- FastTelethonhelper

### 2. Configure

Edit `modules/config.py`:

```python
# Telegram API (get from https://my.telegram.org)
API_ID = your_api_id
API_HASH = 'your_api_hash'

# Bot Tokens (get from @BotFather)
BOT_TOKEN = 'bot1_token'
BOT2_TOKEN = 'bot2_token'

# API Configuration
API_BASE_URL = "your_api_url"
BOT_IDENTIFIER = "your_bot_name"

# Optional: Add your Telegram ID for admin access
ADMIN_USER_IDS = [
    123456789,  # Your Telegram User ID
]
```

### 3. Prepare APK Files

Place your base APK files in the `data/` directory.

### 4. Run

```bash
python run.py
```

## Features

✅ APK building with custom themes
✅ User statistics and history
✅ Admin panel for management
✅ Unique Japanese signatures per build
✅ Automatic queue management

## Getting Your Telegram ID

1. Send `/start` to @userinfobot
2. Copy your User ID
3. Add it to `ADMIN_USER_IDS` in config.py

## Admin Commands

- `/admin` - Open admin panel (admin only)
- `/broadcast <msg>` - Send message to all users

## User Commands

- `/start` - Start the bot
- `/stats` - View your statistics
- `/history` - View build history
- `/logout` - Logout from account
- `/help` - Show help

## Troubleshooting

**Bot won't start:**
- Check all dependencies are installed
- Verify config.py has correct values
- Check bot.log for errors

**Import errors:**
- Install missing packages: `pip install -r requirements.txt`

**Build errors:**
- Ensure apktool.jar exists
- Check Java is installed
- Verify 34.0.0 build tools directory exists

## Documentation

- [User Guide](docs/USER_GUIDE.md)
- [Admin Guide](docs/ADMIN_GUIDE.md)
- [Keystore Info](docs/KEYSTORE_INFO.md)
- [Features](docs/FEATURES.md)

## Support

Check the documentation in the `docs/` folder for detailed information.

---

**Ready to go! 🎉**
