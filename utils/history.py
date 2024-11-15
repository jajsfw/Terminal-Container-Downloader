import json
import os
from datetime import datetime

class DownloadHistory:
    def __init__(self, history_file):
        self.history_file = history_file
        self.history = self.load_history()
        
    def load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception:
            return []
            
    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            print(f"保存历史记录失败: {str(e)}")
            
    def add_record(self, task_id, url, save_path, file_size):
        record = {
            'task_id': task_id,
            'url': url,
            'save_path': save_path,
            'file_size': file_size,
            'start_time': datetime.now().isoformat(),
            'status': '进行中'
        }
        self.history.append(record)
        self.save_history()
        
    def update_record(self, task_id, status):
        for record in self.history:
            if record['task_id'] == task_id:
                record['status'] = status
                record['end_time'] = datetime.now().isoformat()
                break
        self.save_history() 