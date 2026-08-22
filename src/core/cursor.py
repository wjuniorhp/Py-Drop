from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from src.utils import helpers as utils

class CursorTracker(QObject):
    edge_entered = pyqtSignal()
    edge_left = pyqtSignal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.screen_width, self.screen_height = utils.get_screen_size()
        
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
        edge_side = self.config.get("edge_side")
        trigger_width = self.config.get("trigger_width")
        trigger_height_percent = self.config.get("trigger_height_percent")
        if trigger_height_percent is None: trigger_height_percent = 60
        
        # Area bounds
        area_height = int(self.screen_height * (trigger_height_percent / 100.0))
        y_pos = int((self.screen_height - area_height) / 2)
        
        if edge_side == "left":
            on_edge = cx <= trigger_width
        else: # right
            on_edge = cx >= (self.screen_width - trigger_width)
            
        # Check vertical bounds (must be within the area height)
        if on_edge:
            if not (y_pos <= cy <= y_pos + area_height):
                on_edge = False
            
        if on_edge and utils.is_foreground_fullscreen():
            on_edge = False
            
        if on_edge and not self.is_hovering_edge:
            self.is_hovering_edge = True
            self.edge_entered.emit()
        elif not on_edge and self.is_hovering_edge:
            self.is_hovering_edge = False
            self.edge_left.emit()
