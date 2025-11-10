import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Use data/ folder for APKs (same as apk_manager)
APK_DIR = Path("data")


def get_available_apks():
    """Get list of available APKs from data/ folder"""
    try:
        if not APK_DIR.exists():
            APK_DIR.mkdir(parents=True, exist_ok=True)
            logger.warning(f"Created APK directory: {APK_DIR}")
            return []

        apks = []
        apk_files = sorted(APK_DIR.glob("*.apk"))
        
        if not apk_files:
            logger.warning(f"No APK files found in {APK_DIR}")
            return []
        
        for file in apk_files:
            try:
                size_bytes = file.stat().st_size
                size_mb = round(size_bytes / (1024 * 1024), 2)
                
                apks.append({
                    'name': file.stem.replace('_', ' ').title(),
                    'filename': file.name,
                    'path': str(file),
                    'size_mb': size_mb
                })
                logger.debug(f"Found APK: {file.name} ({size_mb} MB)")
            except Exception as e:
                logger.error(f"Error processing APK {file.name}: {str(e)}")
                continue

        logger.info(f"Found {len(apks)} APK(s) in {APK_DIR}")
        return apks
        
    except Exception as e:
        logger.error(f"Error getting available APKs: {str(e)}", exc_info=True)
        return []


def get_apk_path(filename):
    """Get full path of an APK file"""
    try:
        if not filename:
            logger.error("No filename provided")
            return None
            
        # Try data/ folder
        apk_path = APK_DIR / filename
        if apk_path.exists() and apk_path.suffix == '.apk':
            logger.debug(f"Found APK: {apk_path}")
            return str(apk_path)
        
        # Also check apks/ folder for backward compatibility
        old_dir = Path("apks")
        if old_dir.exists():
            apk_path_old = old_dir / filename
            if apk_path_old.exists() and apk_path_old.suffix == '.apk':
                logger.debug(f"Found APK in old location: {apk_path_old}")
                return str(apk_path_old)
        
        logger.error(f"APK not found: {filename}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting APK path for {filename}: {str(e)}", exc_info=True)
        return None
