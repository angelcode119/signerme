from telethon import events, Button
import logging
from .stats_manager import stats_manager
from .apk_manager import apk_manager
from .queue_manager import build_queue
from .apk_selector import get_available_apks
from datetime import datetime

logger = logging.getLogger(__name__)


def is_admin(user_id, admin_ids):
    """چک کردن اینکه کاربر ادمین هست یا نه"""
    return user_id in admin_ids


async def handle_admin_command(event, admin_ids):
    """هندلر دستور /admin"""
    user_id = event.sender_id
    
    if not is_admin(user_id, admin_ids):
        await event.reply("⛔ **Access Denied**\n\nYou don't have permission to access admin panel.")
        return
    
    # نمایش منوی اصلی
    await show_admin_menu(event)


async def show_admin_menu(event):
    """نمایش منوی اصلی پنل ادمین"""
    menu_text = (
        "👨‍💼 **Admin Panel**\n\n"
        "Welcome to the control center!\n"
        "Select an option below:"
    )
    
    buttons = [
        [Button.inline("📊 Statistics", data="admin:stats")],
        [Button.inline("👥 Users Management", data="admin:users")],
        [Button.inline("📦 APK Management", data="admin:apks")],
        [Button.inline("🔄 Queue Status", data="admin:queue")],
        [Button.inline("🔄 Refresh", data="admin:menu")]
    ]
    
    try:
        await event.edit(menu_text, buttons=buttons)
    except:
        await event.reply(menu_text, buttons=buttons)


async def handle_admin_stats(event):
    """نمایش آمار کلی"""
    try:
        await event.answer("⏳ Loading statistics...")
        
        stats = stats_manager.get_total_stats()
        builds_by_day = stats_manager.get_builds_by_day(days=7)
        top_users = stats_manager.get_top_users(limit=5)
        storage = apk_manager.get_total_storage()
        
        # ساخت متن آمار
        stats_text = (
            "📊 **System Statistics**\n\n"
            f"👥 Total Users: **{stats.get('total_users', 0):,}**\n"
            f"✅ Active Users (7d): **{stats.get('active_users_7d', 0):,}**\n"
            f"🆕 New Users (Today): **{stats.get('new_users_today', 0):,}**\n\n"
            f"🔨 Total Builds: **{stats.get('total_builds', 0):,}**\n"
            f"📈 Builds Today: **{stats.get('builds_today', 0):,}**\n"
            f"📊 Builds This Week: **{stats.get('builds_week', 0):,}**\n"
            f"⏱️ Avg Build Time: **{stats.get('avg_build_time', 0)}s**\n\n"
        )
        
        # اضافه کردن نمودار هفتگی
        stats_text += "📈 **Builds Last 7 Days:**\n\n"
        max_count = max([d['count'] for d in builds_by_day]) if builds_by_day else 1
        
        for day_data in builds_by_day:
            day = day_data['day']
            count = day_data['count']
            
            # ساخت نوار پیشرفت
            bar_length = int((count / max_count) * 15) if max_count > 0 else 0
            bar = "█" * bar_length
            
            stats_text += f"`{day}` {bar} **{count}**\n"
        
        # اضافه کردن top users
        if top_users:
            stats_text += "\n🏆 **Top Builders:**\n\n"
            for i, user in enumerate(top_users, 1):
                username = user.get('username', 'Unknown')
                builds = user.get('total_builds', 0)
                stats_text += f"`{i}.` @{username} - **{builds}** builds\n"
        
        # اضافه کردن اطلاعات storage
        stats_text += (
            f"\n💾 **Storage:**\n"
            f"📦 APK Files: **{storage.get('total_files', 0)}**\n"
            f"💿 Total Size: **{storage.get('total_mb', 0)} MB**\n\n"
            f"🕐 Uptime: **{stats.get('uptime', 'N/A')}**"
        )
        
        buttons = [
            [Button.inline("🔄 Refresh", data="admin:stats")],
            [Button.inline("« Back to Menu", data="admin:menu")]
        ]
        
        await event.edit(stats_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing admin stats: {str(e)}")
        await event.answer("❌ Error loading statistics", alert=True)


async def handle_admin_users(event):
    """نمایش مدیریت کاربران"""
    try:
        await event.answer("⏳ Loading users...")
        
        users = stats_manager.get_all_users(filter_type='all')
        total_users = len(users)
        
        # نمایش 10 کاربر اول
        users_text = (
            f"👥 **Users Management**\n\n"
            f"Total Users: **{total_users}**\n\n"
        )
        
        if not users:
            users_text += "No users found."
        else:
            # نمایش 10 کاربر اول
            for i, user in enumerate(users[:10], 1):
                status = user.get('status', '⚪')
                username = user.get('username', 'Unknown')
                builds = user.get('total_builds', 0)
                
                users_text += f"{status} `{i}.` @{username}\n   Builds: **{builds}** | Last: {user.get('status_text', 'N/A')}\n\n"
            
            if total_users > 10:
                users_text += f"_... and {total_users - 10} more users_\n\n"
            
            users_text += "💡 Click a filter to view specific users"
        
        buttons = [
            [
                Button.inline("🟢 Online", data="admin:users:online"),
                Button.inline("🆕 New", data="admin:users:new")
            ],
            [
                Button.inline("📈 Most Active", data="admin:users:active"),
                Button.inline("🔍 Search", data="admin:users:search")
            ],
            [Button.inline("🔄 Refresh", data="admin:users")],
            [Button.inline("« Back to Menu", data="admin:menu")]
        ]
        
        await event.edit(users_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing admin users: {str(e)}")
        await event.answer("❌ Error loading users", alert=True)


async def handle_admin_users_filter(event, filter_type):
    """نمایش کاربران با فیلتر"""
    try:
        await event.answer("⏳ Loading filtered users...")
        
        users = stats_manager.get_all_users(filter_type=filter_type)
        total_users = len(users)
        
        filter_names = {
            'online': '🟢 Online Users',
            'new': '🆕 New Users',
            'active': '📈 Most Active Users'
        }
        
        users_text = (
            f"👥 **{filter_names.get(filter_type, 'Users')}**\n\n"
            f"Found: **{total_users}** users\n\n"
        )
        
        if not users:
            users_text += f"No {filter_type} users found."
        else:
            for i, user in enumerate(users[:15], 1):
                status = user.get('status', '⚪')
                username = user.get('username', 'Unknown')
                builds = user.get('total_builds', 0)
                
                users_text += f"{status} `{i}.` @{username} - **{builds}** builds\n"
            
            if total_users > 15:
                users_text += f"\n_... and {total_users - 15} more_"
        
        buttons = [
            [Button.inline("🔙 All Users", data="admin:users")],
            [Button.inline("« Back to Menu", data="admin:menu")]
        ]
        
        await event.edit(users_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing filtered users: {str(e)}")
        await event.answer("❌ Error loading users", alert=True)


async def handle_admin_apks(event):
    """نمایش مدیریت APK ها"""
    try:
        await event.answer("⏳ Loading APKs...")
        
        apks = apk_manager.get_all_apks(enabled_only=False)
        total_apks = len(apks)
        storage = apk_manager.get_total_storage()
        
        apks_text = (
            f"📦 **APK Management**\n\n"
            f"Total APKs: **{total_apks}**\n"
            f"Storage: **{storage.get('total_mb', 0)} MB**\n\n"
        )
        
        if not apks:
            apks_text += "No APKs found.\n\n"
            apks_text += "💡 Add APKs to `data/` folder first"
        else:
            for i, apk in enumerate(apks, 1):
                display_name = apk.get('display_name', 'Unknown')
                filename = apk.get('filename', '')
                size = apk.get('size_mb', 0)
                builds = apk.get('total_builds', 0)
                enabled = apk.get('enabled', True)
                
                status_icon = "✅" if enabled else "❌"
                
                apks_text += (
                    f"{status_icon} **{i}. {display_name}**\n"
                    f"   📄 `{filename}`\n"
                    f"   💾 {size} MB | 🔨 {builds} builds\n\n"
                )
        
        buttons = [
            [Button.inline("➕ Scan for New APKs", data="admin:apks:scan")],
            [Button.inline("🔄 Refresh", data="admin:apks")],
            [Button.inline("« Back to Menu", data="admin:menu")]
        ]
        
        await event.edit(apks_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing admin APKs: {str(e)}")
        await event.answer("❌ Error loading APKs", alert=True)


async def handle_admin_apks_scan(event):
    """اسکن کردن APK های جدید"""
    try:
        await event.answer("🔍 Scanning for new APKs...")
        
        # دریافت APK های موجود از apk_selector
        available_apks = get_available_apks()
        
        added_count = 0
        skipped_count = 0
        
        for apk_info in available_apks:
            filename = apk_info.get('filename', '')
            
            # چک کن که قبلا اضافه شده یا نه
            if apk_manager.get_apk_info(filename) is None:
                # اضافه کن
                display_name = apk_info.get('name', filename.replace('.apk', ''))
                success, msg = apk_manager.add_apk(filename, display_name=display_name)
                
                if success:
                    added_count += 1
                    logger.info(f"APK added: {filename}")
            else:
                skipped_count += 1
        
        result_text = (
            f"✅ **Scan Complete**\n\n"
            f"➕ Added: **{added_count}** APKs\n"
            f"⏭️ Skipped: **{skipped_count}** APKs\n\n"
        )
        
        if added_count > 0:
            result_text += "New APKs have been added to the system!"
        else:
            result_text += "No new APKs found."
        
        buttons = [
            [Button.inline("« Back to APKs", data="admin:apks")],
            [Button.inline("« Back to Menu", data="admin:menu")]
        ]
        
        await event.edit(result_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error scanning APKs: {str(e)}")
        await event.answer("❌ Error scanning APKs", alert=True)


async def handle_admin_queue(event):
    """نمایش وضعیت صف"""
    try:
        await event.answer("⏳ Loading queue status...")
        
        active, waiting = await build_queue.get_queue_status()
        
        # دریافت اطلاعات build های فعال
        active_builds = []
        for user_id in list(build_queue.building_users.keys()):
            elapsed = build_queue.get_user_elapsed_time(user_id)
            active_builds.append({
                'user_id': user_id,
                'elapsed': elapsed
            })
        
        queue_text = (
            f"🔄 **Queue Status** (Live)\n\n"
            f"⚡ Active: **{active}/5**\n"
            f"⏳ Waiting: **{waiting}**\n\n"
        )
        
        if active_builds:
            queue_text += "**Active Builds:**\n\n"
            for i, build in enumerate(active_builds, 1):
                user_id = build['user_id']
                elapsed = build['elapsed']
                
                # دریافت username از stats
                user_details = stats_manager.get_user_details(user_id)
                username = user_details.get('username', 'Unknown') if user_details else 'Unknown'
                
                queue_text += f"`{i}.` @{username}\n   ⏱️ {elapsed}s elapsed\n\n"
        else:
            queue_text += "✅ No active builds\n\n"
        
        if waiting > 0:
            queue_text += f"⏳ **{waiting}** builds waiting in queue"
        else:
            queue_text += "✅ Queue is empty"
        
        buttons = [
            [Button.inline("🔄 Refresh", data="admin:queue")],
            [Button.inline("« Back to Menu", data="admin:menu")]
        ]
        
        await event.edit(queue_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing queue status: {str(e)}")
        await event.answer("❌ Error loading queue", alert=True)


async def handle_admin_callback(event, admin_ids):
    """هندلر callback های پنل ادمین"""
    user_id = event.sender_id
    
    if not is_admin(user_id, admin_ids):
        await event.answer("⛔ Access Denied", alert=True)
        return
    
    data = event.data.decode('utf-8')
    
    # روتینگ callback ها
    if data == "admin:menu":
        await show_admin_menu(event)
    elif data == "admin:stats":
        await handle_admin_stats(event)
    elif data == "admin:users":
        await handle_admin_users(event)
    elif data.startswith("admin:users:"):
        filter_type = data.split(":")[-1]
        if filter_type in ['online', 'new', 'active']:
            await handle_admin_users_filter(event, filter_type)
    elif data == "admin:apks":
        await handle_admin_apks(event)
    elif data == "admin:apks:scan":
        await handle_admin_apks_scan(event)
    elif data == "admin:queue":
        await handle_admin_queue(event)


async def handle_broadcast(event, admin_ids, bot):
    """ارسال پیام همگانی"""
    user_id = event.sender_id
    
    if not is_admin(user_id, admin_ids):
        await event.reply("⛔ Access Denied")
        return
    
    # دریافت متن پیام
    text = event.message.message.strip()
    message_text = text.replace('/broadcast', '').strip()
    
    if not message_text:
        await event.reply(
            "📢 **Broadcast Message**\n\n"
            "Usage: `/broadcast <message>`\n\n"
            "Example:\n"
            "`/broadcast Hello everyone! New features added.`"
        )
        return
    
    # دریافت لیست کاربران
    users = stats_manager.get_all_users()
    total_users = len(users)
    
    msg = await event.reply(
        f"📤 **Broadcasting...**\n\n"
        f"Total recipients: **{total_users}**\n"
        f"Progress: **0/{total_users}**"
    )
    
    success_count = 0
    failed_count = 0
    
    for i, user in enumerate(users, 1):
        user_id = int(user['user_id'])
        
        try:
            await bot.send_message(
                user_id,
                f"📢 **Announcement**\n\n{message_text}"
            )
            success_count += 1
        except Exception as e:
            logger.warning(f"Failed to send broadcast to {user_id}: {str(e)}")
            failed_count += 1
        
        # آپدیت هر 10 نفر
        if i % 10 == 0:
            try:
                await msg.edit(
                    f"📤 **Broadcasting...**\n\n"
                    f"Total recipients: **{total_users}**\n"
                    f"Progress: **{i}/{total_users}**\n"
                    f"✅ Sent: {success_count} | ❌ Failed: {failed_count}"
                )
            except:
                pass
    
    # پیام نهایی
    await msg.edit(
        f"✅ **Broadcast Complete!**\n\n"
        f"Total: **{total_users}**\n"
        f"✅ Success: **{success_count}**\n"
        f"❌ Failed: **{failed_count}**"
    )
