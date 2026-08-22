from src.core.i18n import tr
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
        return tr("Agora mesmo")
    elif diff < 3600:
        return f"{tr('há ')}{diff // 60}{tr('m')}"
    elif diff < 86400:
        return f"{tr('há ')}{diff // 3600}{tr('h')}"
    else:
        return f"{tr('há ')}{diff // 86400}{tr('d')}"

import datetime
def get_time_group(timestamp):
    """
    Categoriza um timestamp em grupos: Hoje, Ontem, Esta Semana, Este Mês, Antigos.
    Retorna uma tupla (ordem, nome_traduzido).
    """
    if not timestamp:
        return (99, tr("Antigos"))
        
    now = datetime.datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    item_date = datetime.datetime.fromtimestamp(timestamp)
    item_start = item_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    days_diff = (today_start - item_start).days
    
    if days_diff == 0:
        return (0, tr("Hoje"))
    elif days_diff == 1:
        return (1, tr("Ontem"))
    elif days_diff <= 7:
        return (2, tr("Últimos 7 dias"))
    elif days_diff <= 30:
        return (3, tr("Últimos 30 dias"))
    else:
        return (4, tr("Antigos"))

def set_click_through(hwnd, click_through=True):
    """Makes the window click-through (transparent to mouse events)."""
    # WS_EX_TRANSPARENT = 0x00000020
    style = user32.GetWindowLongW(hwnd, -20)
    if click_through:
        user32.SetWindowLongW(hwnd, -20, style | 0x00000020)
    else:
        user32.SetWindowLongW(hwnd, -20, style & ~0x00000020)

def get_foreground_window():
    return user32.GetForegroundWindow()

def set_foreground_window(hwnd):
    if hwnd:
        user32.SetForegroundWindow(hwnd)

def simulate_paste():
    VK_CONTROL = 0x11
    VK_V = 0x56
    KEYEVENTF_KEYUP = 0x0002
    
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    user32.keybd_event(VK_V, 0, 0, 0)
    user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
