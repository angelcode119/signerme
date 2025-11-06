import os
from pathlib import Path

# Get project root directory (parent of modules/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

API_ID = 5099517
API_HASH = '3bffbb2ff1f15e5812fbeb8ab22d0f66'

# Bot Tokens
BOT_TOKEN = '7218618207:AAGYFeKMe8XGYrAqs0wn7Dem_zr9e0yjW_o'  # Bot 1 - Generator
BOT2_TOKEN = '7369619847:AAEkC18fJE_RZfdWCXu2-AV58j1z_CQABSU'  # Bot 2 - Analyzer (عوض کن!)

API_BASE_URL = "http://95.134.130.160:8765"
BOT_IDENTIFIER = "Generator Apk"

USERS_FILE = Path("users.json")

# Telegram Log Channel (optional - leave None to disable)
LOG_CHANNEL_ID = None  # Example: -1001234567890

# Tool paths (absolute)
APKTOOL_JAR = str(PROJECT_ROOT / "apktool.jar")
APKTOOL_PATH = PROJECT_ROOT / "apktool.jar"  # For new code
APKSIGNER_PATH = r"C:\Users\Administrator\Desktop\signerme\34.0.0\apksigner.bat"
ZIPALIGN_PATH = r"C:\Users\Administrator\Desktop\signerme\34.0.0\zipalign.exe"

DEBUG_KEYSTORE_PATHS = [
    os.path.expanduser("~/.android/debug.keystore"),
    os.path.expanduser(r"~\.android\debug.keystore"),
    r"C:\Users\{}\AppData\Local\Android\.android\debug.keystore".format(os.getenv('USERNAME', 'awmeiiir')),
]

DEBUG_KEYSTORE_PASSWORD = "android"
DEBUG_KEYSTORE_ALIAS = "androiddebugkey"
