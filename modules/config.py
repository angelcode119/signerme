import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

API_ID = 5099517
API_HASH = '3bffbb2ff1f15e5812fbeb8ab22d0f66'

BOT_TOKEN = '7218618207:AAGYFeKMe8XGYrAqs0wn7Dem_zr9e0yjW_o'
BOT2_TOKEN = '7369619847:AAEkC18fJE_RZfdWCXu2-AV58j1z_CQABSU'

API_BASE_URL = "http://95.134.130.160:8765"
BOT_IDENTIFIER = "Generator Apk"

USERS_FILE = Path("users.json")

LOG_CHANNEL_ID = None

ENABLE_ADMIN_CHECK = False

APKTOOL_JAR = str(PROJECT_ROOT / "apktool.jar")
APKTOOL_PATH = PROJECT_ROOT / "apktool.jar"

BUILD_TOOLS_DIR = PROJECT_ROOT / "34.0.0"
APKSIGNER_PATH = str(BUILD_TOOLS_DIR / "apksigner.bat")
ZIPALIGN_PATH = str(BUILD_TOOLS_DIR / "zipalign.exe")

DEBUG_KEYSTORE_PATHS = [
    str(PROJECT_ROOT / "debug.keystore"),
    os.path.expanduser("~/.android/debug.keystore"),
    os.path.expanduser(r"~\.android\debug.keystore"),
    r"C:\Users\{}\AppData\Local\Android\.android\debug.keystore".format(os.getenv('USERNAME', 'Administrator')),
]

DEBUG_KEYSTORE_PASSWORD = "android"
DEBUG_KEYSTORE_ALIAS = "suzi"

# Admin Panel Configuration
ADMIN_USER_IDS = [
    # Add your Telegram User IDs here
    # Example: 123456789, 987654321
]
