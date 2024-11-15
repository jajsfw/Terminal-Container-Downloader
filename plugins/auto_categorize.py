from utils.plugin_manager import PluginBase
import os
import shutil
import mimetypes

class AutoCategorizePlugin(PluginBase):
    def __init__(self, manager):
        super().__init__(manager)
        self.name = "自动分类插件"
        self.version = "1.0"
        self.description = "根据文件类型自动分类下载文件"
        
        # 文件类型映射
        self.type_dirs = {
            'image': '图片',
            'video': '视频',
            'audio': '音乐',
            'text': '文档',
            'application': '应用程序',
            'archive': '压缩文件'
        }
        
    def on_download_complete(self, task_id):
        download_task = self.manager.main_window.download_manager.active_downloads.get(task_id)
        if not download_task:
            return
            
        file_path = download_task.save_path
        if not os.path.exists(file_path):
            return
            
        # 获取文件类型
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            return
            
        main_type = mime_type.split('/')[0]
        
        # 特殊处理压缩文件
        if mime_type in ['application/zip', 'application/x-rar-compressed',
                        'application/x-7z-compressed']:
            main_type = 'archive'
            
        # 获取目标目录
        if main_type in self.type_dirs:
            category_dir = os.path.join(
                os.path.dirname(file_path),
                self.type_dirs[main_type]
            )
            
            try:
                # 创建分类目录
                if not os.path.exists(category_dir):
                    os.makedirs(category_dir)
                    
                # 移动文件
                dest_path = os.path.join(category_dir, os.path.basename(file_path))
                
                # 处理文件名冲突
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(dest_path)
                    counter = 1
                    while os.path.exists(dest_path):
                        dest_path = f"{base}_{counter}{ext}"
                        counter += 1
                        
                shutil.move(file_path, dest_path)
                print(f"文件已移动到: {dest_path}")
                
            except Exception as e:
                print(f"移动文件失败: {str(e)}") 