from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QTabWidget, QWidget, QTextEdit,
                           QFormLayout, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
import humanize
from datetime import datetime

class TaskDetailsDialog(QDialog):
    def __init__(self, task_id, download_manager, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.download_manager = download_manager
        self.task = download_manager.active_downloads.get(task_id)
        
        self.setWindowTitle("下载详情")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 基本信息页
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        
        # 文件名
        self.filename_label = QLabel(os.path.basename(self.task.save_path))
        basic_layout.addRow("文件名:", self.filename_label)
        
        # 下载地址
        url_text = QTextEdit()
        url_text.setPlainText(self.task.url)
        url_text.setReadOnly(True)
        url_text.setMaximumHeight(60)
        basic_layout.addRow("下载地址:", url_text)
        
        # 保存路径
        path_text = QTextEdit()
        path_text.setPlainText(self.task.save_path)
        path_text.setReadOnly(True)
        path_text.setMaximumHeight(60)
        basic_layout.addRow("保存路径:", path_text)
        
        # 文件大小
        self.size_label = QLabel()
        basic_layout.addRow("文件大小:", self.size_label)
        
        # 下载进度
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        basic_layout.addRow("下载进度:", self.progress_bar)
        
        # 下载速度
        self.speed_label = QLabel()
        basic_layout.addRow("当前速度:", self.speed_label)
        
        # 已下载大小
        self.downloaded_label = QLabel()
        basic_layout.addRow("已下载:", self.downloaded_label)
        
        # 剩余大小
        self.remaining_label = QLabel()
        basic_layout.addRow("剩余:", self.remaining_label)
        
        # 剩余时间
        self.time_label = QLabel()
        basic_layout.addRow("预计剩余时间:", self.time_label)
        
        # 状态
        self.status_label = QLabel()
        basic_layout.addRow("当前状态:", self.status_label)
        
        tab_widget.addTab(basic_tab, "基本信息")
        
        # 添加标签页到主布局
        layout.addWidget(tab_widget)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        # 控制按钮
        self.pause_btn = QPushButton("暂停")
        self.resume_btn = QPushButton("继续")
        self.cancel_btn = QPushButton("取消")
        close_btn = QPushButton("关闭")
        
        self.pause_btn.clicked.connect(self.pause_download)
        self.resume_btn.clicked.connect(self.resume_download)
        self.cancel_btn.clicked.connect(self.cancel_download)
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.resume_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # 更新定时器
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_info)
        self.update_timer.start(1000)  # 每秒更新一次
        
        # 初始更新
        self.update_info()
        
    def update_info(self):
        """更新显示的��息"""
        if self.task_id not in self.download_manager.active_downloads:
            self.update_timer.stop()
            return
            
        task = self.download_manager.active_downloads[self.task_id]
        
        # 更新文件大小
        self.size_label.setText(humanize.naturalsize(task.total_size, binary=True))
        
        # 更新进度
        progress = (task.downloaded_size / task.total_size * 100) if task.total_size else 0
        self.progress_bar.setValue(int(progress))
        
        # 更新速度
        self.speed_label.setText(humanize.naturalsize(task.speed, binary=True) + "/s")
        
        # 更新已下载大小
        self.downloaded_label.setText(humanize.naturalsize(task.downloaded_size, binary=True))
        
        # 更新剩余大小
        remaining_size = task.total_size - task.downloaded_size
        self.remaining_label.setText(humanize.naturalsize(remaining_size, binary=True))
        
        # 更新剩余时间
        if task.speed > 0:
            remaining_seconds = remaining_size / task.speed
            remaining_time = str(timedelta(seconds=int(remaining_seconds)))
            self.time_label.setText(remaining_time)
        else:
            self.time_label.setText("--:--:--")
            
        # 更新状态
        self.status_label.setText(task.status)
        
        # 更新按钮状态
        self.pause_btn.setEnabled(not task.is_paused and task.status == "下载中")
        self.resume_btn.setEnabled(task.is_paused)
        self.cancel_btn.setEnabled(task.status not in ["完成", "已取消"])
        
    def pause_download(self):
        self.download_manager.pause_download(self.task_id)
        
    def resume_download(self):
        self.download_manager.resume_download(self.task_id)
        
    def cancel_download(self):
        self.download_manager.cancel_download(self.task_id) 