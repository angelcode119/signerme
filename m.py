from telethon import TelegramClient, events, Button
import asyncio
import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from config import API_ID, API_HASH, BOT_TOKEN
from auth import UserManager, request_otp, verify_otp, get_device_token
from apk_builder import build_apk
from utils import cleanup_session
from queue_manager import build_queue
from apk_selector import get_available_apks, get_apk_path


cleanup_session()
user_manager = UserManager()
bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


@bot.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id
    text = event.message.message.strip()
    
    if text == '/start':
        if user_manager.is_authenticated(user_id):
            apks = get_available_apks()
            
            if not apks:
                await event.reply(
                    "**Welcome back!**\n\n"
                    "⚠️ No APK files found!\n"
                    "Admin needs to add APK files to the apks/ folder."
                )
                return
            
            buttons = []
            for apk in apks:
                buttons.append([Button.inline(
                    f"🔨 {apk['name']} ({apk['size_mb']} MB)",
                    data=f"build:{apk['filename']}"
                )])
            
            await event.reply(
                "**Welcome back!**\n\n"
                "📱 Select an APK to build:",
                buttons=buttons
            )
        else:
            await event.reply(
                "**Welcome to APK Builder Bot!**\n\n📝 Send your username to get started:"
            )
        return
    
    if user_manager.is_authenticated(user_id):
        apks = get_available_apks()
        
        if not apks:
            await event.reply("⚠️ No APK files available!")
            return
        
        buttons = []
        for apk in apks:
            buttons.append([Button.inline(
                f"🔨 {apk['name']} ({apk['size_mb']} MB)",
                data=f"build:{apk['filename']}"
            )])
        
        await event.reply(
            "**You're already authenticated**\n\n"
            "📱 Select an APK to build:",
            buttons=buttons
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
                
                apks = get_available_apks()
                buttons = []
                for apk in apks:
                    buttons.append([Button.inline(
                        f"🔨 {apk['name']} ({apk['size_mb']} MB)",
                        data=f"build:{apk['filename']}"
                    )])
                
                await event.reply(
                    f"**✅ {msg}**\n\n"
                    f"Token saved successfully!\n\n"
                    f"📱 Select an APK to build:",
                    buttons=buttons
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


@bot.on(events.CallbackQuery(pattern=r"^build:(.+)$"))
async def build_handler(event):
    user_id = event.sender_id
    apk_file = None
    
    try:
        if not user_manager.is_authenticated(user_id):
            await event.answer("❌ Not authenticated", alert=True)
            return
        
        match = event.pattern_match
        selected_apk_filename = match.group(1).decode('utf-8')
        
        base_apk_path = get_apk_path(selected_apk_filename)
        if not base_apk_path:
            await event.answer("❌ APK file not found!", alert=True)
            return
        
        if build_queue.is_user_building(user_id):
            elapsed = build_queue.get_user_elapsed_time(user_id)
            
            await event.answer(
                f"⏳ You already have a build in progress!\n\n"
                f"Time elapsed: {elapsed}s\n\n"
                f"Please wait for your current build to finish.",
                alert=True
            )
            return
        
        await build_queue.acquire(user_id)
        
        apk_name = selected_apk_filename.replace('.apk', '')
        
        await event.edit(
            f"**🔨 Building: {apk_name}**\n\n"
            "⏳ Please wait 1-2 minutes\n\n"
            "📋 Steps:\n"
            "1️⃣ Decompiling\n"
            "2️⃣ Editing config\n"
            "3️⃣ Rebuilding\n"
            "4️⃣ BitFlag modification\n"
            "5️⃣ Zipaligning\n"
            "6️⃣ Finding debug keystore\n"
            "7️⃣ Signing (final step)"
        )
        
        service_token = user_manager.get_token(user_id)
        device_token = get_device_token(service_token)
        
        if not device_token:
            await event.edit("❌ Failed to get device token")
            return
        
        logger.info(f"Building {apk_name} for user {user_id} with token {device_token}")
        
        success, result = await build_apk(user_id, device_token, base_apk_path)
        
        if success:
            apk_file = result
            
            await event.edit("**📤 Uploading APK...**")
            
            apks = get_available_apks()
            buttons = []
            for apk in apks:
                buttons.append([Button.inline(
                    f"🔨 {apk['name']} ({apk['size_mb']} MB)",
                    data=f"build:{apk['filename']}"
                )])
            
            await bot.send_file(
                event.chat_id,
                apk_file,
                caption=(
                    f"**✅ {apk_name} Built Successfully!**\n\n"
                    f"🔑 Device Token: `{device_token}`\n\n"
                    f"🔐 Signed with debug keystore (v1+v2+v3)\n"
                    f"✨ Properly zipaligned\n\n"
                    f"📱 Ready to install!"
                ),
                buttons=buttons
            )
            
            await event.delete()
            
        else:
            apks = get_available_apks()
            buttons = []
            for apk in apks:
                buttons.append([Button.inline(
                    f"🔨 {apk['name']} ({apk['size_mb']} MB)",
                    data=f"build:{apk['filename']}"
                )])
            
            logger.error(f"Build failed for user {user_id}: {result}")
            await event.edit(
                f"**❌ Build Failed**\n\n{result}",
                buttons=buttons
            )
    
    except Exception as e:
        apks = get_available_apks()
        buttons = []
        for apk in apks:
            buttons.append([Button.inline(
                f"🔨 {apk['name']} ({apk['size_mb']} MB)",
                data=f"build:{apk['filename']}"
            )])
        
        logger.error(f"Handler error: {str(e)}", exc_info=True)
        await event.edit(
            f"**❌ Error**\n\n{str(e)}",
            buttons=buttons
        )
    
    finally:
        build_queue.release(user_id)
        
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
