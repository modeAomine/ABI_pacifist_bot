"""
Core bot class for Arena Breakout
"""
import time
import cv2
import numpy as np
import threading
import random
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

# Добавим временные заглушки для импортов
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

# Пытаемся импортировать модули, если не получается - используем заглушки
try:
    from src.vision.yolo_detector import YOLODetector
except ImportError:
    YOLODetector = None
    print("⚠️ YOLODetector not available, using mock")

try:
    from src.control.mouse_controller import MouseController
except ImportError:
    MouseController = None
    print("⚠️ MouseController not available")

try:
    from src.control.keyboard_controller import KeyboardController
except ImportError:
    KeyboardController = None
    print("⚠️ KeyboardController not available")

try:
    from src.brain.decision_engine import DecisionEngine, BotAction
except ImportError:
    DecisionEngine = None
    BotAction = None
    print("⚠️ DecisionEngine not available")

try:
    from src.utils.telegram_notifier import TelegramNotifier
except ImportError:
    TelegramNotifier = None
    print("⚠️ TelegramNotifier not available")

try:
    from src.core.state_machine import StateMachine, BotState
except ImportError:
    StateMachine = None
    BotState = None

try:
    from src.core.events import EventBus
except ImportError:
    EventBus = None

try:
    from src.capture.screen import ScreenCapture
except ImportError:
    ScreenCapture = None

try:
    from src.utils.config_loader import ConfigLoader
except ImportError:
    ConfigLoader = None


class ArenaBreakoutBot:
    """
    Главный класс бота для Arena Breakout
    Версия: пацифист-бот, который только собирает лут и избегает боя
    """
    
    def __init__(self, config_path: str):
        """
        Инициализация бота
        
        Args:
            config_path: путь к файлу конфигурации
        """
        # Загрузка конфига
        self.config = self._load_config(config_path)
        
        # Настройка логирования
        self._setup_logging()
        
        # Уведомления
        self.notifier = self._setup_notifier()
        
        # Инициализация модулей
        self._init_modules()
        
        # Состояние
        self.running = False
        self.paused = False
        self.stats = {
            'start_time': None,
            'total_loot': 0,
            'actions_taken': 0,
            'errors': 0,
            'explore_time': 0,
            'loot_time': 0
        }
        
        # Event bus для коммуникации между модулями
        self.event_bus = EventBus() if EventBus else None
        
        self.logger.info("🤖 Бот инициализирован")
        print("✅ Bot initialized successfully")
    
    def _setup_logging(self):
        """Настройка логирования"""
        self.logger = logging.getLogger('arena_bot')
        
        # Если логгер не настроен, настраиваем базово
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _load_config(self, config_path: str) -> dict:
        """Загрузка конфигурации"""
        config_path = Path(config_path)
        
        if config_path.exists() and ConfigLoader:
            try:
                return ConfigLoader.load(str(config_path))
            except Exception as e:
                print(f"⚠️ Could not load config: {e}")
        
        # Возвращаем конфиг по умолчанию
        return {
            'bot': {'loop_fps': 10},
            'model': {'path': 'models/best.pt', 'device': 'cpu', 'confidence_threshold': 0.5},
            'capture': {'fps': 30, 'monitor': 1},
            'control': {
                'mouse': {'human_like': True, 'jitter': 5},
                'keyboard': {'human_like': True}
            },
            'strategies': {},
            'logging': {'level': 'INFO'}
        }
    
    def _setup_notifier(self):
        """Настройка уведомлений"""
        if TelegramNotifier:
            return TelegramNotifier(self.config.get('telegram', {}))
        else:
            # Заглушка для уведомлений
            class DummyNotifier:
                def send(self, msg): 
                    print(f"📨 [NOTIFICATION] {msg}")
                def send_photo(self, path, caption): 
                    print(f"📸 [PHOTO] {caption}")
                def send_stats(self, stats): 
                    print(f"📊 [STATS] {stats}")
            return DummyNotifier()
    
    def _init_modules(self):
        """Инициализация всех модулей с проверкой наличия классов"""
        
        # Vision
        if YOLODetector:
            try:
                self.detector = YOLODetector(
                    model_path=self.config.get('model', {}).get('path', 'models/best.pt'),
                    device=self.config.get('model', {}).get('device', 'cpu')
                )
            except Exception as e:
                print(f"⚠️ Error initializing YOLODetector: {e}")
                self.detector = None
        else:
            self.detector = None
        
        # Control
        if MouseController:
            try:
                self.mouse = MouseController(self.config.get('control', {}).get('mouse', {}))
            except Exception as e:
                print(f"⚠️ Error initializing MouseController: {e}")
                self.mouse = None
        else:
            self.mouse = None
        
        if KeyboardController:
            try:
                self.keyboard = KeyboardController(self.config.get('control', {}).get('keyboard', {}))
            except Exception as e:
                print(f"⚠️ Error initializing KeyboardController: {e}")
                self.keyboard = None
        else:
            self.keyboard = None
        
        # Brain
        if DecisionEngine:
            try:
                self.decision_engine = DecisionEngine(self.config)
            except Exception as e:
                print(f"⚠️ Error initializing DecisionEngine: {e}")
                self.decision_engine = None
        else:
            self.decision_engine = None
        
        if StateMachine:
            try:
                self.state_machine = StateMachine()
            except Exception as e:
                print(f"⚠️ Error initializing StateMachine: {e}")
                self.state_machine = None
        else:
            self.state_machine = None
        
        # Capture
        if ScreenCapture:
            try:
                self.capture = ScreenCapture(
                    fps=self.config.get('capture', {}).get('fps', 30),
                    monitor=self.config.get('capture', {}).get('monitor', 1)
                )
            except Exception as e:
                print(f"⚠️ Error initializing ScreenCapture: {e}")
                self.capture = self._create_simple_capture()
        else:
            self.capture = self._create_simple_capture()
    
    def _create_simple_capture(self):
        """Создание простого захвата экрана"""
        try:
            from mss import mss
            import cv2
            
            class SimpleCapture:
                def __init__(self):
                    self.sct = mss()
                    self.monitor = self.sct.monitors[1]
                
                def get_frame(self):
                    screenshot = np.array(self.sct.grab(self.monitor))
                    return cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            
            return SimpleCapture()
        except ImportError:
            print("❌ Cannot create screen capture")
            return None
    
    def start(self):
        """Запуск бота"""
        self.running = True
        self.stats['start_time'] = time.time()
        
        self.logger.info("🚀 Бот запущен")
        print("\n" + "="*50)
        print("🚀 ARENA BREAKOUT PACIFIST BOT STARTED")
        print("="*50)
        print("📊 Press Ctrl+C to stop")
        print("="*50 + "\n")
        
        try:
            self._run_loop()
        except KeyboardInterrupt:
            self.stop()
    
    def _run_loop(self):
        """Главный цикл бота"""
        loop_fps = self.config.get('bot', {}).get('loop_fps', 10)
        loop_delay = 1.0 / loop_fps
        
        while self.running:
            try:
                if self.paused:
                    time.sleep(1)
                    continue
                
                # 1. Захват экрана
                frame = None
                if self.capture:
                    frame = self.capture.get_frame()
                
                # 2. Детекция объектов
                detections = []
                if self.detector and frame is not None:
                    try:
                        detections = self.detector.detect(frame)
                    except Exception as e:
                        self.logger.error(f"Detection error: {e}")
                
                # 3. Получение состояния игры
                game_state = self._get_game_state(frame)
                
                # 4. Принятие решения
                action = self._decide_action(detections, game_state)
                
                # 5. Выполнение действия
                self._execute_action(action, detections, game_state)
                
                # 6. Обновление статистики
                self.stats['actions_taken'] += 1
                
                # 7. Вывод статуса
                if self.stats['actions_taken'] % 10 == 0:
                    self._print_status()
                
                # 8. Задержка
                time.sleep(loop_delay)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                self.stats['errors'] += 1
                time.sleep(5)
    
    def _decide_action(self, detections, game_state):
        """Принятие решения о действии"""
        if self.decision_engine:
            try:
                action = self.decision_engine.decide(detections, game_state)
                return action.value if hasattr(action, 'value') else str(action)
            except Exception as e:
                self.logger.error(f"Decision error: {e}")
        
        # Заглушка для принятия решений
        if detections:
            return 'move_to_loot'
        else:
            return 'explore'
    
    def _execute_action(self, action, detections, game_state):
        """Выполнение действия"""
        action = action.lower() if action else 'explore'
        
        if 'explore' in action:
            self._explore()
            
        elif 'move_to_loot' in action:
            if detections:
                self._move_to_loot(detections[0])
            else:
                self._explore()
            
        elif 'loot' in action:
            self._loot()
            
        elif 'evade' in action:
            self._evade()
            
        elif 'wait' in action:
            time.sleep(1)
        else:
            self._explore()
    
    def _explore(self):
        """Исследование карты"""
        if not self.keyboard:
            print("🔍 Exploring (mock mode)")
            time.sleep(2)
            return
        
        # Случайное движение
        direction = random.choice(['w', 'a', 's', 'd'])
        duration = random.uniform(1.0, 3.0)
        
        self.keyboard.press_key(direction)
        time.sleep(duration)
        self.keyboard.release_key(direction)
        
        # Осматриваемся
        if self.mouse:
            self._look_around()
        
        self.stats['explore_time'] += duration
    
    def _look_around(self):
        """Поворот камеры как человек"""
        if not self.mouse:
            return
        
        # Случайное движение мыши
        for _ in range(random.randint(1, 3)):
            dx = random.randint(-200, 200)
            dy = random.randint(-100, 100)
            try:
                if hasattr(self.mouse, 'move_rel'):
                    self.mouse.move_rel(dx, dy)
                time.sleep(random.uniform(0.3, 0.8))
            except:
                pass
    
    def _move_to_loot(self, target):
        """Движение к луту"""
        if not self.keyboard:
            print(f"🎯 Moving to loot: {target.get('class', 'unknown')}")
            time.sleep(1)
            return
        
        # Поворачиваем камеру к цели
        if self.mouse and 'center' in target:
            try:
                self.mouse.move_to(target['center'][0], target['center'][1])
            except:
                pass
        
        # Идем вперед
        self.keyboard.press_key('w')
        time.sleep(random.uniform(1.5, 2.5))
        self.keyboard.release_key('w')
    
    def _loot(self):
        """Лутание"""
        if not self.keyboard:
            print("📦 Looting...")
            self.stats['total_loot'] += 1
            time.sleep(1)
            return
        
        # Нажимаем кнопку взаимодействия
        interact_key = self.config.get('game', {}).get('interact_key', 'e')
        self.keyboard.tap_key(interact_key)
        
        self.stats['total_loot'] += 1
        self.stats['loot_time'] += 1
    
    def _evade(self):
        """Уклонение от опасности"""
        if not self.keyboard:
            print("🏃 Evading!")
            time.sleep(2)
            return
        
        # Бежим назад
        self.keyboard.press_key('s')
        time.sleep(2)
        self.keyboard.release_key('s')
        
        # Поворачиваем камеру
        if self.mouse:
            try:
                if hasattr(self.mouse, 'move_rel'):
                    self.mouse.move_rel(-500, 0)
            except:
                pass
    
    def _get_game_state(self, frame) -> dict:
        """Получение состояния игры"""
        return {
            'health': 100,
            'ammo': 30,
            'in_combat': False
        }
    
    def _print_status(self):
        """Вывод статуса в консоль"""
        runtime = time.time() - self.stats['start_time']
        print(f"\r📊 Runtime: {runtime//60:.0f}m | "
              f"Loot: {self.stats['total_loot']} | "
              f"Actions: {self.stats['actions_taken']} | "
              f"Errors: {self.stats['errors']}", end='')
    
    def stop(self):
        """Остановка бота"""
        print("\n" + "="*50)
        print("🛑 Stopping bot...")
    
        self.running = False
    
        # Отправка статистики в Telegram
        if self.stats['start_time']:
            runtime = time.time() - self.stats['start_time']
            hours = int(runtime // 3600)
            minutes = int((runtime % 3600) // 60)
        
            stats_message = (
                f"📊 <b>Бот остановлен</b>\n"
                f"⏱️ Время работы: {hours}ч {minutes}м\n"
                "📦 Собрано лута: {self.stats['total_loot']}\n"
                f"⚡ Действий: {self.stats['actions_taken']}\n"
                f"❌ Ошибок: {self.stats['errors']}"
            )
        
            # Печатаем в консоль
            print(stats_message.replace('<b>', '').replace('</b>', ''))
        
            # Отправляем в Telegram
            if hasattr(self, 'notifier') and self.notifier:
                self.notifier.send(stats_message)
    
        # Очистка ресурсов
        self._cleanup()
    
        print("👋 Bot stopped")
        print("="*50)
    
    def _cleanup(self):
        """Очистка ресурсов"""
        if hasattr(self, 'keyboard') and self.keyboard:
            try:
                self.keyboard.release_all()
            except:
                pass
        
        try:
            cv2.destroyAllWindows()
        except:
            pass
        
        self.logger.info("🧹 Resources cleaned up")
    
    def pause(self):
        """Пауза"""
        self.paused = True
        self.logger.info("⏸️ Bot paused")
    
    def resume(self):
        """Продолжение"""
        self.paused = False
        self.logger.info("▶️ Bot resumed")


# Для тестирования
if __name__ == '__main__':
    print("Testing bot module...")
    bot = ArenaBreakoutBot('../configs/bot_config.yaml')
    print("✅ Bot class loaded successfully")