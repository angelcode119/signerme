import re


class ThemeManager:
    def __init__(self):
        self.user_themes = {}
    
    def start_customization(self, user_id):
        """Start theme customization for a user"""
        self.user_themes[user_id] = {
            'step': 'primary_color',
            'theme': {},
            'apk_filename': None
        }
    
    def set_apk(self, user_id, apk_filename):
        """Set the selected APK filename"""
        if user_id in self.user_themes:
            self.user_themes[user_id]['apk_filename'] = apk_filename
    
    def is_customizing(self, user_id):
        """Check if user is in customization mode"""
        return user_id in self.user_themes
    
    def get_current_step(self, user_id):
        """Get current customization step"""
        if user_id in self.user_themes:
            return self.user_themes[user_id]['step']
        return None
    
    def validate_color(self, color):
        """Validate hex color format"""
        if not color:
            return False
        
        # Accept #RRGGBB format
        pattern = r'^#[0-9A-Fa-f]{6}$'
        return bool(re.match(pattern, color))
    
    def set_color(self, user_id, color):
        """Set color for current step and move to next"""
        if user_id not in self.user_themes:
            return False, "Not in customization mode"
        
        current_step = self.user_themes[user_id]['step']
        
        if not self.validate_color(color):
            return False, "Invalid color format. Use #RRGGBB (e.g., #4fc3f7)"
        
        # Store the color
        self.user_themes[user_id]['theme'][current_step] = color.lower()
        
        # Get next step
        next_step = self.get_next_step(current_step)
        
        if next_step:
            self.user_themes[user_id]['step'] = next_step
            return True, next_step
        else:
            # Customization complete
            return True, None
    
    def get_next_step(self, current_step):
        """Get next customization step"""
        steps = [
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
    
    def get_theme(self, user_id):
        """Get complete theme for user"""
        if user_id not in self.user_themes:
            return None
        
        custom_theme = self.user_themes[user_id]['theme']
        
        # Complete theme with defaults
        complete_theme = {
            "primary_color": custom_theme.get('primary_color', '#4fc3f7'),
            "secondary_color": custom_theme.get('secondary_color', '#29b6f6'),
            "accent_color": custom_theme.get('accent_color', '#1976d2'),
            "background_color": "#ffffff",
            "background_secondary_color": "#f5f9fc",
            "text_color": custom_theme.get('text_color', '#212121'),
            "text_secondary_color": "#616161",
            "text_light_color": "#9e9e9e",
            "button_color": custom_theme.get('button_color', '#1976d2'),
            "button_text_color": "#ffffff",
            "button_hover_color": "#1565c0",
            "input_background_color": "#ffffff",
            "input_border_color": "#e0e0e0",
            "input_focus_color": "#4fc3f7",
            "error_color": custom_theme.get('error_color', '#f44336'),
            "success_color": custom_theme.get('success_color', '#4caf50'),
            "warning_color": "#ff9800",
            "info_color": "#2196f3",
            "loader_color": "#4fc3f7",
            "shadow_color": "rgba(0, 0, 0, 0.1)",
            "overlay_color": "rgba(0, 0, 0, 0.5)"
        }
        
        return complete_theme
    
    def get_apk_filename(self, user_id):
        """Get selected APK filename"""
        if user_id in self.user_themes:
            return self.user_themes[user_id].get('apk_filename')
        return None
    
    def cancel_customization(self, user_id):
        """Cancel customization and clean up"""
        if user_id in self.user_themes:
            del self.user_themes[user_id]
    
    def get_step_description(self, step):
        """Get user-friendly description for each step"""
        descriptions = {
            'primary_color': {
                'title': '🎨 Primary Color',
                'desc': 'Main brand color for headers and key elements',
                'example': '#4fc3f7'
            },
            'secondary_color': {
                'title': '🎨 Secondary Color',
                'desc': 'Supporting color for secondary elements',
                'example': '#29b6f6'
            },
            'accent_color': {
                'title': '✨ Accent Color',
                'desc': 'Highlights and important actions',
                'example': '#1976d2'
            },
            'button_color': {
                'title': '🔘 Button Color',
                'desc': 'Primary button background',
                'example': '#1976d2'
            },
            'text_color': {
                'title': '📝 Text Color',
                'desc': 'Main text color',
                'example': '#212121'
            },
            'error_color': {
                'title': '❌ Error Color',
                'desc': 'Error messages and alerts',
                'example': '#f44336'
            },
            'success_color': {
                'title': '✅ Success Color',
                'desc': 'Success messages and confirmations',
                'example': '#4caf50'
            }
        }
        
        return descriptions.get(step, {'title': step, 'desc': '', 'example': '#000000'})


theme_manager = ThemeManager()
