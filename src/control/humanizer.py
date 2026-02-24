"""
Модуль для эмуляции человеческого поведения
"""
import random
import time
import numpy as np
from typing import Tuple, Optional

class Humanizer:
    """
    Класс для добавления "человечности" в действия бота
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.reaction_time_min = self.config.get('reaction_time_min', 0.1)
        self.reaction_time_max = self.config.get('reaction_time_max', 0.3)
        self.mouse_jitter = self.config.get('mouse_jitter', 5)
        self.typing_speed_min = self.config.get('typing_speed_min', 0.05)
        self.typing_speed_max = self.config.get('typing_speed_max', 0.15)
    
    def random_pause(self, min_ms: int = 100, max_ms: int = 500) -> None:
        """
        Случайная пауза как у человека
        
        Args:
            min_ms: минимальная пауза в миллисекундах
            max_ms: максимальная пауза в миллисекундах
        """
        pause_ms = random.randint(min_ms, max_ms)
        time.sleep(pause_ms / 1000)
    
    def get_reaction_time(self) -> float:
        """
        Возвращает случайное время реакции человека
        
        Returns:
            время в секундах
        """
        return random.uniform(self.reaction_time_min, self.reaction_time_max)
    
    def get_mouse_duration(self, distance: Optional[float] = None) -> float:
        """
        Возвращает время движения мыши как у человека
        
        Args:
            distance: расстояние в пикселях (опционально)
            
        Returns:
            время в секундах
        """
        if distance:
            # Чем дальше, тем дольше, но с вариацией
            base_duration = distance / 1000  # примерно 0.1 сек на 100 пикселей
            variation = random.uniform(0.7, 1.3)
            return max(0.1, base_duration * variation)
        else:
            return random.uniform(0.2, 0.6)
    
    def jitter_point(self, x: int, y: int, intensity: Optional[int] = None) -> Tuple[int, int]:
        """
        Добавляет случайное дрожание к координатам (как у руки человека)
        
        Args:
            x: исходная координата X
            y: исходная координата Y
            intensity: интенсивность дрожания (если None, берется из конфига)
            
        Returns:
            новые координаты с дрожанием
        """
        if intensity is None:
            intensity = self.mouse_jitter
        
        jitter_x = random.randint(-intensity, intensity)
        jitter_y = random.randint(-intensity, intensity)
        
        return x + jitter_x, y + jitter_y
    
    def bezier_curve(self, start: Tuple[int, int], end: Tuple[int, int], steps: int) -> list:
        """
        Генерирует точки кривой Безье для естественного движения мыши
        
        Args:
            start: начальная точка (x, y)
            end: конечная точка (x, y)
            steps: количество шагов
            
        Returns:
            список точек (x, y) для движения
        """
        start_x, start_y = start
        end_x, end_y = end
        
        # Контрольные точки для кривой (случайные отклонения)
        cp1 = (
            start_x + (end_x - start_x) * 0.25 + random.randint(-50, 50),
            start_y + (end_y - start_y) * 0.25 + random.randint(-50, 50)
        )
        cp2 = (
            start_x + (end_x - start_x) * 0.75 + random.randint(-50, 50),
            start_y + (end_y - start_y) * 0.75 + random.randint(-50, 50)
        )
        
        points = []
        for i in range(steps + 1):
            t = i / steps
            x = self._bezier_point(start_x, cp1[0], cp2[0], end_x, t)
            y = self._bezier_point(start_y, cp1[1], cp2[1], end_y, t)
            points.append((int(x), int(y)))
        
        return points
    
    def _bezier_point(self, p0: float, p1: float, p2: float, p3: float, t: float) -> float:
        """Кубическая кривая Безье"""
        return (1-t)**3 * p0 + 3*(1-t)**2 * t * p1 + 3*(1-t) * t**2 * p2 + t**3 * p3
    
    def human_type(self, text: str, key_delay: Optional[float] = None) -> None:
        """
        Печатает текст как человек (с задержками между символами)
        
        Args:
            text: текст для печати
            key_delay: задержка между нажатиями (если None, берется случайная)
        """
        try:
            import keyboard
            for char in text:
                if key_delay is None:
                    delay = random.uniform(self.typing_speed_min, self.typing_speed_max)
                else:
                    delay = key_delay
                
                keyboard.write(char)
                time.sleep(delay)
        except ImportError:
            print("⚠️ keyboard module not installed")
    
    def should_make_mistake(self, probability: float = 0.05) -> bool:
        """
        Должен ли бот сделать "ошибку" (опечатку, лишнее движение)
        
        Args:
            probability: вероятность ошибки (0-1)
            
        Returns:
            True если нужно сделать ошибку
        """
        return random.random() < probability
    
    def human_look_around(self, duration: float = 2.0) -> list:
        """
        Генерирует последовательность движений для осмотра вокруг
        
        Args:
            duration: общая длительность осмотра
            
        Returns:
            список движений [(dx, dy, wait), ...]
        """
        movements = []
        time_passed = 0
        
        while time_passed < duration:
            # Случайное направление взгляда
            dx = random.randint(-300, 300)
            dy = random.randint(-100, 100)
            
            # Случайная задержка между движениями
            wait = random.uniform(0.1, 0.4)
            
            movements.append((dx, dy, wait))
            time_passed += wait + 0.1  # примерно
        
        return movements


# Для тестирования
if __name__ == '__main__':
    h = Humanizer()
    print("Testing Humanizer...")
    print(f"Reaction time: {h.get_reaction_time():.2f}s")
    print(f"Mouse duration: {h.get_mouse_duration(500):.2f}s")
    print(f"Jitter point: {h.jitter_point(100, 100)}")
    print("✅ Humanizer works!")