"""
Базовый класс для всех детекторов
"""
from abc import ABC, abstractmethod
import numpy as np
from typing import List, Dict, Any, Optional

class BaseDetector(ABC):
    """Абстрактный базовый класс для всех детекторов"""
    
    @abstractmethod
    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Детектирует объекты на изображении
        
        Args:
            image: входное изображение в формате numpy array (H, W, 3)
            
        Returns:
            Список словарей с ключами:
            - 'class': название класса (str)
            - 'bbox': координаты bounding box [x1, y1, x2, y2] (List[int])
            - 'confidence': уверенность детекции (float)
            - 'center': центр объекта (x, y) (Tuple[int, int])
        """
        pass
    
    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """Загружает модель"""
        pass
    
    @abstractmethod
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Предобработка изображения"""
        pass
    
    def filter_by_confidence(self, detections: List[Dict], threshold: float = 0.5) -> List[Dict]:
        """
        Фильтрует детекции по уверенности
        
        Args:
            detections: список детекций
            threshold: порог уверенности
            
        Returns:
            Отфильтрованный список
        """
        return [d for d in detections if d.get('confidence', 0) >= threshold]