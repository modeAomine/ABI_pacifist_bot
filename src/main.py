#!/usr/bin/env python3
"""
Arena Breakout Pacifist Bot
Main entry point
"""
import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    parser = argparse.ArgumentParser(description='Arena Breakout Bot')
    parser.add_argument('--mode', type=str, choices=['bot', 'record', 'train'], 
                       default='bot', help='Operation mode')
    parser.add_argument('--config', type=str, default='configs/bot_config.yaml',
                       help='Path to config file')
    parser.add_argument('--model', type=str, help='Path to model file')
    
    args = parser.parse_args()
    
    print(f"🚀 Starting bot in {args.mode} mode...")
    
    if args.mode == 'record':
        # Data recording mode
        try:
            from src.data.recorder import DataRecorder
            recorder = DataRecorder()
            recorder.start_recording()
        except ImportError as e:
            print(f"❌ Error importing recorder: {e}")
            print("Make sure src/data/recorder.py exists")
            return 1
    
    elif args.mode == 'train':
        # Training mode
        try:
            from src.training.trainer import ModelTrainer
            trainer = ModelTrainer('configs/training_config.yaml')
            trainer.train()
        except ImportError as e:
            print(f"❌ Error importing trainer: {e}")
            print("Training module not ready yet")
            return 1
    
    else:
        # Bot mode
        try:
            from src.core.bot import ArenaBreakoutBot
            
            # Проверяем существование конфига
            config_path = Path(args.config)
            if not config_path.exists():
                print(f"⚠️ Config file not found: {config_path}")
                print("Using default configuration")
                # Создаем дефолтный конфиг
                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, 'w') as f:
                    f.write("""
bot:
  name: "ArenaBreakoutBot"
  loop_fps: 10
capture:
  fps: 30
  monitor: 1
model:
  path: "models/best.pt"
  device: "cpu"
control:
  mouse:
    human_like: true
  keyboard:
    human_like: true
logging:
  level: "INFO"
                    """)
            
            bot = ArenaBreakoutBot(args.config)
            
            if args.model:
                if hasattr(bot, 'detector') and bot.detector:
                    bot.detector.load_model(args.model)
            
            try:
                bot.start()
            except KeyboardInterrupt:
                bot.stop()
            except Exception as e:
                print(f"❌ Bot error: {e}")
                return 1
                
        except ImportError as e:
            print(f"❌ Error importing bot: {e}")
            print("Make sure all modules are properly implemented")
            return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())