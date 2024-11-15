from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QTableWidget, QTableWidgetItem, QLabel, QCheckBox,
                           QMessageBox)
from PyQt6.QtCore import Qt
import os

class PluginDialog(QDialog):
    def __init__(self, plugin_manager, parent=None):
        super().__init__(parent)
        self.plugin_manager = plugin_manager
        self.setWindowTitle("插件管理")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 插件列表
        self.plugin_table = QTableWidget()
        self.plugin_table.setColumnCount(5)
        self.plugin_table.setHorizontalHeaderLabels([
            "插件名称", "版本", "状态", "描述", "启用"
        ])
        self.plugin_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.plugin_table)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("刷新")
        install_btn = QPushButton("安装插件")
        remove_btn = QPushButton("删除插件")
        close_btn = QPushButton("关闭")
        
        refresh_btn.clicked.connect(self.refresh_plugins)
        install_btn.clicked.connect(self.install_plugin)
        remove_btn.clicked.connect(self.remove_plugin)
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(install_btn)
        btn_layout.addWidget(remove_btn)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # 加载插件列表
        self.refresh_plugins()
        
    def refresh_plugins(self):
        self.plugin_table.setRowCount(0)
        
        for plugin_name, plugin in self.plugin_manager.plugins.items():
            row = self.plugin_table.rowCount()
            self.plugin_table.insertRow(row)
            
            # 插件名称
            self.plugin_table.setItem(row, 0, QTableWidgetItem(plugin.name))
            
            # 版本
            self.plugin_table.setItem(row, 1, QTableWidgetItem(plugin.version))
            
            # 状态
            status = "已加载" if plugin_name in self.plugin_manager.plugins else "未加载"
            self.plugin_table.setItem(row, 2, QTableWidgetItem(status))
            
            # 描述
            self.plugin_table.setItem(row, 3, QTableWidgetItem(plugin.description))
            
            # 启用复选框
            enable_check = QCheckBox()
            enable_check.setChecked(True)  # 默认启用
            enable_check.stateChanged.connect(
                lambda state, p=plugin_name: self.toggle_plugin(p, state)
            )
            self.plugin_table.setCellWidget(row, 4, enable_check)
            
    def toggle_plugin(self, plugin_name, state):
        try:
            if state == Qt.CheckState.Checked.value:
                self.plugin_manager.enable_plugin(plugin_name)
            else:
                self.plugin_manager.disable_plugin(plugin_name)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"切换插件状态失败: {str(e)}")
            
    def install_plugin(self):
        from PyQt6.QtWidgets import QFileDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择插件文件",
            "",
            "Python Files (*.py)"
        )
        if file_name:
            try:
                # 复制插件文件到插件目录
                import shutil
                plugin_name = os.path.basename(file_name)
                dest_path = os.path.join(self.plugin_manager.plugin_dir, plugin_name)
                shutil.copy2(file_name, dest_path)
                
                # 加载新插件
                self.plugin_manager.load_plugin(plugin_name)
                self.refresh_plugins()
                
            except Exception as e:
                QMessageBox.warning(self, "错误", f"安装插件失败: {str(e)}")
                
    def remove_plugin(self):
        selected_items = self.plugin_table.selectedItems()
        if not selected_items:
            return
            
        row = selected_items[0].row()
        plugin_name = self.plugin_table.item(row, 0).text()
        
        response = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除插件 {plugin_name} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if response == QMessageBox.StandardButton.Yes:
            try:
                self.plugin_manager.remove_plugin(plugin_name)
                self.refresh_plugins()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"删除插件失败: {str(e)}") 