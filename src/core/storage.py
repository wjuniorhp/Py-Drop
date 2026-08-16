import json
import os
from pathlib import Path

# Base directory is the directory of this file
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"

class Storage:
    def __init__(self, filename="items.json"):
        self.filepath = DATA_DIR / filename
        self._cache = []
        self.load()

    def load(self):
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._cache = []
        else:
            self._cache = []
        return self._cache

    def save(self, data):
        self._cache = data
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except IOError:
            pass # Fail silently for now

    def get_all(self):
        return self._cache
