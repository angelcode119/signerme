from telethon import events, Button
from FastTelethon import upload_file
import asyncio
import os
import logging
from .apk_builder import build_apk
from .apk_selector import get_apk_path
from .auth import get_device_token
from .queue_manager import build_queue
from .theme_manager import theme_manager

logger = logging.getLogger(__name__)


async def handle_custom_build_start(event, bot, user_manager):
    user_id = event.sender_id
    match = event.pattern_match
    selected_apk_filename = match.group(1).decode('utf-8')
    base_apk_path = get_apk_path(selected_apk_filename)
    if not base_apk_path:
        await event.answer("❌ APK file not found!", alert=True)
        return
    apk_name = selected_apk_filename.replace('.apk', '')
    theme_manager.start_customization(user_id)
    theme_manager.set_apk(user_id, selected_apk_filename)
    step = theme_manager.get_current_step(user_id)
    step_info = theme_manager.get_step_description(step)
    await event.edit(
        f"🎨 **Customize {apk_name}**\n\n"
        f"{step_info['title']}\n"
        f"{step_info['desc']}\n\n"
        f"📝 Example: `{step_info['example']}`\n\n"
        f"Send your value or /skip",
        buttons=[[Button.inline("❌ Cancel", data="cancel_custom")]]
    )


async def handle_theme_input(event, bot, user_manager):
    user_id = event.sender_id
    text = event.message.message.strip()
    if not theme_manager.is_customizing(user_id):
        return False
    if text.lower() == '/skip':
        current_step = theme_manager.get_current_step(user_id)
        next_step = theme_manager.get_next_step(current_step)
        if next_step:
            theme_manager.user_themes[user_id]['step'] = next_step
            step_info = theme_manager.get_step_description(next_step)
            await event.reply(
                f"⏭️ **Skipped**\n\n"
                f"{step_info['title']}\n"
                f"{step_info['desc']}\n\n"
                f"📝 Example: `{step_info['example']}`\n\n"
                f"Send your value or /skip",
                buttons=[[Button.inline("❌ Cancel", data="cancel_custom")]]
            )
        else:
            await start_custom_build(event, user_id, bot, user_manager)
        return True
    success, result = theme_manager.set_value(user_id, text)
    if not success:
        await event.reply(f"❌ {result}\n\nTry again or /skip")
        return True
    if result:
        step_info = theme_manager.get_step_description(result)
        await event.reply(
            f"✅ **Saved!**\n\n"
            f"{step_info['title']}\n"
            f"{step_info['desc']}\n\n"
            f"📝 Example: `{step_info['example']}`\n\n"
            f"Send your value or /skip",
            buttons=[[Button.inline("❌ Cancel", data="cancel_custom")]]
        )
    else:
        await start_custom_build(event, user_id, bot, user_manager)
    return True


async def start_custom_build(event, user_id, bot, user_manager):
    apk_file = None
    try:
        selected_apk_filename = theme_manager.get_apk_filename(user_id)
        base_apk_path = get_apk_path(selected_apk_filename)
        app_type, custom_theme = theme_manager.get_customization_data(user_id)
        if not base_apk_path or not custom_theme:
            await event.reply("❌ Error: Missing build data")
            theme_manager.cancel_customization(user_id)
            return
        if build_queue.is_user_building(user_id):
            elapsed = build_queue.get_user_elapsed_time(user_id)
            await event.reply(
                f"⏳ **در حال ساخت APK شما**\n\n"
                f"⏱️ زمان سپری شده: {elapsed} ثانیه\n\n"
                f"✨ لطفاً صبر کنید تا تکمیل شود..."
            )
            theme_manager.cancel_customization(user_id)
            return
        
        active, waiting = await build_queue.get_queue_status()
        
        if waiting > 0 or active >= 1:
            msg = await event.reply(
                f"⏳ **در صف قرار گرفتید**\n\n"
                f"📍 موقعیت شما: **{waiting + 1}**\n"
                f"👤 یک کاربر در حال ساخت است\n\n"
                f"⏱️ لطفاً صبر کنید...\n"
                f"✨ به زودی نوبت شما می‌شود!"
            )
        
        await build_queue.acquire(user_id)
        
        if waiting > 0 or active >= 1:
            try:
                await msg.delete()
            except:
                pass
        apk_name = selected_apk_filename.replace('.apk', '')
        msg = await event.reply(
            f"🎨 **Creating {apk_name}**\n\n"
            f"⚡ Generating with your custom theme..."
        )
        service_token = user_manager.get_token(user_id)
        device_token = get_device_token(service_token)
        if not device_token:
            await msg.edit("❌ **Authentication failed**\n\nPlease try again")
            theme_manager.cancel_customization(user_id)
            return
        logger.info(f"Building custom {apk_name} for user {user_id}")
        success, result = await build_apk(user_id, device_token, base_apk_path, custom_theme=custom_theme, app_type=app_type)
        if success:
            apk_file = result
            await msg.edit("✅ **Build Complete**\n\n📤 Uploading...")
            
            uploaded_file = await upload_file(
                client=bot,
                file=apk_file
            )
            
            await bot.send_file(
                event.chat_id,
                uploaded_file,
                caption=(
                    f"✅ **Your custom app is ready!**\n\n"
                    f"📱 **{apk_name}**\n\n"
                    f"🎨 Custom themed\n"
                    f"🔐 Secured & Signed\n"
                    f"⚡ Ready for installation\n\n"
                    f"💎 Generated with APK Studio"
                )
            )
            await msg.delete()
        else:
            logger.error(f"Custom build failed for user {user_id}: {result}")
            await msg.edit(f"⚠️ **Generation failed**\n\nSomething went wrong\n\n💬 Please contact support")
    except Exception as e:
        logger.error(f"Custom build handler error: {str(e)}", exc_info=True)
        await event.reply(f"⚠️ **Oops! Something happened**\n\nPlease try again or contact support")
    finally:
        build_queue.release(user_id)
        theme_manager.cancel_customization(user_id)
        if apk_file and await asyncio.to_thread(os.path.exists, apk_file):
            try:
                await asyncio.to_thread(os.remove, apk_file)
                logger.info(f"Cleaned final APK: {apk_file}")
            except Exception as e:
                logger.warning(f"Could not remove final APK: {e}")
