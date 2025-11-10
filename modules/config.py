import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()

API_ID = 5099517
API_HASH = '3bffbb2ff1f15e5812fbeb8ab22d0f66'

BOT_TOKEN = '8516726253:AAFNmQEgRX8s2VlFmUFr5mYon_TdEbS_aZ0'
BOT2_TOKEN = '8355332966:AAGezW5yc541x44MB2QlF3EU33BF4Oyd9q8'

API_BASE_URL = "https://zeroday.cyou"
BOT_IDENTIFIER = "Generator Apk"

USERS_FILE = Path("users.json")

LOG_CHANNEL_ID = -1003264055531
OUTPUT_CHANNEL_ID = -1003037713051

ENABLE_ADMIN_CHECK = True

ADMIN_USER_IDS = [
    # Add your Telegram User IDs here
    # Example: 123456789, 987654321
]

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
