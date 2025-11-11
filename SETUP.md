# Setup Guide

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add your Telegram user ID as admin in `modules/config.py`:
```python
ADMIN_USER_IDS = [
    123456789,  # Replace with your Telegram user ID
]
```

3. Run the bot:
```bash
python run.py
```

## How to Find Your Telegram User ID

Method 1: Use @userinfobot on Telegram
- Open Telegram
- Search for @userinfobot
- Start the bot
- It will show your user ID

Method 2: Use @getmyid_bot
- Search for @getmyid_bot on Telegram
- Start it and get your ID

## Bot Configuration

Edit `modules/config.py` to configure:
- API_ID and API_HASH (from my.telegram.org)
- BOT_TOKEN and BOT2_TOKEN (from @BotFather)
- LOG_CHANNEL_ID and OUTPUT_CHANNEL_ID
- ADMIN_USER_IDS (your user ID)

## Troubleshooting

### Bot freezes or doesn't respond?
- Make sure you added your user ID to ADMIN_USER_IDS
- Check bot.log for errors
- Restart with: Ctrl+C then run again

### "No APKs found" in admin panel?
- Place APK files in `apks/` folder
- Go to admin panel → APK Management → Scan Folder

### Build fails?
- Check if Java is installed: `java -version`
- Check if apktool.jar exists
- Check build-tools in 34.0.0/ folder

## Logs

Check logs in:
- `bot.log` - Main bot log
- `logs/bot2_payload.log` - Bot2 log
- `logs/builds/` - Build history

## Support

If issues persist, check the logs for specific error messages.
