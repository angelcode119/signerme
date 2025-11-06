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

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.config import API_ID, API_HASH, BOT_TOKEN
from modules.auth import UserManager, request_otp, verify_otp, get_device_token
from modules.apk_builder import build_apk
from modules.utils import cleanup_session
from modules.queue_manager import build_queue
from modules.apk_selector import get_available_apks, get_apk_path
from modules.theme_manager import theme_manager
from modules.custom_build_handler import handle_custom_build_start, handle_theme_input


cleanup_session('data/bot1_session')
user_manager = UserManager('data/users.json')
bot = TelegramClient('data/bot1_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)


@bot.on(events.NewMessage)
async def handler(event):
    user_id = event.sender_id
    text = event.message.message.strip()

    if theme_manager.is_customizing(user_id):
        handled = await handle_theme_input(event, bot, user_manager)
        if handled:
            return

    if text == '/start':
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
                user_manager.save_user(user_id, username, token)
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

                await event.reply(
                    "🎉 **Access Granted!**\n\n🎯 Choose your application",
                    buttons=buttons
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

    await event.edit(
        f"🎨 **{apk_name}**\n\n"
        f"Choose generation mode:",
        buttons=[
            [Button.inline("⚡ Quick Generate", data=f"quick:{selected_apk_filename}")],
            [Button.inline("🎨 Custom Theme", data=f"custom:{selected_apk_filename}")]
        ]
    )


@bot.on(events.CallbackQuery(pattern=r"^quick:(.+)$"))
async def quick_build_handler(event):
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
                f"⏳ Already generating an app\n\n"
                f"Time elapsed: {elapsed}s\n\n"
                f"Please wait for completion...",
                alert=True
            )
            return

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

        success, result = await build_apk(user_id, device_token, base_apk_path, custom_theme=None)

        if success:
            apk_file = result

            await event.edit(
                "✨ **Finalizing...**\n\n"
                "🔐 Securing & packaging..."
            )

            await bot.send_file(
                event.chat_id,
                apk_file,
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
