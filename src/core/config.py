import json
import os
from pathlib import Path

# Base directory is the directory of this file
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"

DEFAULT_CONFIG = {
    "edge_side": "left",
    "trigger_width": 5,
    "theme": "dark",
    "sound_enabled": False,
    "hotkey": "Ctrl+Alt+V",
    "shelf_width": 340,
    "translucent_background": False,
    "accent_color": "#4CAF50",
    "language": "pt_BR",
    "trigger_height_percent": 60,
    "click_to_paste": True
}

class Config:
    def __init__(self, filename="config.json"):
        self.filepath = DATA_DIR / filename
        self.settings = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    self.settings.update(user_config)
            except (json.JSONDecodeError, IOError):
                pass
        else:
            self.save() # create default
            
        return self.settings

    def save(self):
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except IOError:
            pass

    def get(self, key):
        return self.settings.get(key, DEFAULT_CONFIG.get(key))
        
    def set(self, key, value):
        self.settings[key] = value
        self.save()
