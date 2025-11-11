import aiohttp
import asyncio
import logging
from .config import API_BASE_URL

logger = logging.getLogger(__name__)


async def check_admin_status(service_token):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}/bot/auth/check",
                headers={"Authorization": f"Bearer {service_token}"},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    is_active = data.get('active', False)
                    device_token = data.get('device_token')
                    message = data.get('message', 'Unknown')

                    if is_active:
                        return True, "Admin active", device_token
                    else:
                        return False, "Account disabled by admin", None

                elif response.status == 401:
                    return False, "Invalid token", None

                else:
                    logger.warning(f"Admin check returned {response.status}")
                    return True, "Could not verify, allowing access", None

    except asyncio.TimeoutError:
        logger.warning("Admin check timeout")
        return True, "Timeout, allowing access", None

    except Exception as e:
        logger.error(f"Admin check error: {str(e)}")
        return True, f"Error: {str(e)}", None


async def periodic_admin_check(user_manager, check_interval=300):
    import asyncio

    while True:
        try:
            await asyncio.sleep(check_interval)

            for user_id_str, user_data in list(user_manager.users.items()):
                username = user_data.get('username')

                if not username:
                    continue

                is_admin, msg, _ = await check_admin_status(username)

                if not is_admin:
                    user_manager.users.pop(user_id_str, None)
                    user_manager.save_users()
                    logger.warning(f"User {username} ({user_id_str}) disabled: {msg}")

        except Exception as e:
            logger.error(f"Periodic admin check error: {str(e)}")
