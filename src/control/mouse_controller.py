"""
Реальное управление мышью с человеческим поведением
"""
import pyautogui
import time
import random
from typing import Optional, Tuple
from .base_controller import BaseController
from .humanizer import Humanizer

class MouseController(BaseController):
    """Реальное управление мышью"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.humanizer = Humanizer(self.config)
        
        # Настройки безопасности
        pyautogui.FAILSAFE = True  # Если мышь в угол - стоп
        pyautogui.PAUSE = 0.01
        
        self.human_like = self.config.get('human_like', True)
        print("🖱️ MouseController готов к работе")
    
    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """Движение к точке"""
        if not duration and self.human_like:
            # Рассчитываем время как у человека
            current_x, current_y = pyautogui.position()
            distance = ((x - current_x) ** 2 + (y - current_y) ** 2) ** 0.5
            duration = self.humanizer.get_mouse_duration(distance)
        
        # Добавляем человеческое дрожание
        if self.human_like:
            target_x, target_y = self.humanizer.jitter_point(x, y)
        else:
            target_x, target_y = x, y
        
        # Двигаемся
        pyautogui.moveTo(target_x, target_y, duration=duration or 0.2)
    
    def click(self, button: str = 'left', clicks: int = 1) -> None:
        """Клик с человеческой паузой"""
        if self.human_like:
            time.sleep(self.humanizer.get_reaction_time())
        pyautogui.click(button=button, clicks=clicks)
    
    def press_key(self, key: str) -> None:
        """Не используется для мыши"""
        pass
    
    def release_key(self, key: str) -> None:
        """Не используется для мыши"""
        pass
    
    def release_all(self) -> None:
        """Не используется для мыши"""
        pass
    
    def scroll(self, clicks: int) -> None:
        """Прокрутка"""
        pyautogui.scroll(clicks)
    
    def move_rel(self, dx: int, dy: int, duration: Optional[float] = None) -> None:
        """Относительное движение"""
        current_x, current_y = pyautogui.position()
        self.move_to(current_x + dx, current_y + dy, duration)