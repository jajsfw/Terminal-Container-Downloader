import os
import importlib.util
import inspect
from PyQt6.QtCore import QObject, pyqtSignal

class PluginBase:
    """插件基类"""
    def __init__(self, manager):
        self.manager = manager
        self.name = "Base Plugin"
        self.version = "1.0"
        self.description = "Base plugin description"
        
    def initialize(self):
        """插件初始化"""
        pass
        
    def cleanup(self):
        """插件清理"""
        pass
        
    def on_download_start(self, task_id, url, save_path):
        """下载开始时调用"""
        pass
        
    def on_download_progress(self, task_id, progress):
        """下载进度更新时调用"""
        pass
        
    def on_download_complete(self, task_id):
        """下载完成时调用"""
        pass
        
    def on_download_error(self, task_id, error):
        """下载出错时调用"""
        pass

class PluginManager(QObject):
    plugin_loaded = pyqtSignal(str)  # 插件名称
    plugin_error = pyqtSignal(str, str)  # 插件名称, 错误信息
    
    def __init__(self):
        super().__init__()
        self.plugins = {}
        self.plugin_dir = os.path.join(os.path.dirname(__file__), '..', 'plugins')
        
        # 创建插件目录
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            
    def load_plugins(self):
        """加载所有插件"""
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                self.load_plugin(filename)
                
    def load_plugin(self, filename):
        """加载单个插件"""
        try:
            module_name = filename[:-3]  # 移除.py后缀
            module_path = os.path.join(self.plugin_dir, filename)
            
            # 加载模块
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找插件类
            for item in dir(module):
                obj = getattr(module, item)
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginBase) and 
                    obj != PluginBase):
                    # 创建插件实例
                    plugin = obj(self)
                    self.plugins[module_name] = plugin
                    plugin.initialize()
                    self.plugin_loaded.emit(plugin.name)
                    break
                    
        except Exception as e:
            self.plugin_error.emit(filename, str(e))
            
    def notify_download_start(self, task_id, url, save_path):
        """通知所有插件下载开始"""
        for plugin in self.plugins.values():
            try:
                plugin.on_download_start(task_id, url, save_path)
            except Exception as e:
                self.plugin_error.emit(plugin.name, str(e))
                
    def notify_download_progress(self, task_id, progress):
        """通知所有插件下载进度"""
        for plugin in self.plugins.values():
            try:
                plugin.on_download_progress(task_id, progress)
            except Exception as e:
                self.plugin_error.emit(plugin.name, str(e))
                
    def notify_download_complete(self, task_id):
        """通知所有插件下载完成"""
        for plugin in self.plugins.values():
            try:
                plugin.on_download_complete(task_id)
            except Exception as e:
                self.plugin_error.emit(plugin.name, str(e))
                
    def notify_download_error(self, task_id, error):
        """通知所有插件下载错误"""
        for plugin in self.plugins.values():
            try:
                plugin.on_download_error(task_id, error)
            except Exception as e:
                self.plugin_error.emit(plugin.name, str(e)) 