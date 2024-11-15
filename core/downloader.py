from threading import Thread, Lock
import requests
import time
from PyQt6.QtCore import QObject, pyqtSignal
from .bt_handler import BTDownloadTask
import os
import json
import urllib.parse

class DownloadManager(QObject):
    download_updated = pyqtSignal(str, dict)  # 发送下载进度更新信号
    
    def __init__(self):
        super().__init__()
        self.active_downloads = {}  # 使用字典存储活动下载
        self.completed_downloads = {}  # 存储已完成的下载
        self.max_concurrent = 3
        self.lock = Lock()
        self.proxy = None
        self.settings = None
        self.downloads_file = "downloads.json"  # 保存下载信息的文件
        self.progress_dir = "progress"  # 保存下载进度的目录
        self.tasks_file = "download_tasks.json"  # 保存任务信息的文件
        self.load_tasks()  # 加载保存的任务
        
        # 创建进度目录
        if not os.path.exists(self.progress_dir):
            os.makedirs(self.progress_dir)
            
    def initialize(self, settings):
        """初始化下载管理器"""
        self.settings = settings
        self.load_downloads()  # 加载保存的下载信息
        
    def load_downloads(self):
        """从文件加载下载信息"""
        try:
            if os.path.exists(self.downloads_file):
                with open(self.downloads_file, 'r', encoding='utf-8') as f:
                    downloads = json.load(f)
                    for task_data in downloads:
                        if task_data['status'] != '完成':  # 只恢复未完成的下载
                            self.resume_download_task(task_data)
        except Exception as e:
            print(f"加载下载信息失败: {str(e)}")
            
    def save_downloads(self):
        """保存下载信息到文件"""
        try:
            downloads = []
            for task_id, task in self.active_downloads.items():
                downloads.append({
                    'task_id': task_id,
                    'url': task.url,
                    'save_path': task.save_path,
                    'status': task.status,
                    'progress': task.progress,
                    'total_size': task.total_size,
                    'downloaded_size': task.downloaded_size
                })
            with open(self.downloads_file, 'w', encoding='utf-8') as f:
                json.dump(downloads, f, indent=4)
        except Exception as e:
            print(f"保存下载信息失败: {str(e)}")
        
    def add_download(self, url, save_path):
        task_id = str(time.time())
        download_task = DownloadTask(self, task_id, url, save_path)
        download_task.status_updated.connect(self._on_task_updated)
        
        with self.lock:
            thread = Thread(target=download_task.start)
            thread.daemon = True
            self.active_downloads[task_id] = download_task
            thread.start()
            self.save_downloads()  # 保存下载信息
            
        return task_id
        
    def resume_download_task(self, task_data):
        """恢复保存的下载任务"""
        task_id = task_data['task_id']
        download_task = DownloadTask(self, task_id, task_data['url'], task_data['save_path'])
        download_task.status_updated.connect(self._on_task_updated)
        download_task.total_size = task_data['total_size']
        download_task.downloaded_size = task_data['downloaded_size']
        
        with self.lock:
            thread = Thread(target=download_task.start)
            thread.daemon = True
            self.active_downloads[task_id] = download_task
            thread.start()
        
    def pause_download(self, task_id):
        if task_id in self.active_downloads:
            self.active_downloads[task_id].pause()
            self.save_downloads()
            
    def resume_download(self, task_id):
        if task_id in self.active_downloads:
            self.active_downloads[task_id].resume()
            self.save_downloads()
            
    def cancel_download(self, task_id):
        if task_id in self.active_downloads:
            self.active_downloads[task_id].cancel()
            del self.active_downloads[task_id]
            self.save_downloads()
            
    def _on_task_updated(self, task_id, status_dict):
        # 当下载完成时，移动到已完成列表
        if status_dict['status'] == '完成':
            task = self.active_downloads.get(task_id)
            if task:
                self.completed_downloads[task_id] = {
                    'task_id': task_id,
                    'url': task.url,
                    'save_path': task.save_path,
                    'status': '完成',
                    'total_size': task.total_size,
                    'downloaded_size': task.total_size,
                    'progress': 100
                }
                
        self.download_updated.emit(task_id, status_dict)
        self.save_downloads()  # 保存状态更新
        
    def add_torrent(self, torrent_path, save_path):
        task_id = str(time.time())
        download_task = BTDownloadTask(task_id, torrent_path, save_path)
        download_task.status_updated.connect(self._on_task_updated)
        
        with self.lock:
            thread = Thread(target=download_task.start)
            thread.daemon = True
            self.active_downloads[task_id] = download_task
            thread.start()
            self.save_downloads()
            
        return task_id
        
    def set_proxy(self, proxy_url):
        self.proxy = {'http': proxy_url, 'https': proxy_url} if proxy_url else None
        
    def save_progress(self, task_id, downloaded_size):
        """保存单个任务的下载进度"""
        progress_file = os.path.join(self.progress_dir, f"{task_id}.json")
        try:
            with open(progress_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'downloaded_size': downloaded_size,
                    'timestamp': time.time()
                }, f)
        except Exception as e:
            print(f"保存进度失败: {str(e)}")
            
    def load_progress(self, task_id):
        """加载任务的下载进度"""
        progress_file = os.path.join(self.progress_dir, f"{task_id}.json")
        try:
            if os.path.exists(progress_file):
                with open(progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 如果进度文件超过7天，则不使用
                    if time.time() - data['timestamp'] < 7 * 24 * 3600:
                        return data['downloaded_size']
        except Exception:
            pass
        return 0
        
    def cleanup_progress(self, task_id):
        """清理任务的进度文件"""
        progress_file = os.path.join(self.progress_dir, f"{task_id}.json")
        try:
            if os.path.exists(progress_file):
                os.remove(progress_file)
        except Exception:
            pass
        
    def load_tasks(self):
        """加载保存的下载任务"""
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                    for task_data in tasks:
                        if task_data['status'] == '完成':
                            self.completed_downloads[task_data['task_id']] = task_data
                        elif task_data['status'] != '已取消':
                            self.resume_task(task_data)
        except Exception as e:
            print(f"加载任务失败: {str(e)}")
            
    def save_tasks(self):
        """保存所有下载任务的信息"""
        try:
            tasks = []
            # 保存活动下载
            for task_id, task in self.active_downloads.items():
                tasks.append({
                    'task_id': task_id,
                    'url': task.url,
                    'save_path': task.save_path,
                    'status': task.status,
                    'progress': task.progress,
                    'total_size': task.total_size,
                    'downloaded_size': task.downloaded_size,
                    'is_paused': task.is_paused
                })
            # 保存已完成的下载
            tasks.extend(list(self.completed_downloads.values()))
            
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=4)
        except Exception as e:
            print(f"保存任务失败: {str(e)}")
            
    def resume_task(self, task_data):
        """恢复保存的任务"""
        task_id = task_data['task_id']
        task = DownloadTask(self, task_id, task_data['url'], task_data['save_path'])
        task.status_updated.connect(self._on_task_updated)
        task.total_size = task_data['total_size']
        task.downloaded_size = task_data['downloaded_size']
        task.is_paused = task_data.get('is_paused', False)
        
        with self.lock:
            thread = Thread(target=task.start)
            thread.daemon = True
            self.active_downloads[task_id] = task
            thread.start()
            
    def retry_download(self, task_id):
        if task_id in self.active_downloads:
            old_task = self.active_downloads[task_id]
            if old_task.status.startswith("错误"):
                # 创建新任务
                new_task_id = str(time.time())
                new_task = DownloadTask(self, new_task_id, old_task.url, old_task.save_path)
                new_task.status_updated.connect(self._on_task_updated)
                
                # 删除旧任务
                del self.active_downloads[task_id]
                
                # 启动新任务
                with self.lock:
                    thread = Thread(target=new_task.start)
                    thread.daemon = True
                    self.active_downloads[new_task_id] = new_task
                    thread.start()
                    
                self.save_tasks()
                return new_task_id
        return None

class DownloadTask(QObject):
    status_updated = pyqtSignal(str, dict)
    
    def __init__(self, manager, task_id, url, save_path):
        super().__init__()
        self.manager = manager
        self.task_id = task_id
        self.url = url
        self.original_save_path = save_path
        self.save_path = save_path
        self.temp_path = save_path + '.downloading'
        self.progress = 0
        self.speed = 0
        self.status = "等待中"
        self.total_size = 0
        self.downloaded_size = 0
        self.is_paused = False
        self.is_cancelled = False
        self.last_update_time = time.time()
        self.last_downloaded_size = 0
        self.headers = {'User-Agent': 'Mozilla/5.0'}  # 添加默认User-Agent
        self.retry_count = 0
        self.max_retries = 3
        self.chunk_timeout = 30
        
    def start(self):
        while self.retry_count < self.max_retries:
            try:
                self.status = "准备下载"
                self._update_status()
                
                # 获取文件信息和正确的扩展名
                response = requests.head(self.url, headers=self.headers, allow_redirects=True)
                response.raise_for_status()  # 检查响应状态
                
                # 从Content-Type获取扩展名
                content_type = response.headers.get('content-type', '')
                extension = self._get_extension_from_content_type(content_type)
                
                # 如果Content-Type没有提供有效扩展名，从URL或Content-Disposition获取
                if not extension:
                    extension = self._get_extension_from_url()
                    if not extension:
                        extension = self._get_extension_from_disposition(response.headers.get('content-disposition', ''))
                
                # 确保文件有正确的扩展名
                if extension and not self.save_path.lower().endswith(extension.lower()):
                    self.save_path = self.save_path + extension
                    self.temp_path = self.save_path + '.downloading'
                
                # 开始下载
                self.status = "下载中"
                self._update_status()
                
                download_response = requests.get(
                    self.url,
                    stream=True,
                    headers=self.headers,
                    timeout=self.chunk_timeout
                )
                download_response.raise_for_status()
                
                # 获取文件大小
                self.total_size = int(download_response.headers.get('content-length', 0))
                
                # 检查是否存在临时文件
                if os.path.exists(self.temp_path):
                    self.downloaded_size = os.path.getsize(self.temp_path)
                    if self.downloaded_size > 0:
                        self.headers['Range'] = f'bytes={self.downloaded_size}-'
                
                # 创建保存目录
                os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
                
                # 写入文件
                mode = 'ab' if self.downloaded_size > 0 else 'wb'
                with open(self.temp_path, mode) as f:
                    for chunk in download_response.iter_content(chunk_size=8192):
                        if self.is_cancelled:
                            return
                            
                        if self.is_paused:
                            self.status = "已暂停"
                            self._update_status()
                            while self.is_paused and not self.is_cancelled:
                                time.sleep(0.1)
                            if self.is_cancelled:
                                return
                            self.status = "下载中"
                            self._update_status()
                            
                        if chunk:
                            f.write(chunk)
                            self.downloaded_size += len(chunk)
                            self._calculate_speed()
                            self._update_status()
                
                # 下载完成后重命名文件
                if os.path.exists(self.save_path):
                    os.remove(self.save_path)
                os.rename(self.temp_path, self.save_path)
                
                self.status = "完成"
                self._update_status()
                return
                
            except requests.exceptions.RequestException as e:
                self.retry_count += 1
                if self.retry_count < self.max_retries:
                    self.status = f"重试 ({self.retry_count}/{self.max_retries})"
                    self._update_status()
                    time.sleep(2)  # 重试前等待
                else:
                    self.status = f"错误: {str(e)}"
                    self._update_status()
            except Exception as e:
                self.status = f"错误: {str(e)}"
                self._update_status()
                break
                
    def _get_extension_from_disposition(self, disposition):
        """从Content-Disposition获取扩展名"""
        import re
        if disposition:
            filename = re.findall("filename=(.+)", disposition)
            if filename:
                filename = filename[0].strip('"\'')
                return os.path.splitext(filename)[1]
        return ''
        
    def pause(self):
        self.is_paused = True
        self.status = "已暂停"
        self._update_status()
        
    def resume(self):
        self.is_paused = False
        self.status = "下载中"
        self._update_status()
        
    def cancel(self):
        self.is_cancelled = True
        self.status = "已取消"
        self._update_status()
        
    def _calculate_speed(self):
        current_time = time.time()
        time_diff = current_time - self.last_update_time
        
        if time_diff >= 1:  # 每秒更新一次速度
            size_diff = self.downloaded_size - self.last_downloaded_size
            self.speed = size_diff / time_diff
            self.last_update_time = current_time
            self.last_downloaded_size = self.downloaded_size
            
    def _update_status(self):
        progress = (self.downloaded_size / self.total_size * 100) if self.total_size else 0
        status_dict = {
            'progress': progress,
            'speed': self.speed,
            'status': self.status,
            'total_size': self.total_size,
            'downloaded_size': self.downloaded_size
        }
        self.status_updated.emit(self.task_id, status_dict)
        
    def _get_extension_from_url(self, url=None):
        """从URL中获取文件扩展名"""
        if url is None:
            url = self.url
        path = urllib.parse.urlparse(url).path
        ext = os.path.splitext(path)[1].lower()
        
        # 验证扩展名的有效性
        if ext and len(ext) <= 5 and ext[1:].isalnum():
            return ext
        return ''
        
    def _get_extension_from_content_type(self, content_type):
        """根据content-type获取文件扩展名"""
        content_type = content_type.lower()
        extension_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/bmp': '.bmp',
            'image/tiff': '.tiff',
            'image/svg+xml': '.svg',
            'video/mp4': '.mp4',
            'video/mpeg': '.mpeg',
            'video/x-msvideo': '.avi',
            'video/quicktime': '.mov',
            'video/x-matroska': '.mkv',
            'video/webm': '.webm',
            'audio/mpeg': '.mp3',
            'audio/wav': '.wav',
            'audio/x-m4a': '.m4a',
            'audio/ogg': '.ogg',
            'audio/x-ms-wma': '.wma',
            'application/pdf': '.pdf',
            'application/zip': '.zip',
            'application/x-rar-compressed': '.rar',
            'application/x-7z-compressed': '.7z',
            'application/x-tar': '.tar',
            'application/x-gzip': '.gz',
            'text/plain': '.txt',
            'text/html': '.html',
            'text/css': '.css',
            'text/javascript': '.js',
            'application/json': '.json',
            'application/xml': '.xml',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/vnd.ms-powerpoint': '.ppt',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx'
        }
        
        # 从Content-Type中提取主类型和子类型
        parts = content_type.split(';')[0].strip()
        return extension_map.get(parts, '')