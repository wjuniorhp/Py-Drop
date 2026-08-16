from PyQt6.QtCore import QThread, pyqtSignal
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012

# Modifiers
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008

class GlobalHotkey(QThread):
    activated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = False
        self.thread_id = None
        self.hotkey_id = 1
        self.modifiers = 0
        self.vk = 0

    def start_hotkey(self, modifiers, vk):
        if self.running:
            self.stop_hotkey()
            
        self.modifiers = modifiers
        self.vk = vk
        self.running = True
        self.start()

    def stop_hotkey(self):
        self.running = False
        if self.thread_id:
            user32.PostThreadMessageA(self.thread_id, WM_QUIT, 0, 0)
        self.wait(1000)

    def run(self):
        self.thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
        
        if not user32.RegisterHotKey(None, self.hotkey_id, self.modifiers, self.vk):
            print("Failed to register hotkey")
            return

        msg = wintypes.MSG()
        while self.running:
            bRet = user32.GetMessageA(ctypes.byref(msg), None, 0, 0)
            if bRet == 0 or bRet == -1:
                break
                
            if msg.message == WM_HOTKEY:
                if msg.wParam == self.hotkey_id:
                    self.activated.emit()
                    
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageA(ctypes.byref(msg))
            
        user32.UnregisterHotKey(None, self.hotkey_id)

def parse_hotkey_string(hotkey_str):
    """
    Parses a string like 'Ctrl+Alt+V' into (modifiers, vk)
    """
    if not hotkey_str:
        return 0, 0
        
    parts = [p.strip().upper() for p in hotkey_str.split('+')]
    
    modifiers = 0
    vk = 0
    
    for part in parts:
        if part in ('CTRL', 'CONTROL'):
            modifiers |= MOD_CONTROL
        elif part == 'ALT':
            modifiers |= MOD_ALT
        elif part == 'SHIFT':
            modifiers |= MOD_SHIFT
        elif part == 'WIN':
            modifiers |= MOD_WIN
        else:
            # Try to get VK code
            if len(part) == 1:
                # Letters A-Z or Numbers 0-9
                vk = ord(part)
            elif part.startswith('F') and part[1:].isdigit():
                f_num = int(part[1:])
                if 1 <= f_num <= 24:
                    vk = 0x6F + f_num # 0x70 is VK_F1
            elif part in ('SPACE', 'SPACEBAR'):
                vk = 0x20
            elif part in ('RETURN', 'ENTER'):
                vk = 0x0D
            elif part in ('ESCAPE', 'ESC'):
                vk = 0x1B
                
    return modifiers, vk
