"""
Загрузчик конфигурационных файлов
"""
import yaml
import os
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigLoader:
    """Загрузчик конфигураций из YAML файлов"""
    
    @staticmethod
    def load(config_path: str) -> Dict[str, Any]:
        """
        Загружает конфигурацию из YAML файла
        
        Args:
            config_path: путь к файлу конфигурации
            
        Returns:
            словарь с конфигурацией
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Подстановка переменных окружения
        config = ConfigLoader._substitute_env_vars(config)
        
        return config
    
    @staticmethod
    def save(config: Dict[str, Any], config_path: str) -> None:
        """
        Сохраняет конфигурацию в YAML файл
        
        Args:
            config: словарь с конфигурацией
            config_path: путь для сохранения
        """
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    @staticmethod
    def _substitute_env_vars(obj: Any) -> Any:
        """
        Рекурсивно заменяет ${VAR} на значения переменных окружения
        
        Args:
            obj: объект для обработки
            
        Returns:
            объект с подставленными переменными
        """
        if isinstance(obj, dict):
            return {key: ConfigLoader._substitute_env_vars(value) 
                   for key, value in obj.items()}
        elif isinstance(obj, list):
            return [ConfigLoader._substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            env_var = obj[2:-1]
            return os.getenv(env_var, obj)
        else:
            return obj
    
    @staticmethod
    def merge(base_config: Dict, override_config: Dict) -> Dict:
        """
        Рекурсивно объединяет два конфига
        
        Args:
            base_config: базовый конфиг
            override_config: конфиг с приоритетными значениями
            
        Returns:
            объединенный конфиг
        """
        result = base_config.copy()
        
        for key, value in override_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigLoader.merge(result[key], value)
            else:
                result[key] = value
        
        return result


# Для тестирования
if __name__ == '__main__':
    # Создаем тестовый конфиг
    test_config = {
        'bot': {
            'name': 'TestBot',
            'version': '1.0.0'
        },
        'telegram': {
            'token': '${TELEGRAM_TOKEN}',
            'chat_id': '${TELEGRAM_CHAT_ID}'
        }
    }
    
    # Сохраняем
    ConfigLoader.save(test_config, 'test_config.yaml')
    print("✅ Config saved")
    
    # Загружаем
    loaded = ConfigLoader.load('test_config.yaml')
    print(f"✅ Config loaded: {loaded}")