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
    try:
        return user_id in admin_ids
    except Exception as e:
        logger.error(f"Error checking admin status: {str(e)}")
        return False


async def handle_admin_command(event, admin_ids):
    """Handler for /admin command"""
    try:
        user_id = event.sender_id
        
        if not is_admin(user_id, admin_ids):
            await event.reply("⛔ **Access Denied**\n\nYou don't have permission to access admin panel.")
            return
        
        await show_admin_menu(event)
    except Exception as e:
        logger.error(f"Error in handle_admin_command: {str(e)}", exc_info=True)
        try:
            await event.reply("❌ Error loading admin panel. Please try again.")
        except:
            pass


async def show_admin_menu(event):
    """Show admin panel main menu"""
    try:
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
    except Exception as e:
        logger.error(f"Error showing admin menu: {str(e)}", exc_info=True)
        try:
            await event.reply("❌ Error displaying menu. Please try /admin again.")
        except:
            pass


async def handle_admin_stats(event):
    """Show general statistics"""
    try:
        await event.answer("⏳ Loading statistics...", alert=False)
        
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
        logger.error(f"Error showing admin stats: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error loading statistics", alert=True)
        except:
            pass


async def handle_admin_users(event):
    """Show user management"""
    try:
        await event.answer("⏳ Loading users...", alert=False)
        
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
        logger.error(f"Error showing admin users: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error loading users", alert=True)
        except:
            pass


async def handle_admin_users_filter(event, filter_type):
    """Show users with filter"""
    try:
        await event.answer("⏳ Loading filtered users...", alert=False)
        
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
                        f"   📝 Reason: {reason}\n\n"
                    )
                
                if total_users > 15:
                    users_text += f"\n_... and {total_users - 15} more_"
            
            buttons = []
            for i, user in enumerate(banned_users[:5], 1):
                username = user.get('username', 'Unknown')
                user_id = user.get('user_id')
                buttons.append([Button.inline(f"🔓 Unban @{username}", data=f"unban:{user_id}")])
            
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
                buttons.append([Button.inline(f"👤 @{username}", data=f"user_page:{user_id}")])
            
            buttons.extend([
                [Button.inline("🔙 All Users", data="admin:users")],
                [Button.inline("« Back to Menu", data="admin:menu")]
            ])
        
        await event.edit(users_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing filtered users: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error loading users", alert=True)
        except:
            pass


async def handle_admin_apks(event):
    """Show APK management"""
    try:
        await event.answer("⏳ Loading APKs...", alert=False)
        
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
                    f"   💾 {size} MB | 🔨 {builds} builds\n\n"
                )
            
            if total_apks > 10:
                apks_text += f"_... and {total_apks - 10} more APKs_\n\n"
        
        buttons = []
        for i, apk in enumerate(apks[:5], 1):
            filename = apk.get('filename', '')
            display_name = apk.get('display_name', 'Unknown')
            buttons.append([Button.inline(f"📱 {display_name}", data=f"apk:{filename}")])
        
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
        logger.error(f"Error showing admin APKs: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error loading APKs", alert=True)
        except:
            pass


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
            "• Max size: 100 MB\n"
            "• Valid Android app\n\n"
            "Send the APK file now..."
        )
        
        buttons = [
            [Button.inline("❌ Cancel Upload", data="admin:apks:cancelupload")]
        ]
        
        await event.edit(upload_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error starting APK upload: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error", alert=True)
        except:
            pass


async def handle_admin_apks_cancel_upload(event):
    """Cancel APK upload"""
    try:
        user_id = event.sender_id
        
        if user_id in admin_upload_state:
            del admin_upload_state[user_id]
        
        await event.answer("❌ Upload cancelled", alert=True)
        await handle_admin_apks(event)
    except Exception as e:
        logger.error(f"Error cancelling upload: {str(e)}", exc_info=True)


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
                "Please send an APK file (.apk)"
            )
            return True
        
        file_size = event.message.document.size
        max_size = 100 * 1024 * 1024
        
        if file_size > max_size:
            await event.reply(
                f"❌ **File Too Large**\n\n"
                f"📦 Your file: {file_size / (1024*1024):.1f} MB\n"
                f"📏 Maximum: 100 MB"
            )
            return True
        
        msg = await event.reply(
            f"📥 **Downloading APK...**\n\n"
            f"📄 {file_name or 'Unknown'}\n"
            f"💾 Size: {file_size / (1024*1024):.1f} MB"
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
        
        await download_file(
            client=bot,
            location=event.message.document,
            file=str(apk_path)
        )
        
        if not apk_path.exists():
            await msg.edit("❌ **Download failed**")
            if user_id in admin_upload_state:
                del admin_upload_state[user_id]
            return True
        
        # Analyze APK
        from .apk_analyzer import APKAnalyzer
        import tempfile
        
        try:
            analyzer = APKAnalyzer(str(apk_path))
            analyze_dir = tempfile.mkdtemp(prefix='admin_analyze_')
            
            results = await analyzer.analyze(analyze_dir)
            
            app_name = results.get('app_name') or safe_filename.replace('.apk', '')
            
            import shutil
            try:
                shutil.rmtree(analyze_dir)
            except:
                pass
            
        except Exception as e:
            logger.warning(f"APK analysis failed: {str(e)}")
            app_name = safe_filename.replace('.apk', '')
        
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
                f"📄 **File**: `{safe_filename}`\n"
                f"💾 **Size**: {apk_path.stat().st_size / (1024*1024):.1f} MB"
            )
        else:
            await msg.edit(f"❌ **Failed to add APK**\n\n{result_msg}")
            if user_id in admin_upload_state:
                del admin_upload_state[user_id]
        
        return True
        
    except Exception as e:
        logger.error(f"Error receiving APK file: {str(e)}", exc_info=True)
        try:
            await event.reply("❌ **Upload failed**\n\nPlease try again.")
        except:
            pass
        
        if user_id in admin_upload_state:
            del admin_upload_state[user_id]
        
        return True


async def handle_admin_apks_scan(event):
    """Scan for new APKs"""
    try:
        await event.answer("🔍 Scanning...", alert=False)
        
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
            else:
                skipped_count += 1
        
        result_text = (
            f"✅ **Scan Complete**\n\n"
            f"➕ Added: **{added_count}** APKs\n"
            f"⏭️ Skipped: **{skipped_count}** APKs"
        )
        
        buttons = [
            [Button.inline("« Back to APKs", data="admin:apks")],
            [Button.inline("« Back to Menu", data="admin:menu")]
        ]
        
        await event.edit(result_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error scanning APKs: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error scanning", alert=True)
        except:
            pass


async def handle_admin_queue(event):
    """Show queue status"""
    try:
        await event.answer("⏳ Loading...", alert=False)
        
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
            queue_text += "✅ No active builds"
        
        buttons = [
            [Button.inline("🔄 Refresh", data="admin:queue")],
            [Button.inline("« Back to Menu", data="admin:menu")]
        ]
        
        await event.edit(queue_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing queue: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error", alert=True)
        except:
            pass


async def handle_admin_callback(event, bot, admin_ids):
    """Handler for admin panel callbacks - with comprehensive error handling"""
    try:
        user_id = event.sender_id
        
        if not is_admin(user_id, admin_ids):
            await event.answer("⛔ Access Denied", alert=True)
            return
        
        data = event.data.decode('utf-8')
        logger.debug(f"Admin callback: {data}")
        
        # Route to appropriate handler
        if data == "admin:menu":
            await show_admin_menu(event)
        elif data == "admin:stats":
            await handle_admin_stats(event)
        elif data == "admin:users":
            await handle_admin_users(event)
        elif data.startswith("admin:users:"):
            filter_type = data.split(":")[-1]
            await handle_admin_users_filter(event, filter_type)
        elif data == "admin:apks":
            await handle_admin_apks(event)
        elif data == "admin:apks:upload":
            await handle_admin_apks_upload(event)
        elif data == "admin:apks:cancelupload":
            await handle_admin_apks_cancel_upload(event)
        elif data == "admin:apks:scan":
            await handle_admin_apks_scan(event)
        elif data == "admin:queue":
            await handle_admin_queue(event)
        elif data.startswith("apk:"):
            filename = data.replace("apk:", "")
            await handle_admin_apk_view(event, filename)
        elif data.startswith("user_page:"):
            user_id_str = data.replace("user_page:", "")
            await handle_admin_user_view(event, user_id_str)
        elif data.startswith("ban:"):
            parts = data.split(":")
            if len(parts) >= 3:
                target_user_id = parts[1]
                reason = parts[2] if len(parts) > 2 else "No reason"
                await handle_admin_user_ban(event, target_user_id, reason)
        elif data.startswith("unban:"):
            target_user_id = data.replace("unban:", "")
            await handle_admin_user_unban(event, target_user_id)
        elif data.startswith("apk_page:"):
            filename = data.replace("apk_page:", "")
            await handle_admin_apk_view(event, filename)
        else:
            logger.warning(f"Unknown admin callback: {data}")
            await event.answer("⚠️ Unknown action", alert=True)
    
    except Exception as e:
        logger.error(f"Error in admin callback handler: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ An error occurred. Please try again.", alert=True)
        except:
            pass


async def handle_admin_apk_view(event, filename):
    """Show APK details"""
    try:
        apk_info = apk_manager.get_apk_info(filename)
        
        if not apk_info:
            await event.answer("❌ APK not found!", alert=True)
            return
        
        display_name = apk_info.get('display_name', 'Unknown')
        size_mb = apk_info.get('size_mb', 0)
        total_builds = apk_info.get('total_builds', 0)
        enabled = apk_info.get('enabled', True)
        
        status = "✅ Enabled" if enabled else "❌ Disabled"
        
        apk_text = (
            f"📦 **APK Details**\n\n"
            f"📱 **Name**: {display_name}\n"
            f"📄 **File**: `{filename}`\n"
            f"💾 **Size**: {size_mb} MB\n"
            f"🔨 **Builds**: {total_builds}\n"
            f"🔘 **Status**: {status}"
        )
        
        buttons = [
            [Button.inline("🔄 Toggle Status", data=f"apk:toggle:{filename}")],
            [Button.inline("🗑️ Delete", data=f"apk:delete:{filename}")],
            [Button.inline("« Back", data="admin:apks")]
        ]
        
        await event.edit(apk_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing APK view: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error", alert=True)
        except:
            pass


async def handle_admin_user_view(event, user_id):
    """Show user details"""
    try:
        user_details = stats_manager.get_user_details(user_id)
        
        if not user_details:
            await event.answer("❌ User not found!", alert=True)
            return
        
        username = user_details.get('username', 'Unknown')
        total_builds = user_details.get('total_builds', 0)
        is_banned = stats_manager.is_user_banned(user_id)
        
        user_text = (
            f"👤 **User Details**\n\n"
            f"Username: @{username}\n"
            f"User ID: `{user_id}`\n"
            f"Status: {'🚫 Banned' if is_banned else '✅ Active'}\n"
            f"Total Builds: **{total_builds}**"
        )
        
        buttons = [
            [Button.inline("🚫 Ban" if not is_banned else "🔓 Unban",
                          data=f"ban:{user_id}:Abuse" if not is_banned else f"unban:{user_id}")],
            [Button.inline("« Back", data="admin:users")]
        ]
        
        await event.edit(user_text, buttons=buttons)
        
    except Exception as e:
        logger.error(f"Error showing user view: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error", alert=True)
        except:
            pass


async def handle_admin_user_ban(event, user_id, reason):
    """Ban user"""
    try:
        success, msg = stats_manager.ban_user(user_id, reason)
        
        if success:
            await event.answer(f"✅ User banned", alert=True)
            await handle_admin_users(event)
        else:
            await event.answer(f"❌ {msg}", alert=True)
    
    except Exception as e:
        logger.error(f"Error banning user: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error", alert=True)
        except:
            pass


async def handle_admin_user_unban(event, user_id):
    """Unban user"""
    try:
        success, msg = stats_manager.unban_user(user_id)
        
        if success:
            await event.answer(f"✅ User unbanned", alert=True)
            await handle_admin_users(event)
        else:
            await event.answer(f"❌ {msg}", alert=True)
    
    except Exception as e:
        logger.error(f"Error unbanning user: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error", alert=True)
        except:
            pass


async def handle_broadcast(event, admin_ids, bot):
    """Send broadcast message"""
    try:
        user_id = event.sender_id
        
        if not is_admin(user_id, admin_ids):
            await event.reply("⛔ Access Denied")
            return
        
        text = event.message.message.strip()
        message_text = text.replace('/broadcast', '').strip()
        
        if not message_text:
            await event.reply(
                "📢 **Broadcast Message**\n\n"
                "Usage: `/broadcast <message>`"
            )
            return
        
        users = stats_manager.get_all_users()
        total_users = len(users)
        
        msg = await event.reply(
            f"📤 **Broadcasting...**\n\n"
            f"Total: **{total_users}**"
        )
        
        success_count = 0
        failed_count = 0
        
        for i, user in enumerate(users, 1):
            try:
                await bot.send_message(
                    int(user['user_id']),
                    f"📢 **Announcement**\n\n{message_text}"
                )
                success_count += 1
            except:
                failed_count += 1
            
            if i % 10 == 0:
                try:
                    await msg.edit(
                        f"📤 **Broadcasting...**\n\n"
                        f"Progress: **{i}/{total_users}**\n"
                        f"✅ Sent: {success_count} | ❌ Failed: {failed_count}"
                    )
                except:
                    pass
        
        await msg.edit(
            f"✅ **Broadcast Complete!**\n\n"
            f"✅ Success: **{success_count}**\n"
            f"❌ Failed: **{failed_count}**"
        )
        
    except Exception as e:
        logger.error(f"Error in broadcast: {str(e)}", exc_info=True)
        try:
            await event.reply("❌ Broadcast failed")
        except:
            pass
