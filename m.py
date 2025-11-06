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
                "⚠️ **No Applications Available**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Contact administrator\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            )
                return
            
            buttons = []
            for apk in apks:
                buttons.append([Button.inline(
                    f"🔨 {apk['name']} ({apk['size_mb']} MB)",
                    data=f"build:{apk['filename']}"
                )])
            
            await event.reply(
                "🎉 **Welcome Back!**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "📱 **Choose Application**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━",
                buttons=buttons
            )
        else:
            await event.reply(
                "🎯 **Welcome to Professional APK Builder**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "🔐 Secure & Fast\n"
                "⚡ Enterprise Grade\n"
                "✨ Professional Signing\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "👤 **Send your username to start**"
            )
        return
    
    if user_manager.is_authenticated(user_id):
        apks = get_available_apks()
        
        if not apks:
            await event.reply(
                "⚠️ **No Applications**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "Contact administrator\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            )
            return
        
        buttons = []
        for apk in apks:
            buttons.append([Button.inline(
                f"🔨 {apk['name']} ({apk['size_mb']} MB)",
                data=f"build:{apk['filename']}"
            )])
        
        await event.reply(
            "✅ **Authentication Active**\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📱 **Choose Application**\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━",
            buttons=buttons
        )
        return
    
    if user_id in user_manager.waiting_otp:
        username = user_manager.waiting_otp[user_id]
        
        if text.isdigit() and len(text) == 6:
            await event.reply("🔍 **Verifying...**")
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
                    f"✅ **Authentication Successful**\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📱 **Choose Application**\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━",
                    buttons=buttons
                )
            else:
                await event.reply(f"❌ {msg}\n\n📝 Send username again")
                del user_manager.waiting_otp[user_id]
        else:
            await event.reply("❌ **Invalid Code**\n\nEnter 6-digit OTP")
    else:
        username = text
        await event.reply("⏳ **Requesting Code...**")
        success, msg = request_otp(username)
        
        if success:
            user_manager.waiting_otp[user_id] = username
            await event.reply(
                f"✅ **Code Sent**\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"🔢 **Enter 6-digit OTP**\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            )
        else:
            await event.reply(f"❌ {msg}\n\nTry again")


@bot.on(events.CallbackQuery(pattern=r"^build:(.+)$"))
async def build_handler(event):
    user_id = event.sender_id
    apk_file = None
    
    try:
        if not user_manager.is_authenticated(user_id):
            await event.answer("❌ Authentication required", alert=True)
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
                f"⏳ Build in progress\n\n"
                f"Elapsed: {elapsed}s\n\n"
                f"Please wait...",
                alert=True
            )
            return
        
        await build_queue.acquire(user_id)
        
        apk_name = selected_apk_filename.replace('.apk', '')
        
        await event.edit(
            f"🔨 **Building {apk_name}**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⏳ Please wait...\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        service_token = user_manager.get_token(user_id)
        device_token = get_device_token(service_token)
        
        if not device_token:
            await event.edit("❌ **Authentication Failed**")
            return
        
        logger.info(f"Building {apk_name} for user {user_id} with token {device_token}")
        
        success, result = await build_apk(user_id, device_token, base_apk_path)
        
        if success:
            apk_file = result
            
            await event.edit(
                "🔏 **Signing & Uploading...**\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "⏳ Almost done...\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            )
            
            await bot.send_file(
                event.chat_id,
                apk_file,
                caption=(
                    f"✅ **Build Completed**\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"📦 **{apk_name}**\n\n"
                    f"🔐 Signed & Encrypted\n"
                    f"📱 Ready to Install\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"💎 Professional Builder"
                )
            )
            
            await event.delete()
            
        else:
            logger.error(f"Build failed for user {user_id}: {result}")
            await event.edit(
                f"❌ **Build Failed**\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"⚠️ An error occurred\n\n"
                f"💬 Contact support\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━"
            )
    
    except Exception as e:
        logger.error(f"Handler error: {str(e)}", exc_info=True)
        await event.edit(
            f"⚠️ **System Error**\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"❌ Unexpected error\n\n"
            f"💬 Contact support\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━"
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
