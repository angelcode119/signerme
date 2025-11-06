import requests
import logging
from .config import API_BASE_URL

logger = logging.getLogger(__name__)


def check_admin_status(username):
    """
    Check if user is still admin (not disabled)
    
    Returns:
        (is_admin: bool, message: str)
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/bot/check-admin",
            params={"username": username},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            is_admin = data.get('is_admin', False)
            
            if is_admin:
                return True, "Admin active"
            else:
                return False, "Account disabled by admin"
        
        elif response.status_code == 404:
            return False, "User not found"
        
        else:
            logger.warning(f"Admin check returned {response.status_code}")
            # در صورت خطا، به کاربر اجازه بده (fail-safe)
            return True, "Could not verify, allowing access"
        
    except requests.exceptions.Timeout:
        logger.warning("Admin check timeout")
        # Timeout → اجازه بده
        return True, "Timeout, allowing access"
    
    except Exception as e:
        logger.error(f"Admin check error: {str(e)}")
        # Error → اجازه بده
        return True, f"Error: {str(e)}"


async def periodic_admin_check(user_manager, check_interval=300):
    """
    Periodically check all authenticated users
    
    check_interval: seconds between checks (default 5 min)
    """
    import asyncio
    
    while True:
        try:
            await asyncio.sleep(check_interval)
            
            # Check all authenticated users
            for user_id_str, user_data in list(user_manager.users.items()):
                username = user_data.get('username')
                
                if not username:
                    continue
                
                is_admin, msg = check_admin_status(username)
                
                if not is_admin:
                    # Remove user from authenticated list
                    user_manager.users.pop(user_id_str, None)
                    user_manager.save_users()
                    logger.warning(f"User {username} ({user_id_str}) disabled: {msg}")
                
        except Exception as e:
            logger.error(f"Periodic admin check error: {str(e)}")
