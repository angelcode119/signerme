# 📱 APK Files Directory

This directory contains the base APK files that users can select for building.

## How to Add APKs

1. Place your APK files here (e.g., `Instagram.apk`, `Telegram.apk`)
2. The bot will automatically detect them
3. Users will see them in the bot menu

## Example Structure

```
apks/
├── Instagram.apk
├── Telegram.apk
├── WhatsApp.apk
└── README.md
```

## File Requirements

- **Format:** `.apk` files only
- **Size:** Any size (recommended < 200 MB for faster builds)
- **Naming:** Use clear, descriptive names (users will see the filename)

## Auto-Detection

The bot automatically scans this directory and shows available APKs to users with:
- App name (from filename)
- File size (in MB)
- Select button

## Admin Upload

Admins can also upload APKs directly through the bot:
- Use `/admin` command
- Navigate to APK Management
- Click "➕ Upload APK"
- Send APK file via Telegram

## Notes

- APKs added here are immediately available to all users
- Remove APK files to make them unavailable
- Restart not required for new APKs
- APK files are not stored in git (see .gitignore)

---

**Place your base APK files here to get started!**
