"""
Модуль логирования для бота
"""
import logging
import sys
from pathlib import Path
from typing import Optional
import yaml
from datetime import datetime

# Глобальный экземпляр логгера
_logger = None

def setup_logging(config_path: Optional[str] = None, log_level: Optional[str] = None) -> logging.Logger:
    """
    Настройка логирования
    
    Args:
        config_path: путь к конфигу логирования (опционально)
        log_level: уровень логирования (опционально)
        
    Returns:
        настроенный логгер
    """
    global _logger
    
    if _logger is not None:
        return _logger
    
    # Создаем логгер
    logger = logging.getLogger('arena_bot')
    
    # Если указан конфиг, загружаем из него
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            level = config.get('level', 'INFO')
            log_file = config.get('file', 'logs/bot.log')
            format_str = config.get('format', 'detailed')
        except:
            # Если ошибка, используем значения по умолчанию
            level = log_level or 'INFO'
            log_file = 'logs/bot.log'
            format_str = 'detailed'
    else:
        # Значения по умолчанию
        level = log_level or 'INFO'
        log_file = 'logs/bot.log'
        format_str = 'detailed'
    
    # Устанавливаем уровень
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Создаем папку для логов если нужно
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Формат логов
    if format_str == 'detailed':
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    elif format_str == 'simple':
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
    else:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
    
    # Очищаем старые обработчики
    logger.handlers.clear()
    
    # Консольный вывод
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Файловый вывод
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to create file handler: {e}")
    
    _logger = logger
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Получение логгера
    
    Args:
        name: имя для дочернего логгера (опционально)
        
    Returns:
        экземпляр логгера
    """
    global _logger
    
    if _logger is None:
        _logger = setup_logging()
    
    if name:
        return _logger.getChild(name)
    
    return _logger


class LoggerMixin:
    """Mixin класс для добавления логгера в другие классы"""
    
    @property
    def logger(self) -> logging.Logger:
        """Логгер для класса"""
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger


# Для тестирования
if __name__ == '__main__':
    # Настраиваем логирование
    logger = setup_logging(log_level='DEBUG')
    
    # Тестируем
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    # Тестируем дочерний логгер
    child = get_logger('test')
    child.info("Child logger message")
    
    print("✅ Logger works!")