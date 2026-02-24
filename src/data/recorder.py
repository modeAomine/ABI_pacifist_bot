# src/data/recorder.py
import cv2
import numpy as np
from mss import mss
import time
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

class DataRecorder:
    """Запись геймплея для создания датасета"""
    
    def __init__(self, output_dir: str = 'data/raw'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.sct = mss()
        self.monitor = self.sct.monitors[1]
        
        self.recording = False
        self.frame_count = 0
        self.fps = 0
        self.last_time = time.time()
        
        print(f"📁 Screenshots will be saved to: {self.output_dir.absolute()}")
    
    def start_recording(self, save_every_n_frames: int = 30) -> None:
        """Start recording gameplay"""
        print(f"\n🔴 Recording (saving every {save_every_n_frames} frame)")
        print("Press 'Q' to stop")
        print("-" * 50)
        
        self.recording = True
        self.frame_count = 0
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        while self.recording:
            # Capture screen
            screenshot = np.array(self.sct.grab(self.monitor))
            frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
            
            # Calculate FPS
            self.frame_count += 1
            if self.frame_count % 30 == 0:
                current_time = time.time()
                self.fps = 30 / (current_time - self.last_time)
                self.last_time = current_time
            
            # Save every N-th frame
            if self.frame_count % save_every_n_frames == 0:
                filename = f"{timestamp}_frame_{self.frame_count:06d}.png"
                filepath = self.output_dir / filename
                cv2.imwrite(str(filepath), frame)
                
                print(f"📸 Saved frame {self.frame_count} | FPS: {self.fps:.1f} | {filename}")
            
            # Preview
            preview = frame.copy()
            cv2.putText(preview, f"Recording... Frames: {self.frame_count}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.putText(preview, f"Saved: {self.frame_count // save_every_n_frames}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(preview, "Press 'Q' to stop", 
                       (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Data Recording', preview)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.recording = False
                break
        
        self.stop_recording()
    
    def stop_recording(self) -> None:
        """Stop recording and show stats"""
        self.recording = False
        cv2.destroyAllWindows()
        saved = self.frame_count // 30
        print(f"\n⏹️ Recording stopped")
        print(f"📊 Total frames: {self.frame_count}")
        print(f"💾 Saved images: {saved}")