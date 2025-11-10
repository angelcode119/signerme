import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class StatsManager:
    def __init__(self):
        self.logs_dir = Path("logs/builds")
        self.stats_file = Path("data/stats.json")
        self.user_stats_file = Path("data/user_stats.json")
        
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._load_stats()
        self._load_user_stats()
    
    def _load_stats(self):
        """بارگذاری آمار کلی"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                'total_builds': 0,
                'total_users': 0,
                'start_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            self._save_stats()
    
    def _save_stats(self):
        """ذخیره آمار کلی"""
        self.stats['last_updated'] = datetime.now().isoformat()
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
    
    def _load_user_stats(self):
        """بارگذاری آمار کاربران"""
        if self.user_stats_file.exists():
            with open(self.user_stats_file, 'r', encoding='utf-8') as f:
                self.user_stats = json.load(f)
        else:
            self.user_stats = {}
            self._save_user_stats()
    
    def _save_user_stats(self):
        """ذخیره آمار کاربران"""
        with open(self.user_stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_stats, f, indent=2, ensure_ascii=False)
    
    def log_build(self, user_id, username, apk_name, duration, success, is_custom=False, error=None):
        """ثبت اطلاعات یک build"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            log_file = self.logs_dir / f"{today}.json"
            
            # بارگذاری لاگ‌های امروز
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # اضافه کردن لاگ جدید
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'username': username,
                'apk_name': apk_name,
                'duration': duration,
                'success': success,
                'is_custom': is_custom,
                'error': error
            }
            logs.append(log_entry)
            
            # ذخیره لاگ
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
            
            # آپدیت آمار کلی
            if success:
                self.stats['total_builds'] += 1
                self._save_stats()
            
            # آپدیت آمار کاربر
            self._update_user_stats(user_id, username, apk_name, duration, success, is_custom)
            
            logger.info(f"Build logged: {username} - {apk_name} - {'Success' if success else 'Failed'}")
            
        except Exception as e:
            logger.error(f"Error logging build: {str(e)}")
    
    def _update_user_stats(self, user_id, username, apk_name, duration, success, is_custom):
        """آپدیت آمار یک کاربر"""
        user_id_str = str(user_id)
        
        if user_id_str not in self.user_stats:
            self.user_stats[user_id_str] = {
                'username': username,
                'total_builds': 0,
                'quick_builds': 0,
                'custom_builds': 0,
                'failed_builds': 0,
                'total_duration': 0,
                'first_build': datetime.now().isoformat(),
                'last_build': None,
                'last_active': datetime.now().isoformat(),
                'apk_usage': {},
                'banned': False,
                'ban_reason': None,
                'ban_date': None
            }
            self.stats['total_users'] += 1
            self._save_stats()
        
        user = self.user_stats[user_id_str]
        user['username'] = username  # آپدیت username در صورت تغییر
        user['last_active'] = datetime.now().isoformat()
        
        if success:
            user['total_builds'] += 1
            user['last_build'] = datetime.now().isoformat()
            user['total_duration'] += duration
            
            if is_custom:
                user['custom_builds'] += 1
            else:
                user['quick_builds'] += 1
            
            # آمار APK مورد استفاده
            if apk_name not in user['apk_usage']:
                user['apk_usage'][apk_name] = 0
            user['apk_usage'][apk_name] += 1
        else:
            user['failed_builds'] += 1
        
        self._save_user_stats()
    
    def get_total_stats(self):
        """دریافت آمار کلی سیستم"""
        try:
            total_users = len(self.user_stats)
            total_builds = self.stats.get('total_builds', 0)
            
            # محاسبه کاربران فعال
            active_7d = self._get_active_users_count(days=7)
            new_today = self._get_new_users_today()
            
            # محاسبه build های امروز و هفته
            builds_today = self._get_builds_count(days=0)
            builds_week = self._get_builds_count(days=7)
            
            # میانگین زمان build
            avg_build_time = self._get_avg_build_time()
            
            # Uptime
            start_date = datetime.fromisoformat(self.stats.get('start_date', datetime.now().isoformat()))
            uptime = datetime.now() - start_date
            uptime_str = self._format_timedelta(uptime)
            
            return {
                'total_users': total_users,
                'active_users_7d': active_7d,
                'new_users_today': new_today,
                'total_builds': total_builds,
                'builds_today': builds_today,
                'builds_week': builds_week,
                'avg_build_time': avg_build_time,
                'uptime': uptime_str
            }
        except Exception as e:
            logger.error(f"Error getting total stats: {str(e)}")
            return {}
    
    def _get_active_users_count(self, days=7):
        """تعداد کاربران فعال در N روز گذشته"""
        cutoff = datetime.now() - timedelta(days=days)
        count = 0
        
        for user_data in self.user_stats.values():
            last_active = datetime.fromisoformat(user_data.get('last_active', '2020-01-01T00:00:00'))
            if last_active > cutoff:
                count += 1
        
        return count
    
    def _get_new_users_today(self):
        """تعداد کاربران جدید امروز"""
        today = datetime.now().date()
        count = 0
        
        for user_data in self.user_stats.values():
            first_build = datetime.fromisoformat(user_data.get('first_build', '2020-01-01T00:00:00')).date()
            if first_build == today:
                count += 1
        
        return count
    
    def _get_builds_count(self, days=0):
        """تعداد build ها در N روز گذشته (0 = امروز)"""
        if days == 0:
            # فقط امروز
            today = datetime.now().strftime('%Y-%m-%d')
            log_file = self.logs_dir / f"{today}.json"
            
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    return len([l for l in logs if l.get('success', False)])
            return 0
        else:
            # N روز گذشته
            count = 0
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                log_file = self.logs_dir / f"{date}.json"
                
                if log_file.exists():
                    with open(log_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                        count += len([l for l in logs if l.get('success', False)])
            
            return count
    
    def _get_avg_build_time(self):
        """میانگین زمان build (ثانیه)"""
        total_duration = 0
        total_count = 0
        
        for user_data in self.user_stats.values():
            if user_data.get('total_builds', 0) > 0:
                total_duration += user_data.get('total_duration', 0)
                total_count += user_data.get('total_builds', 0)
        
        if total_count > 0:
            return int(total_duration / total_count)
        return 0
    
    def get_builds_by_day(self, days=7):
        """دریافت تعداد build ها در N روز گذشته"""
        result = []
        
        for i in range(days - 1, -1, -1):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            day_name = date.strftime('%a')
            log_file = self.logs_dir / f"{date_str}.json"
            
            count = 0
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    count = len([l for l in logs if l.get('success', False)])
            
            result.append({
                'day': day_name,
                'date': date_str,
                'count': count
            })
        
        return result
    
    def get_top_users(self, limit=5, days=None):
        """دریافت بهترین کاربران بر اساس تعداد build"""
        users_list = []
        
        for user_id, user_data in self.user_stats.items():
            users_list.append({
                'user_id': user_id,
                'username': user_data.get('username', 'Unknown'),
                'total_builds': user_data.get('total_builds', 0)
            })
        
        # مرتب‌سازی بر اساس تعداد build
        users_list.sort(key=lambda x: x['total_builds'], reverse=True)
        
        return users_list[:limit]
    
    def get_all_users(self, filter_type='all'):
        """دریافت لیست کاربران با فیلتر"""
        users_list = []
        now = datetime.now()
        
        for user_id, user_data in self.user_stats.items():
            last_active = datetime.fromisoformat(user_data.get('last_active', '2020-01-01T00:00:00'))
            time_diff = now - last_active
            
            # تعیین وضعیت
            if time_diff.total_seconds() < 600:  # 10 دقیقه
                status = '🟢'
                status_text = 'Online'
            elif time_diff.total_seconds() < 3600:  # 1 ساعت
                status = '🟡'
                status_text = 'Recently'
            elif time_diff.total_seconds() < 86400:  # 24 ساعت
                status = '🔴'
                status_text = 'Offline'
            else:
                status = '⚪'
                status_text = 'Inactive'
            
            user_info = {
                'user_id': user_id,
                'username': user_data.get('username', 'Unknown'),
                'status': status,
                'status_text': status_text,
                'last_active': last_active,
                'total_builds': user_data.get('total_builds', 0),
                'first_build': user_data.get('first_build'),
                'last_build': user_data.get('last_build')
            }
            
            # فیلتر کردن
            if filter_type == 'online' and status != '🟢':
                continue
            elif filter_type == 'new':
                first_build = datetime.fromisoformat(user_data.get('first_build', '2020-01-01T00:00:00'))
                if (now - first_build).days > 7:
                    continue
            elif filter_type == 'active':
                if user_data.get('total_builds', 0) < 10:
                    continue
            
            users_list.append(user_info)
        
        # مرتب‌سازی بر اساس آخرین فعالیت
        users_list.sort(key=lambda x: x['last_active'], reverse=True)
        
        return users_list
    
    def get_user_details(self, user_id):
        """دریافت جزئیات کامل یک کاربر"""
        user_id_str = str(user_id)
        
        if user_id_str not in self.user_stats:
            return None
        
        user_data = self.user_stats[user_id_str]
        
        # محاسبه میانگین زمان build
        total_builds = user_data.get('total_builds', 0)
        total_duration = user_data.get('total_duration', 0)
        avg_time = int(total_duration / total_builds) if total_builds > 0 else 0
        
        # محاسبه زمان کل
        total_time_str = self._format_seconds(total_duration)
        
        # last active
        last_active = datetime.fromisoformat(user_data.get('last_active', datetime.now().isoformat()))
        last_active_str = self._format_time_ago(last_active)
        
        return {
            'username': user_data.get('username', 'Unknown'),
            'user_id': user_id,
            'total_builds': total_builds,
            'quick_builds': user_data.get('quick_builds', 0),
            'custom_builds': user_data.get('custom_builds', 0),
            'failed_builds': user_data.get('failed_builds', 0),
            'avg_build_time': avg_time,
            'total_time': total_time_str,
            'first_build': user_data.get('first_build'),
            'last_build': user_data.get('last_build'),
            'last_active': last_active_str,
            'apk_usage': user_data.get('apk_usage', {})
        }
    
    def _format_timedelta(self, td):
        """فرمت کردن timedelta به فرمت قابل خواندن"""
        days = td.days
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _format_seconds(self, seconds):
        """فرمت کردن ثانیه به فرمت قابل خواندن"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _format_time_ago(self, dt):
        """فرمت کردن زمان به "چند وقت پیش" """
        now = datetime.now()
        diff = now - dt
        
        if diff.total_seconds() < 60:
            return "just now"
        elif diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes}m ago"
        elif diff.total_seconds() < 86400:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        else:
            days = diff.days
            return f"{days}d ago"
    
    def update_user_activity(self, user_id, username):
        """آپدیت آخرین فعالیت کاربر"""
        user_id_str = str(user_id)
        
        if user_id_str in self.user_stats:
            self.user_stats[user_id_str]['last_active'] = datetime.now().isoformat()
            self.user_stats[user_id_str]['username'] = username
            self._save_user_stats()
    
    def ban_user(self, user_id, reason=None):
        """مسدود کردن کاربر"""
        user_id_str = str(user_id)
        
        if user_id_str not in self.user_stats:
            return False, "User not found"
        
        self.user_stats[user_id_str]['banned'] = True
        self.user_stats[user_id_str]['ban_reason'] = reason or "No reason provided"
        self.user_stats[user_id_str]['ban_date'] = datetime.now().isoformat()
        self._save_user_stats()
        
        logger.info(f"User banned: {user_id} - Reason: {reason}")
        return True, "User banned successfully"
    
    def unban_user(self, user_id):
        """رفع مسدودیت کاربر"""
        user_id_str = str(user_id)
        
        if user_id_str not in self.user_stats:
            return False, "User not found"
        
        self.user_stats[user_id_str]['banned'] = False
        self.user_stats[user_id_str]['ban_reason'] = None
        self.user_stats[user_id_str]['ban_date'] = None
        self._save_user_stats()
        
        logger.info(f"User unbanned: {user_id}")
        return True, "User unbanned successfully"
    
    def is_user_banned(self, user_id):
        """چک کردن اینکه کاربر ban شده یا نه"""
        user_id_str = str(user_id)
        
        if user_id_str not in self.user_stats:
            return False
        
        return self.user_stats[user_id_str].get('banned', False)
    
    def get_banned_users(self):
        """دریافت لیست کاربران ban شده"""
        banned_users = []
        
        for user_id, user_data in self.user_stats.items():
            if user_data.get('banned', False):
                ban_date = user_data.get('ban_date')
                if ban_date:
                    try:
                        ban_dt = datetime.fromisoformat(ban_date)
                        time_ago = self._format_time_ago(ban_dt)
                    except:
                        time_ago = "Unknown"
                else:
                    time_ago = "Unknown"
                
                banned_users.append({
                    'user_id': user_id,
                    'username': user_data.get('username', 'Unknown'),
                    'ban_reason': user_data.get('ban_reason', 'No reason'),
                    'ban_date': ban_date,
                    'ban_time_ago': time_ago
                })
        
        # مرتب‌سازی بر اساس تاریخ ban (جدیدترین اول)
        banned_users.sort(key=lambda x: x.get('ban_date', ''), reverse=True)
        
        return banned_users


# Global instance
stats_manager = StatsManager()
