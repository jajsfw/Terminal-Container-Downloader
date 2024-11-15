from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtCore import QObject, pyqtSignal

class NotificationManager(QObject):
    notify = pyqtSignal(str, str)  # 标题, 消息
    
    def __init__(self, tray_icon):
        super().__init__()
        self.tray_icon = tray_icon
        self.notify.connect(self._show_notification)
        
    def _show_notification(self, title, message):
        if self.tray_icon and self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.Information,
                3000  # 显示3秒
            )
            
    def download_complete(self, filename):
        self.notify.emit("下载完成", f"文件 {filename} 已下载完成")
        
    def download_error(self, filename, error):
        self.notify.emit("下载错误", f"文件 {filename} 下载失败: {error}")
        
    def download_started(self, filename):
        self.notify.emit("开始下载", f"开始下载文件: {filename}") 