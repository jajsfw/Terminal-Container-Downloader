from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSpinBox, QLineEdit, QPushButton, QGroupBox)
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("下载设置")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 基本设置组
        basic_group = QGroupBox("基本设置")
        basic_layout = QVBoxLayout()
        
        # 最大同时下载数
        concurrent_layout = QHBoxLayout()
        concurrent_label = QLabel("最大同时下载数:")
        self.concurrent_spin = QSpinBox()
        self.concurrent_spin.setRange(1, 10)
        self.concurrent_spin.setValue(self.settings.get('max_concurrent', 3))
        concurrent_layout.addWidget(concurrent_label)
        concurrent_layout.addWidget(self.concurrent_spin)
        basic_layout.addLayout(concurrent_layout)
        
        # 默认保存路径
        save_path_layout = QHBoxLayout()
        save_path_label = QLabel("默认保存路径:")
        self.save_path_input = QLineEdit()
        self.save_path_input.setText(self.settings.get('default_save_path', ''))
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_path)
        save_path_layout.addWidget(save_path_label)
        save_path_layout.addWidget(self.save_path_input)
        save_path_layout.addWidget(browse_btn)
        basic_layout.addLayout(save_path_layout)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # BT设置组
        bt_group = QGroupBox("BT设置")
        bt_layout = QVBoxLayout()
        
        # 最大上传速度
        upload_layout = QHBoxLayout()
        upload_label = QLabel("最大上传速度(KB/s):")
        self.upload_spin = QSpinBox()
        self.upload_spin.setRange(0, 10000)
        self.upload_spin.setValue(self.settings.get('max_upload_speed', 0))
        upload_layout.addWidget(upload_label)
        upload_layout.addWidget(self.upload_spin)
        bt_layout.addLayout(upload_layout)
        
        # 最大下载速度
        download_layout = QHBoxLayout()
        download_label = QLabel("最大下载速度(KB/s):")
        self.download_spin = QSpinBox()
        self.download_spin.setRange(0, 10000)
        self.download_spin.setValue(self.settings.get('max_download_speed', 0))
        download_layout.addWidget(download_label)
        download_layout.addWidget(self.download_spin)
        bt_layout.addLayout(download_layout)
        
        bt_group.setLayout(bt_layout)
        layout.addWidget(bt_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def browse_path(self):
        from PyQt6.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, "选择默认保存路径")
        if path:
            self.save_path_input.setText(path)
            
    def get_settings(self):
        return {
            'max_concurrent': self.concurrent_spin.value(),
            'default_save_path': self.save_path_input.text(),
            'max_upload_speed': self.upload_spin.value(),
            'max_download_speed': self.download_spin.value()
        } 