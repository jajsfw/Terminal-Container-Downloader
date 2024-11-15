import sys
import os

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow

def init_resources():
    """初始化资源目录"""
    resources_dir = os.path.join(current_dir, 'resources')
    icons_dir = os.path.join(resources_dir, 'icons')
    sounds_dir = os.path.join(resources_dir, 'sounds')
    
    # 创建资源目录
    for directory in [resources_dir, icons_dir, sounds_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            
    # 创建必要的数据目录
    data_dirs = ['downloads', 'plugins', 'themes', 'logs', 'backups']
    for directory in data_dirs:
        dir_path = os.path.join(current_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

def main():
    try:
        # 初始化资源
        init_resources()
        
        # 创建应用
        app = QApplication(sys.argv)
        
        # 设置应用程序信息
        app.setApplicationName("Terminal Container Downloader")
        app.setOrganizationName("DownloadManager")
        
        # 设置应用图标
        icon_path = os.path.join(current_dir, 'resources', 'icons', 'app.png')
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        
        # 创建并显示主窗口
        window = MainWindow()
        window.show()
        
        return app.exec()
    except Exception as e:
        print(f"启动错误: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
