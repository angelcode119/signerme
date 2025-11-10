import os
from pathlib import Path


APK_DIR = Path("apks")


def get_available_apks():
    if not APK_DIR.exists():
        APK_DIR.mkdir(exist_ok=True)
        return []

    apks = []
    for file in sorted(APK_DIR.glob("*.apk")):
        apks.append({
            'name': file.stem,
            'filename': file.name,
            'path': str(file),
            'size_mb': round(file.stat().st_size / (1024 * 1024), 2)
        })

    return apks


def get_apk_path(filename):
    apk_path = APK_DIR / filename
    if apk_path.exists() and apk_path.suffix == '.apk':
        return str(apk_path)
    return None
