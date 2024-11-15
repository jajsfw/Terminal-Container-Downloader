from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QProgressBar, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt, QTimer
import humanize
import os
from datetime import timedelta

class DownloadInfoDialog(QDialog):
    def __init__(self, task_id, download_manager, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.download_manager = download_manager
        self.task = download_manager.active_downloads.get(task_id)
        
        self.setWindowTitle("下载信息")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QVBoxLayout()
        
        # 文件名
        self.filename_label = QLabel(os.path.basename(self.task.save_path))
        basic_layout.addWidget(self.filename_label)
        
        # 保存路径
        path_text = QTextEdit()
        path_text.setPlainText(self.task.save_path)
        path_text.setReadOnly(True)
        path_text.setMaximumHeight(60)
        basic_layout.addWidget(path_text)
        
        # 下载地址
        url_text = QTextEdit()
        url_text.setPlainText(self.task.url)
        url_text.setReadOnly(True)
        url_text.setMaximumHeight(60)
        basic_layout.addWidget(url_text)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 下载进度组
        progress_group = QGroupBox("下载进度")
        progress_layout = QVBoxLayout()
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        progress_layout.addWidget(self.progress_bar)
        
        # 下载信息
        info_layout = QHBoxLayout()
        self.speed_label = QLabel("速度: 0 B/s")
        self.size_label = QLabel("大小: 0 B")
        self.time_label = QLabel("剩余时间: --:--:--")
        info_layout.addWidget(self.speed_label)
        info_layout.addWidget(self.size_label)
        info_layout.addWidget(self.time_label)
        progress_layout.addLayout(info_layout)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # 状态信息组
        status_group = QGroupBox("状态信息")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("状态: 等待中")
        status_layout.addWidget(self.status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
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
        """更新显示的信息"""
        if self.task_id not in self.download_manager.active_downloads:
            self.update_timer.stop()
            return
            
        task = self.download_manager.active_downloads[self.task_id]
        
        # 更新进度条
        progress = (task.downloaded_size / task.total_size * 100) if task.total_size else 0
        self.progress_bar.setValue(int(progress))
        
        # 更新速度
        speed_text = humanize.naturalsize(task.speed, binary=True) + "/s"
        self.speed_label.setText(f"速度: {speed_text}")
        
        # 更新大小
        total_size = humanize.naturalsize(task.total_size, binary=True)
        downloaded_size = humanize.naturalsize(task.downloaded_size, binary=True)
        self.size_label.setText(f"大小: {downloaded_size} / {total_size}")
        
        # 更新剩余时间
        if task.speed > 0:
            remaining_bytes = task.total_size - task.downloaded_size
            remaining_seconds = remaining_bytes / task.speed
            remaining_time = str(timedelta(seconds=int(remaining_seconds)))
            self.time_label.setText(f"剩余时间: {remaining_time}")
        else:
            self.time_label.setText("剩余时间: --:--:--")
            
        # 更新状态
        self.status_label.setText(f"状态: {task.status}")
        
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
        self.accept() 