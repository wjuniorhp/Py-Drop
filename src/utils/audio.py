import winsound
import threading

class AudioEngine:
    def __init__(self, config):
        self.config = config

    def _play_async(self, sound_type):
        if not self.config.get("sound_enabled"):
            return
            
        def play():
            try:
                if sound_type == "copy":
                    # A high-pitched short pip
                    winsound.Beep(1200, 50)
                elif sound_type == "delete":
                    # A low thud
                    winsound.Beep(300, 80)
                elif sound_type == "toggle":
                    # Click
                    winsound.Beep(800, 40)
            except Exception:
                pass
                
        threading.Thread(target=play, daemon=True).start()

    def play_copy(self):
        self._play_async("copy")
        
    def play_delete(self):
        self._play_async("delete")
        
    def play_toggle(self):
        self._play_async("toggle")
