# 📱 APK Files Directory

This folder contains all the APK files that users can select to build.

## Usage

1. Add your APK files to this directory
2. Bot will automatically detect them
3. Users will see them as buttons:
   - 🔨 AppName (File Size)

## Supported

- `.apk` files only
- Any size
- Multiple APKs

## Example

```
apks/
  ├── MyApp.apk       (15.5 MB)
  ├── GameApp.apk     (45.2 MB)
  └── ToolApp.apk     (8.3 MB)
```

Users will see:

```
🔨 MyApp (15.5 MB)
🔨 GameApp (45.2 MB)
🔨 ToolApp (8.3 MB)
```

## Notes

- File names should be descriptive
- No special characters recommended
- Bot reads files on each request (no restart needed)
