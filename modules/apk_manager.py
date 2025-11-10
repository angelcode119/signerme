import json
import os
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class APKManager:
    def __init__(self):
        self.apks_file = Path("data/apks.json")
        self.apks_dir = Path("data")
        
        self.apks_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_apks()
    
    def _load_apks(self):
        if self.apks_file.exists():
            with open(self.apks_file, 'r', encoding='utf-8') as f:
                self.apks = json.load(f)
        else:
            self.apks = {}
            self._save_apks()
    
    def _save_apks(self):
        with open(self.apks_file, 'w', encoding='utf-8') as f:
            json.dump(self.apks, f, indent=2, ensure_ascii=False)
    
    def add_apk(self, filename, display_name=None, category=None, enabled=True):
        try:
            apk_path = self.apks_dir / filename
            
            if not apk_path.exists():
                return False, f"APK file not found: {filename}"
            
            if not display_name:
                display_name = filename.replace('.apk', '').replace('_', ' ').title()
            
            size_bytes = apk_path.stat().st_size
            size_mb = round(size_bytes / (1024 * 1024), 1)
            
            self.apks[filename] = {
                'display_name': display_name,
                'filename': filename,
                'size_mb': size_mb,
                'size_bytes': size_bytes,
                'category': category or 'Other',
                'enabled': enabled,
                'added_date': datetime.now().isoformat(),
                'total_builds': 0,
                'last_build': None
            }
            
            self._save_apks()
            logger.info(f"APK added: {display_name} ({filename})")
            return True, "APK added successfully"
            
        except Exception as e:
            logger.error(f"Error adding APK: {str(e)}")
            return False, str(e)
    
    def update_apk(self, filename, display_name=None, category=None, enabled=None):
        try:
            if filename not in self.apks:
                return False, "APK not found"
            
            if display_name is not None:
                self.apks[filename]['display_name'] = display_name
            
            if category is not None:
                self.apks[filename]['category'] = category
            
            if enabled is not None:
                self.apks[filename]['enabled'] = enabled
            
            self._save_apks()
            logger.info(f"APK updated: {filename}")
            return True, "APK updated successfully"
            
        except Exception as e:
            logger.error(f"Error updating APK: {str(e)}")
            return False, str(e)
    
    def delete_apk(self, filename):
        try:
            if filename not in self.apks:
                return False, "APK not found"
            
            del self.apks[filename]
            self._save_apks()
            logger.info(f"APK deleted: {filename}")
            return True, "APK deleted successfully"
            
        except Exception as e:
            logger.error(f"Error deleting APK: {str(e)}")
            return False, str(e)
    
    def increment_build_count(self, filename):
        if filename in self.apks:
            self.apks[filename]['total_builds'] += 1
            self.apks[filename]['last_build'] = datetime.now().isoformat()
            self._save_apks()
    
    def get_apk_info(self, filename):
        return self.apks.get(filename)
    
    def get_all_apks(self, enabled_only=False):
        apks_list = []
        
        for filename, data in self.apks.items():
            if enabled_only and not data.get('enabled', True):
                continue
            
            apks_list.append(data)
        
        apks_list.sort(key=lambda x: x.get('total_builds', 0), reverse=True)
        
        return apks_list
    
    def get_apk_stats(self, filename):
        if filename not in self.apks:
            return None
        
        apk_data = self.apks[filename]
        
        return {
            'display_name': apk_data.get('display_name', filename),
            'filename': filename,
            'size_mb': apk_data.get('size_mb', 0),
            'total_builds': apk_data.get('total_builds', 0),
            'added_date': apk_data.get('added_date'),
            'last_build': apk_data.get('last_build'),
            'category': apk_data.get('category', 'Other'),
            'enabled': apk_data.get('enabled', True)
        }
    
    def get_total_storage(self):
        total_bytes = 0
        total_files = len(self.apks)
        
        for apk_data in self.apks.values():
            total_bytes += apk_data.get('size_bytes', 0)
        
        total_mb = round(total_bytes / (1024 * 1024), 1)
        
        return {
            'total_files': total_files,
            'total_mb': total_mb,
            'total_bytes': total_bytes
        }
    
    def get_categories(self):
        categories = set()
        
        for apk_data in self.apks.values():
            categories.add(apk_data.get('category', 'Other'))
        
        return sorted(list(categories))
    
    def search_apks(self, query):
        query_lower = query.lower()
        results = []
        
        for filename, data in self.apks.items():
            display_name = data.get('display_name', '').lower()
            
            if query_lower in display_name or query_lower in filename.lower():
                results.append(data)
        
        return results


apk_manager = APKManager()
