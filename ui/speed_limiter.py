from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QSlider, 
                           QPushButton, QSpinBox)
from PyQt6.QtCore import Qt
import humanize

class SpeedLimiter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        
        # 速度限制开关
        self.enable_btn = QPushButton("限速")
        self.enable_btn.setCheckable(True)
        self.enable_btn.setFixedWidth(60)
        self.enable_btn.clicked.connect(self.toggle_limit)
        
        # 速度输入框
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(0, 10240)  # 0-10MB/s
        self.speed_spin.setSuffix(" KB/s")
        self.speed_spin.setFixedWidth(100)
        self.speed_spin.valueChanged.connect(self.update_speed_limit)
        
        # 速度滑块
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(0, 10240)
        self.speed_slider.valueChanged.connect(self.speed_spin.setValue)
        
        # 当前速度显示
        self.speed_label = QLabel("当前: 0 B/s")
        self.speed_label.setFixedWidth(120)
        
        layout.addWidget(self.enable_btn)
        layout.addWidget(self.speed_spin)
        layout.addWidget(self.speed_slider)
        layout.addWidget(self.speed_label)
        
        # 初始状态：禁用
        self.speed_spin.setEnabled(False)
        self.speed_slider.setEnabled(False)
        
    def toggle_limit(self, enabled):
        self.speed_spin.setEnabled(enabled)
        self.speed_slider.setEnabled(enabled)
        if enabled:
            self.update_speed_limit(self.speed_spin.value())
        else:
            self.update_speed_limit(0)
            
    def update_speed_limit(self, value):
        if self.parent():
            self.parent().download_manager.set_speed_limit(value)
            
    def update_current_speed(self, speed):
        self.speed_label.setText(f"当前: {humanize.naturalsize(speed, binary=True)}/s") 