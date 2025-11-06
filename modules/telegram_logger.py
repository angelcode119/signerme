import logging
import asyncio
from datetime import datetime
from telethon import TelegramClient

logger = logging.getLogger(__name__)


class TelegramLogHandler:
    """Send important logs to Telegram channel"""
    
    def __init__(self, bot_client, log_channel_id=None):
        self.bot = bot_client
        self.log_channel_id = log_channel_id
        self.queue = asyncio.Queue()
        self.enabled = log_channel_id is not None
        
    async def log_event(self, event_type, user_id, username, details):
        """
        Log an event to Telegram channel
        
        event_type: 'build_start', 'build_success', 'build_fail', 'auth', etc.
        user_id: Telegram user ID
        username: Auth username
        details: Dict with additional info
        """
        if not self.enabled:
            return
        
        try:
            # Format message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if event_type == 'build_start':
                emoji = "🚀"
                title = "Build Started"
                message = (
                    f"{emoji} **{title}**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"👤 **User:** `{user_id}`\n"
                    f"📝 **Username:** {username or 'Unknown'}\n"
                    f"📱 **App:** {details.get('app_name', 'Unknown')}\n"
                    f"📦 **Package:** `{details.get('package', 'Unknown')}`\n"
                    f"💾 **Size:** {details.get('size', 'Unknown')}\n"
                    f"🤖 **Bot:** {details.get('bot', 'Unknown')}\n\n"
                    f"⏰ **Time:** {timestamp}"
                )
            
            elif event_type == 'build_success':
                emoji = "✅"
                title = "Build Successful"
                duration = details.get('duration', 0)
                message = (
                    f"{emoji} **{title}**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"👤 **User:** `{user_id}`\n"
                    f"📝 **Username:** {username or 'Unknown'}\n"
                    f"📱 **App:** {details.get('app_name', 'Unknown')}\n"
                    f"⏱️ **Duration:** {duration}s\n"
                    f"📦 **Output:** {details.get('output_size', 'Unknown')}\n"
                    f"🤖 **Bot:** {details.get('bot', 'Unknown')}\n\n"
                    f"⏰ **Time:** {timestamp}"
                )
            
            elif event_type == 'build_fail':
                emoji = "❌"
                title = "Build Failed"
                message = (
                    f"{emoji} **{title}**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"👤 **User:** `{user_id}`\n"
                    f"📝 **Username:** {username or 'Unknown'}\n"
                    f"📱 **App:** {details.get('app_name', 'Unknown')}\n"
                    f"⚠️ **Error:** {details.get('error', 'Unknown')}\n"
                    f"🤖 **Bot:** {details.get('bot', 'Unknown')}\n\n"
                    f"⏰ **Time:** {timestamp}"
                )
            
            elif event_type == 'auth':
                emoji = "🔐"
                title = "New Authentication"
                message = (
                    f"{emoji} **{title}**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"👤 **User:** `{user_id}`\n"
                    f"📝 **Username:** {username}\n"
                    f"🤖 **Bot:** {details.get('bot', 'Unknown')}\n\n"
                    f"⏰ **Time:** {timestamp}"
                )
            
            else:
                # Generic event
                message = (
                    f"📊 **{event_type}**\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"👤 **User:** `{user_id}`\n"
                    f"📝 **Username:** {username or 'Unknown'}\n"
                    f"📋 **Details:** {details}\n\n"
                    f"⏰ **Time:** {timestamp}"
                )
            
            # Send to channel
            await self.bot.send_message(self.log_channel_id, message)
            logger.debug(f"Log sent to channel: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to send log to channel: {str(e)}")
    
    async def log_admin_check(self, username, is_admin):
        """Log admin status check"""
        if not self.enabled:
            return
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if is_admin:
                emoji = "✅"
                status = "Active"
            else:
                emoji = "⚠️"
                status = "Disabled"
            
            message = (
                f"{emoji} **Admin Status Check**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📝 **Username:** {username}\n"
                f"🔒 **Status:** {status}\n\n"
                f"⏰ **Time:** {timestamp}"
            )
            
            await self.bot.send_message(self.log_channel_id, message)
            
        except Exception as e:
            logger.error(f"Failed to send admin check log: {str(e)}")
