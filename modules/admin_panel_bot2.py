from telethon import events, Button
import logging
from .stats_manager import stats_manager
from .queue_manager import build_queue

logger = logging.getLogger(__name__)


def is_admin(user_id, admin_ids):
    try:
        return user_id in admin_ids
    except Exception as e:
        logger.error(f"Admin check error: {str(e)}")
        return False


async def handle_admin_command(event, admin_ids):
    try:
        user_id = event.sender_id
        
        if not is_admin(user_id, admin_ids):
            await event.reply("⛔ Access Denied")
            return
        
        await event.reply(
            "🎯 **Payload Injector - Admin Panel**\n\n"
            "Welcome to the admin dashboard!\n"
            "Select an option below:"
        )
        
        buttons = [
            [Button.inline("📊 Statistics", data="admin:stats")],
            [Button.inline("👥 Users Management", data="admin:users")],
            [Button.inline("🔄 Queue Status", data="admin:queue")]
        ]
        
        try:
            await event.reply("🎯 **Admin Panel**", buttons=buttons)
        except Exception as e:
            logger.error(f"Error sending admin panel: {str(e)}")
            await event.reply("❌ Error opening admin panel")
    
    except Exception as e:
        logger.error(f"Admin command error: {str(e)}", exc_info=True)


async def handle_admin_callback(event, bot, admin_ids):
    try:
        user_id = event.sender_id
        
        if not is_admin(user_id, admin_ids):
            await event.answer("⛔ Access Denied", alert=True)
            return
        
        data = event.data.decode('utf-8')
        
        if data == "admin:menu":
            await handle_admin_menu(event)
        
        elif data == "admin:stats":
            await handle_admin_stats(event)
        
        elif data == "admin:users":
            await handle_admin_users(event, filter_type='all')
        
        elif data.startswith("admin:users:"):
            filter_type = data.split(":")[-1]
            await handle_admin_users(event, filter_type)
        
        elif data == "admin:queue":
            await handle_admin_queue(event)
        
        elif data.startswith("user_page:"):
            parts = data.split(":")
            user_id_target = int(parts[1])
            await handle_user_details(event, user_id_target)
        
        elif data.startswith("ban:"):
            user_id_to_ban = int(data.split(":")[1])
            await handle_ban_user(event, user_id_to_ban)
        
        elif data.startswith("unban:"):
            user_id_to_unban = int(data.split(":")[1])
            await handle_unban_user(event, user_id_to_unban)
    
    except Exception as e:
        logger.error(f"Admin callback error: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error", alert=True)
        except:
            pass


async def handle_admin_menu(event):
    try:
        buttons = [
            [Button.inline("📊 Statistics", data="admin:stats")],
            [Button.inline("👥 Users Management", data="admin:users")],
            [Button.inline("🔄 Queue Status", data="admin:queue")]
        ]
        
        await event.edit("🎯 **Admin Panel**\n\nSelect an option:", buttons=buttons)
    
    except Exception as e:
        logger.error(f"Admin menu error: {str(e)}")


async def handle_admin_stats(event):
    try:
        stats = stats_manager.get_total_stats()
        builds_by_day = stats_manager.get_builds_by_day(days=7)
        top_users = stats_manager.get_top_users(limit=5)
        
        stats_text = (
            f"📊 **System Statistics**\n\n"
            f"👥 **Users:**\n"
            f"Total: **{stats.get('total_users', 0)}**\n"
            f"Active (7d): **{stats.get('active_users_7d', 0)}**\n"
            f"New (7d): **{stats.get('new_users_7d', 0)}**\n\n"
            f"🔨 **Injections:**\n"
            f"Total: **{stats.get('total_builds', 0)}**\n"
            f"Success Rate: **{stats.get('success_rate', 0)}%**\n"
            f"Today: **{builds_by_day.get('today', 0)}**\n"
            f"Yesterday: **{builds_by_day.get('yesterday', 0)}**\n\n"
            f"🕐 Uptime: **{stats.get('uptime', 'N/A')}**"
        )
        
        buttons = [
            [Button.inline("« Back to Menu", data="admin:menu")]
        ]
        
        try:
            await event.edit(stats_text, buttons=buttons)
        
        except Exception as e:
            if 'MessageNotModifiedError' not in str(e):
                logger.error(f"Stats display error: {str(e)}")
    
    except Exception as e:
        logger.error(f"Admin stats error: {str(e)}", exc_info=True)


async def handle_admin_users(event, filter_type='all'):
    try:
        users = stats_manager.get_all_users(filter_type='all')
        total_users = len(users)
        banned_count = len([u for u in users if stats_manager.is_user_banned(u['user_id'])])
        
        users_text = (
            f"👥 **User Management**\n\n"
            f"Total Users: **{total_users}**\n"
            f"Banned: **{banned_count}**\n\n"
            f"Filter: **{filter_type.title()}**"
        )
        
        buttons = [
            [
                Button.inline("🟢 Online", data="admin:users:online"),
                Button.inline("🆕 New", data="admin:users:new")
            ],
            [
                Button.inline("📈 Most Active", data="admin:users:active"),
                Button.inline("🚫 Banned", data="admin:users:banned")
            ],
            [Button.inline("« Back to Menu", data="admin:menu")]
        ]
        
        try:
            await event.edit(users_text, buttons=buttons)
        except Exception as e:
            if 'MessageNotModifiedError' in str(e) or 'not modified' in str(e).lower():
                await event.answer("✅ Already showing this view")
            else:
                logger.error(f"Users display error: {str(e)}")
    
    except Exception as e:
        logger.error(f"Admin users error: {str(e)}", exc_info=True)


async def handle_admin_queue(event):
    try:
        active = 0
        waiting = build_queue.queue.qsize() if hasattr(build_queue, 'queue') else 0
        
        active_users = []
        for user_id_str, start_time in list(build_queue.building_users.items()):
            if start_time:
                user_id = int(user_id_str)
                elapsed = build_queue.get_user_elapsed_time(user_id)
                active += 1
                user_details = stats_manager.get_user_details(user_id)
                username = user_details.get('username', 'Unknown') if user_details else 'Unknown'
                active_users.append({
                    'user_id': user_id,
                    'username': username,
                    'elapsed': elapsed
                })
        
        queue_text = (
            f"🔄 **Queue Status** (Live)\n\n"
            f"⚡ Active: **{active}/1** (only one user at a time)\n"
            f"⏳ Waiting: **{waiting}** users in queue\n\n"
        )
        
        if active_users:
            queue_text += "**Active Injections:**\n"
            for i, user_info in enumerate(active_users, 1):
                username = user_info['username']
                elapsed = user_info['elapsed']
                
                queue_text += f"`{i}.` @{username}\n   ⏱️ {elapsed}s elapsed\n\n"
        else:
            queue_text += "✅ No active injections"
        
        buttons = [
            [Button.inline("« Back to Menu", data="admin:menu")]
        ]
        
        try:
            await event.edit(queue_text, buttons=buttons)
        
        except Exception as e:
            if 'MessageNotModifiedError' not in str(e):
                logger.error(f"Queue display error: {str(e)}")
    
    except Exception as e:
        logger.error(f"Admin queue error: {str(e)}", exc_info=True)


async def handle_user_details(event, user_id):
    try:
        user_details = stats_manager.get_user_details(user_id)
        
        if not user_details:
            await event.answer("❌ User not found", alert=True)
            return
        
        username = user_details.get('username', 'Unknown')
        is_banned = stats_manager.is_user_banned(user_id)
        
        details_text = (
            f"👤 **User Details**\n\n"
            f"Username: @{username}\n"
            f"User ID: `{user_id}`\n"
            f"Status: {'🚫 Banned' if is_banned else '✅ Active'}\n\n"
            f"📊 **Statistics:**\n"
            f"Total Injections: **{user_details.get('total_builds', 0)}**\n"
            f"Successful: **{user_details.get('successful_builds', 0)}**\n"
            f"Failed: **{user_details.get('failed_builds', 0)}**\n"
            f"Success Rate: **{user_details.get('success_rate', 0)}%**"
        )
        
        if is_banned:
            buttons = [
                [Button.inline("✅ Unban User", data=f"unban:{user_id}")],
                [Button.inline("« Back", data="admin:users")]
            ]
        else:
            buttons = [
                [Button.inline("🚫 Ban User", data=f"ban:{user_id}")],
                [Button.inline("« Back", data="admin:users")]
            ]
        
        try:
            await event.edit(details_text, buttons=buttons)
        except Exception as e:
            logger.error(f"User details display error: {str(e)}")
    
    except Exception as e:
        logger.error(f"User details error: {str(e)}", exc_info=True)


async def handle_ban_user(event, user_id):
    try:
        success, msg = stats_manager.ban_user(user_id, reason="Banned by admin")
        
        if success:
            await event.answer("✅ User banned successfully", alert=True)
            await handle_user_details(event, user_id)
        else:
            await event.answer(f"❌ {msg}", alert=True)
    
    except Exception as e:
        logger.error(f"Error banning user: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error", alert=True)
        except:
            pass


async def handle_unban_user(event, user_id):
    try:
        success, msg = stats_manager.unban_user(user_id)
        
        if success:
            await event.answer("✅ User unbanned successfully", alert=True)
            await handle_user_details(event, user_id)
        else:
            await event.answer(f"❌ {msg}", alert=True)
    
    except Exception as e:
        logger.error(f"Error unbanning user: {str(e)}", exc_info=True)
        try:
            await event.answer("❌ Error", alert=True)
        except:
            pass


async def handle_broadcast(event, admin_ids, bot):
    try:
        user_id = event.sender_id
        
        if not is_admin(user_id, admin_ids):
            await event.reply("⛔ Access Denied")
            return
        
        text = event.message.message.strip()
        message_text = text.replace('/broadcast', '').strip()

        if not message_text:
            await event.reply(
                "❌ **Invalid Format**\n\n"
                "Usage: `/broadcast your message here`"
            )
            return

        from modules.auth import UserManager
        user_manager = UserManager()
        users = user_manager.users
        
        sent = 0
        failed = 0
        
        status_msg = await event.reply(f"📤 Broadcasting to {len(users)} users...")
        
        for user_id_str in users.keys():
            try:
                target_user_id = int(user_id_str)
                await bot.send_message(target_user_id, message_text)
                sent += 1
            except Exception as e:
                failed += 1
                logger.debug(f"Failed to send to {user_id_str}: {str(e)}")
        
        await status_msg.edit(
            f"✅ **Broadcast Complete**\n\n"
            f"📤 Sent: {sent}\n"
            f"❌ Failed: {failed}\n"
            f"📊 Total: {len(users)}"
        )
    
    except Exception as e:
        logger.error(f"Broadcast error: {str(e)}", exc_info=True)
        await event.reply("❌ Broadcast failed")
