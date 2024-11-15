from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor
import collections

class SpeedChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)
        self.speeds = collections.deque(maxlen=60)  # 保存最近60秒的速度
        self.max_speed = 1  # 防止除零错误
        
        # 更新定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)  # 每秒更新一次
        
    def add_speed(self, speed):
        self.speeds.append(speed)
        self.max_speed = max(max(self.speeds), 1)
        self.update()
        
    def paintEvent(self, event):
        if not self.speeds:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置画笔
        pen = QPen(QColor(0, 120, 215))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # 计算坐标
        width = self.width()
        height = self.height()
        x_step = width / (len(self.speeds) - 1) if len(self.speeds) > 1 else width
        
        # 绘制速度曲线
        path = []
        for i, speed in enumerate(self.speeds):
            x = i * x_step
            y = height - (speed / self.max_speed * height)
            path.append((x, y))
            
        # 绘制线条
        for i in range(len(path) - 1):
            painter.drawLine(
                int(path[i][0]), int(path[i][1]),
                int(path[i + 1][0]), int(path[i + 1][1])
            ) 