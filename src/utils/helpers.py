import ctypes
from ctypes import wintypes

# Windows API types
user32 = ctypes.windll.user32

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG)
    ]

def get_cursor_pos():
    """Returns the current (x, y) coordinates of the global cursor."""
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)

def get_screen_size():
    """Returns the width and height of the primary monitor."""
    width = user32.GetSystemMetrics(0) # SM_CXSCREEN
    height = user32.GetSystemMetrics(1) # SM_CYSCREEN
    return width, height

def is_foreground_fullscreen():
    """Returns True if the current active foreground window is fullscreen."""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return False
        
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    
    screen_w, screen_h = get_screen_size()
    
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    
    # A fullscreen window covers the entire screen
    if width >= screen_w and height >= screen_h:
        # Ignore the desktop wallpaper itself
        class_name = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_name, 256)
        if class_name.value not in ("Progman", "WorkerW"):
            return True
            
    return False

def make_window_transparent(hwnd, alpha=255):
    """Sets a window to be layered and transparent if needed."""
    # WS_EX_LAYERED = 0x00080000
    # GWL_EXSTYLE = -20
    # LWA_ALPHA = 0x00000002
    
    style = user32.GetWindowLongW(hwnd, -20)
    # user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
    # user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)
    pass

import time
def format_relative_time(timestamp):
    if not timestamp:
        return ""
    diff = int(time.time() - timestamp)
    if diff < 60:
        return "Agora mesmo"
    elif diff < 3600:
        return f"há {diff // 60}m"
    elif diff < 86400:
        return f"há {diff // 3600}h"
    else:
        return f"há {diff // 86400}d"

def set_click_through(hwnd, click_through=True):
    """Makes the window click-through (transparent to mouse events)."""
    # WS_EX_TRANSPARENT = 0x00000020
    style = user32.GetWindowLongW(hwnd, -20)
    if click_through:
        user32.SetWindowLongW(hwnd, -20, style | 0x00000020)
    else:
        user32.SetWindowLongW(hwnd, -20, style & ~0x00000020)
