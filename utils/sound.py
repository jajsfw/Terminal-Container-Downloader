from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
import os

class SoundManager:
    def __init__(self):
        self.enabled = True
        self.complete_sound = QSoundEffect()
        self.error_sound = QSoundEffect()
        
        # 设置声音文件路径（需要添加声音文件）
        sound_dir = os.path.join(os.path.dirname(__file__), '..', 'resources', 'sounds')
        
        complete_path = os.path.join(sound_dir, 'complete.wav')
        error_path = os.path.join(sound_dir, 'error.wav')
        
        if os.path.exists(complete_path):
            self.complete_sound.setSource(QUrl.fromLocalFile(complete_path))
        if os.path.exists(error_path):
            self.error_sound.setSource(QUrl.fromLocalFile(error_path))
            
    def play_complete(self):
        if self.enabled and self.complete_sound.isLoaded():
            self.complete_sound.play()
            
    def play_error(self):
        if self.enabled and self.error_sound.isLoaded():
            self.error_sound.play()
            
    def set_enabled(self, enabled):
        self.enabled = enabled 