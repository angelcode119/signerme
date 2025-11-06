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

    def set_apk(self, user_id, apk_filename):
        if user_id in self.user_themes:
            self.user_themes[user_id]['apk_filename'] = apk_filename

    def is_customizing(self, user_id):
        return user_id in self.user_themes

    def get_current_step(self, user_id):
        if user_id in self.user_themes:
            return self.user_themes[user_id]['step']
        return None

    def validate_color(self, color):
        if not color:
            return False

        pattern = r'^
        return bool(re.match(pattern, color))

    def set_value(self, user_id, value):
        if user_id not in self.user_themes:
            return False, "Not in customization mode"

        current_step = self.user_themes[user_id]['step']

        if current_step == 'app_type':
            if not value or len(value.strip()) == 0:
                return False, "App type cannot be empty"

            self.user_themes[user_id]['app_type'] = value.strip().lower()

            next_step = self.get_next_step(current_step)
            if next_step:
                self.user_themes[user_id]['step'] = next_step
                return True, next_step
            else:
                return True, None

        if not self.validate_color(value):
            return False, "Invalid color format. Use

        self.user_themes[user_id]['theme'][current_step] = value.lower()

        next_step = self.get_next_step(current_step)

        if next_step:
            self.user_themes[user_id]['step'] = next_step
            return True, next_step
        else:
            return True, None

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
            current_index = steps.index(current_step)
            if current_index + 1 < len(steps):
                return steps[current_index + 1]
        except ValueError:
            pass

        return None

    def get_customization_data(self, user_id):
        if user_id not in self.user_themes:
            return None, None

        app_type = self.user_themes[user_id].get('app_type')
        custom_theme = self.user_themes[user_id]['theme']

        complete_theme = {
            "primary_color": custom_theme.get('primary_color', '
            "secondary_color": custom_theme.get('secondary_color', '
            "accent_color": custom_theme.get('accent_color', '
            "background_color": "
            "background_secondary_color": "
            "text_color": custom_theme.get('text_color', '
            "text_secondary_color": "
            "text_light_color": "
            "button_color": custom_theme.get('button_color', '
            "button_text_color": "
            "button_hover_color": "
            "input_background_color": "
            "input_border_color": "
            "input_focus_color": "
            "error_color": custom_theme.get('error_color', '
            "success_color": custom_theme.get('success_color', '
            "warning_color": "
            "info_color": "
            "loader_color": "
            "shadow_color": "rgba(0, 0, 0, 0.1)",
            "overlay_color": "rgba(0, 0, 0, 0.5)"
        }

        return app_type, complete_theme

    def get_apk_filename(self, user_id):
        if user_id in self.user_themes:
            return self.user_themes[user_id].get('apk_filename')
        return None

    def cancel_customization(self, user_id):
        if user_id in self.user_themes:
            del self.user_themes[user_id]

    def get_step_description(self, step):
        descriptions = {
            'app_type': {
                'title': '🏷️ App Type',
                'desc': 'Application type identifier',
                'example': 'mparivahan',
                'is_color': False
            },
            'primary_color': {
                'title': '🎨 Primary Color',
                'desc': 'Main brand color for headers and key elements',
                'example': '
                'is_color': True
            },
            'secondary_color': {
                'title': '🎨 Secondary Color',
                'desc': 'Supporting color for secondary elements',
                'example': '
                'is_color': True
            },
            'accent_color': {
                'title': '✨ Accent Color',
                'desc': 'Highlights and important actions',
                'example': '
                'is_color': True
            },
            'button_color': {
                'title': '🔘 Button Color',
                'desc': 'Primary button background',
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
                'desc': 'Error messages and alerts',
                'example': '
                'is_color': True
            },
            'success_color': {
                'title': '✅ Success Color',
                'desc': 'Success messages and confirmations',
                'example': '
                'is_color': True
            }
        }

        return descriptions.get(step, {'title': step, 'desc': '', 'example': '', 'is_color': False})


theme_manager = ThemeManager()
