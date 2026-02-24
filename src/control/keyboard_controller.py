"""
Управление клавиатурой с эмуляцией человеческого поведения
"""
import time
import random
from typing import List, Optional
from .base_controller import BaseController
from .humanizer import Humanizer

class KeyboardController(BaseController):
    """Управление клавиатурой с человеческим поведением"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.humanizer = Humanizer(self.config)
        self.pressed_keys = set()
        
        # Настройки
        self.press_duration = self.config.get('press_duration', 0.1)
        self.human_like = self.config.get('human_like', True)
        
        # Пытаемся импортировать keyboard
        try:
            import keyboard
            self.keyboard = keyboard
            self.keyboard_available = True
        except ImportError:
            print("⚠️ keyboard module not installed. Install with: pip install keyboard")
            self.keyboard_available = False
    
    def press_key(self, key: str) -> None:
        """Нажатие клавиши"""
        if not self.keyboard_available:
            print(f"⌨️ [MOCK] Press key: {key}")
            self.pressed_keys.add(key)
            return
        
        try:
            self.keyboard.press(key)
            self.pressed_keys.add(key)
            
            if self.human_like:
                # Человек не нажимает клавиши мгновенно
                time.sleep(self.humanizer.get_reaction_time() / 2)
        except Exception as e:
            print(f"❌ Error pressing key {key}: {e}")
    
    def release_key(self, key: str) -> None:
        """Отжатие клавиши"""
        if not self.keyboard_available:
            print(f"⌨️ [MOCK] Release key: {key}")
            self.pressed_keys.discard(key)
            return
        
        try:
            self.keyboard.release(key)
            self.pressed_keys.discard(key)
        except Exception as e:
            print(f"❌ Error releasing key {key}: {e}")
    
    def tap_key(self, key: str, duration: Optional[float] = None) -> None:
        """Краткое нажатие клавиши (нажать и отпустить)"""
        if duration is None:
            duration = self.press_duration
        
        self.press_key(key)
        
        if self.human_like:
            # Случайная вариация длительности
            actual_duration = duration * random.uniform(0.8, 1.2)
        else:
            actual_duration = duration
        
        time.sleep(actual_duration)
        self.release_key(key)
    
    def press_keys(self, keys: List[str]) -> None:
        """Нажатие нескольких клавиш одновременно"""
        for key in keys:
            self.press_key(key)
    
    def release_all(self) -> None:
        """Отжатие всех клавиш"""
        if not self.keyboard_available:
            print("⌨️ [MOCK] Release all keys")
            self.pressed_keys.clear()
            return
        
        try:
            for key in list(self.pressed_keys):
                self.keyboard.release(key)
            self.pressed_keys.clear()
        except Exception as e:
            print(f"❌ Error releasing keys: {e}")
    
    def type_text(self, text: str, human_like: bool = True) -> None:
        """Печать текста"""
        if not self.keyboard_available:
            print(f"⌨️ [MOCK] Type: {text}")
            return
        
        if human_like and self.human_like:
            self.humanizer.human_type(text)
        else:
            self.keyboard.write(text)
    
    def press_hotkey(self, *args) -> None:
        """Нажатие горячей комбинации клавиш"""
        if not self.keyboard_available:
            print(f"⌨️ [MOCK] Hotkey: {args}")
            return
        
        try:
            self.keyboard.send('+'.join(args))
        except Exception as e:
            print(f"❌ Error sending hotkey {args}: {e}")
    
    def is_pressed(self, key: str) -> bool:
        """Проверка, нажата ли клавиша"""
        if not self.keyboard_available:
            return key in self.pressed_keys
        
        try:
            return self.keyboard.is_pressed(key)
        except:
            return False
    
    def wait_for_key(self, key: str, timeout: Optional[float] = None) -> bool:
        """Ожидание нажатия клавиши"""
        if not self.keyboard_available:
            print(f"⌨️ [MOCK] Wait for {key}")
            return True
        
        try:
            return self.keyboard.wait(key, timeout=timeout) is not None
        except:
            return False


# Для тестирования
if __name__ == '__main__':
    kb = KeyboardController()
    print("Testing KeyboardController...")
    
    print("Press 'q' to continue...")
    kb.wait_for_key('q')
    
    print("Tapping 'a'")
    kb.tap_key('a')
    
    print("✅ KeyboardController works!")