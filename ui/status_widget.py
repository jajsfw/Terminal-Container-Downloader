from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
import humanize

class StatusWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        
        # 活动下载数
        self.active_label = QLabel("活动: 0")
        self.active_label.setFixedWidth(80)
        
        # 等待下载数
        self.waiting_label = QLabel("等待: 0")
        self.waiting_label.setFixedWidth(80)
        
        # 已完成数
        self.completed_label = QLabel("完成: 0")
        self.completed_label.setFixedWidth(80)
        
        # 总下载量
        self.total_size_label = QLabel("总下载: 0 B")
        self.total_size_label.setFixedWidth(150)
        
        # 平均速度
        self.avg_speed_label = QLabel("平均: 0 B/s")
        self.avg_speed_label.setFixedWidth(120)
        
        layout.addWidget(self.active_label)
        layout.addWidget(self.waiting_label)
        layout.addWidget(self.completed_label)
        layout.addWidget(self.total_size_label)
        layout.addWidget(self.avg_speed_label)
        layout.addStretch()
        
    def update_stats(self, stats):
        self.active_label.setText(f"活动: {len(stats['active_downloads'])}")
        self.waiting_label.setText(f"等待: {len(stats['waiting_downloads'])}")
        self.completed_label.setText(f"完成: {stats['completed_downloads']}")
        self.total_size_label.setText(
            f"总下载: {humanize.naturalsize(stats['total_bytes'], binary=True)}"
        )
        self.avg_speed_label.setText(
            f"平均: {humanize.naturalsize(stats['average_speed'], binary=True)}/s"
        ) 