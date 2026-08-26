import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.core.clipboard import ClipboardWatcher
from src.core.cursor import CursorTracker
from src.ui.shelf import EdgeDropShelf
from src.core.config import Config
from src.core.storage import Storage
from src.utils.audio import AudioEngine
from src.core.hotkey import GlobalHotkey, parse_hotkey_string
from src.core.i18n import set_language

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Py-Drop")
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a2a2a; border: 1px solid #555555; padding: 4px; border-radius: 4px; }")
    
    config = Config()
    set_language(config.get("language"))
    
    audio = AudioEngine(config)
    storage = Storage()
    
    clipboard_watcher = ClipboardWatcher(storage, audio)
    
    shelf = EdgeDropShelf(clipboard_watcher, config, audio)
    
    tracker = CursorTracker(config)
    tracker.edge_entered.connect(shelf.handle_edge_enter)
    tracker.edge_left.connect(shelf.handle_edge_leave)
    
    def toggle_shelf_event():
        if shelf.is_open:
            shelf.close_shelf()
        else:
            from src.utils.helpers import get_cursor_pos, get_screen_geometry
            cx, cy = get_cursor_pos()
            s_name, sx, sy, sw, sh = get_screen_geometry(cx, cy)
            edge_sides = config.get("edge_sides", {})
            edge_side = edge_sides.get(s_name, config.get("edge_side", "left"))
            shelf.handle_edge_enter((s_name, sx, sy, sw, sh, edge_side))
            shelf.open_shelf()
            
    hotkey = GlobalHotkey()
    hotkey.activated.connect(toggle_shelf_event)
    
    modifiers, vk = parse_hotkey_string(config.get("hotkey"))
    if vk != 0:
        hotkey.start_hotkey(modifiers, vk)
        
    shelf.set_hotkey_manager(hotkey)

    tracker.start()
    
    app.setQuitOnLastWindowClosed(False)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
