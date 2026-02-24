"""
YOLOv8 детектор для компьютерного зрения
"""
import numpy as np
from typing import List, Dict, Any, Optional
from .base_detector import BaseDetector

class YOLODetector(BaseDetector):
    """YOLOv8 детектор"""
    
    def __init__(self, model_path: Optional[str] = None, device: str = 'cpu'):
        """
        Инициализация YOLO детектора
        
        Args:
            model_path: путь к файлу модели
            device: устройство для инференса ('cpu' или 'cuda')
        """
        self.device = device
        self.model = None
        self.class_names = []
        
        # Попытка импортировать YOLO
        self._import_yolo()
        
        if model_path:
            self.load_model(model_path)
    
    def _import_yolo(self):
        """Пытается импортировать YOLO, если не получается - создает заглушку"""
        try:
            from ultralytics import YOLO
            self.YOLO = YOLO
            self.yolo_available = True
        except ImportError:
            print("⚠️ YOLO not installed. Install with: pip install ultralytics")
            self.yolo_available = False
    
    def load_model(self, model_path: str) -> None:
        """Загрузка модели YOLO"""
        if not self.yolo_available:
            print(f"⚠️ Using mock model (YOLO not installed)")
            self.model = "mock"
            self.class_names = ['loot_crate', 'weapon_box', 'enemy']
            return
        
        try:
            self.model = self.YOLO(model_path)
            self.class_names = list(self.model.names.values())
            print(f"✅ Модель загружена: {model_path}")
            print(f"📋 Классы: {self.class_names}")
        except Exception as e:
            print(f"❌ Ошибка загрузки модели: {e}")
            self.model = "mock"
            self.class_names = ['loot_crate', 'weapon_box', 'enemy']
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Базовая предобработка"""
        return image
    
    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Детекция объектов
        
        Args:
            image: входное изображение
            
        Returns:
            Список детекций
        """
        # Если модель не загружена или это мок
        if self.model is None:
            return []
        
        if not self.yolo_available or self.model == "mock":
            # Возвращаем мок-детекции для тестирования
            return self._mock_detections(image)
        
        try:
            # Реальный инференс YOLO
            results = self.model(image, verbose=False)[0]
            
            detections = []
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls_id = int(box.cls[0])
                
                detection = {
                    'class': self.class_names[cls_id],
                    'class_id': cls_id,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'center': (int((x1 + x2) / 2), int((y1 + y2) / 2)),
                    'confidence': conf
                }
                detections.append(detection)
            
            return detections
            
        except Exception as e:
            print(f"❌ Ошибка детекции: {e}")
            return []
    
    def _mock_detections(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Генерирует мок-детекции для тестирования
        """
        import random
        
        h, w = image.shape[:2]
        detections = []
        
        # Иногда "видим" объекты
        if random.random() < 0.3:  # 30% шанс
            for _ in range(random.randint(1, 3)):
                x1 = random.randint(100, w-200)
                y1 = random.randint(100, h-200)
                x2 = x1 + random.randint(50, 150)
                y2 = y1 + random.randint(50, 150)
                
                detection = {
                    'class': random.choice(self.class_names),
                    'class_id': 0,
                    'bbox': [x1, y1, x2, y2],
                    'center': ((x1 + x2) // 2, (y1 + y2) // 2),
                    'confidence': random.uniform(0.5, 0.95)
                }
                detections.append(detection)
        
        return detections