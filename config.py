import os
from pathlib import Path

API_ID = 5099517
API_HASH = '3bffbb2ff1f15e5812fbeb8ab22d0f66'
BOT_TOKEN = '7369619847:AAECDyBuAyntBsgT00JGre2jcLnXTDJUxPA'
API_BASE_URL = "http://95.134.130.160:8765"
BOT_IDENTIFIER = "Generator Apk"

USERS_FILE = Path("users.json")
APKTOOL_JAR = "apktool.jar"

APKSIGNER_PATH = r"C:\Users\awmeiiir\AppData\Local\Android\Sdk\build-tools\34.0.0\apksigner.bat"
ZIPALIGN_PATH = r"C:\Users\awmeiiir\AppData\Local\Android\Sdk\build-tools\34.0.0\zipalign.exe"

DEBUG_KEYSTORE_PATHS = [
    os.path.expanduser("~/.android/debug.keystore"),
    os.path.expanduser(r"~\.android\debug.keystore"),
    r"C:\Users\{}\AppData\Local\Android\.android\debug.keystore".format(os.getenv('USERNAME', 'awmeiiir')),
]

DEBUG_KEYSTORE_PASSWORD = "android"
DEBUG_KEYSTORE_ALIAS = "androiddebugkey"
