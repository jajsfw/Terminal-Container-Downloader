from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

class SystemTray(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon("resources/icon.png"))  # 需要添加一个图标文件
        self.setVisible(True)
        
        # 创建托盘菜单
        self.menu = QMenu()
        
        # 显示主窗口动作
        show_action = self.menu.addAction("显示主窗口")
        show_action.triggered.connect(parent.show)
        
        # 添加分隔符
        self.menu.addSeparator()
        
        # 退出动作
        quit_action = self.menu.addAction("退出")
        quit_action.triggered.connect(parent.close)
        
        self.setContextMenu(self.menu)
        
        # 连接信号
        self.activated.connect(self.on_tray_activated)
        
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.parent().show() 