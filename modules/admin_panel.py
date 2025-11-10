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
            for i, apk in enumerate(apks[:10], 1):  # نمایش 10 تا اول
                display_name = apk.get('display_name', 'Unknown')
                filename = apk.get('filename', '')
                size = apk.get('size_mb', 0)
                builds = apk.get('total_builds', 0)
                enabled = apk.get('enabled', True)
                
                status_icon = "✅" if enabled else "❌"
                
                apks_text += (
                    f"{status_icon} **{display_name}**\n"
                    f"   📄 `{filename}`\n"
                    f"   💾 {size} MB | 🔨 {builds} builds\n"
                    f"   [📊 Stats](callback:admin:apk:stats:{filename}) | "
                    f"[✏️ Edit](callback:admin:apk:edit:{filename}) | "
                    f"[🗑️ Delete](callback:admin:apk:delete:{filename})\n\n"
                )
            
            if total_apks > 10:
                apks_text += f"_... and {total_apks - 10} more APKs_\n\n"
        
        # ساخت دکمه‌ها برای 5 APK اول
        buttons = []
        for i, apk in enumerate(apks[:5], 1):
            filename = apk.get('filename', '')
            display_name = apk.get('display_name', 'Unknown')
            buttons.append([Button.inline(f"📱 {display_name}", data=f"admin:apk:view:{filename}")])
        
        buttons.extend([
            [Button.inline("➕ Scan for New APKs", data="admin:apks:scan")],
            [Button.inline("🔄 Refresh", data="admin:apks")],
            [Button.inline("« Back to Menu", data="admin:menu")]
        ])
        
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


async def handle_admin_apk_view(event, filename):
    """نمایش جزئیات یک APK"""
    try:
        await event.answer("⏳ Loading APK details...")
        
        apk_info = apk_manager.get_apk_info(filename)
        
        if not apk_info:
            await event.answer("❌ APK not found!", alert=True)
            return
        
        display_name = apk_info.get('display_name', 'Unknown')
        size_mb = apk_info.get('size_mb', 0)
        total_builds = apk_info.get('total_builds', 0)
        category = apk_info.get('category', 'Other')
        enabled = apk_info.get('enabled', True)
        added_date = apk_info.get('added_date', 'Unknown')
        last_build = apk_info.get('last_build', 'Never')
        
        # فرمت کردن تاریخ‌ها
        if added_date != 'Unknown':
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(added_date)
                added_date = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        
        if last_build != 'Never':
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(last_build)
                last_build = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        
        status = "✅ Enabled" if enabled else "❌ Disabled"
        
        apk_text = (
            f"📦 **APK Details**\n\n"
            f"📱 **Name**: {display_name}\n"
            f"📄 **File**: `{filename}`\n"
            f"💾 **Size**: {size_mb} MB\n"
            f"📂 **Category**: {category}\n"
            f"🔨 **Total Builds**: {total_builds}\n"
            f"📅 **Added**: {added_date}\n"
            f"🕐 **Last Build**: {last_build}\n"
            f"🔘 **Status**: {status}\n"
        )
        
        buttons = [
            [
                Button.inline("✏️ Edit Name", data=f"admin:apk:editname:{filename}"),
                Button.inline("📊 Full Stats", data=f"admin:apk:stats:{filename}")
            ],
            [
                Button.inline("✅ Enable" if not enabled else "❌ Disable", 
                            data=f"admin:apk:toggle:{filename}")
            ],
            [Button.inline("🗑️ Delete APK", data=f"admin:apk:confirmdelete:{filename}")],
            [Button.inline("« Back to APKs", data="admin:apks")]
        ]
        
        await event.edit(apk_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing APK view: {str(e)}")
        await event.answer("❌ Error loading APK details", alert=True)


async def handle_admin_apk_stats(event, filename):
    """نمایش آمار دقیق یک APK"""
    try:
        await event.answer("⏳ Loading statistics...")
        
        apk_info = apk_manager.get_apk_stats(filename)
        
        if not apk_info:
            await event.answer("❌ APK not found!", alert=True)
            return
        
        display_name = apk_info.get('display_name', 'Unknown')
        total_builds = apk_info.get('total_builds', 0)
        
        # محاسبه آمار از لاگ‌ها
        from datetime import datetime, timedelta
        import json
        import os
        
        builds_today = 0
        builds_week = 0
        builds_month = 0
        
        logs_dir = Path("logs/builds")
        today = datetime.now().date()
        
        for i in range(30):  # 30 روز گذشته
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            log_file = logs_dir / f"{date_str}.json"
            
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    
                    for log in logs:
                        if log.get('apk_name') == filename.replace('.apk', '') and log.get('success'):
                            if i == 0:
                                builds_today += 1
                            if i < 7:
                                builds_week += 1
                            builds_month += 1
        
        stats_text = (
            f"📊 **APK Statistics**\n\n"
            f"📱 **{display_name}**\n"
            f"📄 `{filename}`\n\n"
            f"🔨 **Total Builds**: {total_builds}\n"
            f"📈 **Today**: {builds_today}\n"
            f"📊 **This Week**: {builds_week}\n"
            f"📅 **This Month**: {builds_month}\n\n"
        )
        
        if total_builds > 0:
            stats_text += f"📉 **Average**:\n"
            stats_text += f"   • Daily: ~{int(total_builds / max(1, (datetime.now() - datetime.fromisoformat(apk_info.get('added_date', datetime.now().isoformat()))).days))}\n"
            stats_text += f"   • Weekly: ~{builds_week}\n"
        
        buttons = [
            [Button.inline("« Back to APK", data=f"admin:apk:view:{filename}")],
            [Button.inline("« Back to APKs", data="admin:apks")]
        ]
        
        await event.edit(stats_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing APK stats: {str(e)}")
        await event.answer("❌ Error loading statistics", alert=True)


async def handle_admin_apk_toggle(event, filename):
    """فعال/غیرفعال کردن APK"""
    try:
        apk_info = apk_manager.get_apk_info(filename)
        
        if not apk_info:
            await event.answer("❌ APK not found!", alert=True)
            return
        
        current_status = apk_info.get('enabled', True)
        new_status = not current_status
        
        success, msg = apk_manager.update_apk(filename, enabled=new_status)
        
        if success:
            status_text = "✅ Enabled" if new_status else "❌ Disabled"
            await event.answer(f"APK {status_text}", alert=True)
            # نمایش مجدد جزئیات
            await handle_admin_apk_view(event, filename)
        else:
            await event.answer(f"❌ {msg}", alert=True)
        
    except Exception as e:
        logger.error(f"Error toggling APK: {str(e)}")
        await event.answer("❌ Error updating APK", alert=True)


async def handle_admin_apk_delete_confirm(event, filename):
    """تایید حذف APK"""
    try:
        apk_info = apk_manager.get_apk_info(filename)
        
        if not apk_info:
            await event.answer("❌ APK not found!", alert=True)
            return
        
        display_name = apk_info.get('display_name', 'Unknown')
        total_builds = apk_info.get('total_builds', 0)
        
        confirm_text = (
            f"⚠️ **Confirm Delete**\n\n"
            f"Are you sure you want to delete?\n\n"
            f"📱 **{display_name}**\n"
            f"📄 `{filename}`\n"
            f"🔨 {total_builds} builds recorded\n\n"
            f"⚠️ **Warning**: This action cannot be undone!\n"
            f"The APK file will remain in data/ folder,\n"
            f"only removed from bot's database."
        )
        
        buttons = [
            [
                Button.inline("✅ Yes, Delete", data=f"admin:apk:delete:{filename}"),
                Button.inline("❌ Cancel", data=f"admin:apk:view:{filename}")
            ]
        ]
        
        await event.edit(confirm_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing delete confirm: {str(e)}")
        await event.answer("❌ Error", alert=True)


async def handle_admin_apk_delete(event, filename):
    """حذف APK"""
    try:
        apk_info = apk_manager.get_apk_info(filename)
        
        if not apk_info:
            await event.answer("❌ APK not found!", alert=True)
            return
        
        display_name = apk_info.get('display_name', 'Unknown')
        
        success, msg = apk_manager.delete_apk(filename)
        
        if success:
            await event.answer(f"✅ {display_name} deleted", alert=True)
            await handle_admin_apks(event)
        else:
            await event.answer(f"❌ {msg}", alert=True)
        
    except Exception as e:
        logger.error(f"Error deleting APK: {str(e)}")
        await event.answer("❌ Error deleting APK", alert=True)


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
    elif data.startswith("admin:apk:view:"):
        filename = data.replace("admin:apk:view:", "")
        await handle_admin_apk_view(event, filename)
    elif data.startswith("admin:apk:stats:"):
        filename = data.replace("admin:apk:stats:", "")
        await handle_admin_apk_stats(event, filename)
    elif data.startswith("admin:apk:toggle:"):
        filename = data.replace("admin:apk:toggle:", "")
        await handle_admin_apk_toggle(event, filename)
    elif data.startswith("admin:apk:confirmdelete:"):
        filename = data.replace("admin:apk:confirmdelete:", "")
        await handle_admin_apk_delete_confirm(event, filename)
    elif data.startswith("admin:apk:delete:"):
        filename = data.replace("admin:apk:delete:", "")
        await handle_admin_apk_delete(event, filename)
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
