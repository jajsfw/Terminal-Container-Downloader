from utils.plugin_manager import PluginBase
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt6.QtWidgets import QMessageBox
import platform
import subprocess

class AutoNotifyPlugin(PluginBase):
    def __init__(self, manager):
        super().__init__(manager)
        self.name = "自动通知插件"
        self.version = "1.0"
        self.description = "通过多种方式通知下载状态"
        
        # 邮件设置
        self.email_enabled = False
        self.smtp_server = ""
        self.smtp_port = 587
        self.smtp_user = ""
        self.smtp_pass = ""
        self.notify_email = ""
        
        # 加载配置
        self.load_config()
        
    def load_config(self):
        """从settings加载配置"""
        settings = self.manager.main_window.settings
        self.email_enabled = settings.get('notify_email_enabled', False)
        self.smtp_server = settings.get('notify_smtp_server', '')
        self.smtp_port = settings.get('notify_smtp_port', 587)
        self.smtp_user = settings.get('notify_smtp_user', '')
        self.smtp_pass = settings.get('notify_smtp_pass', '')
        self.notify_email = settings.get('notify_email', '')
        
    def on_download_start(self, task_id, url, save_path):
        filename = os.path.basename(save_path)
        self.send_notification(
            "下载开始",
            f"开始下载: {filename}\n来源: {url}"
        )
        
    def on_download_complete(self, task_id):
        download_task = self.manager.main_window.download_manager.active_downloads.get(task_id)
        if not download_task:
            return
            
        filename = os.path.basename(download_task.save_path)
        self.send_notification(
            "下载完成",
            f"文件 {filename} 下载完成！"
        )
        
    def on_download_error(self, task_id, error):
        download_task = self.manager.main_window.download_manager.active_downloads.get(task_id)
        if not download_task:
            return
            
        filename = os.path.basename(download_task.save_path)
        self.send_notification(
            "下载错误",
            f"文件 {filename} 下载失败: {error}"
        )
        
    def send_notification(self, title, message):
        """发送通知"""
        # 发送桌面通知
        self.send_desktop_notification(title, message)
        
        # 如果启用了邮件通知，发送邮件
        if self.email_enabled and all([
            self.smtp_server, self.smtp_user,
            self.smtp_pass, self.notify_email
        ]):
            self.send_email_notification(title, message)
            
    def send_desktop_notification(self, title, message):
        """发送桌面通知"""
        system = platform.system()
        
        try:
            if system == "Windows":
                # Windows 10 Toast通知
                from win10toast import ToastNotifier
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=5)
                
            elif system == "Darwin":  # macOS
                # 使用osascript发送通知
                subprocess.run([
                    'osascript',
                    '-e', f'display notification "{message}" with title "{title}"'
                ])
                
            elif system == "Linux":
                # 使用notify-send发送通知
                subprocess.run(['notify-send', title, message])
                
        except Exception as e:
            print(f"发送桌面通知失败: {str(e)}")
            
    def send_email_notification(self, title, message):
        """发送邮件通知"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.notify_email
            msg['Subject'] = f"下载通知: {title}"
            
            body = MIMEText(message)
            msg.attach(body)
            
            # 连接SMTP服务器
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            
            # 发送邮件
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"发送邮件通知失败: {str(e)}") 