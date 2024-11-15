from utils.plugin_manager import PluginBase
import os
import re

class AutoRenamePlugin(PluginBase):
    def __init__(self, manager):
        super().__init__(manager)
        self.name = "自动重命名插件"
        self.version = "1.0"
        self.description = "根据文件内容自动重命名下载文件"
        
    def on_download_complete(self, task_id):
        download_task = self.manager.main_window.download_manager.active_downloads.get(task_id)
        if not download_task:
            return
            
        file_path = download_task.save_path
        if not os.path.exists(file_path):
            return
            
        # 获取文件名和扩展名
        dir_path = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        
        # 清理文件名
        new_name = self._clean_filename(name)
        
        # 如果文件名发生变化，进行重命名
        if new_name != name:
            new_path = os.path.join(dir_path, new_name + ext)
            try:
                # 如果目标文件已存在，添加数字后缀
                if os.path.exists(new_path):
                    counter = 1
                    while os.path.exists(new_path):
                        new_path = os.path.join(dir_path, f"{new_name}_{counter}{ext}")
                        counter += 1
                
                os.rename(file_path, new_path)
                print(f"文件已重命名: {filename} -> {os.path.basename(new_path)}")
                
            except Exception as e:
                print(f"重命名失败: {str(e)}")
                
    def _clean_filename(self, name):
        # 移除特殊字符
        name = re.sub(r'[\\/*?:"<>|]', '', name)
        # 替换多个空格为单个空格
        name = re.sub(r'\s+', ' ', name)
        # 移除首尾空格
        name = name.strip()
        return name 