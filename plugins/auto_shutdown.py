from utils.plugin_manager import PluginBase
import os
import platform
import subprocess
import time
from PyQt6.QtWidgets import QMessageBox

class AutoShutdownPlugin(PluginBase):
    def __init__(self, manager):
        super().__init__(manager)
        self.name = "自动关机插件"
        self.version = "1.0"
        self.description = "所有下载完成后自动关机"
        self.active_downloads = 0
        self.shutdown_scheduled = False
        
    def on_download_start(self, task_id, url, save_path):
        self.active_downloads += 1
        self.shutdown_scheduled = False
        
    def on_download_complete(self, task_id):
        self.active_downloads -= 1
        self._check_shutdown()
        
    def on_download_error(self, task_id, error):
        self.active_downloads -= 1
        self._check_shutdown()
        
    def _check_shutdown(self):
        if self.active_downloads <= 0 and not self.shutdown_scheduled:
            response = QMessageBox.question(
                self.manager.main_window,
                "自动关机",
                "所有下载已完成，是否关机？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if response == QMessageBox.StandardButton.Yes:
                self.shutdown_scheduled = True
                self._schedule_shutdown()
                
    def _schedule_shutdown(self):
        try:
            # 等待1分钟后关机
            if platform.system() == "Windows":
                subprocess.run(["shutdown", "/s", "/t", "60"])
                QMessageBox.information(
                    self.manager.main_window,
                    "自动关机",
                    "系统将在1分钟后关机。\n如要取消，请在命令行中运行: shutdown /a"
                )
            else:  # Linux/Mac
                subprocess.run(["shutdown", "-h", "+1"])
                QMessageBox.information(
                    self.manager.main_window,
                    "自动关机",
                    "系统将在1分钟后关机。\n如要取消，请在终端中运行: shutdown -c"
                )
        except Exception as e:
            QMessageBox.warning(
                self.manager.main_window,
                "错误",
                f"设置自动关机失败: {str(e)}"
            ) 