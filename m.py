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
        
        if build_queue.is_building():
            current_user = build_queue.get_current_user()
            elapsed = build_queue.get_elapsed_time()
            
            await event.answer(
                f"⏳ Server is busy!\n\n"
                f"Another user is building APK...\n"
                f"Time elapsed: {elapsed}s\n\n"
                f"Please wait and try again in a moment.",
                alert=True
            )
            return
        
        await event.edit("⏳ **Waiting in queue...**")
        
        queue_position = await build_queue.acquire(user_id)
        
        if queue_position:
            await event.edit(
                f"⏳ **You were in queue (position #{queue_position})**\n\n"
                f"Now building your APK..."
            )
            await asyncio.sleep(1)
        
        await event.edit(
            "**🔨 Building APK...**\n\n"
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
                    f"🔐 Signed with debug keystore (v1+v2+v3)\n"
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
        build_queue.release()
        
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
