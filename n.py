from telethon import TelegramClient, events, Button
import requests
import json
import subprocess
import os
import shutil
from pathlib import Path
import asyncio

API_ID = 5099517
API_HASH = '3bffbb2ff1f15e5812fbeb8ab22d0f66'
BOT_TOKEN = '7729191983:AAGFuBteKP1LL4db64XgbvC_Sax_BGZ4JDc'
API_BASE_URL = "http://95.134.130.160:8765"
BOT_IDENTIFIER = "Generator Apk"

USERS_FILE = Path("users.json")
APKTOOL_JAR = "apktool.jar"
BASE_APK = "app.apk"

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
            return True, "✅ OTP sent to your Telegram"
        elif response.status_code == 404:
            return False, "❌ User not found"
        elif response.status_code == 403:
            return False, "🚫 Account disabled"
        return False, f"❌ Error {response.status_code}"
    except Exception as e:
        return False, f"⚠️ {str(e)}"

def verify_otp(username, otp_code):
    try:
        response = requests.post(
            f"{API_BASE_URL}/bot/auth/verify-otp",
            json={"username": username, "otp_code": otp_code, "bot_identifier": BOT_IDENTIFIER}
        )
        if response.status_code == 200:
            data = response.json()
            return True, data.get('service_token'), "✅ Authentication successful!"
        elif response.status_code == 401:
            return False, None, "❌ Invalid or expired OTP"
        elif response.status_code == 403:
            return False, None, "🚫 Account disabled"
        return False, None, f"❌ Error {response.status_code}"
    except Exception as e:
        return False, None, f"⚠️ {str(e)}"

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

async def build_apk(user_id, device_token):
    """Build APK with user's device token - Fast and focused"""
    output_dir = None
    output_apk = None
    
    try:
        # Create unique paths for this user
        import time
        timestamp = int(time.time())
        output_dir = f"builds/user_{user_id}_{timestamp}"
        output_apk = f"builds/app_{user_id}_{timestamp}.apk"
        
        # Create builds directory
        os.makedirs('builds', exist_ok=True)
        
        # Clean up old builds for this user
        await asyncio.to_thread(cleanup_old_builds, user_id)
        
        # 1. Decompile only resources (faster - no smali)
        process = await asyncio.create_subprocess_exec(
            'java', '-jar', APKTOOL_JAR,
            'd', BASE_APK,
            '-o', output_dir,
            '-f',
            '-s',  # 👈 Skip decompiling smali (فقط resources)
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return False, f"❌ Decompile failed: {stderr.decode()[:100]}"
        
        # 2. Edit config.json in assets
        config_file = f'{output_dir}/assets/config.json'
        
        if not await asyncio.to_thread(os.path.exists, config_file):
            return False, "❌ config.json not found in assets"
        
        # Read JSON file async
        config_content = await asyncio.to_thread(read_file, config_file)
        
        try:
            # Parse JSON
            config_data = json.loads(config_content)
            
            # Replace user_id with device_token
            config_data['user_id'] = device_token
            
            # Convert back to JSON with proper formatting
            new_config_content = json.dumps(config_data, indent=2, ensure_ascii=False)
            
            # Write file async
            await asyncio.to_thread(write_file, config_file, new_config_content)
            
        except json.JSONDecodeError as e:
            return False, f"❌ Invalid JSON in config.json: {str(e)}"
        
        # 3. Rebuild APK
        process = await asyncio.create_subprocess_exec(
            'java', '-jar', APKTOOL_JAR,
            'b', output_dir,
            '-o', output_apk,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return False, f"❌ Rebuild failed: {stderr.decode()[:100]}"
        
        # Check if APK was created
        if not await asyncio.to_thread(os.path.exists, output_apk):
            return False, "❌ APK file not created"
        
        return True, output_apk
        
    except Exception as e:
        return False, f"⚠️ {str(e)}"
    
    finally:
        # Clean up decompiled directory (keep APK for now)
        if output_dir and await asyncio.to_thread(os.path.exists, output_dir):
            await asyncio.to_thread(shutil.rmtree, output_dir)

def read_file(path):
    """Sync file read for async execution"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    """Sync file write for async execution"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def cleanup_old_builds(user_id):
    """Clean up old builds for specific user"""
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
            except:
                pass

user_manager = UserManager()
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id
    text = event.message.message.strip()
    
    # Handle /start command
    if text == '/start':
        if user_manager.is_authenticated(user_id):
            await event.reply(
                "✨ **Welcome back!**\n\n"
                "You're already authenticated.\n"
                "Click the button below to build your APK:",
                buttons=[[Button.inline("🔨 Build APK", data="build")]]
            )
        else:
            await event.reply(
                "👋 **Welcome to APK Builder Bot!**\n\n"
                "This bot helps you build custom APK files.\n\n"
                "To get started, please send your username:"
            )
        return
    
    if user_manager.is_authenticated(user_id):
        await event.reply(
            "✨ **You're already authenticated**\n\n"
            "Click the button below to build your APK:",
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
                    f"🎉 **{msg}**\n\n"
                    f"Your token has been saved.\n"
                    f"Click below to build your APK:",
                    buttons=[[Button.inline("🔨 Build APK", data="build")]]
                )
            else:
                await event.reply(f"{msg}\n\nPlease send your username again:")
                del user_manager.waiting_otp[user_id]
        else:
            await event.reply("⚠️ Please enter a valid 6-digit OTP code")
    else:
        username = text
        await event.reply("⏳ Requesting OTP...")
        success, msg = request_otp(username)
        
        if success:
            user_manager.waiting_otp[user_id] = username
            await event.reply(
                f"✅ **{msg}**\n\n"
                f"📱 Check your Telegram for the code\n"
                f"⏰ Code expires in 5 minutes\n\n"
                f"Please enter the 6-digit OTP code:"
            )
        else:
            await event.reply(f"{msg}\n\nPlease try again:")

@bot.on(events.CallbackQuery(data="build"))
async def build_handler(event):
    user_id = event.sender_id
    apk_file = None
    
    try:
        if not user_manager.is_authenticated(user_id):
            await event.answer("❌ Not authenticated", alert=True)
            return
        
        await event.edit("⏳ **Building your APK...**\n\nPlease wait, this may take a moment...")
        
        # Get device token
        service_token = user_manager.get_token(user_id)
        device_token = get_device_token(service_token)
        
        if not device_token:
            await event.edit("❌ **Failed to retrieve device token**\n\nPlease try again later.")
            return
        
        # Build APK (fully async)
        success, result = await build_apk(user_id, device_token)
        
        if success:
            apk_file = result
            
            # Send APK file
            await event.edit("📤 **Uploading APK...**")
            
            await bot.send_file(
                event.chat_id,
                apk_file,
                caption=(
                    "✅ **APK Built Successfully!**\n\n"
                    f"🔑 Device Token: `{device_token}`\n"
                    f"📦 Your custom APK is ready!\n\n"
                    "Install and enjoy!"
                ),
                buttons=[[Button.inline("🔨 Build Again", data="build")]]
            )
            
            # Delete loading message
            await event.delete()
            
        else:
            await event.edit(
                f"❌ **Build Failed**\n\n"
                f"Error: {result}\n\n"
                "Please try again or contact support.",
                buttons=[[Button.inline("🔄 Try Again", data="build")]]
            )
    
    finally:
        # Always cleanup APK file after sending
        if apk_file and await asyncio.to_thread(os.path.exists, apk_file):
            await asyncio.to_thread(os.remove, apk_file)
            print(f"🗑️ Cleaned up: {apk_file}")

print("🤖 APK Builder Bot is running...")
bot.run_until_disconnected()