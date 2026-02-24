"""
Управление мышью с человеческим поведением
"""
import pyautogui
import time
from typing import Optional, Tuple
from .base_controller import BaseController
from .humanizer import Humanizer

class MouseController(BaseController):
    """Управление мышью с человеческим поведением"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.humanizer = Humanizer(self.config)
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01
        
        # Настройки
        self.human_like = self.config.get('human_like', True)
        self.jitter = self.config.get('jitter', 5)
        self.bezier_curve = self.config.get('bezier_curve', True)
    
    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """Плавное движение к точке"""
        if duration is None:
            # Рассчитываем расстояние для определения времени
            current_x, current_y = pyautogui.position()
            distance = ((x - current_x) ** 2 + (y - current_y) ** 2) ** 0.5
            duration = self.humanizer.get_mouse_duration(distance)
        
        # Добавляем случайное отклонение (человеческий фактор)
        if self.human_like:
            target_x, target_y = self.humanizer.jitter_point(x, y, self.jitter)
        else:
            target_x, target_y = x, y
        
        # Кривая Безье для естественного движения
        if self.bezier_curve and self.human_like:
            self._bezier_move(target_x, target_y, duration)
        else:
            pyautogui.moveTo(target_x, target_y, duration=duration, 
                            tween=pyautogui.easeInOutQuad)
    
    def _bezier_move(self, target_x: int, target_y: int, duration: float):
        """Движение по кривой Безье (как человек)"""
        start_x, start_y = pyautogui.position()
        
        # Генерируем точки кривой
        steps = int(duration * 60)  # 60 FPS
        points = self.humanizer.bezier_curve(
            (start_x, start_y), 
            (target_x, target_y), 
            steps
        )
        
        # Двигаемся по точкам
        step_duration = duration / steps
        for point in points:
            pyautogui.moveTo(point[0], point[1])
            time.sleep(step_duration)
    
    def move_rel(self, dx: int, dy: int, duration: Optional[float] = None) -> None:
        """Относительное движение"""
        current_x, current_y = pyautogui.position()
        self.move_to(current_x + dx, current_y + dy, duration)
    
    def click(self, button: str = 'left', clicks: int = 1) -> None:
        """Клик с человеческой задержкой"""
        if self.human_like:
            # Реакция человека перед кликом
            time.sleep(self.humanizer.get_reaction_time())
        
        pyautogui.click(button=button, clicks=clicks)
        
        if self.human_like and clicks > 1:
            # Задержка между кликами
            time.sleep(self.humanizer.get_reaction_time())
    
    def press_key(self, key: str) -> None:
        """Для мыши не используется"""
        pass
    
    def release_key(self, key: str) -> None:
        """Для мыши не используется"""
        pass
    
    def release_all(self) -> None:
        """Для мыши не используется"""
        pass
    
    def scroll(self, clicks: int) -> None:
        """Прокрутка колесика"""
        pyautogui.scroll(clicks)
    
    def drag_to(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """Перетаскивание"""
        pyautogui.dragTo(x, y, duration=duration, button='left')
    
    def get_position(self) -> Tuple[int, int]:
        """Текущая позиция мыши"""
        return pyautogui.position()