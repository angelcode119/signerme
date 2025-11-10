import re

class ThemeManager:
    def __init__(self):
        self.user_themes = {}

    def start_customization(self, user_id):
        self.user_themes[user_id] = {
            'step': 'app_type',
            'theme': {},
            'app_type': None,
            'apk_filename': None
        }

    def is_customizing(self, user_id):
        return user_id in self.user_themes

    def cancel_customization(self, user_id):
        if user_id in self.user_themes:
            del self.user_themes[user_id]

    def set_apk(self, user_id, apk_filename):
        if user_id in self.user_themes:
            self.user_themes[user_id]['apk_filename'] = apk_filename

    def get_apk_filename(self, user_id):
        return self.user_themes.get(user_id, {}).get('apk_filename')

    def is_valid_color(self, color):
        if not color or not isinstance(color, str):
            return False
        pattern = r'^
        return bool(re.match(pattern, color))

    def set_value(self, user_id, value):
        if user_id not in self.user_themes:
            return False, "Session expired"
        current_step = self.user_themes[user_id]['step']
        if current_step == 'app_type':
            self.user_themes[user_id]['app_type'] = value
        else:
            if not self.is_valid_color(value):
                return False, "Invalid color format. Use:
            self.user_themes[user_id]['theme'][current_step] = value
        next_step = self.get_next_step(current_step)
        if next_step:
            self.user_themes[user_id]['step'] = next_step
            return True, next_step
        else:
            return True, None

    def get_current_step(self, user_id):
        return self.user_themes.get(user_id, {}).get('step')

    def get_next_step(self, current_step):
        steps = [
            'app_type',
            'primary_color',
            'secondary_color',
            'accent_color',
            'button_color',
            'text_color',
            'error_color',
            'success_color'
        ]
        try:
            idx = steps.index(current_step)
            if idx + 1 < len(steps):
                return steps[idx + 1]
        except ValueError:
            pass
        return None

    def get_customization_data(self, user_id):
        data = self.user_themes.get(user_id, {})
        return data.get('app_type'), data.get('theme', {})

    def get_step_description(self, step):
        descriptions = {
            'app_type': {
                'title': '📱 App Type',
                'desc': 'Enter app type',
                'example': 'social',
                'is_color': False
            },
            'primary_color': {
                'title': '🎨 Primary Color',
                'desc': 'Main theme color',
                'example': '
                'is_color': True
            },
            'secondary_color': {
                'title': '🎨 Secondary Color',
                'desc': 'Secondary theme color',
                'example': '
                'is_color': True
            },
            'accent_color': {
                'title': '✨ Accent Color',
                'desc': 'Highlight color',
                'example': '
                'is_color': True
            },
            'button_color': {
                'title': '🔘 Button Color',
                'desc': 'Button background',
                'example': '
                'is_color': True
            },
            'text_color': {
                'title': '📝 Text Color',
                'desc': 'Main text color',
                'example': '
                'is_color': True
            },
            'error_color': {
                'title': '❌ Error Color',
                'desc': 'Error messages',
                'example': '
                'is_color': True
            },
            'success_color': {
                'title': '✅ Success Color',
                'desc': 'Success messages',
                'example': '
                'is_color': True
            }
        }
        return descriptions.get(step, {
            'title': 'Unknown',
            'desc': '',
            'example': '',
            'is_color': False
        })


theme_manager = ThemeManager()
