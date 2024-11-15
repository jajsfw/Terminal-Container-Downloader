from utils.plugin_manager import PluginBase
import zipfile
import os

class AutoExtractPlugin(PluginBase):
    def __init__(self, manager):
        super().__init__(manager)
        self.name = "自动解压插件"
        self.version = "1.0"
        self.description = "下载完成后自动解压压缩文件"
        
    def on_download_complete(self, task_id):
        # 获取下载文件路径
        download_task = self.manager.main_window.download_manager.active_downloads.get(task_id)
        if not download_task:
            return
            
        file_path = download_task.save_path
        if not os.path.exists(file_path):
            return
            
        # 检查是否是zip文件
        if file_path.lower().endswith('.zip'):
            try:
                # 创建解压目录
                extract_dir = os.path.splitext(file_path)[0]
                if not os.path.exists(extract_dir):
                    os.makedirs(extract_dir)
                    
                # 解压文件
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                    
                print(f"已自动解压文件到: {extract_dir}")
                
            except Exception as e:
                print(f"解压失败: {str(e)}") 