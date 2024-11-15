import json
import os

class Settings:
    def __init__(self):
        self.settings_file = "config.json"
        self.default_settings = {
            'max_concurrent': 3,
            'default_save_path': os.path.expanduser("~/Downloads"),
            'history_file': "download_history.json"
        }
        self.settings = self.load_settings()
        
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return {**self.default_settings, **json.load(f)}
            return self.default_settings.copy()
        except Exception:
            return self.default_settings.copy()
            
    def save_settings(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"保存设置失败: {str(e)}")
            
    def get(self, key, default=None):
        return self.settings.get(key, default)
        
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings() 