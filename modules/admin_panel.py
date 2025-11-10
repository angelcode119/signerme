from telethon import events, Button
from FastTelethonhelper import download_file
import logging
import os
from pathlib import Path
from .stats_manager import stats_manager
from .apk_manager import apk_manager
from .queue_manager import build_queue
from .apk_selector import get_available_apks
from datetime import datetime

logger = logging.getLogger(__name__)

admin_upload_state = {}


def is_admin(user_id, admin_ids):
    """Check if user is admin"""
    return user_id in admin_ids


async def handle_admin_command(event, admin_ids):
    """Handler for /admin command"""
    user_id = event.sender_id
    
    if not is_admin(user_id, admin_ids):
        await event.reply("⛔ **Access Denied**\n\nYou don't have permission to access admin panel.")
        return
    
    await show_admin_menu(event)


async def show_admin_menu(event):
    """Show admin panel main menu"""
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
    """Show general statistics"""
    try:
        await event.answer("⏳ Loading statistics...")
        
        stats = stats_manager.get_total_stats()
        builds_by_day = stats_manager.get_builds_by_day(days=7)
        top_users = stats_manager.get_top_users(limit=5)
        storage = apk_manager.get_total_storage()
        
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
        
        stats_text += "📈 **Builds Last 7 Days:**\n\n"
        max_count = max([d['count'] for d in builds_by_day]) if builds_by_day else 1
        
        for day_data in builds_by_day:
            day = day_data['day']
            count = day_data['count']
            
            bar_length = int((count / max_count) * 15) if max_count > 0 else 0
            bar = "█" * bar_length
            
            stats_text += f"`{day}` {bar} **{count}**\n"
        
        if top_users:
            stats_text += "\n🏆 **Top Builders:**\n\n"
            for i, user in enumerate(top_users, 1):
                username = user.get('username', 'Unknown')
                builds = user.get('total_builds', 0)
                stats_text += f"`{i}.` @{username} - **{builds}** builds\n"
        
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
    """Show user management"""
    try:
        await event.answer("⏳ Loading users...")
        
        users = stats_manager.get_all_users(filter_type='all')
        total_users = len(users)
        
        banned_count = len([u for u in users if stats_manager.is_user_banned(u['user_id'])])
        
        users_text = (
            f"👥 **Users Management**\n\n"
            f"Total Users: **{total_users}**\n"
            f"🚫 Banned: **{banned_count}**\n\n"
        )
        
        if not users:
            users_text += "No users found."
        else:
            for i, user in enumerate(users[:10], 1):
                status = user.get('status', '⚪')
                username = user.get('username', 'Unknown')
                builds = user.get('total_builds', 0)
                user_id = user.get('user_id')
                
                is_banned = stats_manager.is_user_banned(user_id)
                ban_icon = " 🚫" if is_banned else ""
                
                users_text += f"{status} `{i}.` @{username}{ban_icon}\n   Builds: **{builds}** | Last: {user.get('status_text', 'N/A')}\n\n"
            
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
                Button.inline("🚫 Banned", data="admin:users:banned")
            ],
            [Button.inline("🔄 Refresh", data="admin:users")],
            [Button.inline("« Back to Menu", data="admin:menu")]
        ]
        
        await event.edit(users_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing admin users: {str(e)}")
        await event.answer("❌ Error loading users", alert=True)


async def handle_admin_users_filter(event, filter_type):
    """Show users with filter"""
    try:
        await event.answer("⏳ Loading filtered users...")
        
        if filter_type == 'banned':
            banned_users = stats_manager.get_banned_users()
            total_users = len(banned_users)
            
            users_text = (
                f"🚫 **Banned Users**\n\n"
                f"Total Banned: **{total_users}**\n\n"
            )
            
            if not banned_users:
                users_text += "No banned users."
            else:
                for i, user in enumerate(banned_users[:15], 1):
                    username = user.get('username', 'Unknown')
                    reason = user.get('ban_reason', 'No reason')
                    time_ago = user.get('ban_time_ago', 'Unknown')
                    user_id = user.get('user_id')
                    
                    users_text += (
                        f"`{i}.` @{username}\n"
                        f"   🚫 Banned {time_ago}\n"
                        f"   📝 Reason: {reason}\n"
                        f"   [🔓 Unban](callback:admin:user:unban:{user_id})\n\n"
                    )
                
                if total_users > 15:
                    users_text += f"\n_... and {total_users - 15} more_"
            
            buttons = []
            for i, user in enumerate(banned_users[:5], 1):
                username = user.get('username', 'Unknown')
                user_id = user.get('user_id')
                buttons.append([Button.inline(f"🔓 Unban @{username}", data=f"admin:user:unban:{user_id}")])
            
            buttons.extend([
                [Button.inline("🔙 All Users", data="admin:users")],
                [Button.inline("« Back to Menu", data="admin:menu")]
            ])
        else:
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
                for i, user in enumerate(users[:10], 1):
                    status = user.get('status', '⚪')
                    username = user.get('username', 'Unknown')
                    builds = user.get('total_builds', 0)
                    user_id = user.get('user_id')
                    
                    is_banned = stats_manager.is_user_banned(user_id)
                    ban_icon = " 🚫" if is_banned else ""
                    
                    users_text += f"{status} `{i}.` @{username}{ban_icon} - **{builds}** builds\n"
                
                if total_users > 10:
                    users_text += f"\n_... and {total_users - 10} more_"
            
            buttons = []
            for i, user in enumerate(users[:3], 1):
                username = user.get('username', 'Unknown')
                user_id = user.get('user_id')
                buttons.append([Button.inline(f"👤 @{username}", data=f"admin:user:view:{user_id}")])
            
            buttons.extend([
                [Button.inline("🔙 All Users", data="admin:users")],
                [Button.inline("« Back to Menu", data="admin:menu")]
            ])
        
        await event.edit(users_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing filtered users: {str(e)}")
        await event.answer("❌ Error loading users", alert=True)


async def handle_admin_apks(event):
    """Show APK management"""
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
            for i, apk in enumerate(apks[:10], 1):
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
        
        buttons = []
        for i, apk in enumerate(apks[:5], 1):
            filename = apk.get('filename', '')
            display_name = apk.get('display_name', 'Unknown')
            buttons.append([Button.inline(f"📱 {display_name}", data=f"admin:apk:view:{filename}")])
        
        buttons.extend([
            [
                Button.inline("➕ Upload APK", data="admin:apks:upload"),
                Button.inline("🔍 Scan Folder", data="admin:apks:scan")
            ],
            [Button.inline("🔄 Refresh", data="admin:apks")],
            [Button.inline("« Back to Menu", data="admin:menu")]
        ])
        
        await event.edit(apks_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing admin APKs: {str(e)}")
        await event.answer("❌ Error loading APKs", alert=True)


async def handle_admin_apks_upload(event):
    """Start new APK upload process"""
    try:
        user_id = event.sender_id
        
        admin_upload_state[user_id] = {
            'active': True,
            'step': 'waiting_file'
        }
        
        upload_text = (
            "📤 **Upload New APK**\n\n"
            "Please send me the APK file.\n\n"
            "📋 **Requirements:**\n"
            "• File format: .apk\n"
            "• Max size: 50 MB\n"
            "• Valid Android app\n\n"
            "After upload, you can set:\n"
            "• Display name\n"
            "• Category\n\n"
            "Send the APK file now..."
        )
        
        buttons = [
            [Button.inline("❌ Cancel Upload", data="admin:apks:cancelupload")]
        ]
        
        await event.edit(upload_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error starting APK upload: {str(e)}")
        await event.answer("❌ Error", alert=True)


async def handle_admin_apks_cancel_upload(event):
    """Cancel APK upload"""
    user_id = event.sender_id
    
    if user_id in admin_upload_state:
        del admin_upload_state[user_id]
    
    await event.answer("❌ Upload cancelled", alert=True)
    await handle_admin_apks(event)


async def handle_admin_apk_file_received(event, bot):
    """Receive APK file from admin"""
    user_id = event.sender_id
    
    if user_id not in admin_upload_state or not admin_upload_state[user_id].get('active'):
        return False
    
    try:
        if not event.message.document:
            return False
        
        file_name = None
        if event.message.document.attributes:
            for attr in event.message.document.attributes:
                if hasattr(attr, 'file_name'):
                    file_name = attr.file_name
                    break
        
        is_apk = False
        if file_name and file_name.lower().endswith('.apk'):
            is_apk = True
        
        if event.message.document.mime_type == 'application/vnd.android.package-archive':
            is_apk = True
        
        if not is_apk:
            await event.reply(
                "❌ **Invalid file type**\n\n"
                "Please send an APK file (.apk)\n\n"
                "Send APK or /cancel to abort."
            )
            return True
        
        file_size = event.message.document.size
        max_size = 100 * 1024 * 1024
        
        if file_size > max_size:
            await event.reply(
                f"❌ **File Too Large**\n\n"
                f"📦 Your file: {file_size / (1024*1024):.1f} MB\n"
                f"📏 Maximum: 100 MB\n\n"
                "Please send a smaller APK."
            )
            return True
        
        msg = await event.reply(
            f"📥 **Downloading APK...**\n\n"
            f"📄 {file_name or 'Unknown'}\n"
            f"💾 Size: {file_size / (1024*1024):.1f} MB\n\n"
            f"⏳ Please wait..."
        )
        
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        import time
        timestamp = int(time.time())
        safe_filename = file_name.replace(' ', '_') if file_name else f"app_{timestamp}.apk"
        
        apk_path = data_dir / safe_filename
        if apk_path.exists():
            name_parts = safe_filename.rsplit('.', 1)
            safe_filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
            apk_path = data_dir / safe_filename
        
        last_update = [0]
        
        async def progress_callback(current, total):
            progress = (current / total) * 100
            
            if progress - last_update[0] >= 10:
                last_update[0] = progress
                try:
                    await msg.edit(
                        f"📥 **Downloading APK...**\n\n"
                        f"📄 {file_name or 'Unknown'}\n"
                        f"Progress: {progress:.1f}%\n"
                        f"Downloaded: {current / (1024*1024):.1f} / {total / (1024*1024):.1f} MB"
                    )
                except:
                    pass
        
        await download_file(
            client=bot,
            location=event.message.document,
            file=str(apk_path),
            progress_callback=progress_callback
        )
        
        if not apk_path.exists() or apk_path.stat().st_size == 0:
            await msg.edit("❌ **Download failed**\n\nPlease try again.")
            if user_id in admin_upload_state:
                del admin_upload_state[user_id]
            return True
        
        await msg.edit(
            f"✅ **Downloaded successfully!**\n\n"
            f"🔍 Analyzing APK...\n"
            f"⏳ Extracting app info..."
        )
        
        from .apk_analyzer import APKAnalyzer
        import tempfile
        
        try:
            analyzer = APKAnalyzer(str(apk_path))
            analyze_dir = tempfile.mkdtemp(prefix='admin_analyze_')
            
            results = await analyzer.analyze(analyze_dir)
            
            app_name = results.get('app_name') or safe_filename.replace('.apk', '').replace('_', ' ')
            package_name = results.get('package_name') or 'unknown.package'
            
            import shutil
            try:
                shutil.rmtree(analyze_dir)
            except:
                pass
            
        except Exception as e:
            logger.warning(f"APK analysis failed: {str(e)}")
            app_name = safe_filename.replace('.apk', '').replace('_', ' ')
            package_name = 'unknown.package'
        
        success, result_msg = apk_manager.add_apk(
            filename=safe_filename,
            display_name=app_name,
            category='Other',
            enabled=True
        )
        
        if success:
            if user_id in admin_upload_state:
                del admin_upload_state[user_id]
            
            await msg.edit(
                f"✅ **APK Added Successfully!**\n\n"
                f"📱 **App Name**: {app_name}\n"
                f"📦 **Package**: `{package_name}`\n"
                f"📄 **File**: `{safe_filename}`\n"
                f"💾 **Size**: {apk_path.stat().st_size / (1024*1024):.1f} MB\n\n"
                f"The APK is now available for users!"
            )
            
            await event.reply(
                "What's next?",
                buttons=[
                    [Button.inline("📦 View APK", data=f"admin:apk:view:{safe_filename}")],
                    [Button.inline("« Back to APKs", data="admin:apks")]
                ]
            )
        else:
            await msg.edit(
                f"❌ **Failed to add APK**\n\n"
                f"Error: {result_msg}\n\n"
                f"File saved to: `data/{safe_filename}`"
            )
            
            if user_id in admin_upload_state:
                del admin_upload_state[user_id]
        
        return True
        
    except Exception as e:
        logger.error(f"Error receiving APK file: {str(e)}")
        await event.reply(
            f"❌ **Upload failed**\n\n"
            f"An error occurred.\n"
            f"Please try again."
        )
        
        if user_id in admin_upload_state:
            del admin_upload_state[user_id]
        
        return True


async def handle_admin_apks_scan(event):
    """Scan for new APKs"""
    try:
        await event.answer("🔍 Scanning for new APKs...")
        
        available_apks = get_available_apks()
        
        added_count = 0
        skipped_count = 0
        
        for apk_info in available_apks:
            filename = apk_info.get('filename', '')
            
            if apk_manager.get_apk_info(filename) is None:
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
    """Show queue status"""
    try:
        await event.answer("⏳ Loading queue status...")
        
        active, waiting = await build_queue.get_queue_status()
        
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
    """Show APK details"""
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
    """Show APK detailed statistics"""
    try:
        await event.answer("⏳ Loading statistics...")
        
        apk_info = apk_manager.get_apk_stats(filename)
        
        if not apk_info:
            await event.answer("❌ APK not found!", alert=True)
            return
        
        display_name = apk_info.get('display_name', 'Unknown')
        total_builds = apk_info.get('total_builds', 0)
        
        from datetime import datetime, timedelta
        import json
        import os
        
        builds_today = 0
        builds_week = 0
        builds_month = 0
        
        logs_dir = Path("logs/builds")
        today = datetime.now().date()
        
        for i in range(30):
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
    """Enable/disable APK"""
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
            await handle_admin_apk_view(event, filename)
        else:
            await event.answer(f"❌ {msg}", alert=True)
        
    except Exception as e:
        logger.error(f"Error toggling APK: {str(e)}")
        await event.answer("❌ Error updating APK", alert=True)


async def handle_admin_apk_delete_confirm(event, filename):
    """Confirm APK deletion"""
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
    """Delete APK"""
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


async def handle_admin_callback(event, bot, admin_ids):
    """Handler for admin panel callbacks"""
    user_id = event.sender_id
    
    if not is_admin(user_id, admin_ids):
        await event.answer("⛔ Access Denied", alert=True)
        return
    
    data = event.data.decode('utf-8')
    
    if data == "admin:menu":
        await show_admin_menu(event)
    elif data == "admin:stats":
        await handle_admin_stats(event)
    elif data == "admin:users":
        await handle_admin_users(event)
    elif data.startswith("admin:users:"):
        filter_type = data.split(":")[-1]
        if filter_type in ['online', 'new', 'active', 'banned']:
            await handle_admin_users_filter(event, filter_type)
    elif data.startswith("admin:user:view:"):
        user_id = data.replace("admin:user:view:", "")
        await handle_admin_user_view(event, user_id)
    elif data.startswith("admin:user:confirmban:"):
        user_id = data.replace("admin:user:confirmban:", "")
        await handle_admin_user_ban_confirm(event, user_id)
    elif data.startswith("admin:user:ban:"):
        parts = data.split(":")
        user_id = parts[3]
        reason = parts[4] if len(parts) > 4 else "No reason"
        await handle_admin_user_ban(event, user_id, reason)
    elif data.startswith("admin:user:unban:"):
        user_id = data.replace("admin:user:unban:", "")
        await handle_admin_user_unban(event, user_id)
    elif data == "admin:apks":
        await handle_admin_apks(event)
    elif data == "admin:apks:upload":
        await handle_admin_apks_upload(event)
    elif data == "admin:apks:cancelupload":
        await handle_admin_apks_cancel_upload(event)
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


async def handle_admin_user_view(event, user_id):
    """Show complete user details"""
    try:
        await event.answer("⏳ Loading user details...")
        
        user_details = stats_manager.get_user_details(user_id)
        
        if not user_details:
            await event.answer("❌ User not found!", alert=True)
            return
        
        username = user_details.get('username', 'Unknown')
        total_builds = user_details.get('total_builds', 0)
        quick_builds = user_details.get('quick_builds', 0)
        custom_builds = user_details.get('custom_builds', 0)
        failed_builds = user_details.get('failed_builds', 0)
        avg_time = user_details.get('avg_build_time', 0)
        total_time = user_details.get('total_time', '0m')
        first_build = user_details.get('first_build')
        last_build = user_details.get('last_build')
        last_active = user_details.get('last_active', 'Unknown')
        
        success_rate = 0
        if total_builds > 0:
            success_rate = ((total_builds - failed_builds) / total_builds) * 100
        
        is_banned = stats_manager.is_user_banned(user_id)
        ban_status = "🚫 **BANNED**" if is_banned else "✅ Active"
        
        user_text = (
            f"👤 **User Details**\n\n"
            f"Username: @{username}\n"
            f"User ID: `{user_id}`\n"
            f"Status: {ban_status}\n\n"
        )
        
        if is_banned:
            user_data = stats_manager.user_stats.get(str(user_id), {})
            ban_reason = user_data.get('ban_reason', 'Unknown')
            ban_date = user_data.get('ban_date', 'Unknown')
            
            if ban_date != 'Unknown':
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(ban_date)
                    ban_date = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            user_text += (
                f"⚠️ **Ban Info:**\n"
                f"📝 Reason: {ban_reason}\n"
                f"📅 Date: {ban_date}\n\n"
            )
        
        user_text += (
            f"📊 **Build Statistics:**\n"
            f"  • Total Builds: **{total_builds}**\n"
            f"  • Quick Builds: **{quick_builds}**\n"
            f"  • Custom Builds: **{custom_builds}**\n"
            f"  • Failed Builds: **{failed_builds}**\n"
            f"  • Success Rate: **{success_rate:.1f}%**\n\n"
            f"⏱️ **Time Statistics:**\n"
            f"  • Avg Build Time: **{avg_time}s**\n"
            f"  • Total Time: **{total_time}**\n\n"
            f"📅 **Activity:**\n"
            f"  • Last Active: **{last_active}**\n"
        )
        
        if first_build:
            user_text += f"  • First Build: {first_build[:10]}\n"
        if last_build:
            user_text += f"  • Last Build: {last_build[:10]}\n"
        
        if is_banned:
            buttons = [
                [Button.inline("🔓 Unban User", data=f"admin:user:unban:{user_id}")],
                [Button.inline("« Back to Users", data="admin:users")]
            ]
        else:
            buttons = [
                [Button.inline("🚫 Ban User", data=f"admin:user:confirmban:{user_id}")],
                [Button.inline("« Back to Users", data="admin:users")]
            ]
        
        await event.edit(user_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing user view: {str(e)}")
        await event.answer("❌ Error loading user details", alert=True)


async def handle_admin_user_ban_confirm(event, user_id):
    """Confirm user ban"""
    try:
        user_details = stats_manager.get_user_details(user_id)
        
        if not user_details:
            await event.answer("❌ User not found!", alert=True)
            return
        
        username = user_details.get('username', 'Unknown')
        total_builds = user_details.get('total_builds', 0)
        
        confirm_text = (
            f"🚫 **Confirm Ban**\n\n"
            f"Are you sure you want to BAN?\n\n"
            f"👤 @{username}\n"
            f"🆔 ID: `{user_id}`\n"
            f"📊 Total Builds: {total_builds}\n\n"
            f"⚠️ **User will not be able to:**\n"
            f"  • Build APKs\n"
            f"  • Access bot features\n\n"
            f"Select reason:"
        )
        
        buttons = [
            [Button.inline("Spam", data=f"admin:user:ban:{user_id}:Spam")],
            [Button.inline("Abuse", data=f"admin:user:ban:{user_id}:Abuse")],
            [Button.inline("Violation", data=f"admin:user:ban:{user_id}:Violation")],
            [Button.inline("Other", data=f"admin:user:ban:{user_id}:Other")],
            [Button.inline("❌ Cancel", data=f"admin:user:view:{user_id}")]
        ]
        
        await event.edit(confirm_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing ban confirm: {str(e)}")
        await event.answer("❌ Error", alert=True)


async def handle_admin_user_ban(event, user_id, reason):
    """Ban user"""
    try:
        user_details = stats_manager.get_user_details(user_id)
        
        if not user_details:
            await event.answer("❌ User not found!", alert=True)
            return
        
        username = user_details.get('username', 'Unknown')
        
        success, msg = stats_manager.ban_user(user_id, reason)
        
        if success:
            await event.answer(f"✅ @{username} has been banned", alert=True)
            
            await event.edit(
                f"🚫 **User Banned**\n\n"
                f"@{username} has been banned successfully!\n\n"
                f"📝 Reason: {reason}\n"
                f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
                f"User can no longer access the bot.",
                buttons=[
                    [Button.inline("🔓 Unban", data=f"admin:user:unban:{user_id}")],
                    [Button.inline("« Back to Users", data="admin:users")]
                ]
            )
        else:
            await event.answer(f"❌ {msg}", alert=True)
        
    except Exception as e:
        logger.error(f"Error banning user: {str(e)}")
        await event.answer("❌ Error banning user", alert=True)


async def handle_admin_user_unban(event, user_id):
    """Unban user"""
    try:
        user_details = stats_manager.get_user_details(user_id)
        
        if not user_details:
            await event.answer("❌ User not found!", alert=True)
            return
        
        username = user_details.get('username', 'Unknown')
        
        success, msg = stats_manager.unban_user(user_id)
        
        if success:
            await event.answer(f"✅ @{username} has been unbanned", alert=True)
            
            await handle_admin_user_view(event, user_id)
        else:
            await event.answer(f"❌ {msg}", alert=True)
        
    except Exception as e:
        logger.error(f"Error unbanning user: {str(e)}")
        await event.answer("❌ Error unbanning user", alert=True)


async def handle_broadcast(event, admin_ids, bot):
    """Send broadcast message"""
    user_id = event.sender_id
    
    if not is_admin(user_id, admin_ids):
        await event.reply("⛔ Access Denied")
        return
    
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
    
    await msg.edit(
        f"✅ **Broadcast Complete!**\n\n"
        f"Total: **{total_users}**\n"
        f"✅ Success: **{success_count}**\n"
        f"❌ Failed: **{failed_count}**"
    )
