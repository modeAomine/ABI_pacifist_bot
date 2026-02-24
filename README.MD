# Arena Breakout Pacifist Bot 🤖

Бот для автоматического сбора лута в игре Arena Breakout. Использует компьютерное зрение (YOLO) для детекции объектов и эмулирует человеческое поведение для обхода античита.

## 🎯 Возможности

- ✅ Компьютерное зрение (YOLOv8) для поиска лута
- ✅ Эмуляция человеческих движений мыши (кривые Безье, микро-дрожание)
- ✅ Случайные паузы и "ошибки" как у реального игрока
- ✅ Telegram уведомления о работе
- ✅ Режим записи данных для обучения
- ✅ Поддержка нескольких аккаунтов
- ✅ Работа на облачных серверах (защита от HWID бана)

## 🏗️ Архитектура
```src/
├── core/ # Ядро бота
├── vision/ # Компьютерное зрение (YOLO)
├── control/ # Управление мышью/клавиатурой
├── brain/ # Принятие решений
├── data/ # Сбор данных
└── utils/ # Утилиты (Telegram, логи)
```

## 🚀 Установка

1. Клонируй репозиторий:
```bash
git clone https://github.com/modeAomine/ABI_pacifist_bot
cd arena-breakout-bot

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt