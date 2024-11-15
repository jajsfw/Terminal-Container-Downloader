from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QTabWidget, QWidget, QTableWidget,
                           QTableWidgetItem)
from PyQt6.QtCore import Qt
import humanize
from datetime import datetime, timedelta

class StatisticsDialog(QDialog):
    def __init__(self, statistics, parent=None):
        super().__init__(parent)
        self.statistics = statistics
        self.setWindowTitle("下载统计")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 概览页
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        # 总体统计
        stats = self.statistics.stats
        overview_layout.addWidget(QLabel(f"总下载数: {stats['total_downloads']}"))
        overview_layout.addWidget(QLabel(f"完成下载: {stats['completed_downloads']}"))
        overview_layout.addWidget(QLabel(f"失败下载: {stats['failed_downloads']}"))
        overview_layout.addWidget(QLabel(
            f"总下载量: {humanize.naturalsize(stats['total_bytes'], binary=True)}"
        ))
        
        # 速度统计
        overview_layout.addWidget(QLabel("速度统计"))
        overview_layout.addWidget(QLabel(
            f"当前速度: {humanize.naturalsize(stats['current_speed'], binary=True)}/s"
        ))
        overview_layout.addWidget(QLabel(
            f"最大速度: {humanize.naturalsize(stats['max_speed'], binary=True)}/s"
        ))
        overview_layout.addWidget(QLabel(
            f"平均速度: {humanize.naturalsize(stats['average_speed'], binary=True)}/s"
        ))
        
        # 运行时间
        hours = stats['active_time'] // 3600
        minutes = (stats['active_time'] % 3600) // 60
        overview_layout.addWidget(QLabel(f"运行时间: {int(hours)}小时{int(minutes)}分钟"))
        
        tab_widget.addTab(overview_tab, "概览")
        
        # 每日统计页
        daily_tab = QWidget()
        daily_layout = QVBoxLayout(daily_tab)
        
        daily_table = QTableWidget()
        daily_table.setColumnCount(5)
        daily_table.setHorizontalHeaderLabels([
            "日期", "开始下载", "完成下载", "失败下载", "下载量"
        ])
        
        # 填充每日数据
        row = 0
        for date, data in sorted(stats['daily_stats'].items(), reverse=True):
            daily_table.insertRow(row)
            daily_table.setItem(row, 0, QTableWidgetItem(date))
            daily_table.setItem(row, 1, QTableWidgetItem(str(data['started'])))
            daily_table.setItem(row, 2, QTableWidgetItem(str(data['completed'])))
            daily_table.setItem(row, 3, QTableWidgetItem(str(data['failed'])))
            daily_table.setItem(row, 4, QTableWidgetItem(
                humanize.naturalsize(data.get('bytes', 0), binary=True)
            ))
            row += 1
            
        daily_layout.addWidget(daily_table)
        tab_widget.addTab(daily_tab, "每日统计")
        
        layout.addWidget(tab_widget)
        
        # 按钮
        btn_layout = QHBoxLayout()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout) 