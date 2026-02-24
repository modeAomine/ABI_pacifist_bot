"""
Telegram уведомления для бота
"""
import os
import requests
from dotenv import load_dotenv
from datetime import datetime

class TelegramNotifier:
    """Отправка уведомлений в Telegram"""
    
    def __init__(self, config=None):
        # Загружаем переменные из .env файла
        load_dotenv()
        
        # Получаем токен и chat_id (сначала из конфига, потом из .env)
        if config and config.get('enabled'):
            self.token = config.get('token')
            self.chat_id = config.get('chat_id')
        else:
            self.token = os.getenv('TELEGRAM_TOKEN')
            self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
            self.bot_name = os.getenv('BOT_NAME', 'ArenaBot')
        
        # Проверяем, всё ли есть для работы
        if self.token and self.chat_id:
            self.enabled = True
            self.api_url = f"https://api.telegram.org/bot{self.token}"
            print("✅ Telegram уведомления включены")
            
            # Отправляем тестовое сообщение при запуске
            self.send("🟢 Бот запущен и готов к работе!")
        else:
            self.enabled = False
            print("📵 Telegram уведомления отключены (нет токена или chat_id)")
    
    def send(self, message):
        """Отправка сообщения"""
        if not self.enabled:
            # Если Telegram отключен, просто печатаем в консоль
            print(f"📨 [Telegram] {message}")
            return True
        
        try:
            # Добавляем имя бота и время
            timestamp = datetime.now().strftime("%H:%M:%S")
            full_message = f"🤖 <b>{self.bot_name}</b> [{timestamp}]\n{message}"
            
            url = f"{self.api_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': full_message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Telegram: {message[:50]}...")
                return True
            else:
                print(f"❌ Telegram error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def send_stats(self, stats):
        """Отправка статистики"""
        message = "📊 <b>Статистика</b>\n"
        for key, value in stats.items():
            message += f"• {key}: {value}\n"
        return self.send(message)
    
    def send_screenshot(self, image_path, caption=""):
        """Отправка скриншота (пока заглушка)"""
        print(f"📸 [Telegram] Screenshot: {caption}")
        return True


# Для тестирования
if __name__ == "__main__":
    # Тестируем без .env файла
    print("Тест 1: Без .env")
    notifier1 = TelegramNotifier()
    notifier1.send("Тестовое сообщение 1")
    
    print("\nТест 2: С конфигом")
    notifier2 = TelegramNotifier({'enabled': True, 'token': 'test', 'chat_id': 'test'})
    notifier2.send_stats({'loot': 10, 'time': '5m'})