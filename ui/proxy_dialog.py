from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QComboBox, QGroupBox,
                           QCheckBox)
from PyQt6.QtCore import Qt

class ProxyDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("代理设置")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # 代理启用选项
        self.enable_proxy = QCheckBox("启用代理")
        self.enable_proxy.setChecked(self.settings.get('proxy_enabled', False))
        layout.addWidget(self.enable_proxy)
        
        # 代理设置组
        proxy_group = QGroupBox("代理设置")
        proxy_layout = QVBoxLayout()
        
        # 代理类型
        type_layout = QHBoxLayout()
        type_label = QLabel("代理类型:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["HTTP", "SOCKS5"])
        self.type_combo.setCurrentText(self.settings.get('proxy_type', 'HTTP'))
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        proxy_layout.addLayout(type_layout)
        
        # 代理服务器
        server_layout = QHBoxLayout()
        server_label = QLabel("服务器:")
        self.server_input = QLineEdit()
        self.server_input.setText(self.settings.get('proxy_host', ''))
        server_layout.addWidget(server_label)
        server_layout.addWidget(self.server_input)
        proxy_layout.addLayout(server_layout)
        
        # 代理端口
        port_layout = QHBoxLayout()
        port_label = QLabel("端口:")
        self.port_input = QLineEdit()
        self.port_input.setText(str(self.settings.get('proxy_port', '')))
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)
        proxy_layout.addLayout(port_layout)
        
        # 认证信息
        auth_layout = QVBoxLayout()
        self.auth_check = QCheckBox("需要认证")
        self.auth_check.setChecked(self.settings.get('proxy_auth', False))
        auth_layout.addWidget(self.auth_check)
        
        # 用户名
        user_layout = QHBoxLayout()
        user_label = QLabel("用户名:")
        self.user_input = QLineEdit()
        self.user_input.setText(self.settings.get('proxy_user', ''))
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_input)
        auth_layout.addLayout(user_layout)
        
        # 密码
        pass_layout = QHBoxLayout()
        pass_label = QLabel("密码:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setText(self.settings.get('proxy_pass', ''))
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_input)
        auth_layout.addLayout(pass_layout)
        
        proxy_layout.addLayout(auth_layout)
        proxy_group.setLayout(proxy_layout)
        layout.addWidget(proxy_group)
        
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
        self.enable_proxy.toggled.connect(proxy_group.setEnabled)
        self.auth_check.toggled.connect(self.user_input.setEnabled)
        self.auth_check.toggled.connect(self.pass_input.setEnabled)
        
        # 初始状态
        proxy_group.setEnabled(self.enable_proxy.isChecked())
        self.user_input.setEnabled(self.auth_check.isChecked())
        self.pass_input.setEnabled(self.auth_check.isChecked())
        
    def get_settings(self):
        return {
            'proxy_enabled': self.enable_proxy.isChecked(),
            'proxy_type': self.type_combo.currentText(),
            'proxy_host': self.server_input.text(),
            'proxy_port': self.port_input.text(),
            'proxy_auth': self.auth_check.isChecked(),
            'proxy_user': self.user_input.text(),
            'proxy_pass': self.pass_input.text()
        } 