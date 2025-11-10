from telethon import TelegramClient, events, Button
from FastTelethonhelper import fast_upload
import asyncio
import os
import sys
import logging
import time
from datetime import datetime

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

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.config import API_ID, API_HASH, BOT_TOKEN, ENABLE_ADMIN_CHECK

try:
    from modules.config import LOG_CHANNEL_ID
except ImportError:
    LOG_CHANNEL_ID = None

try:
    from modules.config import OUTPUT_CHANNEL_ID
except ImportError:
    OUTPUT_CHANNEL_ID = None

from modules.auth import UserManager, request_otp, verify_otp, get_device_token
from modules.apk_builder import build_apk
from modules.utils import cleanup_session
from modules.queue_manager import build_queue
from modules.apk_selector import get_available_apks, get_apk_path
from modules.theme_manager import theme_manager
from modules.custom_build_handler import handle_custom_build_start, handle_theme_input
from modules.admin_check import check_admin_status

cleanup_session('data/bot1_session')
user_manager = UserManager('data/users.json')
bot = TelegramClient('data/bot1_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

build_queue_list = asyncio.Queue()
is_building = False

def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

@bot.on(events.NewMessage)
async def handler(event):
    if not event.is_private:
        return
    
    user_id = event.sender_id
    text = event.message.message.strip()
    
    if theme_manager.is_customizing(user_id):
        handled = await handle_theme_input(event, bot, user_manager)
        if handled:
            return
    
    if text == '/start':
        if user_id in user_manager.waiting_otp:
            del user_manager.waiting_otp[user_id]
            
        if user_manager.is_authenticated(user_id):
            apks = get_available_apks()
            if not apks:
                await event.reply(
                    "📭 **No apps available yet**\n\n"
                    "Please contact administrator"
                )
                return
            
            buttons = []
            for apk in apks:
                buttons.append([Button.inline(
                    f"🔨 {apk['name']} ({apk['size_mb']} MB)",
                    data=f"build:{apk['filename']}"
                )])
            
            await event.reply(
                "✨ **Welcome back, Creator!**\n\n"
                "🎯 Select an app to generate",
                buttons=buttons
            )
        else:
            await event.reply(
                "🎨 **Welcome to APK Generator Studio**\n\n"
                "🚀 Create custom applications\n"
                "⚡ Lightning fast generation\n"
                "🔐 Professional security\n\n"
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
                replaced = user_manager.save_user(user_id, username, token)
                del user_manager.waiting_otp[user_id]
                
                apks = get_available_apks()
                if not apks:
                    await event.reply("❌ No apps available")
                    return
                
                buttons = []
                for apk in apks:
                    buttons.append([Button.inline(
                        f"🔨 {apk['name']} ({apk['size_mb']} MB)",
                        data=f"build:{apk['filename']}"
                    )])
                
                message = "🎉 **Access Granted!**\n\n"
                if replaced:
                    message += "⚠️ Previous session deactivated\n\n"
                message += "🎯 Choose your application"
                
                await event.reply(message, buttons=buttons)
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

@bot.on(events.CallbackQuery(pattern=r"^build:(.+)$"))
async def build_handler(event):
    user_id = event.sender_id
    
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
            f"⏳ Already generating an app\n\n"
            f"Time elapsed: {elapsed}s\n\n"
            f"Please wait for completion...",
            alert=True
        )
        return
    
    apk_name = selected_apk_filename.replace('.apk', '')
    
    try:
        await event.edit(
            f"🎨 **{apk_name}**\n\n"
            f"Choose generation mode:",
            buttons=[
                [Button.inline("⚡ Quick Generate", data=f"quick:{selected_apk_filename}")],
                [Button.inline("🎨 Custom Theme", data=f"custom:{selected_apk_filename}")]
            ]
        )
    except:
        pass

def progress_callback(done, total):
    percent = (done / total) * 100
    return f"📤 Uploading: {percent:.1f}%"

@bot.on(events.CallbackQuery(pattern=r"^quick:(.+)$"))
async def quick_build_handler(event):
    user_id = event.sender_id
    
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
            f"⏳ Already generating an app\n\n"
            f"Time elapsed: {elapsed}s\n\n"
            f"Please wait for completion...",
            alert=True
        )
        return
    
    user_data = user_manager.users.get(str(user_id), {})
    username = user_data.get('username', 'Unknown')
    service_token = user_data.get('token')
    
    if ENABLE_ADMIN_CHECK and service_token:
        is_active, admin_msg, device_token = check_admin_status(service_token)
        if not is_active:
            logger.warning(f"User {username} ({user_id}) denied: {admin_msg}")
            
            if LOG_CHANNEL_ID:
                try:
                    await bot.send_message(
                        LOG_CHANNEL_ID,
                        f"⚠️ **Access Denied**\n\n"
                        f"👤 User: `{username}` ({user_id})\n"
                        f"🤖 Bot: APK Generator\n"
                        f"❌ Reason: {admin_msg}"
                    )
                except:
                    pass
            
            await event.answer(admin_msg, alert=True)
            return
    
    queue_position = build_queue_list.qsize()
    
    if queue_position > 0 or is_building:
        queue_msg = await bot.send_message(
            event.chat_id,
            f"⏳ **Added to Queue**\n\n"
            f"📍 Position: {queue_position + 1}\n"
            f"⏱️ Please wait...\n\n"
            f"Your build will start automatically!"
        )
        
        await build_queue_list.put({
            'user_id': user_id,
            'username': username,
            'apk_filename': selected_apk_filename,
            'base_apk_path': base_apk_path,
            'chat_id': event.chat_id,
            'queue_msg': queue_msg,
            'service_token': service_token
        })
    else:
        await build_queue_list.put({
            'user_id': user_id,
            'username': username,
            'apk_filename': selected_apk_filename,
            'base_apk_path': base_apk_path,
            'chat_id': event.chat_id,
            'queue_msg': None,
            'service_token': service_token
        })

async def process_build_queue():
    global is_building
    
    while True:
        try:
            build_data = await build_queue_list.get()
            
            is_building = True
            
            user_id = build_data['user_id']
            username = build_data['username']
            selected_apk_filename = build_data['apk_filename']
            base_apk_path = build_data['base_apk_path']
            chat_id = build_data['chat_id']
            queue_msg = build_data['queue_msg']
            service_token = build_data['service_token']
            
            if queue_msg:
                try:
                    await queue_msg.delete()
                except:
                    pass
            
            apk_file = None
            progress_message = None
            start_time = time.time()
            
            try:
                await build_queue.acquire(user_id)
                
                apk_name = selected_apk_filename.replace('.apk', '')
                
                progress_message = await bot.send_message(
                    chat_id,
                    f"🎨 **Creating {apk_name}**\n\n"
                    f"⚡ Generating your application..."
                )
                
                if LOG_CHANNEL_ID:
                    try:
                        apk_size_mb = os.path.getsize(base_apk_path) / (1024 * 1024)
                        await bot.send_message(
                            LOG_CHANNEL_ID,
                            f"📦 **Build Started**\n\n"
                            f"👤 User: `{username}` ({user_id})\n"
                            f"🤖 Bot: APK Generator\n"
                            f"📱 App: {apk_name}\n"
                            f"💾 Size: {apk_size_mb:.1f} MB"
                        )
                    except Exception as e:
                        logger.error(f"Failed to send log: {e}")
                
                device_token = get_device_token(service_token)
                
                if not device_token:
                    await progress_message.edit("❌ **Authentication failed**\n\nPlease try again")
                    continue
                
                logger.info(f"Building {apk_name} for user {user_id} with token {device_token}")
                
                success, result = await build_apk(user_id, device_token, base_apk_path, custom_theme=None)
                
                if success:
                    apk_file = result
                    
                    await progress_message.edit(
                        "✅ **Build Complete**\n\n"
                        "📤 Uploading...\n"
                        "⏳ 0%"
                    )
                    
                    uploaded_file = await fast_upload(
                        client=bot,
                        file_location=apk_file,
                        reply=progress_message,
                        name=f"{apk_name}.apk",
                        progress_bar_function=progress_callback
                    )
                    
                    await bot.send_file(
                        chat_id,
                        uploaded_file,
                        caption=(
                            f"✅ **Your app is ready!**\n\n"
                            f"📱 **{apk_name}**\n\n"
                            f"🔐 Secured & Signed\n"
                            f"⚡ Ready for installation\n\n"
                            f"🎨 Generated with APK Studio"
                        )
                    )
                    
                    if OUTPUT_CHANNEL_ID:
                        try:
                            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            final_size = os.path.getsize(apk_file)
                            duration = int(time.time() - start_time)
                            
                            channel_caption = (
                                "📦 **New APK Build**\n\n"
                                f"👤 User: `{username}` ({user_id})\n"
                                f"📱 App: {apk_name}\n\n"
                                f"💾 Size: {format_size(final_size)}\n"
                                f"⏱️ Duration: {duration}s\n"
                                f"🕐 Time: {now}\n\n"
                                "🎨 **APK Generator Studio**"
                            )
                            
                            await bot.send_file(
                                OUTPUT_CHANNEL_ID,
                                uploaded_file,
                                caption=channel_caption
                            )
                            
                            logger.info(f"✅ File sent to output channel: {OUTPUT_CHANNEL_ID}")
                        except Exception as e:
                            logger.error(f"Failed to send to output channel: {str(e)}")
                    
                    if progress_message:
                        await progress_message.delete()
                    
                    if LOG_CHANNEL_ID:
                        try:
                            duration = int(time.time() - start_time)
                            await bot.send_message(
                                LOG_CHANNEL_ID,
                                f"✅ **Build Success**\n\n"
                                f"👤 User: `{username}` ({user_id})\n"
                                f"🤖 Bot: APK Generator\n"
                                f"📱 App: {apk_name}\n"
                                f"📦 Output Size: {format_size(os.path.getsize(apk_file))}\n"
                                f"⏱️ Duration: {duration}s"
                            )
                        except Exception as e:
                            logger.error(f"Failed to send log: {e}")
                else:
                    logger.error(f"Build failed for user {user_id}: {result}")
                    
                    if LOG_CHANNEL_ID:
                        try:
                            await bot.send_message(
                                LOG_CHANNEL_ID,
                                f"❌ **Build Failed**\n\n"
                                f"👤 User: `{username}` ({user_id})\n"
                                f"🤖 Bot: APK Generator\n"
                                f"📱 App: {apk_name}\n"
                                f"⚠️ Error: {result or 'Unknown error'}"
                            )
                        except Exception as e:
                            logger.error(f"Failed to send log: {e}")
                    
                    await progress_message.edit(
                        f"⚠️ **Generation failed**\n\n"
                        f"Something went wrong\n\n"
                        f"💬 Please contact support"
                    )
            
            except Exception as e:
                logger.error(f"Process error: {str(e)}", exc_info=True)
                try:
                    if progress_message:
                        await progress_message.edit(
                            f"⚠️ **Oops! Something happened**\n\n"
                            f"Please try again or contact support"
                        )
                except:
                    pass
            
            finally:
                build_queue.release(user_id)
                
                if apk_file and await asyncio.to_thread(os.path.exists, apk_file):
                    try:
                        await asyncio.to_thread(os.remove, apk_file)
                        logger.info(f"Cleaned final APK: {apk_file}")
                    except Exception as e:
                        logger.warning(f"Could not remove final APK: {e}")
                
                is_building = False
                build_queue_list.task_done()
        
        except Exception as e:
            logger.error(f"Queue processing error: {str(e)}", exc_info=True)
            is_building = False

@bot.on(events.CallbackQuery(data="cancel_custom"))
async def cancel_custom_handler(event):
    user_id = event.sender_id
    theme_manager.cancel_customization(user_id)
    
    apks = get_available_apks()
    buttons = []
    for apk in apks:
        buttons.append([Button.inline(
            f"🔨 {apk['name']} ({apk['size_mb']} MB)",
            data=f"build:{apk['filename']}"
        )])
    
    await event.edit(
        "❌ **Customization cancelled**\n\n"
        "🎯 Select an app to generate",
        buttons=buttons
    )

@bot.on(events.CallbackQuery(pattern=r"^custom:(.+)$"))
async def custom_build_start_handler(event):
    await handle_custom_build_start(event, bot, user_manager)

print("=" * 70)
print("🎨 APK Generator Studio - Professional Edition")
print("=" * 70)

async def main():
    if LOG_CHANNEL_ID:
        logger.info(f"✅ Log channel enabled: {LOG_CHANNEL_ID}")
    else:
        logger.info("⚠️  Log channel disabled")
    
    if OUTPUT_CHANNEL_ID:
        logger.info(f"✅ Output channel enabled: {OUTPUT_CHANNEL_ID}")
    else:
        logger.info("⚠️  Output channel disabled")
    
    asyncio.create_task(process_build_queue())
    
    logger.info("Bot1 (APK Generator) started and ready!")
    logger.info("🔒 Only accepting messages in private chat")
    
    await bot.run_until_disconnected()

if __name__ == '__main__':
    bot.loop.run_until_complete(main())