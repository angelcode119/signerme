from telethon import TelegramClient, events, Button
import asyncio
import os
import sys
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from config import API_ID, API_HASH, BOT_TOKEN
from auth import UserManager, request_otp, verify_otp
from utils import cleanup_session
from queue_manager import build_queue
from apk_downloader import download_apk, format_size
from apk_analyzer import APKAnalyzer


# Use different bot token for bot2
BOT2_TOKEN = '7369619847:AAECDyBuAyntBsgT00JGre2jcLnXTDJUxPA'  # Replace with your bot2 token

cleanup_session('bot2_session')
user_manager = UserManager('users2.json')
bot = TelegramClient('bot2_session', API_ID, API_HASH).start(bot_token=BOT2_TOKEN)

# Store user's download URLs temporarily
user_downloads = {}


@bot.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id
    text = event.message.message.strip()
    
    if text == '/start':
        if user_manager.is_authenticated(user_id):
            await event.reply(
                "✨ **Welcome back to APK Analyzer!**\n\n"
                "📥 Send me an APK download link\n"
                "🔍 I'll analyze it for you"
            )
        else:
            await event.reply(
                "🔍 **Welcome to APK Analyzer Studio**\n\n"
                "📱 Download & analyze APK files\n"
                "🎨 Extract icon & app info\n"
                "⚡ Fast & secure\n\n"
                "👤 **Enter your username**"
            )
        return
    
    if user_manager.is_authenticated(user_id):
        # Check if it's a URL
        if text.startswith(('http://', 'https://')):
            # Check if user already processing
            if build_queue.is_user_building(user_id):
                elapsed = build_queue.get_user_elapsed_time(user_id)
                await event.reply(
                    f"⏳ Already processing an APK\n\n"
                    f"Time elapsed: {elapsed}s\n\n"
                    f"Please wait..."
                )
                return
            
            # Start processing
            await process_apk_url(event, user_id, text)
        else:
            await event.reply(
                "📥 **Send APK download link**\n\n"
                "Example:\n"
                "`https://example.com/app.apk`"
            )
        return
    
    # Authentication flow
    if user_id in user_manager.waiting_otp:
        username = user_manager.waiting_otp[user_id]
        
        if text.isdigit() and len(text) == 6:
            await event.reply("🔐 **Verifying your code...**")
            success, token, msg = verify_otp(username, text)
            
            if success:
                user_manager.save_user(user_id, username, token)
                del user_manager.waiting_otp[user_id]
                
                await event.reply(
                    f"🎉 **Access Granted!**\n\n"
                    f"📥 Send me an APK download link"
                )
            else:
                await event.reply(f"❌ {msg}\n\n📝 Please send your username again")
                del user_manager.waiting_otp[user_id]
        else:
            await event.reply("❌ **Invalid code**\n\nPlease enter a valid 6-digit code")
    else:
        username = text
        await event.reply("📨 **Sending verification code...**")
        success, msg = request_otp(username)
        
        if success:
            user_manager.waiting_otp[user_id] = username
            await event.reply(
                f"✅ **Code delivered!**\n\n"
                f"🔐 Enter your 6-digit code"
            )
        else:
            await event.reply(f"❌ {msg}\n\nPlease try again")


async def process_apk_url(event, user_id, url):
    """Process APK from URL"""
    msg = None
    apk_path = None
    icon_path = None
    
    try:
        await build_queue.acquire(user_id)
        
        # Send initial message
        msg = await event.reply(
            "📥 **Downloading APK...**\n\n"
            "⏳ Please wait..."
        )
        
        # Generate unique filename
        timestamp = int(time.time())
        downloads_dir = "downloads"
        os.makedirs(downloads_dir, exist_ok=True)
        
        apk_path = os.path.join(downloads_dir, f"apk_{user_id}_{timestamp}.apk")
        
        # Download APK with progress
        last_update = [0]  # Use list to modify in callback
        
        async def progress_callback(progress, downloaded, total):
            # Update every 10%
            if progress - last_update[0] >= 10:
                last_update[0] = progress
                await msg.edit(
                    f"📥 **Downloading APK...**\n\n"
                    f"Progress: {progress:.1f}%\n"
                    f"Downloaded: {format_size(downloaded)} / {format_size(total)}"
                )
        
        success, message, downloaded_path = await download_apk(url, apk_path, progress_callback)
        
        if not success:
            await msg.edit(
                f"❌ **Download failed**\n\n"
                f"{message}\n\n"
                f"Please check the URL and try again"
            )
            return
        
        # Analyze APK
        await msg.edit(
            "🔍 **Analyzing APK...**\n\n"
            "⏳ Extracting information..."
        )
        
        analyzer = APKAnalyzer(apk_path)
        analyze_dir = os.path.join(downloads_dir, f"analyze_{user_id}_{timestamp}")
        
        results = await analyzer.analyze(analyze_dir)
        
        app_name = results.get('app_name') or 'Unknown'
        package_name = results.get('package_name') or 'Unknown'
        icon_path = results.get('icon_path')
        
        # Get file size
        file_size = os.path.getsize(apk_path)
        
        # Send results
        caption = (
            f"✅ **Analysis Complete!**\n\n"
            f"📱 **App Name:** {app_name}\n"
            f"📦 **Package:** `{package_name}`\n"
            f"💾 **Size:** {format_size(file_size)}\n\n"
            f"🔍 APK Analyzer Studio"
        )
        
        if icon_path and os.path.exists(icon_path):
            # Send icon with caption
            await bot.send_file(
                event.chat_id,
                icon_path,
                caption=caption
            )
            await msg.delete()
        else:
            await msg.edit(caption)
        
    except Exception as e:
        logger.error(f"Process error: {str(e)}", exc_info=True)
        if msg:
            await msg.edit(
                f"⚠️ **Processing failed**\n\n"
                f"An error occurred\n\n"
                f"💬 Please try again"
            )
    
    finally:
        build_queue.release(user_id)
        
        # Cleanup files
        if apk_path and os.path.exists(apk_path):
            try:
                os.remove(apk_path)
                logger.info(f"Cleaned APK: {apk_path}")
            except Exception as e:
                logger.warning(f"Could not remove APK: {e}")
        
        if icon_path and os.path.exists(icon_path):
            try:
                # Clean up analyze directory
                analyze_dir = os.path.dirname(icon_path)
                if os.path.exists(analyze_dir):
                    import shutil
                    shutil.rmtree(analyze_dir)
                    logger.info(f"Cleaned analyze dir: {analyze_dir}")
            except Exception as e:
                logger.warning(f"Could not clean analyze dir: {e}")


print("=" * 70)
print("🔍 APK Analyzer Studio - Professional Edition")
print("=" * 70)
logger.info("Bot2 started and ready!")
bot.run_until_disconnected()
