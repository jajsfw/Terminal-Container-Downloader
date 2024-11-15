from PyQt6.QtCore import QObject, pyqtSignal
import os
import time
import shutil

class BTDownloadTask(QObject):
    status_updated = pyqtSignal(str, dict)
    
    def __init__(self, task_id, torrent_path, save_path):
        super().__init__()
        self.task_id = task_id
        self.torrent_path = torrent_path
        self.save_path = save_path
        self.status = "等待中"
        self.is_paused = False
        self.is_cancelled = False
        
    def start(self):
        try:
            self.status = "正在解析种子文件"
            self._update_status()
            
            # 模拟下载过程
            total_size = os.path.getsize(self.torrent_path)  # 使用种子文件大小作为示例
            downloaded_size = 0
            
            while downloaded_size < total_size and not self.is_cancelled:
                if self.is_paused:
                    self.status = "已暂停"
                    self._update_status()
                    time.sleep(1)
                    continue
                
                # 模拟下载进度
                chunk_size = min(8192, total_size - downloaded_size)
                downloaded_size += chunk_size
                time.sleep(0.1)  # 模拟下载延迟
                
                self.status = "下载中"
                self._update_status_with_progress(downloaded_size, total_size)
            
            if not self.is_cancelled:
                # 复制种子文件到目标位置（仅作为示例）
                dest_path = os.path.join(self.save_path, os.path.basename(self.torrent_path))
                shutil.copy2(self.torrent_path, dest_path)
                
                self.status = "完成"
                self._update_status_with_progress(total_size, total_size)
            
        except Exception as e:
            self.status = f"错误: {str(e)}"
            self._update_status()
    
    def pause(self):
        self.is_paused = True
        
    def resume(self):
        self.is_paused = False
        
    def cancel(self):
        self.is_cancelled = True
        
    def _update_status(self):
        status_dict = {
            'progress': 0,
            'speed': 0,
            'status': self.status,
            'total_size': 0,
            'downloaded_size': 0
        }
        self.status_updated.emit(self.task_id, status_dict)
        
    def _update_status_with_progress(self, downloaded_size, total_size):
        progress = (downloaded_size / total_size * 100) if total_size else 0
        status_dict = {
            'progress': progress,
            'speed': 8192,  # 模拟固定速度
            'status': self.status,
            'total_size': total_size,
            'downloaded_size': downloaded_size
        }
        self.status_updated.emit(self.task_id, status_dict)