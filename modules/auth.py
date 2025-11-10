import json
import requests
from pathlib import Path
from .config import API_BASE_URL, BOT_IDENTIFIER, USERS_FILE


class UserManager:
    def __init__(self, users_file=None):
        self.users_file = Path(users_file) if users_file else USERS_FILE
        self.users = self.load_users()
        self.waiting_otp = {}

    def load_users(self):
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}

    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)

    def is_authenticated(self, user_id):
        return str(user_id) in self.users and self.users[str(user_id)].get('token')

    def get_token(self, user_id):
        return self.users.get(str(user_id), {}).get('token')

    def save_user(self, user_id, username, token):
        user_id_str = str(user_id)
        
        replaced_session = False
        for uid, data in list(self.users.items()):
            if data.get('username') == username and uid != user_id_str:
                del self.users[uid]
                replaced_session = True
        
        self.users[user_id_str] = {'username': username, 'token': token}
        self.save_users()
        
        return replaced_session
    
    def get_username(self, user_id):
        return self.users.get(str(user_id), {}).get('username')
    
    def logout_user(self, user_id):
        """Logout user (delete from users)"""
        user_id_str = str(user_id)
        if user_id_str in self.users:
            del self.users[user_id_str]
            self.save_users()
            return True
        return False


def request_otp(username):
    try:
        response = requests.post(
            f"{API_BASE_URL}/bot/auth/request-otp",
            json={"username": username, "bot_identifier": BOT_IDENTIFIER}
        )
        if response.status_code == 200:
            return True, "OTP sent to your Telegram"
        elif response.status_code == 404:
            return False, "User not found"
        elif response.status_code == 403:
            return False, "Account disabled"
        return False, f"Error {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def verify_otp(username, otp_code):
    try:
        response = requests.post(
            f"{API_BASE_URL}/bot/auth/verify-otp",
            json={"username": username, "otp_code": otp_code, "bot_identifier": BOT_IDENTIFIER}
        )
        if response.status_code == 200:
            data = response.json()
            return True, data.get('service_token'), "Authentication successful!"
        elif response.status_code == 401:
            return False, None, "Invalid or expired OTP"
        elif response.status_code == 403:
            return False, None, "Account disabled"
        return False, None, f"Error {response.status_code}"
    except Exception as e:
        return False, None, f"Error: {str(e)}"


def get_device_token(service_token):
    try:
        response = requests.get(
            f"{API_BASE_URL}/bot/auth/check",
            headers={"Authorization": f"Bearer {service_token}"}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('device_token')
        return None
    except:
        return None
