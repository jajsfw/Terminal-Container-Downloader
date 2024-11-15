from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QTableWidget, QTableWidgetItem,
                           QToolBar, QStatusBar, QFileDialog, QHeaderView, QMenu, QHBoxLayout, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QDesktopServices, QColor
from .download_dialog import NewDownloadDialog
from core.downloader import DownloadManager
import humanize
from .system_tray import SystemTray
import os
from datetime import datetime, timedelta
from .settings_dialog import SettingsDialog
from utils.settings import Settings
from utils.history import DownloadHistory
from .history_dialog import HistoryDialog
from .proxy_dialog import ProxyDialog
from .speed_chart import SpeedChart
from utils.notification import NotificationManager
from utils.statistics import DownloadStatistics
from .progress_bar import DownloadProgressBar
from utils.sound import SoundManager
from utils.plugin_manager import PluginManager
from utils.theme_manager import ThemeManager
from .theme_dialog import ThemeDialog
from .plugin_dialog import PluginDialog
from .status_widget import StatusWidget
from .task_details_dialog import TaskDetailsDialog
from .download_info_dialog import DownloadInfoDialog
from .custom_widgets import ToolButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            self.setWindowTitle("Terminal Container Downloader")
            self.setMinimumSize(800, 600)
            
            # 创建主要部件
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.layout = QVBoxLayout(self.central_widget)
            
            # 首先创建设置管理器
            self.settings = Settings()
            
            # 创建下载管理器并初始化
            self.download_manager = DownloadManager()
            self.download_manager.initialize(self.settings)
            self.download_manager.download_updated.connect(self.update_download_status)
            
            # 创建工具栏
            self.toolbar = QToolBar()
            self.addToolBar(self.toolbar)
            self.create_toolbar()
            
            # 创建下载列表
            self.create_download_list()
            
            # 创建状态栏
            self.statusBar = QStatusBar()
            self.setStatusBar(self.statusBar)
            
            # 添加下载项映射
            self.download_rows = {}
            
            # 添加系统托盘
            self.tray = SystemTray(self)
            
            # 添加历史记录管理
            self.history = DownloadHistory(self.settings.get('history_file'))
            
            # 添加速度图表
            self.speed_chart = SpeedChart()
            self.speed_chart.setFixedHeight(100)
            
            # 添加通知管理器
            self.notification_manager = NotificationManager(self.tray)
            
            # 添加统计管理器
            self.statistics = DownloadStatistics()
            self.statistics.stats_updated.connect(self.update_status_bar)
            
            # 添加声音管理器
            self.sound_manager = SoundManager()
            
            # 添加主题管理器
            self.theme_manager = ThemeManager()
            self.theme_manager.theme_changed.connect(self.apply_theme)
            
            # 添加插件管理器
            self.plugin_manager = PluginManager()
            self.plugin_manager.plugin_loaded.connect(self.on_plugin_loaded)
            self.plugin_manager.plugin_error.connect(self.on_plugin_error)
            
            # 创建状态组件
            self.status_widget = StatusWidget(self)
            self.statusBar.addPermanentWidget(self.status_widget)
            
            # 加载已保存的下载
            self.load_saved_downloads()
            
            # 应用默认主题
            self.apply_theme(self.theme_manager.current_theme)
            
            # 加载插件
            self.plugin_manager.load_plugins()
            
        except Exception as e:
            print(f"主窗口初始化错误: {str(e)}")
            raise
        
    def create_toolbar(self):
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setStyleSheet("""
            QToolBar {
                spacing: 5px;
                padding: 5px;
            }
        """)
        self.addToolBar(toolbar)
        
        # 下载控制组
        download_group = QWidget()
        download_layout = QHBoxLayout(download_group)
        download_layout.setContentsMargins(0, 0, 0, 0)
        download_layout.setSpacing(5)
        
        # 创建按钮
        new_download_btn = ToolButton("新建下载", "resources/icons/new.png")
        import_torrent_btn = ToolButton("导入种子", "resources/icons/torrent.png")
        
        self.pause_btn = ToolButton("暂停", "resources/icons/pause.png")
        self.resume_btn = ToolButton("继续", "resources/icons/resume.png")
        self.cancel_btn = ToolButton("取消", "resources/icons/cancel.png")
        self.retry_btn = ToolButton("重试", "resources/icons/retry.png")
        
        # 添加按钮到布局
        download_layout.addWidget(new_download_btn)
        download_layout.addWidget(import_torrent_btn)
        download_layout.addWidget(self.pause_btn)
        download_layout.addWidget(self.resume_btn)
        download_layout.addWidget(self.cancel_btn)
        download_layout.addWidget(self.retry_btn)
        
        toolbar.addWidget(download_group)
        toolbar.addSeparator()
        
        # 设置按钮组
        settings_group = QWidget()
        settings_layout = QHBoxLayout(settings_group)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(5)
        
        settings_btn = ToolButton("设置", "resources/icons/settings.png")
        history_btn = ToolButton("历史记录", "resources/icons/history.png")
        proxy_btn = ToolButton("代理设置", "resources/icons/proxy.png")
        theme_btn = ToolButton("主题设置", "resources/icons/theme.png")
        plugin_btn = ToolButton("插件管理", "resources/icons/plugin.png")
        
        settings_layout.addWidget(settings_btn)
        settings_layout.addWidget(history_btn)
        settings_layout.addWidget(proxy_btn)
        settings_layout.addWidget(theme_btn)
        settings_layout.addWidget(plugin_btn)
        
        toolbar.addWidget(settings_group)
        
        # 连接信号
        new_download_btn.clicked.connect(self.new_download)
        import_torrent_btn.clicked.connect(self.import_torrent)
        self.pause_btn.clicked.connect(self.pause_selected)
        self.resume_btn.clicked.connect(self.resume_selected)
        self.cancel_btn.clicked.connect(self.cancel_selected)
        self.retry_btn.clicked.connect(self.retry_selected)
        settings_btn.clicked.connect(self.show_settings)
        history_btn.clicked.connect(self.show_history)
        proxy_btn.clicked.connect(self.show_proxy_settings)
        theme_btn.clicked.connect(self.show_theme_settings)
        plugin_btn.clicked.connect(self.show_plugin_manager)
        
    def create_download_list(self):
        self.download_table = QTableWidget()
        self.download_table.setColumnCount(6)
        self.download_table.setHorizontalHeaderLabels([
            "文件名", "大小", "进度", "速度", "剩余时间", "状态"
        ])
        
        # 设置表格属性
        self.download_table.setAlternatingRowColors(True)
        self.download_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.download_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.download_table.verticalHeader().setVisible(False)
        self.download_table.setShowGrid(False)
        
        # 设置列宽
        header = self.download_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        
        self.download_table.setColumnWidth(1, 100)
        self.download_table.setColumnWidth(2, 200)
        self.download_table.setColumnWidth(3, 100)
        self.download_table.setColumnWidth(4, 100)
        self.download_table.setColumnWidth(5, 100)
        
        # 设置样式
        self.download_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: transparent;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #E0E0E0;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 5px;
                border: none;
                border-bottom: 2px solid #2196F3;
            }
        """)
        
        # 添加到主布局
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 10, 10, 10)
        container_layout.setSpacing(10)
        
        container_layout.addWidget(self.download_table)
        
        # 添加速度图表
        self.speed_chart = SpeedChart()
        self.speed_chart.setFixedHeight(100)
        self.speed_chart.setStyleSheet("background-color: white; border: 1px solid #E0E0E0;")
        container_layout.addWidget(self.speed_chart)
        
        self.layout.addWidget(container)
        
    def load_saved_downloads(self):
        """加载已保存的下载任务到列表中"""
        # 加载活动下载
        for task_id, task in self.download_manager.active_downloads.items():
            self.add_download_to_table(task_id, {
                'url': task.url,
                'save_path': task.save_path
            })
            
        # 加载已完成的下载
        for task_id, task_data in self.download_manager.completed_downloads.items():
            row = self.download_table.rowCount()
            self.download_table.insertRow(row)
            self.download_rows[task_id] = row
            
            # 设置文件名
            filename_item = QTableWidgetItem(os.path.basename(task_data['save_path']))
            filename_item.setToolTip(task_data['save_path'])
            self.download_table.setItem(row, 0, filename_item)
            
            # 设置大小
            size_text = humanize.naturalsize(task_data['total_size'], binary=True)
            self.download_table.setItem(row, 1, QTableWidgetItem(size_text))
            
            # 设置进度条
            progress_bar = DownloadProgressBar()
            progress_bar.setProgress(100, "完成")
            self.download_table.setCellWidget(row, 2, progress_bar)
            
            # 设置速度
            self.download_table.setItem(row, 3, QTableWidgetItem("-"))
            
            # 设置剩余时间
            self.download_table.setItem(row, 4, QTableWidgetItem("-"))
            
            # 设置状态
            status_item = QTableWidgetItem("完成")
            status_item.setForeground(QColor(self.theme_manager.current_theme['success_color']))
            self.download_table.setItem(row, 5, status_item)
        
    def new_download(self):
        dialog = NewDownloadDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            task_id = self.download_manager.add_download(
                data['url'], 
                data['save_path']
            )
            self.add_download_to_table(task_id, data)
            
    def add_download_to_table(self, task_id, data):
        row = self.download_table.rowCount()
        self.download_table.insertRow(row)
        self.download_rows[task_id] = row
        
        # 文件名
        filename_item = QTableWidgetItem(os.path.basename(data['save_path']))
        filename_item.setToolTip(data['save_path'])  # 显示完整路径
        self.download_table.setItem(row, 0, filename_item)
        
        # 大小
        self.download_table.setItem(row, 1, QTableWidgetItem("计算中..."))
        
        # 进度条
        progress_bar = DownloadProgressBar()
        self.download_table.setCellWidget(row, 2, progress_bar)
        
        # 速度
        self.download_table.setItem(row, 3, QTableWidgetItem("0 B/s"))
        
        # 剩余时间
        self.download_table.setItem(row, 4, QTableWidgetItem("--:--:--"))
        
        # 状态
        status_item = QTableWidgetItem("等待中")
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.download_table.setItem(row, 5, status_item)
        
        # 添加到历史记录
        self.history.add_record(
            task_id,
            data.get('url', ''),
            data['save_path'],
            0  # 初始文件大小为0
        )
        
    def update_download_status(self, task_id, status):
        if task_id not in self.download_rows:
            return
            
        row = self.download_rows[task_id]
        
        # 更新进度条
        progress_bar = self.download_table.cellWidget(row, 2)
        speed_text = humanize.naturalsize(status['speed'], binary=True) + "/s"
        progress_bar.setProgress(status['progress'], speed_text)
        
        # 更新速度
        self.download_table.item(row, 3).setText(speed_text)
        
        # 计算并更新剩余时间
        if status['speed'] > 0:
            remaining_bytes = status['total_size'] - status['downloaded_size']
            remaining_seconds = remaining_bytes / status['speed']
            remaining_time = str(timedelta(seconds=int(remaining_seconds)))
        else:
            remaining_time = "--:--:--"
        self.download_table.item(row, 4).setText(remaining_time)
        
        # 更新状态和颜色
        status_item = self.download_table.item(row, 5)
        status_item.setText(status['status'])
        
        # 设置状态颜色
        if status['status'] == "完成":
            color = self.theme_manager.current_theme['success_color']
        elif status['status'].startswith("错误"):
            color = self.theme_manager.current_theme['error_color']
        elif status['status'] == "已暂停":
            color = self.theme_manager.current_theme['warning_color']
        else:
            color = self.theme_manager.current_theme['accent_color']
            
        status_item.setForeground(QColor(color))
        self.download_table.item(row, 0).setForeground(QColor(color))
        
        # 更新文件大小
        size_text = humanize.naturalsize(status['total_size'], binary=True)
        self.download_table.item(row, 1).setText(size_text)
        
        # 更新统计信息
        self.statistics.update_speed(status['speed'])
        if status['status'] == "完成":
            self.statistics.complete_download(status['total_size'])
            self.sound_manager.play_complete()
            self.notification_manager.download_complete(
                os.path.basename(self.download_table.item(row, 0).text())
            )
        elif status['status'].startswith("错误"):
            self.statistics.fail_download()
            self.sound_manager.play_error()
            self.notification_manager.download_error(
                os.path.basename(self.download_table.item(row, 0).text()),
                status['status']
            )
        
        # 更新速度图表
        self.speed_chart.add_speed(status['speed'])
        
        # 通知插件
        self.plugin_manager.notify_download_progress(task_id, status)
        
        if status['status'] == "完成":
            self.plugin_manager.notify_download_complete(task_id)
        elif status['status'].startswith("错误"):
            self.plugin_manager.notify_download_error(task_id, status['status'])
        
        # 更新状态统计
        stats = {
            'active_downloads': [t for t in self.download_manager.active_downloads.values()
                               if not t.status.startswith(("完成", "错误", "取消"))],
            'waiting_downloads': [],
            'completed_downloads': self.statistics.stats['completed_downloads'],
            'total_bytes': self.statistics.stats['total_bytes'],
            'average_speed': self.statistics.stats['average_speed']
        }
        self.status_widget.update_stats(stats)
        
    def get_selected_task_ids(self):
        selected_rows = set(item.row() for item in self.download_table.selectedItems())
        return [task_id for task_id, row in self.download_rows.items() 
                if row in selected_rows]
        
    def pause_selected(self):
        """暂停选中的下载"""
        for task_id in self.get_selected_task_ids():
            self.download_manager.pause_download(task_id)
            
    def resume_selected(self):
        """继续选中的下载"""
        for task_id in self.get_selected_task_ids():
            self.download_manager.resume_download(task_id)
            
    def cancel_selected(self):
        """取消选中的下载"""
        reply = QMessageBox.question(
            self,
            "确认取消",
            "确定要取消选中的下载吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for task_id in self.get_selected_task_ids():
                self.download_manager.cancel_download(task_id)
                
    def import_torrent(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择种子文件",
            "",
            "Torrent Files (*.torrent)"
        )
        if file_name:
            save_dir = QFileDialog.getExistingDirectory(
                self,
                "选择保存目录"
            )
            if save_dir:
                task_id = self.download_manager.add_torrent(
                    file_name,
                    save_dir
                )
                self.add_download_to_table(task_id, {
                    'save_path': os.path.join(save_dir, os.path.basename(file_name)),
                    'url': file_name
                })
        
    def closeEvent(self, event):
        """重写关闭事件，实现最小化到托盘"""
        if self.tray.isVisible():
            self.hide()
            event.ignore()
        
    def show_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            new_settings = dialog.get_settings()
            for key, value in new_settings.items():
                self.settings.set(key, value)
            self.download_manager.max_concurrent = new_settings['max_concurrent']
            
    def show_history(self):
        dialog = HistoryDialog(self.history, self)
        dialog.exec()
        
    def new_download_with_data(self, data):
        """从历史记录重新下载时用"""
        task_id = self.download_manager.add_download(
            data['url'], 
            data['save_path']
        )
        self.add_download_to_table(task_id, data)
        
    def show_proxy_settings(self):
        dialog = ProxyDialog(self.settings, self)
        if dialog.exec():
            proxy_settings = dialog.get_settings()
            for key, value in proxy_settings.items():
                self.settings.set(key, value)
            self.apply_proxy_settings()
            
    def apply_proxy_settings(self):
        if self.settings.get('proxy_enabled'):
            proxy_type = self.settings.get('proxy_type')
            proxy_host = self.settings.get('proxy_host')
            proxy_port = self.settings.get('proxy_port')
            
            proxy_url = f"{proxy_type.lower()}://"
            
            if self.settings.get('proxy_auth'):
                proxy_url += f"{self.settings.get('proxy_user')}:{self.settings.get('proxy_pass')}@"
                
            proxy_url += f"{proxy_host}:{proxy_port}"
            
            self.download_manager.set_proxy(proxy_url)
        else:
            self.download_manager.set_proxy(None)
            
    def retry_selected(self):
        """重试选中的下载"""
        for task_id in self.get_selected_task_ids():
            new_task_id = self.download_manager.retry_download(task_id)
            if new_task_id:
                # 更新UI中的任务ID映射
                row = self.download_rows.pop(task_id)
                self.download_rows[new_task_id] = row
                
    def show_statistics(self):
        dialog = StatisticsDialog(self.statistics, self)
        dialog.exec()
        
    def update_status_bar(self, stats):
        status_text = (
            f"总下载: {stats['total_downloads']} | "
            f"完成: {stats['completed_downloads']} | "
            f"失败: {stats['failed_downloads']} | "
            f"当前速度: {humanize.naturalsize(stats['current_speed'], binary=True)}/s"
        )
        self.statusBar.showMessage(status_text)
        
    def on_plugin_loaded(self, plugin_name):
        self.statusBar.showMessage(f"已加载插件: {plugin_name}", 3000)
        
    def on_plugin_error(self, plugin_name, error):
        self.statusBar.showMessage(f"插件 {plugin_name} 错误: {error}", 5000)
        
    def apply_theme(self, theme):
        """应用主题"""
        # 应用全局样式表
        self.setStyleSheet(self.theme_manager.get_style_sheet())
        
        # 更新状态栏颜色
        self.statusBar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {theme['toolbar_background']};
                color: {theme['text_color']};
            }}
        """)
        
        # 更新表样式
        self.download_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme['window_background']};
                alternate-background-color: {theme['table_alternate_background']};
                gridline-color: {theme['table_gridline']};
                color: {theme['text_color']};
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QHeaderView::section {{
                background-color: {theme['accent_color']};
                color: white;
                padding: 5px;
                border: none;
            }}
        """)
        
    def show_theme_settings(self):
        dialog = ThemeDialog(self.theme_manager, self)
        dialog.exec()
        
    def show_plugin_manager(self):
        dialog = PluginDialog(self.plugin_manager, self)
        dialog.exec()
        
    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        # 获取选中的任务
        selected_tasks = self.get_selected_task_ids()
        if not selected_tasks:
            return
            
        # 添加菜单项
        details_action = menu.addAction("查看详情")  # 添加详情菜单项
        menu.addSeparator()
        open_file = menu.addAction("打开文件")
        open_folder = menu.addAction("打开所在文件夹")
        menu.addSeparator()
        copy_url = menu.addAction("复制下载链接")
        menu.addSeparator()
        remove_item = menu.addAction("从列表中移除")
        
        # 处理菜单动作
        action = menu.exec(self.download_table.viewport().mapToGlobal(pos))
        if not action:
            return
            
        task_id = selected_tasks[0]
        task = self.download_manager.active_downloads.get(task_id)
        if not task:
            return
            
        if action == details_action:
            self.show_task_details(task_id)
        elif action == open_file:
            self.open_file(task.save_path)
        elif action == open_folder:
            self.open_folder(task.save_path)
        elif action == copy_url:
            QApplication.clipboard().setText(task.url)
        elif action == remove_item:
            self.remove_download_item(task_id)
            
    def open_file(self, path):
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
            
    def open_folder(self, path):
        if os.path.exists(path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(path)))
            
    def remove_download_item(self, task_id):
        if task_id in self.download_rows:
            row = self.download_rows[task_id]
            self.download_table.removeRow(row)
            del self.download_rows[task_id]
            
            # 更新其他行的索引
            for tid, r in self.download_rows.items():
                if r > row:
                    self.download_rows[tid] = r - 1
                    
    def update_button_states(self):
        """更新按钮状态"""
        selected_tasks = self.get_selected_task_ids()
        has_selection = len(selected_tasks) > 0
        
        # 获取选中任务的状态
        has_active = False
        has_paused = False
        has_error = False
        
        for task_id in selected_tasks:
            task = self.download_manager.active_downloads.get(task_id)
            if task:
                if task.status.startswith("错误"):
                    has_error = True
                elif task.is_paused:
                    has_paused = True
                else:
                    has_active = True
                    
        # 更新按钮状态
        self.pause_btn.setEnabled(has_selection and has_active)
        self.resume_btn.setEnabled(has_selection and has_paused)
        self.cancel_btn.setEnabled(has_selection)
        self.retry_btn.setEnabled(has_selection and has_error)
        
    def show_task_details(self, task_id):
        """显示下载任务详情"""
        dialog = TaskDetailsDialog(task_id, self.download_manager, self)
        dialog.exec()
        
    def show_download_info(self, row, column):
        """显示下载详细信息"""
        task_id = None
        for tid, r in self.download_rows.items():
            if r == row:
                task_id = tid
                break
            
        if task_id and task_id in self.download_manager.active_downloads:
            dialog = DownloadInfoDialog(task_id, self.download_manager, self)
            dialog.exec()
        