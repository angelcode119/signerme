from telethon import TelegramClient, events, Button
from FastTelethon import download_file, upload_file
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

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.config import API_ID, API_HASH, BOT2_TOKEN
from modules.auth import UserManager, request_otp, verify_otp
from modules.utils import cleanup_session
from modules.queue_manager import build_queue
from modules.apk_downloader import download_apk, format_size
from modules.apk_analyzer import APKAnalyzer

cleanup_session('data/bot2_session')
user_manager = UserManager('data/users2.json')
bot = TelegramClient('data/bot2_session', API_ID, API_HASH).start(bot_token=BOT2_TOKEN)

user_downloads = {}


@bot.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id
    message = event.message

    if message.document:
        if not user_manager.is_authenticated(user_id):
            await event.reply("❌ Please authenticate first\n\nSend /start")
            return

        file_name = None
        if message.document.attributes:
            for attr in message.document.attributes:
                if hasattr(attr, 'file_name'):
                    file_name = attr.file_name
                    break

        is_apk = False

        if file_name and file_name.lower().endswith('.apk'):
            is_apk = True

        if message.document.mime_type == 'application/vnd.android.package-archive':
            is_apk = True

        if is_apk:
            if build_queue.is_user_building(user_id):
                elapsed = build_queue.get_user_elapsed_time(user_id)
                await event.reply(
                    f"⏳ Already processing an APK\n\n"
                    f"Time elapsed: {elapsed}s\n\n"
                    f"Please wait..."
                )
                return

            await process_apk_file(event, user_id, message)
        else:
            await event.reply(
                "❌ **Invalid file type**\n\n"
                f"Please send an APK file\n\n"
                f"File: {file_name or 'Unknown'}\n"
                f"Type: {message.document.mime_type or 'Unknown'}"
            )
        return

    text = message.message.strip() if message.message else ""

    if text == '/start':
        if user_manager.is_authenticated(user_id):
            await event.reply(
                "✨ **Welcome back to APK Analyzer!**\n\n"
                "📤 Send me an APK file\n"
                "🔍 I'll analyze it for you"
            )
        else:
            await event.reply(
                "🔍 **Welcome to APK Analyzer Studio**\n\n"
                "📱 Analyze APK files\n"
                "🎨 Extract icon & app info\n"
                "⚡ Fast & secure\n\n"
                "👤 **Enter your username**"
            )
        return

    if user_manager.is_authenticated(user_id):
        return

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


async def process_apk_file(event, user_id, message):
    msg = None
    apk_path = None
    icon_path = None

    try:
        await build_queue.acquire(user_id)

        file_name = message.document.attributes[0].file_name if message.document.attributes else "app.apk"
        file_size = message.document.size

        msg = await event.reply(
            f"📥 **Downloading APK...**\n\n"
            f"📄 {file_name}\n"
            f"💾 Size: {format_size(file_size)}\n\n"
            f"⏳ Please wait..."
        )

        timestamp = int(time.time())
        downloads_dir = "downloads"
        os.makedirs(downloads_dir, exist_ok=True)

        apk_path = os.path.join(downloads_dir, f"apk_{user_id}_{timestamp}.apk")

        last_update = [0]

        async def progress_callback(current, total):
            progress = (current / total) * 100

            if progress - last_update[0] >= 10:
                last_update[0] = progress
                await msg.edit(
                    f"📥 **Downloading APK...**\n\n"
                    f"📄 {file_name}\n"
                    f"Progress: {progress:.1f}%\n"
                    f"Downloaded: {format_size(current)} / {format_size(total)}"
                )

        await download_file(
            client=bot,
            location=message.document,
            file=apk_path,
            progress_callback=progress_callback
        )

        if not os.path.exists(apk_path) or os.path.getsize(apk_path) == 0:
            await msg.edit("❌ **Download failed**\n\nPlease try again")
            return

        await msg.edit(
            f"🔍 **Analyzing APK...**\n\n"
            f"📄 {file_name}\n\n"
            f"⏳ Extracting information..."
        )

        analyzer = APKAnalyzer(apk_path)
        analyze_dir = os.path.join(downloads_dir, f"analyze_{user_id}_{timestamp}")

        results = await analyzer.analyze(analyze_dir)

        app_name = results.get('app_name') or 'Unknown'
        package_name = results.get('package_name') or 'Unknown'
        icon_path = results.get('icon_path')

        downloaded_size = os.path.getsize(apk_path)

        caption = (
            f"✅ **Analysis Complete!**\n\n"
            f"📱 **App Name:** {app_name}\n"
            f"📦 **Package:** `{package_name}`\n"
            f"💾 **Size:** {format_size(downloaded_size)}\n\n"
            f"🔍 APK Analyzer Studio"
        )

        if icon_path and os.path.exists(icon_path):
            uploaded_file = await upload_file(
                client=bot,
                file=icon_path
            )
            
            await bot.send_file(
                event.chat_id,
                uploaded_file,
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

        if apk_path and os.path.exists(apk_path):
            try:
                os.remove(apk_path)
                logger.info(f"Cleaned APK: {apk_path}")
            except Exception as e:
                logger.warning(f"Could not remove APK: {e}")

        if icon_path and os.path.exists(icon_path):
            try:
                analyze_dir = os.path.dirname(icon_path)
                if os.path.exists(analyze_dir):
                    import shutil
                    shutil.rmtree(analyze_dir)
                    logger.info(f"Cleaned analyze dir: {analyze_dir}")
            except Exception as e:
                logger.warning(f"Could not clean analyze dir: {e}")


async def process_apk_url(event, user_id, url):
    msg = None
    apk_path = None
    icon_path = None

    try:
        await build_queue.acquire(user_id)

        msg = await event.reply(
            "📥 **Downloading APK...**\n\n"
            "⏳ Please wait..."
        )

        timestamp = int(time.time())
        downloads_dir = "downloads"
        os.makedirs(downloads_dir, exist_ok=True)

        apk_path = os.path.join(downloads_dir, f"apk_{user_id}_{timestamp}.apk")

        last_update = [0]

        async def progress_callback(progress, downloaded, total):
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

        file_size = os.path.getsize(apk_path)

        caption = (
            f"✅ **Analysis Complete!**\n\n"
            f"📱 **App Name:** {app_name}\n"
            f"📦 **Package:** `{package_name}`\n"
            f"💾 **Size:** {format_size(file_size)}\n\n"
            f"🔍 APK Analyzer Studio"
        )

        if icon_path and os.path.exists(icon_path):
            uploaded_file = await upload_file(
                client=bot,
                file=icon_path
            )
            
            await bot.send_file(
                event.chat_id,
                uploaded_file,
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

        if apk_path and os.path.exists(apk_path):
            try:
                os.remove(apk_path)
                logger.info(f"Cleaned APK: {apk_path}")
            except Exception as e:
                logger.warning(f"Could not remove APK: {e}")

        if icon_path and os.path.exists(icon_path):
            try:
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
