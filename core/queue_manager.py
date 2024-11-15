from PyQt6.QtCore import QObject, pyqtSignal
from collections import deque
import json
import os

class QueueManager(QObject):
    queue_updated = pyqtSignal()
    
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.waiting_queue = deque()
        self.queue_file = "download_queue.json"
        self.load_queue()
        
    def add_task(self, task_data):
        self.waiting_queue.append(task_data)
        self.save_queue()
        self.queue_updated.emit()
        
    def get_next_task(self):
        if self.waiting_queue:
            task = self.waiting_queue.popleft()
            self.save_queue()
            self.queue_updated.emit()
            return task
        return None
        
    def remove_task(self, task_id):
        self.waiting_queue = deque(
            task for task in self.waiting_queue 
            if task['task_id'] != task_id
        )
        self.save_queue()
        self.queue_updated.emit()
        
    def move_up(self, task_id):
        for i, task in enumerate(self.waiting_queue):
            if task['task_id'] == task_id and i > 0:
                self.waiting_queue[i], self.waiting_queue[i-1] = \
                    self.waiting_queue[i-1], self.waiting_queue[i]
                self.save_queue()
                self.queue_updated.emit()
                break
                
    def move_down(self, task_id):
        for i, task in enumerate(self.waiting_queue):
            if task['task_id'] == task_id and i < len(self.waiting_queue) - 1:
                self.waiting_queue[i], self.waiting_queue[i+1] = \
                    self.waiting_queue[i+1], self.waiting_queue[i]
                self.save_queue()
                self.queue_updated.emit()
                break
                
    def save_queue(self):
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.waiting_queue), f, indent=4)
        except Exception as e:
            print(f"保存队列失败: {str(e)}")
            
    def load_queue(self):
        try:
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    self.waiting_queue = deque(json.load(f))
        except Exception as e:
            print(f"加载队列失败: {str(e)}")
            self.waiting_queue = deque() 