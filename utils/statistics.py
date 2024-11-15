from PyQt6.QtCore import QObject, pyqtSignal
import json
import os
from datetime import datetime, timedelta
import time

class DownloadStatistics(QObject):
    stats_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.stats_file = "download_stats.json"
        self.stats = {
            'total_downloads': 0,
            'completed_downloads': 0,
            'failed_downloads': 0,
            'total_bytes': 0,
            'daily_stats': {},
            'current_speed': 0,
            'max_speed': 0,
            'average_speed': 0,
            'active_time': 0
        }
        self.start_time = time.time()
        self.load_stats()
        
    def load_stats(self):
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    saved_stats = json.load(f)
                    self.stats.update(saved_stats)
        except Exception as e:
            print(f"加载统计数据失败: {str(e)}")
            
    def save_stats(self):
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=4)
        except Exception as e:
            print(f"保存统计数据失败: {str(e)}")
            
    def update_speed(self, speed):
        self.stats['current_speed'] = speed
        self.stats['max_speed'] = max(speed, self.stats['max_speed'])
        self.stats['active_time'] = time.time() - self.start_time
        if self.stats['active_time'] > 0:
            self.stats['average_speed'] = self.stats['total_bytes'] / self.stats['active_time']
        self.stats_updated.emit(self.stats)
        
    def add_download(self):
        self.stats['total_downloads'] += 1
        self._update_daily_stats('started')
        self.save_stats()
        self.stats_updated.emit(self.stats)
        
    def complete_download(self, bytes_downloaded):
        self.stats['completed_downloads'] += 1
        self.stats['total_bytes'] += bytes_downloaded
        self._update_daily_stats('completed')
        self.save_stats()
        self.stats_updated.emit(self.stats)
        
    def fail_download(self):
        self.stats['failed_downloads'] += 1
        self._update_daily_stats('failed')
        self.save_stats()
        self.stats_updated.emit(self.stats)
        
    def _update_daily_stats(self, event_type):
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.stats['daily_stats']:
            self.stats['daily_stats'][today] = {
                'started': 0,
                'completed': 0,
                'failed': 0,
                'bytes': 0
            }
        self.stats['daily_stats'][today][event_type] += 1 