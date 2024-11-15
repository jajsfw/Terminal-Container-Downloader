from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QListWidget, QListWidgetItem, QLabel, QColorDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPixmap
import os

class ThemeDialog(QDialog):
    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.setWindowTitle("主题设置")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # 主题列表
        self.theme_list = QListWidget()
        self.theme_list.itemSelectionChanged.connect(self.preview_theme)
        layout.addWidget(self.theme_list)
        
        # 预览区域
        preview_group = QVBoxLayout()
        preview_group.addWidget(QLabel("预览"))
        
        # 颜色预览
        self.color_preview = QLabel()
        self.color_preview.setMinimumHeight(100)
        preview_group.addWidget(self.color_preview)
        
        layout.addLayout(preview_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        new_btn = QPushButton("新建主题")
        edit_btn = QPushButton("编辑主题")
        delete_btn = QPushButton("删除主题")
        apply_btn = QPushButton("应用")
        close_btn = QPushButton("关闭")
        
        new_btn.clicked.connect(self.create_new_theme)
        edit_btn.clicked.connect(self.edit_theme)
        delete_btn.clicked.connect(self.delete_theme)
        apply_btn.clicked.connect(self.apply_theme)
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(new_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # 加载主题列表
        self.load_themes()
        
    def load_themes(self):
        self.theme_list.clear()
        for filename in os.listdir(self.theme_manager.themes_dir):
            if filename.endswith('.json'):
                theme_name = filename[:-5]  # 移除.json后缀
                item = QListWidgetItem(theme_name)
                self.theme_list.addItem(item)
                
    def preview_theme(self):
        if not self.theme_list.selectedItems():
            return
            
        theme_name = self.theme_list.selectedItems()[0].text()
        theme_path = os.path.join(self.theme_manager.themes_dir, f"{theme_name}.json")
        
        # 创建预览图
        pixmap = QPixmap(self.color_preview.width(), self.color_preview.height())
        painter = QPainter(pixmap)
        
        # 绘制主题颜色预览
        theme = self.theme_manager.load_theme_data(theme_name)
        if theme:
            rect_width = pixmap.width() / 6
            x = 0
            for color_key in ['window_background', 'accent_color', 'success_color', 
                            'error_color', 'warning_color', 'text_color']:
                color = QColor(theme[color_key])
                painter.fillRect(x, 0, rect_width, pixmap.height(), color)
                x += rect_width
                
        painter.end()
        self.color_preview.setPixmap(pixmap)
        
    def create_new_theme(self):
        dialog = ThemeEditDialog(None, self.theme_manager, self)
        if dialog.exec():
            self.load_themes()
            
    def edit_theme(self):
        if not self.theme_list.selectedItems():
            return
            
        theme_name = self.theme_list.selectedItems()[0].text()
        dialog = ThemeEditDialog(theme_name, self.theme_manager, self)
        if dialog.exec():
            self.load_themes()
            
    def delete_theme(self):
        if not self.theme_list.selectedItems():
            return
            
        theme_name = self.theme_list.selectedItems()[0].text()
        if theme_name in ['default', 'dark']:  # 保护默认主题
            return
            
        theme_path = os.path.join(self.theme_manager.themes_dir, f"{theme_name}.json")
        try:
            os.remove(theme_path)
            self.load_themes()
        except Exception as e:
            print(f"删除主题失败: {str(e)}")
            
    def apply_theme(self):
        if not self.theme_list.selectedItems():
            return
            
        theme_name = self.theme_list.selectedItems()[0].text()
        self.theme_manager.load_theme(theme_name) 