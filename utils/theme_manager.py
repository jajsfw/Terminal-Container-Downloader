from PyQt6.QtCore import QObject, pyqtSignal
import json
import os

class ThemeManager(QObject):
    theme_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.themes_dir = os.path.join(os.path.dirname(__file__), '..', 'themes')
        self.current_theme = {}
        
        # 创建主题目录
        if not os.path.exists(self.themes_dir):
            os.makedirs(self.themes_dir)
            self._create_default_themes()
            
        # 加载默认主题
        self.load_theme('default')
        
    def _create_default_themes(self):
        # 默认主题
        default_theme = {
            'name': 'default',
            'window_background': '#FFFFFF',
            'text_color': '#000000',
            'accent_color': '#2196F3',
            'success_color': '#4CAF50',
            'error_color': '#F44336',
            'warning_color': '#FFC107',
            'progress_bar_background': '#E3F2FD',
            'progress_bar_chunk': '#2196F3',
            'table_alternate_background': '#F5F5F5',
            'table_gridline': '#E0E0E0',
            'toolbar_background': '#F5F5F5'
        }
        
        # 深色主题
        dark_theme = {
            'name': 'dark',
            'window_background': '#121212',
            'text_color': '#FFFFFF',
            'accent_color': '#BB86FC',
            'success_color': '#00C853',
            'error_color': '#CF6679',
            'warning_color': '#FFD600',
            'progress_bar_background': '#1F1F1F',
            'progress_bar_chunk': '#BB86FC',
            'table_alternate_background': '#1F1F1F',
            'table_gridline': '#2D2D2D',
            'toolbar_background': '#1F1F1F'
        }
        
        # 保存主题文件
        self._save_theme(default_theme)
        self._save_theme(dark_theme)
        
    def _save_theme(self, theme):
        theme_path = os.path.join(self.themes_dir, f"{theme['name']}.json")
        with open(theme_path, 'w', encoding='utf-8') as f:
            json.dump(theme, f, indent=4)
            
    def load_theme(self, theme_name):
        theme_path = os.path.join(self.themes_dir, f"{theme_name}.json")
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                self.current_theme = json.load(f)
                self.theme_changed.emit(self.current_theme)
        except Exception as e:
            print(f"加载主题失败: {str(e)}")
            
    def get_style_sheet(self):
        """生成Qt样式表"""
        return f"""
            QMainWindow {{
                background-color: {self.current_theme['window_background']};
                color: {self.current_theme['text_color']};
            }}
            
            QTableWidget {{
                background-color: {self.current_theme['window_background']};
                alternate-background-color: {self.current_theme['table_alternate_background']};
                gridline-color: {self.current_theme['table_gridline']};
                color: {self.current_theme['text_color']};
            }}
            
            QProgressBar {{
                border: 2px solid {self.current_theme['accent_color']};
                border-radius: 5px;
                text-align: center;
                background-color: {self.current_theme['progress_bar_background']};
            }}
            
            QProgressBar::chunk {{
                background-color: {self.current_theme['progress_bar_chunk']};
                border-radius: 3px;
            }}
            
            QToolBar {{
                background-color: {self.current_theme['toolbar_background']};
                border: none;
            }}
            
            QPushButton {{
                background-color: {self.current_theme['accent_color']};
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }}
            
            QPushButton:hover {{
                background-color: {self.current_theme['accent_color']}CC;
            }}
        """ 