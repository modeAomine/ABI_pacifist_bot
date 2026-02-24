"""
Модуль принятия решений для бота
"""
from enum import Enum
import random
import time
from typing import List, Dict, Any, Optional

class BotAction(Enum):
    """Возможные действия бота"""
    EXPLORE = "explore"
    MOVE_TO_LOOT = "move_to_loot"
    LOOT = "loot"
    EVADE = "evade"
    WAIT = "wait"
    STUCK = "stuck"

class DecisionEngine:
    """
    Главный модуль принятия решений
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.current_action = BotAction.EXPLORE
        self.current_target = None
        self.last_decision_time = time.time()
        self.consecutive_failures = 0
        
        # Параметры из конфига
        self.loot_classes = self.config.get('loot_classes', 
                                           ['loot_crate', 'weapon_box', 'ammo_box', 'medkit'])
        self.explore_timeout = self.config.get('explore_timeout', 10)
        self.loot_confidence_threshold = self.config.get('loot_confidence_threshold', 0.5)
        
        print("🧠 DecisionEngine initialized")
    
    def decide(self, 
               detections: List[Dict[str, Any]], 
               game_state: Dict[str, Any]) -> BotAction:
        """
        Принимает решение на основе детекций и состояния игры
        
        Args:
            detections: список обнаруженных объектов
            game_state: состояние игры (здоровье, позиция и т.д.)
            
        Returns:
            BotAction: выбранное действие
        """
        # Приоритет 1: Опасность (пока заглушка)
        if self._is_in_danger(detections, game_state):
            self.current_action = BotAction.EVADE
            return self.current_action
        
        # Приоритет 2: Лут рядом
        loot = self._find_loot(detections)
        if loot and self._should_loot(loot):
            self.current_action = BotAction.MOVE_TO_LOOT
            self.current_target = loot[0]
            return self.current_action
        
        # Приоритет 3: Исследование
        if self._should_explore():
            self.current_action = BotAction.EXPLORE
            return self.current_action
        
        # По умолчанию
        return BotAction.WAIT
    
    def _is_in_danger(self, detections, game_state) -> bool:
        """Проверка на опасность"""
        # TODO: реализовать детекцию врагов
        # Пока всегда возвращаем False (нет опасности)
        return False
    
    def _find_loot(self, detections):
        """Поиск лута среди детекций"""
        return [d for d in detections 
                if d.get('class') in self.loot_classes 
                and d.get('confidence', 0) >= self.loot_confidence_threshold]
    
    def _should_loot(self, loot) -> bool:
        """Проверка, стоит ли лутать"""
        if not self.current_target:
            return True
        
        # Не лутаем одно и то же слишком часто
        current_time = time.time()
        if current_time - self.last_decision_time < 2:
            return False
        
        return True
    
    def _should_explore(self) -> bool:
        """Проверка, нужно ли исследовать"""
        # Если давно не меняли действие - пора
        if time.time() - self.last_decision_time > self.explore_timeout:
            return True
        return False
    
    def get_action_name(self, action: BotAction) -> str:
        """Получить название действия"""
        return action.value
    
    def reset(self):
        """Сброс состояния"""
        self.current_action = BotAction.EXPLORE
        self.current_target = None
        self.last_decision_time = time.time()
        self.consecutive_failures = 0


# Для тестирования
if __name__ == '__main__':
    engine = DecisionEngine()
    print(f"Current action: {engine.current_action}")
    
    # Тест с мок-детекциями
    mock_detections = [
        {'class': 'loot_crate', 'confidence': 0.8, 'bbox': [100,100,200,200]}
    ]
    action = engine.decide(mock_detections, {})
    print(f"Decision with loot: {action}")
    print("✅ DecisionEngine works!")