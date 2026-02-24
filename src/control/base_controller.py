from abc import ABC, abstractmethod
from typing import Tuple, Optional

class BaseController(ABC):
    """Базовый класс для всех контроллеров"""
    
    @abstractmethod
    def move_to(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """Плавное движение к точке"""
        pass
    
    @abstractmethod
    def click(self, button: str = 'left', clicks: int = 1) -> None:
        """Клик мышью"""
        pass
    
    @abstractmethod
    def press_key(self, key: str) -> None:
        """Нажатие клавиши"""
        pass
    
    @abstractmethod
    def release_key(self, key: str) -> None:
        """Отжатие клавиши"""
        pass
    
    @abstractmethod
    def release_all(self) -> None:
        """Отжатие всех клавиш"""
        pass