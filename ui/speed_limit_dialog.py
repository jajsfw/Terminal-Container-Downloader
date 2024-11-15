from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSpinBox, QCheckBox, QPushButton, QGroupBox)
from PyQt6.QtCore import Qt
import humanize

class SpeedLimitDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("速度限制设置")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 全局速度限制
        global_group = QGroupBox("全局速度限制")
        global_layout = QVBoxLayout()
        
        # 启用全局限速
        self.enable_global = QCheckBox("启用全局速度限制")
        self.enable_global.setChecked(self.settings.get('speed_limit_enabled', False))
        global_layout.addWidget(self.enable_global)
        
        # 下载速度限制
        download_layout = QHBoxLayout()
        download_label = QLabel("最大下载速度:")
        self.download_spin = QSpinBox()
        self.download_spin.setRange(0, 102400)  # 0-100MB/s
        self.download_spin.setSuffix(" KB/s")
        self.download_spin.setValue(self.settings.get('max_download_speed', 0))
        download_layout.addWidget(download_label)
        download_layout.addWidget(self.download_spin)
        global_layout.addLayout(download_layout)
        
        global_group.setLayout(global_layout)
        layout.addWidget(global_group)
        
        # 时间段限速
        time_group = QGroupBox("时间段限速")
        time_layout = QVBoxLayout()
        
        # 启用时间段限速
        self.enable_time = QCheckBox("启用时间段限速")
        self.enable_time.setChecked(self.settings.get('time_limit_enabled', False))
        time_layout.addWidget(self.enable_time)
        
        # 时间段设置
        time_range_layout = QHBoxLayout()
        time_range_label = QLabel("限速时间段:")
        self.start_hour = QSpinBox()
        self.start_hour.setRange(0, 23)
        self.start_hour.setValue(self.settings.get('limit_start_hour', 0))
        self.end_hour = QSpinBox()
        self.end_hour.setRange(0, 23)
        self.end_hour.setValue(self.settings.get('limit_end_hour', 0))
        
        time_range_layout.addWidget(time_range_label)
        time_range_layout.addWidget(self.start_hour)
        time_range_layout.addWidget(QLabel("点 至"))
        time_range_layout.addWidget(self.end_hour)
        time_range_layout.addWidget(QLabel("点"))
        time_layout.addLayout(time_range_layout)
        
        # 时间段速度限制
        time_speed_layout = QHBoxLayout()
        time_speed_label = QLabel("限制速度:")
        self.time_speed_spin = QSpinBox()
        self.time_speed_spin.setRange(0, 102400)
        self.time_speed_spin.setSuffix(" KB/s")
        self.time_speed_spin.setValue(self.settings.get('time_limit_speed', 0))
        time_speed_layout.addWidget(time_speed_label)
        time_speed_layout.addWidget(self.time_speed_spin)
        time_layout.addLayout(time_speed_layout)
        
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)
        
        # 当前状态显示
        status_layout = QHBoxLayout()
        self.status_label = QLabel()
        self.update_status_label()
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        # 连接信号
        self.enable_global.toggled.connect(self.download_spin.setEnabled)
        self.enable_time.toggled.connect(self.start_hour.setEnabled)
        self.enable_time.toggled.connect(self.end_hour.setEnabled)
        self.enable_time.toggled.connect(self.time_speed_spin.setEnabled)
        
        # 初始状态
        self.download_spin.setEnabled(self.enable_global.isChecked())
        self.start_hour.setEnabled(self.enable_time.isChecked())
        self.end_hour.setEnabled(self.enable_time.isChecked())
        self.time_speed_spin.setEnabled(self.enable_time.isChecked())
        
    def update_status_label(self):
        current_speed = self.parent().download_manager.get_current_speed()
        self.status_label.setText(
            f"当前下载速度: {humanize.naturalsize(current_speed, binary=True)}/s"
        )
        
    def get_settings(self):
        return {
            'speed_limit_enabled': self.enable_global.isChecked(),
            'max_download_speed': self.download_spin.value(),
            'time_limit_enabled': self.enable_time.isChecked(),
            'limit_start_hour': self.start_hour.value(),
            'limit_end_hour': self.end_hour.value(),
            'time_limit_speed': self.time_speed_spin.value()
        } 