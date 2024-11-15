from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem)
from PyQt6.QtCore import Qt

class QueueDialog(QDialog):
    def __init__(self, queue_manager, parent=None):
        super().__init__(parent)
        self.queue_manager = queue_manager
        self.setWindowTitle("下载队列")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 创建队列表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["文件名", "URL/种子", "保存位置"])
        layout.addWidget(self.table)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        
        move_up_btn = QPushButton("上移")
        move_down_btn = QPushButton("下移")
        remove_btn = QPushButton("移除")
        close_btn = QPushButton("关闭")
        
        move_up_btn.clicked.connect(self.move_up_selected)
        move_down_btn.clicked.connect(self.move_down_selected)
        remove_btn.clicked.connect(self.remove_selected)
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(move_up_btn)
        btn_layout.addWidget(move_down_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # 连接信号
        self.queue_manager.queue_updated.connect(self.refresh_table)
        
        # 初始化表格
        self.refresh_table()
        
    def refresh_table(self):
        self.table.setRowCount(0)
        for task in self.queue_manager.waiting_queue:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(
                os.path.basename(task['save_path'])
            ))
            self.table.setItem(row, 1, QTableWidgetItem(
                task.get('url') or task.get('torrent_path')
            ))
            self.table.setItem(row, 2, QTableWidgetItem(task['save_path']))
            
    def move_up_selected(self):
        for item in self.table.selectedItems():
            row = item.row()
            if row > 0:
                task_id = list(self.queue_manager.waiting_queue)[row]['task_id']
                self.queue_manager.move_up(task_id)
                break
                
    def move_down_selected(self):
        for item in self.table.selectedItems():
            row = item.row()
            if row < self.table.rowCount() - 1:
                task_id = list(self.queue_manager.waiting_queue)[row]['task_id']
                self.queue_manager.move_down(task_id)
                break
                
    def remove_selected(self):
        for item in self.table.selectedItems():
            row = item.row()
            task_id = list(self.queue_manager.waiting_queue)[row]['task_id']
            self.queue_manager.remove_task(task_id)
            break 