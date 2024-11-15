from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QFileDialog)
from PyQt6.QtCore import Qt

class NewDownloadDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建下载")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # URL输入
        url_layout = QHBoxLayout()
        url_label = QLabel("下载地址:")
        self.url_input = QLineEdit()
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        # 保存路径选择
        path_layout = QHBoxLayout()
        path_label = QLabel("保存位置:")
        self.path_input = QLineEdit()
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)
        
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
        path = QFileDialog.getSaveFileName(self, "选择保存位置")[0]
        if path:
            self.path_input.setText(path)
            
    def get_data(self):
        return {
            'url': self.url_input.text(),
            'save_path': self.path_input.text()
        } 