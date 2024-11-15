from utils.plugin_manager import PluginBase
import os
import shutil
import time
from datetime import datetime

class AutoBackupPlugin(PluginBase):
    def __init__(self, manager):
        super().__init__(manager)
        self.name = "自动备份插件"
        self.version = "1.0"
        self.description = "自动备份下载完成的文件"
        self.backup_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'backups'
        )
        
        # 创建备份目录
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
    def on_download_complete(self, task_id):
        download_task = self.manager.main_window.download_manager.active_downloads.get(task_id)
        if not download_task:
            return
            
        file_path = download_task.save_path
        if not os.path.exists(file_path):
            return
            
        try:
            # 创建以日期命名的备份目录
            date_dir = os.path.join(
                self.backup_dir,
                datetime.now().strftime('%Y-%m-%d')
            )
            if not os.path.exists(date_dir):
                os.makedirs(date_dir)
                
            # 备份文件
            filename = os.path.basename(file_path)
            backup_path = os.path.join(date_dir, filename)
            
            # 如果文件已存在，添加时间戳
            if os.path.exists(backup_path):
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime('%H-%M-%S')
                backup_path = os.path.join(date_dir, f"{name}_{timestamp}{ext}")
                
            # 复制文件
            shutil.copy2(file_path, backup_path)
            print(f"文件已备份到: {backup_path}")
            
            # 清理旧备份（保留最近7天）
            self._cleanup_old_backups()
            
        except Exception as e:
            print(f"备份失败: {str(e)}")
            
    def _cleanup_old_backups(self):
        """清理7天前的备份"""
        current_time = time.time()
        for date_dir in os.listdir(self.backup_dir):
            dir_path = os.path.join(self.backup_dir, date_dir)
            if os.path.isdir(dir_path):
                # 获取目录的修改时间
                dir_time = os.path.getmtime(dir_path)
                # 如果目录超过7天
                if current_time - dir_time > 7 * 24 * 3600:
                    try:
                        shutil.rmtree(dir_path)
                        print(f"已清理旧备份: {date_dir}")
                    except Exception as e:
                        print(f"清理备份失败: {str(e)}") 