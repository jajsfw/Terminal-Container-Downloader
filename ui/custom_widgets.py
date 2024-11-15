from PyQt6.QtWidgets import QPushButton, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

class ToolButton(QPushButton):
    def __init__(self, text="", icon_path=None, parent=None):
        super().__init__(text, parent)
        if icon_path:
            self.setIcon(QIcon(icon_path))
        self.setFixedHeight(32)
        self.setMinimumWidth(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
class StatusLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setMinimumWidth(100)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter) 