from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
                           QPushButton, QHBoxLayout)
from PyQt6.QtCore import Qt
import humanize
from datetime import datetime

class HistoryDialog(QDialog):
    def __init__(self, history, parent=None):
        super().__init__(parent)
        self.history = history
        self.setWindowTitle("下载历史")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # 创建历史记录表格
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "文件名", "大小", "状态", "开始时间", "结束时间", "下载地址"
        ])
        layout.addWidget(self.table)
        
        # 添加按钮
        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("清空历史")
        retry_btn = QPushButton("重新下载")
        close_btn = QPushButton("关闭")
        
        clear_btn.clicked.connect(self.clear_history)
        retry_btn.clicked.connect(self.retry_download)
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(clear_btn)
        btn_layout.addWidget(retry_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        # 加载历史记录
        self.load_history()
        
    def load_history(self):
        self.table.setRowCount(0)
        for record in reversed(self.history.history):  # 最新的记录显示在前面
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # 文件名
            self.table.setItem(row, 0, QTableWidgetItem(
                os.path.basename(record['save_path'])
            ))
            
            # 文件大小
            size = humanize.naturalsize(record['file_size'], binary=True)
            self.table.setItem(row, 1, QTableWidgetItem(size))
            
            # 状态
            self.table.setItem(row, 2, QTableWidgetItem(record['status']))
            
            # 开始时间
            start_time = datetime.fromisoformat(record['start_time'])
            self.table.setItem(row, 3, QTableWidgetItem(
                start_time.strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            # 结束时间
            if 'end_time' in record:
                end_time = datetime.fromisoformat(record['end_time'])
                self.table.setItem(row, 4, QTableWidgetItem(
                    end_time.strftime("%Y-%m-%d %H:%M:%S")
                ))
            else:
                self.table.setItem(row, 4, QTableWidgetItem("-"))
            
            # 下载地址
            self.table.setItem(row, 5, QTableWidgetItem(record['url']))
            
    def clear_history(self):
        self.history.history = []
        self.history.save_history()
        self.table.setRowCount(0)
        
    def retry_download(self):
        selected_rows = set(item.row() for item in self.table.selectedItems())
        for row in selected_rows:
            url = self.table.item(row, 5).text()
            save_path = os.path.join(
                os.path.dirname(self.history.history[-(row+1)]['save_path']),
                self.table.item(row, 0).text()
            )
            self.parent().new_download_with_data({
                'url': url,
                'save_path': save_path
            }) 