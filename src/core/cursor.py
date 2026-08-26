from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from src.utils import helpers as utils

class CursorTracker(QObject):
    edge_entered = pyqtSignal(object)
    edge_left = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        
        self.is_hovering_edge = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._track)
        self.timer.setInterval(50)

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def _track(self):
        cx, cy = utils.get_cursor_pos()
        trigger_width = self.config.get("trigger_width")
        trigger_height_percent = self.config.get("trigger_height_percent")
        if trigger_height_percent is None: trigger_height_percent = 60
        
        # Get screen geometry for the current cursor position
        s_name, sx, sy, sw, sh = utils.get_screen_geometry(cx, cy)
        
        edge_sides = self.config.get("edge_sides", {})
        edge_side = edge_sides.get(s_name, self.config.get("edge_side", "left"))
        
        # Area bounds
        area_height = int(sh * (trigger_height_percent / 100.0))
        y_pos = sy + int((sh - area_height) / 2)
        
        if edge_side == "left":
            on_edge = cx <= sx + trigger_width
        else: # right
            on_edge = cx >= (sx + sw - trigger_width)
            
        # Check vertical bounds (must be within the area height)
        if on_edge:
            if not (y_pos <= cy <= y_pos + area_height):
                on_edge = False
            
        if on_edge and not self.is_hovering_edge:
            self.is_hovering_edge = True
            self.edge_entered.emit((s_name, sx, sy, sw, sh, edge_side))
        elif not on_edge and self.is_hovering_edge:
            self.is_hovering_edge = False
            self.edge_left.emit()

