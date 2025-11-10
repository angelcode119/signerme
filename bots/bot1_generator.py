from telethon import TelegramClient, events, Button
from FastTelethonhelper import upload_file
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

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.config import API_ID, API_HASH, BOT_TOKEN
try:
    from modules.config import ADMIN_USER_IDS
except ImportError:
    ADMIN_USER_IDS = []

from modules.auth import UserManager, request_otp, verify_otp, get_device_token
from modules.apk_builder import build_apk
from modules.utils import cleanup_session
from modules.queue_manager import build_queue
from modules.apk_selector import get_available_apks, get_apk_path
from modules.theme_manager import theme_manager
from modules.custom_build_handler import handle_custom_build_start, handle_theme_input
from modules.admin_panel import (
    handle_admin_command, 
    handle_admin_callback, 
    handle_broadcast,
    handle_admin_apk_file_received
)
from modules.stats_manager import stats_manager
from modules.apk_manager import apk_manager


cleanup_session('data/bot1_session')
user_manager = UserManager('data/users.json')
bot = TelegramClient('data/bot1_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


@bot.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id
    text = event.message.message.strip()
    
    if user_id in ADMIN_USER_IDS and event.message.document:
        handled = await handle_admin_apk_file_received(event, bot)
        if handled:
            return
    
    username = user_manager.get_username(user_id)
    if username:
        stats_manager.update_user_activity(user_id, username)
    
    if text == '/admin':
        await handle_admin_command(event, ADMIN_USER_IDS)
        return
    
    if text.startswith('/broadcast '):
        await handle_broadcast(event, ADMIN_USER_IDS, bot)
        return
    
    if text == '/stats':
        if not user_manager.is_authenticated(user_id):
            await event.reply("❌ Please login first\n\nSend /start")
            return
        
        if stats_manager.is_user_banned(user_id):
            await event.reply("🚫 Your account has been banned")
            return
        
        user_details = stats_manager.get_user_details(user_id)
        if not user_details:
            await event.reply("❌ No statistics available")
            return
        
        username = user_details.get('username', 'Unknown')
        total_builds = user_details.get('total_builds', 0)
        quick_builds = user_details.get('quick_builds', 0)
        custom_builds = user_details.get('custom_builds', 0)
        failed_builds = user_details.get('failed_builds', 0)
        avg_time = user_details.get('avg_build_time', 0)
        total_time = user_details.get('total_time', '0m')
        first_build = user_details.get('first_build', 'N/A')
        last_build = user_details.get('last_build', 'N/A')
        apk_usage = user_details.get('apk_usage', {})
        
        success_rate = 0
        if total_builds > 0:
            success_rate = ((total_builds - failed_builds) / total_builds) * 100
        
        most_used_apk = "None"
        if apk_usage:
            most_used = max(apk_usage.items(), key=lambda x: x[1])
            most_used_apk = f"{most_used[0]} - {most_used[1]} times"
        
        if first_build != 'N/A':
            try:
                first_build = first_build[:10]
            except:
                pass
        
        if last_build != 'N/A':
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_build)
                last_build = stats_manager._format_time_ago(dt)
            except:
                last_build = 'N/A'
        
        stats_text = (
            f"📊 **Your Statistics**\n\n"
            f"👤 Username: @{username}\n\n"
            f"🔨 **Total Builds:** {total_builds}\n"
            f"⚡ Quick Builds: {quick_builds}\n"
            f"🎨 Custom Builds: {custom_builds}\n"
            f"❌ Failed Builds: {failed_builds}\n\n"
            f"⏱️ **Average Time:** {avg_time}s\n"
            f"📈 **Success Rate:** {success_rate:.1f}%\n"
            f"⏳ **Total Time:** {total_time}\n\n"
            f"🏆 **Most Used APK:**\n"
            f"   {most_used_apk}\n\n"
            f"📅 **Member Since:** {first_build}\n"
            f"🕐 **Last Build:** {last_build}"
        )
        
        await event.reply(
            stats_text,
            buttons=[
                [Button.inline("📜 View History", data="user:history")],
                [Button.inline("🏠 Back to Menu", data="user:menu")]
            ]
        )
        return
    
    if text == '/history':
        if not user_manager.is_authenticated(user_id):
            await event.reply("❌ Please login first\n\nSend /start")
            return
        
        if stats_manager.is_user_banned(user_id):
            await event.reply("🚫 Your account has been banned")
            return
        
        import json
        from datetime import datetime, timedelta
        from pathlib import Path
        
        logs_dir = Path("logs/builds")
        history = []
        
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            log_file = logs_dir / f"{date_str}.json"
            
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    
                    for log in logs:
                        if log.get('user_id') == user_id:
                            history.append(log)
        
        history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        if not history:
            await event.reply(
                "📜 **Your Build History**\n\n"
                "No builds yet.\n"
                "Start building to see your history!",
                buttons=[[Button.inline("🏠 Back to Menu", data="user:menu")]]
            )
            return
        
        history_text = f"📜 **Your Build History**\n\n"
        history_text += f"Total Builds: **{len(history)}**\n\n"
        
        for i, build in enumerate(history[:10], 1):
            success = build.get('success', False)
            apk_name = build.get('apk_name', 'Unknown')
            duration = build.get('duration', 0)
            is_custom = build.get('is_custom', False)
            timestamp = build.get('timestamp', '')
            error = build.get('error')
            
            status_icon = "✅" if success else "❌"
            build_type = "(Custom)" if is_custom else "(Quick)"
            
            try:
                dt = datetime.fromisoformat(timestamp)
                date_str = dt.strftime('%Y-%m-%d %H:%M')
            except:
                date_str = timestamp[:16] if timestamp else 'Unknown'
            
            history_text += f"{status_icon} **{date_str}**\n"
            history_text += f"   📱 {apk_name} {build_type}\n"
            
            if success:
                history_text += f"   ⏱️ Duration: {duration}s\n\n"
            else:
                error_msg = error or "Unknown error"
                history_text += f"   ⚠️ Failed: {error_msg}\n\n"
        
        if len(history) > 10:
            history_text += f"_... and {len(history) - 10} more builds_\n\n"
        
        successful = len([b for b in history if b.get('success')])
        success_rate = (successful / len(history)) * 100 if history else 0
        
        history_text += f"📊 Success Rate: **{success_rate:.1f}%**"
        
        await event.reply(
            history_text,
            buttons=[
                [Button.inline("📊 View Stats", data="user:stats")],
                [Button.inline("🏠 Back to Menu", data="user:menu")]
            ]
        )
        return
    
    if text == '/logout':
        if not user_manager.is_authenticated(user_id):
            await event.reply("❌ You are not logged in")
            return
        
        username = user_manager.get_username(user_id)
        
        await event.reply(
            f"⚠️ **Confirm Logout**\n\n"
            f"Are you sure you want to logout?\n\n"
            f"Username: @{username}\n\n"
            f"You will need to login again to use the bot.",
            buttons=[
                [Button.inline("✅ Yes, Logout", data="user:logout:confirm")],
                [Button.inline("❌ Cancel", data="user:menu")]
            ]
        )
        return
    
    if text == '/help':
        is_admin = user_id in ADMIN_USER_IDS
        
        if is_admin:
            help_text = (
                "🎯 **APK Studio - Admin Help**\n\n"
                "**Admin Commands:**\n"
                "• `/admin` - Open admin panel\n"
                "• `/broadcast <message>` - Send message to all users\n"
                "• `/help` - Show this help\n\n"
                "**Admin Panel Features:**\n"
                "• 📊 Statistics - View system stats\n"
                "• 👥 User Management - Ban/unban users\n"
                "• 📱 APK Management - Add/remove APKs\n"
                "• 📋 Queue Status - Monitor builds\n\n"
                "**User Commands:**\n"
                "• `/start` - Start the bot\n"
                "• `/stats` - View your statistics\n"
                "• `/history` - View build history\n"
                "• `/logout` - Logout from account"
            )
        else:
            help_text = (
                "🎯 **APK Studio - User Help**\n\n"
                "**Available Commands:**\n"
                "• `/start` - Start the bot and login\n"
                "• `/stats` - View your statistics\n"
                "• `/history` - View build history\n"
                "• `/logout` - Logout from account\n"
                "• `/help` - Show this help\n\n"
                "**How to Build APK:**\n"
                "1️⃣ Send `/start` and login\n"
                "2️⃣ Select an APK from menu\n"
                "3️⃣ Choose Quick or Custom build\n"
                "4️⃣ Wait for completion\n"
                "5️⃣ Download your APK\n\n"
                "**Build Types:**\n"
                "• ⚡ Quick Build - Default theme\n"
                "• 🎨 Custom Build - Custom colors\n\n"
                "**Your Statistics:**\n"
                "Track your builds, success rate,\n"
                "and most used APKs with `/stats`"
            )
        
        await event.reply(help_text)
        return

    if theme_manager.is_customizing(user_id):
        handled = await handle_theme_input(event, bot, user_manager)
        if handled:
            return

    if text == '/start':
        if stats_manager.is_user_banned(user_id):
            await event.reply(
                "🚫 **Access Denied**\n\n"
                "Your account has been banned.\n\n"
                "📝 If you think this is a mistake,\n"
                "please contact the administrator."
            )
            return
        
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

            buttons.append([Button.inline("🚪 Logout", data="user:logout")])
            
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
                    message += "⚠️ Previous device logged out\n\n"
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
    
    if stats_manager.is_user_banned(user_id):
        await event.answer("🚫 Your account has been banned", alert=True)
        return

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

    await event.edit(
        f"🎨 **{apk_name}**\n\n"
        f"Choose generation mode:",
        buttons=[
            [Button.inline("⚡ Quick Generate", data=f"quick:{selected_apk_filename}")],
            [Button.inline("🎨 Custom Theme", data=f"custom:{selected_apk_filename}")]
        ]
    )


@bot.on(events.CallbackQuery)
async def callback_handler(event):
    """General handler for all callback queries"""
    data = event.data.decode('utf-8')
    user_id = event.sender_id
    
    if data.startswith('admin:'):
        await handle_admin_callback(event, ADMIN_USER_IDS)
        return
    
    if data == "user:stats":
        user_details = stats_manager.get_user_details(user_id)
        if not user_details:
            await event.answer("❌ No statistics available", alert=True)
            return
        
        username = user_details.get('username', 'Unknown')
        total_builds = user_details.get('total_builds', 0)
        quick_builds = user_details.get('quick_builds', 0)
        custom_builds = user_details.get('custom_builds', 0)
        failed_builds = user_details.get('failed_builds', 0)
        avg_time = user_details.get('avg_build_time', 0)
        apk_usage = user_details.get('apk_usage', {})
        
        success_rate = 0
        if total_builds > 0:
            success_rate = ((total_builds - failed_builds) / total_builds) * 100
        
        most_used_apk = "None"
        if apk_usage:
            most_used = max(apk_usage.items(), key=lambda x: x[1])
            most_used_apk = f"{most_used[0]} - {most_used[1]} times"
        
        stats_text = (
            f"📊 **Your Statistics**\n\n"
            f"👤 Username: @{username}\n\n"
            f"🔨 **Total Builds:** {total_builds}\n"
            f"⚡ Quick: {quick_builds} | 🎨 Custom: {custom_builds}\n"
            f"❌ Failed: {failed_builds}\n\n"
            f"⏱️ **Average Time:** {avg_time}s\n"
            f"📈 **Success Rate:** {success_rate:.1f}%\n\n"
            f"🏆 **Most Used APK:**\n"
            f"   {most_used_apk}"
        )
        
        await event.edit(
            stats_text,
            buttons=[
                [Button.inline("📜 View History", data="user:history")],
                [Button.inline("🏠 Back to Menu", data="user:menu")]
            ]
        )
        return
    
    elif data == "user:history":
        await event.answer("⏳ Loading history...")
        
        import json
        from datetime import datetime, timedelta
        from pathlib import Path
        
        logs_dir = Path("logs/builds")
        history = []
        
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            log_file = logs_dir / f"{date_str}.json"
            
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    for log in logs:
                        if log.get('user_id') == user_id:
                            history.append(log)
        
        history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        if not history:
            await event.edit(
                "📜 **Your Build History**\n\n"
                "No builds yet.",
                buttons=[[Button.inline("🏠 Back", data="user:menu")]]
            )
            return
        
        history_text = f"📜 **Your Build History**\n\nTotal: **{len(history)}**\n\n"
        
        for i, build in enumerate(history[:5], 1):
            success = build.get('success', False)
            apk_name = build.get('apk_name', 'Unknown')
            timestamp = build.get('timestamp', '')
            
            status_icon = "✅" if success else "❌"
            
            try:
                dt = datetime.fromisoformat(timestamp)
                date_str = dt.strftime('%m-%d %H:%M')
            except:
                date_str = 'Unknown'
            
            history_text += f"{status_icon} {date_str} - {apk_name}\n"
        
        if len(history) > 5:
            history_text += f"\n_... and {len(history) - 5} more_"
        
        await event.edit(
            history_text,
            buttons=[
                [Button.inline("📊 View Stats", data="user:stats")],
                [Button.inline("🏠 Back", data="user:menu")]
            ]
        )
        return
    
    elif data == "user:menu":
        apks = get_available_apks()
        buttons = []
        for apk in apks:
            buttons.append([Button.inline(
                f"🔨 {apk['name']} ({apk['size_mb']} MB)",
                data=f"build:{apk['filename']}"
            )])
        
        buttons.append([Button.inline("🚪 Logout", data="user:logout")])
        
        await event.edit(
            "✨ **Welcome back!**\n\n"
            "🎯 Select an app to generate",
            buttons=buttons
        )
        return
    
    elif data == "user:logout":
        username = user_manager.get_username(user_id)
        
        await event.edit(
            f"⚠️ **Confirm Logout**\n\n"
            f"Are you sure you want to logout?\n\n"
            f"Username: @{username}",
            buttons=[
                [Button.inline("✅ Yes, Logout", data="user:logout:confirm")],
                [Button.inline("❌ Cancel", data="user:menu")]
            ]
        )
        return
    
    elif data == "user:logout:confirm":
        username = user_manager.get_username(user_id)
        
        user_id_str = str(user_id)
        if user_id_str in user_manager.users:
            del user_manager.users[user_id_str]
            user_manager.save_users()
        
        await event.edit(
            f"✅ **Logged Out**\n\n"
            f"@{username} has been logged out successfully.\n\n"
            f"To use the bot again, send /start"
        )
        return
    
    raise events.StopPropagation


@bot.on(events.CallbackQuery(pattern=r"^quick:(.+)$"))
async def quick_build_handler(event):
    user_id = event.sender_id
    apk_file = None
    
    username = user_manager.get_username(user_id)

    try:
        if stats_manager.is_user_banned(user_id):
            await event.answer("🚫 Your account has been banned", alert=True)
            return
        
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

        active, waiting = await build_queue.get_queue_status()
        
        if waiting > 0 or active >= 5:
            await event.edit(
                f"⏳ **Queue System**\n\n"
                f"🔄 Active: {active}/5\n"
                f"⏱️ Waiting: {waiting}\n\n"
                f"You are in queue. Please wait..."
            )
        
        await build_queue.acquire(user_id)

        apk_name = selected_apk_filename.replace('.apk', '')

        await event.edit(
            f"🎨 **Creating {apk_name}**\n\n"
            f"⚡ Generating your application..."
        )

        service_token = user_manager.get_token(user_id)
        device_token = get_device_token(service_token)

        if not device_token:
            await event.edit("❌ **Authentication failed**\n\nPlease try again")
            return

        logger.info(f"Building {apk_name} for user {user_id} with token {device_token}")

        import time
        start_time = time.time()
        success, result = await build_apk(user_id, device_token, base_apk_path, custom_theme=None)
        build_duration = int(time.time() - start_time)
        
        apk_name = selected_apk_filename.replace('.apk', '')
        stats_manager.log_build(
            user_id=user_id,
            username=username or 'Unknown',
            apk_name=apk_name,
            duration=build_duration,
            success=success,
            is_custom=False,
            error=None if success else result
        )
        
        if success:
            apk_manager.increment_build_count(selected_apk_filename)

        if success:
            apk_file = result

            await event.edit(
                "✅ **Build Complete**\n\n"
                "📤 Uploading..."
            )

            uploaded_file = await upload_file(
                client=bot,
                file=apk_file
            )
            
            await bot.send_file(
                event.chat_id,
                uploaded_file,
                caption=(
                    f"✅ **Your app is ready!**\n\n"
                    f"📱 **{apk_name}**\n\n"
                    f"🔐 Secured & Signed\n"
                    f"⚡ Ready for installation\n\n"
                    f"🎨 Generated with APK Studio"
                )
            )

            await event.delete()

        else:
            logger.error(f"Build failed for user {user_id}: {result}")
            await event.edit(
                f"⚠️ **Generation failed**\n\n"
                f"Something went wrong\n\n"
                f"💬 Please contact support"
            )

    except Exception as e:
        logger.error(f"Handler error: {str(e)}", exc_info=True)
        await event.edit(
            f"⚠️ **Oops! Something happened**\n\n"
            f"Please try again or contact support"
        )

    finally:
        build_queue.release(user_id)

        if apk_file and await asyncio.to_thread(os.path.exists, apk_file):
            try:
                await asyncio.to_thread(os.remove, apk_file)
                logger.info(f"Cleaned final APK: {apk_file}")
            except Exception as e:
                logger.warning(f"Could not remove final APK: {e}")


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
logger.info("Bot started and ready!")
bot.run_until_disconnected()
