"""
Реальное управление клавиатурой
"""
import time
import random
from typing import Optional
from .base_controller import BaseController

class KeyboardController(BaseController):
    """Реальное управление клавиатурой"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.pressed_keys = set()
        
        try:
            import keyboard
            self.keyboard = keyboard
            self.available = True
            print("⌨️ KeyboardController готов к работе")
        except ImportError:
            print("⚠️ keyboard не установлен. Движения будут в консоли")
            self.available = False
    
    # Обязательные методы из BaseController
    
    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """Для клавиатуры не используется"""
        pass
    
    def click(self, button: str = 'left', clicks: int = 1) -> None:
        """Для клавиатуры не используется"""
        pass
    
    def press_key(self, key: str) -> None:
        """Нажать клавишу"""
        if not self.available:
            print(f"⌨️ [НАЖАТ] {key}")
            self.pressed_keys.add(key)
            return
        
        self.keyboard.press(key)
        self.pressed_keys.add(key)
    
    def release_key(self, key: str) -> None:
        """Отпустить клавишу"""
        if not self.available:
            print(f"⌨️ [ОТПУСТИТЬ] {key}")
            self.pressed_keys.discard(key)
            return
        
        self.keyboard.release(key)
        self.pressed_keys.discard(key)
    
    def release_all(self) -> None:
        """Отпустить все клавиши"""
        if not self.available:
            print("⌨️ [ВСЕ ОТПУЩЕНЫ]")
            self.pressed_keys.clear()
            return
        
        for key in list(self.pressed_keys):
            self.keyboard.release(key)
        self.pressed_keys.clear()
    
    def tap_key(self, key: str, duration: float = 0.1) -> None:
        """Коротко нажать и отпустить"""
        self.press_key(key)
        time.sleep(duration)
        self.release_key(key)
    
    def type_text(self, text: str, delay: float = 0.1) -> None:
        """Напечатать текст"""
        if not self.available:
            print(f"⌨️ [ПЕЧАТЬ] {text}")
            return
        
        self.keyboard.write(text, delay=delay)