from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QLineEdit, QColorDialog, QFormLayout)
from PyQt6.QtGui import QColor
import json
import os

class ThemeEditDialog(QDialog):
    def __init__(self, theme_name, theme_manager, parent=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.theme_name = theme_name
        self.setWindowTitle("编辑主题" if theme_name else "新建主题")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # 主题名称
        self.name_input = QLineEdit()
        if theme_name:
            self.name_input.setText(theme_name)
            self.name_input.setEnabled(False)  # 编辑模式下不允许修改名称
        form_layout.addRow("主题名称:", self.name_input)
        
        # 颜色选择器
        self.color_inputs = {}
        color_names = {
            'window_background': '窗口背景',
            'text_color': '文本颜色',
            'accent_color': '强调色',
            'success_color': '成功色',
            'error_color': '错误色',
            'warning_color': '警告色',
            'progress_bar_background': '进度条背景',
            'progress_bar_chunk': '进度条前景',
            'table_alternate_background': '表格交替背景',
            'table_gridline': '表格网格线',
            'toolbar_background': '工具栏背景'
        }
        
        # 加载当前主题数据
        if theme_name:
            theme_data = self.theme_manager.load_theme_data(theme_name)
        else:
            theme_data = self.theme_manager.current_theme
        
        for key, label in color_names.items():
            color_layout = QHBoxLayout()
            color_input = QLineEdit()
            color_input.setText(theme_data.get(key, '#000000'))
            pick_btn = QPushButton("选择")
            
            # 使用lambda创建闭包保存当前的key和input引用
            def create_color_picker(k, input_field):
                return lambda: self.pick_color(k, input_field)
            
            pick_btn.clicked.connect(create_color_picker(key, color_input))
            
            color_layout.addWidget(color_input)
            color_layout.addWidget(pick_btn)
            
            self.color_inputs[key] = color_input
            form_layout.addRow(f"{label}:", color_layout)
        
        layout.addLayout(form_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        
        save_btn.clicked.connect(self.save_theme)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def pick_color(self, key, input_field):
        current_color = QColor(input_field.text())
        color = QColorDialog.getColor(current_color, self)
        if color.isValid():
            input_field.setText(color.name())
            
    def save_theme(self):
        name = self.name_input.text().strip()
        if not name:
            return
            
        theme_data = {
            'name': name
        }
        
        # 收集所有颜色值
        for key, input_field in self.color_inputs.items():
            theme_data[key] = input_field.text()
            
        # 保存主题
        self.theme_manager._save_theme(theme_data)
        self.accept() 