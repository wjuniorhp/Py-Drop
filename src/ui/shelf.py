from src.core.i18n import tr
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QScrollArea, QFrame, QApplication, QStackedWidget, QSlider, QRadioButton, QCheckBox, QComboBox, QFormLayout, QMenu
)
from PyQt6.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal, QMimeData, QUrl, QByteArray, QRect, QRectF
from PyQt6.QtGui import QIcon, QFont, QCursor, QColor, QPainter, QDrag, QDesktopServices, QKeyEvent, QPainterPath
from PyQt6.QtSvg import QSvgRenderer
from src.utils import helpers as utils
import os
import re

def create_svg(inner_html, color, size=18):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{inner_html}</svg>"""

class SvgButton(QPushButton):
    def __init__(self, inner_html, size=18, color="#666666", hover_color="#ffffff", size_fixed=24):
        super().__init__()
        self.inner_html = inner_html
        self.size_svg = size
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self._is_active = False
        self.active_color = "#4CAF50"
        
        self.setFixedSize(size_fixed, size_fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("background: transparent; border: none;")

    def set_active(self, active):
        self._is_active = active
        self.update()

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._is_active:
            current_color = self.active_color
        else:
            current_color = self.hover_color if self.is_hovered else self.color
        svg = create_svg(self.inner_html, current_color, self.size_svg)
        renderer = QSvgRenderer(QByteArray(svg.encode('utf-8')))
        renderer.render(painter)

class SvgLabel(QWidget):
    def __init__(self, inner_html, size=18, color="#aaaaaa"):
        super().__init__()
        self.inner_html = inner_html
        self.size_svg = size
        self.color = color
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        svg = create_svg(self.inner_html, self.color, self.size_svg)
        renderer = QSvgRenderer(QByteArray(svg.encode('utf-8')))
        renderer.render(painter)

class StackedIconsWidget(QWidget):
    def __init__(self, pixmaps, size=32, show_plus=False):
        super().__init__()
        self.pixmaps = pixmaps
        self.icon_size = size
        self.show_plus = show_plus
        # calculate width based on overlaps
        extra_h = 16 if show_plus else 0
        self.setFixedSize(size + (len(pixmaps)-1)*15 + 10, size + 10 + extra_h)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        inner_size = self.icon_size - 8
        spacing = 6
        
        for i, pixmap in enumerate(reversed(self.pixmaps)):
            offset = i * spacing
            rect = QRect(offset, offset, inner_size, inner_size)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(40, 40, 40))
            painter.drawRoundedRect(rect, 4, 4)
            painter.drawPixmap(rect, pixmap)
            
        if self.show_plus:
            offset = (len(self.pixmaps) - 1) * spacing
            rect = QRect(offset, offset, inner_size, inner_size)
            painter.setPen(QColor(255, 255, 255, 180))
            painter.setFont(self.font())
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "+")

    def set_invalid(self, invalid):
        self.is_invalid = invalid
        self.update()

class InvalidableLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.is_invalid = False
        
    def set_invalid(self, invalid):
        self.is_invalid = invalid
        self.update()
        
    def paintEvent(self, event):
        pix = self.pixmap()
        if pix and not pix.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            x = (self.width() - pix.width()) // 2
            y = (self.height() - pix.height()) // 2
            painter.save()
            path = QPainterPath()
            path.addRoundedRect(QRectF(x, y, pix.width(), pix.height()), 6, 6)
            painter.setClipPath(path)
            painter.drawPixmap(x, y, pix)
            painter.restore()
            if getattr(self, "is_invalid", False):
                painter.fillRect(self.rect(), QColor(20, 20, 20, 160))
                pen = painter.pen()
                pen.setColor(QColor(255, 100, 100, 200))
                pen.setWidth(2)
                painter.setPen(pen)
                y_line = self.height() // 2
                painter.drawLine(0, y_line, self.width(), y_line)
        else:
            super().paintEvent(event)
            if getattr(self, "is_invalid", False):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.fillRect(self.rect(), QColor(20, 20, 20, 160))
                pen = painter.pen()
                pen.setColor(QColor(255, 100, 100, 200))
                pen.setWidth(2)
                painter.setPen(pen)
                y_line = self.height() // 2
                painter.drawLine(0, y_line, self.width(), y_line)

# SVG Paths
PATH_PIN = '<path d="M12 17v5"/><path d="M9 10.76a2 2 0 0 1-1.11 1.79l-1.78.9A2 2 0 0 0 5 15.24V16a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-.76a2 2 0 0 0-1.11-1.79l-1.78-.9A2 2 0 0 1 15 10.76V7a1 1 0 0 1 1-1 2 2 0 0 0 0-4H8a2 2 0 0 0 0 4 1 1 0 0 1 1 1z"/>'
PATH_TRASH = '<polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>'
PATH_PAUSE = '<rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect>'
PATH_PLAY = '<polygon points="5 3 19 12 5 21 5 3"></polygon>'
PATH_SETTINGS = '<circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>'
PATH_FILE = '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline>'
PATH_LINK = '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>'
PATH_FOLDER = '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>'
PATH_GLOBE = '<circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>'
PATH_X = '<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>'
PATH_IMAGE = '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline>'
PATH_COLOR = '<path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path>'
PATH_TEXT = '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline>'

def _format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f'{size:.0f} {unit}' if unit in ['B', 'KB'] else f'{size:.1f} {unit}'
        size /= 1024.0
    return f'{size:.1f} TB'

class ImagePreviewWindow(QWidget):
    _active_windows = []

    def __init__(self, image_path, source_rect, parent=None):
        super().__init__(None)
        ImagePreviewWindow._active_windows.append(self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowTransparentForInput)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        from PyQt6.QtGui import QPixmap, QGuiApplication
        from PyQt6.QtCore import QRect, QPropertyAnimation, QEasingCurve
        
        self.image_path = image_path
        self.source_rect = source_rect
        
        screen = QGuiApplication.screenAt(source_rect.center())
        if not screen:
            screen = QGuiApplication.primaryScreen()
            
        screen_geom = screen.geometry()
        self.setGeometry(screen_geom)
        
        local_source = QRect(
            source_rect.x() - screen_geom.x(),
            source_rect.y() - screen_geom.y(),
            source_rect.width(),
            source_rect.height()
        )
        self.local_source = local_source
        
        self.pixmap = QPixmap(image_path)
        
        target_width = source_rect.width() * 5
        target_height = source_rect.height() * 5
        
        self.pixmap = self.pixmap.scaled(target_width, target_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        target_width = self.pixmap.width()
        target_height = self.pixmap.height()
        
        target_x = local_source.left() - target_width - 20
        if target_x < 0:
            target_x = local_source.right() + 20
            
        target_y = local_source.top() - (target_height - local_source.height()) // 2
        if target_y < 20: target_y = 20
        if target_y + target_height > screen_geom.height() - 20:
            target_y = screen_geom.height() - target_height - 20
            
        self.local_target = QRect(target_x, target_y, target_width, target_height)
        
        self.lbl = QLabel(self)
        self.lbl.setScaledContents(True)
        self.lbl.setPixmap(self.pixmap)
        self.lbl.setGeometry(self.local_source)
        self.lbl.setStyleSheet("""
            QLabel {
                border-radius: 8px;
                border: 2px solid rgba(255, 255, 255, 50);
                background-color: rgba(26, 26, 26, 250);
            }
        """)
        
        self.anim = QPropertyAnimation(self.lbl, b"geometry")
        self.anim.setDuration(250)
        self.anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self.anim.setStartValue(self.local_source)
        self.anim.setEndValue(self.local_target)
        
        self.is_closing = False
        
    def showEvent(self, event):
        self.anim.start()
        super().showEvent(event)

    def close_animated(self):
        if self.is_closing: return
        self.is_closing = True
        from PyQt6.QtCore import QEasingCurve
        self.anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.anim.setStartValue(self.lbl.geometry())
        self.anim.setEndValue(self.local_source)
        
        def on_finished():
            self.close()
            if self in ImagePreviewWindow._active_windows:
                ImagePreviewWindow._active_windows.remove(self)
                
        self.anim.finished.connect(on_finished)
        self.anim.start()

    @classmethod
    def close_all(cls):
        for w in list(cls._active_windows):
            if not w.is_closing:
                w.close_animated()

class SubItemWidget(QFrame):
    copy_clicked = pyqtSignal(str)
    delete_clicked = pyqtSignal(str)
    
    def get_darker(self, hex_color):
        from PyQt6.QtGui import QColor
        c = QColor(hex_color)
        return c.darker(150).name()

    def __init__(self, file_path, parent_id=None, audio=None, accent_color="#4CAF50"):
        super().__init__()
        self.file_path = file_path
        self.accent_color = accent_color
        self.parent_id = parent_id
        self.audio = audio
        self.setStyleSheet("""
            SubItemWidget {
                background-color: transparent;
                border-radius: 4px;
                border: 1px solid transparent;
            }
            SubItemWidget:hover {
                background-color: rgba(50, 50, 50, 150);
                border: 1px solid rgba(255, 255, 255, 20);
            }
        """)
        self.setFixedHeight(36)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(24, 24)
        has_thumb = False
        if os.path.exists(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                from PyQt6.QtGui import QPixmap
                img = QPixmap(file_path)
                if not img.isNull():
                    img = img.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                    
                    # Apply rounded corners to thumbnail
                    from PyQt6.QtGui import QPainter, QPainterPath
                    from PyQt6.QtCore import QRectF
                    rounded = QPixmap(24, 24)
                    rounded.fill(Qt.GlobalColor.transparent)
                    painter = QPainter(rounded)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    path = QPainterPath()
                    path.addRoundedRect(QRectF(0, 0, 24, 24), 4, 4)
                    painter.setClipPath(path)
                    
                    # Center the cropped image
                    x = (24 - img.width()) // 2
                    y = (24 - img.height()) // 2
                    painter.drawPixmap(x, y, img)
                    painter.end()
                    
                    icon_lbl.setPixmap(rounded)
                    has_thumb = True
                    
        if not has_thumb:
            from PyQt6.QtWidgets import QFileIconProvider
            from PyQt6.QtCore import QFileInfo
            provider = QFileIconProvider()
            icon = provider.icon(QFileInfo(file_path))
            if not icon.isNull():
                icon_lbl.setPixmap(icon.pixmap(24, 24))
                
        layout.addWidget(icon_lbl)
        v_layout = QVBoxLayout()
        v_layout.setSpacing(2)
        v_layout.setContentsMargins(0, 0, 0, 0)
        name_lbl = QLabel(os.path.basename(file_path))
        name_lbl.setStyleSheet("color: #e0e0e0; font-size: 11px;")
        size_lbl = QLabel(_format_size(os.path.getsize(file_path)) if os.path.exists(file_path) else tr("Not found"))
        size_lbl.setStyleSheet("color: #888888; font-size: 9px;")
        v_layout.addWidget(name_lbl)
        v_layout.addWidget(size_lbl)
        layout.addLayout(v_layout)
        layout.addStretch()
        
        self.actions_widget = QWidget(self)
        self.actions_layout = QHBoxLayout(self.actions_widget)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_layout.setSpacing(5)
        
        dir_btn = SvgButton(PATH_FOLDER, size=12, color="#666666", hover_color="#ffffff")
        dir_btn.setToolTip(tr("Abrir pasta"))
        def open_dir():
            if os.path.exists(self.file_path):
                if os.path.isdir(self.file_path): os.startfile(self.file_path)
                else: os.startfile(os.path.dirname(self.file_path))
        dir_btn.clicked.connect(open_dir)
        self.actions_layout.addWidget(dir_btn)
        
        del_btn = SvgButton(PATH_X, size=12, color="#666666", hover_color="#ff4444")
        del_btn.setToolTip(tr("Remove item"))
        def on_del():
            if self.audio: self.audio.play_delete()
            self.delete_clicked.emit(self.file_path)
        del_btn.clicked.connect(on_del)
        self.actions_layout.addWidget(del_btn)
        
        layout.addWidget(self.actions_widget)
        
        self.actions_widget.hide()

    def enterEvent(self, event):
        self.actions_widget.show()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.actions_widget.hide()
        super().leaveEvent(event)
        

    def _on_preview_ready(self, item_dict):
        item_id = item_dict.get("item_id")
        title = item_dict.get("title")
        img_path = item_dict.get("image")
        
        if self.item_id != item_id:
            return
        
        # In-place UI update
        if title:
            self.item["link_title"] = title
            self.link_title_lbl.setText(title)
        else:
            self.link_title_lbl.setText("Link")
            
        if img_path and os.path.exists(img_path):
            self.item["link_image"] = img_path
            from PyQt6.QtGui import QPixmap
            img = QPixmap(img_path)
            if not img.isNull():
                self.link_img_lbl = QLabel()
                pixmap = img.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                self.link_img_lbl.setPixmap(pixmap)
                self.link_img_lbl.setFixedSize(64, 64)
                self.link_img_lbl.setStyleSheet("border-radius: 8px; background-color: #2a2a2a;")
                self.link_img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.link_img_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                
                # Insert at the beginning of the horizontal layout
                self.content_layout.itemAt(self.content_layout.count() - 1).layout().insertWidget(0, self.link_img_lbl)
                
        # Persist the fetched data to history via the watcher
        shelf = self.window()
        if hasattr(shelf, 'clipboard_watcher'):
            shelf.clipboard_watcher.update_item(item_id, {
                "link_title": title,
                "link_image": img_path,
                "preview_fetched": True
            })

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
            event.accept()
        else:
            super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        drag = QDrag(self)
        mimedata = QMimeData()
        if os.path.exists(self.file_path):
            mimedata.setUrls([QUrl.fromLocalFile(self.file_path)])
            
        if hasattr(self, 'parent_id') and self.parent_id:
            from PyQt6.QtCore import QByteArray
            mimedata.setData("edgedrop/internal-drag-subitem", QByteArray(self.parent_id.encode('utf-8')))
            
        drag.setMimeData(mimedata)
        
        # Add visual preview of the dragged item
        original_pixmap = self.grab()
        from PyQt6.QtGui import QPixmap, QPainter
        transparent_pixmap = QPixmap(original_pixmap.size())
        transparent_pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(transparent_pixmap)
        painter.setOpacity(0.6)  # 60% opacity
        painter.drawPixmap(0, 0, original_pixmap)
        painter.end()
        
        drag.setPixmap(transparent_pixmap)
        drag.setHotSpot(event.pos())
        shelf = self.window()
        shelf.is_dragging = True
        shelf.active_drag_is_top_level = False
        
        if hasattr(self, 'parent_id') and self.parent_id:
            shelf.active_drag_source_id = self.parent_id
            
        if hasattr(shelf, 'start_auto_scroll'):
            shelf.start_auto_scroll()
            
        drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.LinkAction | Qt.DropAction.MoveAction)
        
        if hasattr(shelf, 'stop_auto_scroll'):
            shelf.stop_auto_scroll()
            
        shelf.is_dragging = False
        shelf.active_drag_source_id = None
        if hasattr(shelf, '_check_close'): shelf._check_close()
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if hasattr(self, 'drag_start_position') and (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
                if self.audio: self.audio.play_copy()
                self.setStyleSheet(f"SubItemWidget {{ background-color: {self.get_darker(self.accent_color)}; border-radius: 4px; border: 1px solid {self.accent_color}; }}")
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(300, lambda: self.setStyleSheet("""
                    SubItemWidget {
                        background-color: transparent;
                        border-radius: 4px;
                        border: 1px solid transparent;
                    }
                    SubItemWidget:hover {
                        background-color: rgba(50, 50, 50, 150);
                        border: 1px solid rgba(255, 255, 255, 20);
                    }
                """))
                self.copy_clicked.emit(self.file_path)
                event.accept()
                return
        elif event.button() == Qt.MouseButton.RightButton:
            ext = os.path.splitext(self.file_path)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'] and os.path.exists(self.file_path):
                if hasattr(self, 'preview_window') and self.preview_window is not None and not getattr(self.preview_window, 'is_closing', False):
                    self.preview_window.close_animated()
                    self.preview_window = None
                else:
                    ImagePreviewWindow.close_all()
                    from PyQt6.QtCore import QRect, QPoint
                    source_rect = QRect(self.mapToGlobal(QPoint(0,0)), self.size())
                    self.preview_window = ImagePreviewWindow(self.file_path, source_rect)
                    self.preview_window.show()
                if self.audio: self.audio.play_toggle()
                return
        super().mouseReleaseEvent(event)
import colorsys

def parse_color_string(s):
    s = str(s).strip()
    
    import re
    hex_match = re.match(r'^#?([0-9a-fA-F]{3,8})$', s)
    if hex_match:
        val = hex_match.group(1)
        if len(val) in [3, 4, 6, 8]:
            return '#' + val
            
    rgb_match = re.match(r'^rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)$', s, re.IGNORECASE)
    if rgb_match:
        r, g, b = int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3))
        a = float(rgb_match.group(4)) if rgb_match.group(4) else 1.0
        return f"rgba({r}, {g}, {b}, {a})"
        
    hsl_match = re.match(r'^hsla?\s*\(\s*([\d.]+)\s*,\s*([\d.]+)%?\s*,\s*([\d.]+)%?(?:\s*,\s*([\d.]+))?\s*\)$', s, re.IGNORECASE)
    if hsl_match:
        h = float(hsl_match.group(1)) / 360.0
        s_val = float(hsl_match.group(2)) / 100.0
        l_val = float(hsl_match.group(3)) / 100.0
        a = float(hsl_match.group(4)) if hsl_match.group(4) else 1.0
        r, g, b = colorsys.hls_to_rgb(h, l_val, s_val)
        return f"rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {a})"
        
    return None

class SelectableLabel(QLabel):
    def contextMenuEvent(self, event):
        if self.hasSelectedText():
            from PyQt6.QtWidgets import QMenu
            from PyQt6.QtGui import QPainter, QColor
            
            class CustomMenu(QMenu):
                def paintEvent(self, e):
                    painter = QPainter(self)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    painter.setBrush(QColor("#1f1f1f"))
                    painter.setPen(QColor("#333333"))
                    painter.drawRoundedRect(self.rect().adjusted(0, 0, -1, -1), 6, 6)
                    super().paintEvent(e)
                    
            menu = CustomMenu(self)
            menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
            menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            
            # The global stylesheet applies, but we want our custom actions
            copy_action = menu.addAction(tr("Copy"))
            copy_action.setShortcut("Ctrl+C")
            
            menu.addSeparator()
            
            select_all_action = menu.addAction(tr("Select All"))
            select_all_action.setShortcut("Ctrl+A")
            
            action = menu.exec(event.globalPos())
            if action == copy_action:
                QApplication.clipboard().setText(self.selectedText())
            elif action == select_all_action:
                self.setSelection(0, len(self.text()))
        else:
            event.ignore()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            if not self.hasSelectedText():
                event.ignore()
            else:
                super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            if not self.hasSelectedText():
                event.ignore()
            else:
                super().mouseReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)

class TimeDividerWidget(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        lbl = QLabel(title)
        lbl.setStyleSheet("color: rgba(255, 255, 255, 100); font-size: 11px; font-weight: bold;")
        lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("border: 1px solid rgba(255, 255, 255, 30);")
        line.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        layout.addWidget(lbl)
        layout.addWidget(line, stretch=1)

from PyQt6.QtCore import QRunnable, QObject, pyqtSignal

class ImageLoaderWorkerSignals(QObject):
    finished = pyqtSignal(object) # QImage

class ImageLoaderWorker(QRunnable):
    def __init__(self, path, target_width, target_height):
        super().__init__()
        self.path = path
        self.target_width = target_width
        self.target_height = target_height
        self.signals = ImageLoaderWorkerSignals()
        
    def run(self):
        from PyQt6.QtGui import QImage
        img = QImage(self.path)
        if not img.isNull():
            img = img.scaled(self.target_width, self.target_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.signals.finished.emit(img)

class ItemCard(QFrame):
    delete_clicked = pyqtSignal(str)
    pin_clicked = pyqtSignal(str)
    copy_clicked = pyqtSignal(object)
    delete_subitem_clicked = pyqtSignal(str, str)

    def get_darker(self, hex_color):
        from PyQt6.QtGui import QColor
        c = QColor(hex_color)
        return c.darker(150).name()

    def __init__(self, item, shelf_width, audio=None, accent_color="#4CAF50"):
        super().__init__()
        self.item = item
        self.item_id = item.get("id")
        
        # Snapshots for fast rendering checks
        self.render_timestamp = item.get("timestamp")
        self.render_type = item.get("type")
        self.render_pinned = item.get("pinned")
        self.render_content_len = len(item.get("content")) if isinstance(item.get("content"), list) else 1
        
        self.audio = audio
        self.shelf_width = shelf_width
        self.accent_color = accent_color
        self.drag_start_position = QPoint()
        
        # Prevent long strings without spaces (like temp image paths) from expanding the card horizontally
        self.setMaximumWidth(self.shelf_width - 28)
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("ItemCard")
        self.setStyleSheet("""
            #ItemCard {
                background-color: rgba(26, 26, 26, 200);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 10);
            }
            #ItemCard:hover {
                background-color: rgba(40, 40, 40, 220);
                border: 1px solid rgba(255, 255, 255, 30);
            }
        """)
        self.setAcceptDrops(True)
        
        self.stack_overlay = QLabel(tr("Drop here to group"), self)
        self.stack_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stack_overlay.setStyleSheet(f"""
            background-color: rgba(30, 30, 30, 230);
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            border: 2px dashed {self.accent_color};
            border-radius: 8px;
        """)
        self.stack_overlay.hide()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        
        item_type = item.get("type", "text")
        content = item.get("content", "")
        
        parsed_color = None
        if item_type == "text":
            parsed_color = parse_color_string(content)
                
        if item_type == "link": icon_path = PATH_LINK
        elif item_type == "file": icon_path = PATH_FILE
        elif item_type == "files": icon_path = PATH_FOLDER
        elif item_type == "image": icon_path = PATH_IMAGE
        elif parsed_color: icon_path = PATH_COLOR
        else: icon_path = PATH_TEXT
        
        icon_lbl = SvgLabel(icon_path, size=16, color="#aaaaaa")
        icon_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        header.addWidget(icon_lbl)
        
        time_text = utils.format_relative_time(item.get("timestamp"))
        self.time_lbl = QLabel(time_text)
        self.time_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.time_lbl.setStyleSheet("color: #555555; font-size: 10px; margin-left: 5px;")
        header.addWidget(self.time_lbl)
        
        if item_type == "link":
            act_btn = SvgButton(PATH_GLOBE, size=14, color="#888888")
            act_btn.setToolTip(tr("Open link in browser"))
            act_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.item.get("content"))))
            header.addWidget(act_btn)
        elif item_type == "file":
            act_btn = SvgButton(PATH_FOLDER, size=14, color="#888888")
            act_btn.setToolTip(tr("Open folder"))
            def open_dir():
                path = self.item.get("content")
                if os.path.isdir(path): os.startfile(path)
                else: os.startfile(os.path.dirname(path))
            act_btn.clicked.connect(open_dir)
            header.addWidget(act_btn)
        elif item_type == "text":
            text_content = str(content).strip()
            if os.path.exists(text_content):
                act_btn = SvgButton(PATH_FOLDER, size=14, color="#888888")
                act_btn.setToolTip(tr("Open folder"))
                def open_text_dir():
                    path = self.item.get("content").strip()
                    if os.path.isdir(path): os.startfile(path)
                    else: os.startfile(os.path.dirname(path))
                act_btn.clicked.connect(open_text_dir)
                header.addWidget(act_btn)
        elif item_type == "files":
            files = self.item.get("content", [])
            if files:
                dirs = set(os.path.normcase(os.path.dirname(p)) for p in files)
                if len(dirs) == 1:
                    act_btn = SvgButton(PATH_FOLDER, size=14, color="#888888")
                    act_btn.setToolTip(tr("Open folder"))
                    def open_group_dir():
                        d = list(dirs)[0]
                        if os.path.isdir(d): os.startfile(d)
                    act_btn.clicked.connect(open_group_dir)
                    header.addWidget(act_btn)
            
        header.addStretch()
        
        is_pinned = item.get("pinned", False)
        self.pin_btn = SvgButton(PATH_PIN, size=16, color="#666666", hover_color="#ffffff")
        self.pin_btn.setToolTip(tr("Pin item"))
        self.pin_btn.set_active(is_pinned)
        self.pin_btn.clicked.connect(self.on_pin)
        header.addWidget(self.pin_btn)
        
        self.del_btn = SvgButton(PATH_X, size=16, color="#666666", hover_color="#ff4444")
        self.del_btn.setToolTip(tr("Remove item"))
        self.del_btn.clicked.connect(self.on_delete)
        header.addWidget(self.del_btn)
        
        layout.addLayout(header)
        
        content = item.get("content", "")
        self.expanded = False
        self.full_content = content
        
        content_layout = QHBoxLayout()
        
        if item_type == "file":
            file_vlayout = QVBoxLayout()
            ext = os.path.splitext(content)[1].lower()
            if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'] and os.path.exists(content):
                from PyQt6.QtGui import QPixmap
                self.icon_widget = InvalidableLabel()
                pixmap = QPixmap(content)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(self.shelf_width - 80, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.icon_widget.setPixmap(pixmap)
                    self.icon_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.icon_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                    file_vlayout.addWidget(self.icon_widget)
            elif os.path.exists(content):
                from PyQt6.QtWidgets import QFileIconProvider
                from PyQt6.QtCore import QFileInfo
                provider = QFileIconProvider()
                icon = provider.icon(QFileInfo(content))
                if not icon.isNull():
                    self.icon_widget = InvalidableLabel()
                    self.icon_widget.setPixmap(icon.pixmap(48, 48))
                    self.icon_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.icon_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                    file_vlayout.addWidget(self.icon_widget)
            filename = os.path.basename(content)
            self.lbl = QLabel(filename)
            self.lbl.setWordWrap(True)
            self.lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.lbl.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold; background: transparent;")
            file_vlayout.addWidget(self.lbl)
            path_lbl = QLabel(os.path.dirname(content))
            path_lbl.setWordWrap(True)
            path_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            path_lbl.setStyleSheet("color: #888888; font-size: 11px; background: transparent;")
            file_vlayout.addWidget(path_lbl)
            content_layout.addLayout(file_vlayout)
        elif item_type == "image":
            img_vlayout = QVBoxLayout()
            self.icon_widget = InvalidableLabel()
            self.icon_widget.setFixedSize(self.shelf_width - 80, 120)
            self.icon_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.icon_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            # Use placeholder color
            self.icon_widget.setStyleSheet("background-color: #2a2a2a; border-radius: 5px;")
            
            from PyQt6.QtCore import QThreadPool
            from PyQt6.QtGui import QPixmap
            worker = ImageLoaderWorker(content, self.shelf_width - 80, 120)
            def on_image_loaded(img):
                if not img.isNull():
                    self.icon_widget.setPixmap(QPixmap.fromImage(img))
                    self.icon_widget.setStyleSheet("")
            worker.signals.finished.connect(on_image_loaded)
            QThreadPool.globalInstance().start(worker)
            img_vlayout.addWidget(self.icon_widget)
            content_layout.addLayout(img_vlayout)
        elif item_type == "files":
            files_vlayout = QVBoxLayout()
            self.summary_widget = QWidget()
            summary_layout = QVBoxLayout(self.summary_widget)
            summary_layout.setContentsMargins(0,0,0,0)
            if len(content) == 1:
                title_txt = tr("Folder") if os.path.isdir(content[0]) else tr("1 file")
            else:
                title_txt = tr("{} files").replace("{}", str(len(content)))
            self.title_lbl = QLabel(title_txt)
            self.title_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.title_lbl.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold; background: transparent;")
            summary_layout.addWidget(self.title_lbl)
            self.summary_body_widget = QWidget()
            body_hlayout = QHBoxLayout(self.summary_body_widget)
            body_hlayout.setContentsMargins(0, 0, 0, 0)
            
            icons_vlayout = QVBoxLayout()
            icons_vlayout.setSpacing(0)
            icons_vlayout.setContentsMargins(0, 0, 0, 0)
            from PyQt6.QtWidgets import QFileIconProvider
            from PyQt6.QtCore import QFileInfo
            provider = QFileIconProvider()
            selected_paths = []
            seen_exts = set()
            for path in content:
                ext = os.path.splitext(path)[1].lower()
                if ext not in seen_exts:
                    seen_exts.add(ext)
                    selected_paths.append(path)
                    if len(selected_paths) == 3: break
            if len(selected_paths) < 3:
                for path in content:
                    if path not in selected_paths:
                        selected_paths.append(path)
                        if len(selected_paths) == 3: break
            pixmaps = []
            for path in selected_paths:
                if os.path.exists(path):
                    ext = os.path.splitext(path)[1].lower()
                    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                        from PyQt6.QtGui import QPixmap
                        img = QPixmap(path)
                        if not img.isNull():
                            img = img.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                            pixmaps.append(img)
                            continue
                    icon = provider.icon(QFileInfo(path))
                    if not icon.isNull():
                        pixmaps.append(icon.pixmap(32, 32))
            if pixmaps:
                self.icon_widget = StackedIconsWidget(pixmaps, size=32, show_plus=len(content)>3)
                self.icon_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                icons_vlayout.addWidget(self.icon_widget)
            icons_vlayout.addStretch()
            body_hlayout.addLayout(icons_vlayout)
            file_names = [f"• {os.path.basename(p)}" for p in content]
            display_text = "\n".join(file_names) if len(content) <= 4 else "\n".join(file_names[:3]) + "\n" + tr("... and {} more").replace("{}", str(len(content) - 3))
            self.lbl = QLabel(display_text)
            self.lbl.setWordWrap(True)
            self.lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.lbl.setStyleSheet("color: #cccccc; font-size: 12px; background: transparent;")
            self.lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            body_hlayout.addWidget(self.lbl, stretch=1)
            summary_layout.addWidget(self.summary_body_widget)
            files_vlayout.addWidget(self.summary_widget)
            self.expanded_widget = QWidget()
            expanded_layout = QVBoxLayout(self.expanded_widget)
            expanded_layout.setContentsMargins(0, 0, 0, 0)
            expanded_layout.setSpacing(2)
            for path in content:
                sub_item = SubItemWidget(path, parent_id=self.item.get("id"), audio=self.audio, accent_color=self.accent_color)
                sub_item.copy_clicked.connect(self._on_subitem_copy)
                sub_item.delete_clicked.connect(self._on_subitem_delete)
                expanded_layout.addWidget(sub_item)
            self.expanded_widget.setMaximumHeight(0)
            self.expanded_widget.setVisible(False)
            self.expand_anim = QPropertyAnimation(self.expanded_widget, b"maximumHeight")
            self.expand_anim.setDuration(250)
            self.expand_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
            
            files_vlayout.addWidget(self.expanded_widget)
            content_layout.addLayout(files_vlayout)
        elif item_type == "link":
            link_hlayout = QHBoxLayout()
            link_hlayout.setSpacing(10)
            
            self.link_text_vlayout = QVBoxLayout()
            self.link_text_vlayout.setSpacing(4)
            
            title_text = item.get("link_title")
            if not title_text:
                title_text = tr("Loading preview...") if not item.get("preview_fetched") else tr("Link")
            
            self.link_title_lbl = QLabel(title_text)
            self.link_title_lbl.setWordWrap(True)
            self.link_title_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.link_title_lbl.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold; background: transparent;")
            self.link_text_vlayout.addWidget(self.link_title_lbl)
            
            url_lbl = QLabel(content)
            url_lbl.setWordWrap(True)
            url_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            url_lbl.setStyleSheet("color: #4da6ff; font-size: 11px; background: transparent; text-decoration: underline;")
            self.link_text_vlayout.addWidget(url_lbl)
            self.link_text_vlayout.addStretch()
            
            link_hlayout.addLayout(self.link_text_vlayout, stretch=1)
            
            # Check if we already have an image
            if item.get("link_image") and os.path.exists(item.get("link_image")):
                from PyQt6.QtGui import QPixmap
                img = QPixmap(item.get("link_image"))
                if not img.isNull():
                    self.link_img_lbl = QLabel()
                    pixmap = img.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                    self.link_img_lbl.setPixmap(pixmap)
                    self.link_img_lbl.setFixedSize(64, 64)
                    self.link_img_lbl.setStyleSheet("border-radius: 8px; background-color: #2a2a2a;")
                    self.link_img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.link_img_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                    link_hlayout.insertWidget(0, self.link_img_lbl)
            
            content_layout.addLayout(link_hlayout)
            self.content_layout = content_layout
            
            if not item.get("link_title") and not item.get("preview_fetched"):
                item["preview_fetched"] = True
                from src.core.link_preview import LinkPreviewWorker
                cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "cache")
                self.worker = LinkPreviewWorker(content, self.item_id, cache_dir)
                self.worker.preview_ready.connect(self._on_preview_ready)
                self.worker.start()
        else:
            if parsed_color:
                color_sq = QLabel()
                color_sq.setFixedSize(16, 16)
                color_sq.setStyleSheet(f"background-color: {parsed_color}; border-radius: 4px;")
                color_sq.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                content_layout.addWidget(color_sq)
                
            can_expand = len(content) >= 120 or "\n" in content
            
            if can_expand:
                text_vlayout = QVBoxLayout()
                text_vlayout.setContentsMargins(0,0,0,0)
                text_vlayout.setSpacing(0)
                
                self.summary_body_widget = QWidget()
                summary_layout = QVBoxLayout(self.summary_body_widget)
                summary_layout.setContentsMargins(0,0,0,0)
                
                lines = content.split('\n')
                if len(lines) > 4:
                    display_text = '\n'.join(lines[:4]) + "\n..."
                else:
                    display_text = content if len(content) < 120 else content[:120] + "..."
                
                self.lbl = QLabel(display_text)
                self.lbl.setWordWrap(True)
                self.lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                self.lbl.setStyleSheet("color: #e0e0e0; font-size: 13px; background: transparent;")
                summary_layout.addWidget(self.lbl)
                
                self.expanded_widget = QWidget()
                expanded_layout = QVBoxLayout(self.expanded_widget)
                expanded_layout.setContentsMargins(0, 0, 0, 0)
                
                full_display_text = content if len(content) < 5000 else content[:5000] + "\n\n[...texto longo truncado...]"
                
                self.full_lbl = SelectableLabel(full_display_text)
                self.full_lbl.setWordWrap(True)
                self.full_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
                self.full_lbl.setStyleSheet("color: #e0e0e0; font-size: 13px; background: transparent;")
                expanded_layout.addWidget(self.full_lbl)
                
                self.expanded_widget.setMaximumHeight(0)
                self.expanded_widget.setVisible(False)
                
                self.expand_anim = QPropertyAnimation(self.expanded_widget, b"maximumHeight")
                self.expand_anim.setDuration(250)
                self.expand_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
                
                text_vlayout.addWidget(self.summary_body_widget)
                text_vlayout.addWidget(self.expanded_widget)
                content_layout.addLayout(text_vlayout)
            else:
                self.lbl = QLabel(content)
                self.lbl.setWordWrap(True)
                self.lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                self.lbl.setStyleSheet("color: #e0e0e0; font-size: 13px; background: transparent;")
                content_layout.addWidget(self.lbl)
        layout.addLayout(content_layout)
        self.check_validity()

    def _on_subitem_copy(self, path):
        self.copy_clicked.emit({"type": "file", "content": path})

    def _on_subitem_delete(self, path):
        self.delete_subitem_clicked.emit(self.item_id, path)

    def check_validity(self):
        item_type = self.item.get("type", "text")
        content = self.item.get("content", "")
        self.is_invalid = False
        if item_type == "file":
            if not os.path.exists(content):
                self.is_invalid = True
                if hasattr(self, 'lbl'): self.lbl.setStyleSheet("color: #666666; font-size: 14px; font-weight: bold; background: transparent; text-decoration: line-through;")
                if hasattr(self, 'icon_widget'): self.icon_widget.set_invalid(True)
            else:
                if hasattr(self, 'lbl'): self.lbl.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold; background: transparent; text-decoration: none;")
                if hasattr(self, 'icon_widget'): self.icon_widget.set_invalid(False)
        elif item_type == "image":
            if not os.path.exists(content):
                self.is_invalid = True
                if hasattr(self, 'icon_widget'): self.icon_widget.set_invalid(True)
            else:
                if hasattr(self, 'icon_widget'): self.icon_widget.set_invalid(False)
        elif item_type == "files":
            missing = any(not os.path.exists(p) for p in content[:3])
            if missing:
                self.is_invalid = True
                if hasattr(self, 'title_lbl'): self.title_lbl.setStyleSheet("color: #666666; font-size: 14px; font-weight: bold; background: transparent; text-decoration: line-through;")
                if hasattr(self, 'icon_widget'): self.icon_widget.set_invalid(True)
            else:
                if hasattr(self, 'title_lbl'): self.title_lbl.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold; background: transparent; text-decoration: none;")
                if hasattr(self, 'icon_widget'): self.icon_widget.set_invalid(False)

    def on_pin(self):
        if self.audio: self.audio.play_toggle()
        self.pin_clicked.emit(self.item_id)
        
    def on_delete(self):
        if self.audio: self.audio.play_delete()
        self.delete_clicked.emit(self.item_id)
        
    def resizeEvent(self, event):
        if hasattr(self, 'stack_overlay'):
            self.stack_overlay.resize(self.size())
        super().resizeEvent(event)
        
    def _is_valid_grouping(self, event):
        dest_type = self.item.get("type")
        if dest_type not in ["file", "files", "image"]:
            return False
            
        mime = event.mimeData()
        if mime.hasFormat("edgedrop/internal-drag-subitem"):
            return True
            
        if mime.hasFormat("edgedrop/internal-drag-item"):
            source_id = str(mime.data("edgedrop/internal-drag-item"), 'utf-8')
            shelf = self.window()
            source_item = next((x for x in shelf.clipboard_watcher.get_history() if x.get("id") == source_id), None)
            if source_item and source_item.get("type") in ["file", "files", "image"]:
                return True
            return False
            
        if mime.hasImage():
            return True
        if mime.hasUrls():
            return any(u.isLocalFile() for u in mime.urls())
            
        return False

    def dragEnterEvent(self, event):
        shelf = self.window()
        if getattr(shelf, 'active_drag_source_id', None) == self.item_id:
            event.ignore()
            return
            
        if self._is_valid_grouping(event):
            self.stack_overlay.show()
            self.stack_overlay.raise_()
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dragMoveEvent(self, event):
        shelf = self.window()
        if getattr(shelf, 'active_drag_source_id', None) == self.item_id:
            event.ignore()
            return
            
        if self._is_valid_grouping(event):
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        if hasattr(self, 'stack_overlay'):
            self.stack_overlay.hide()
        super().dragLeaveEvent(event)
        
    def dropEvent(self, event):
        if hasattr(self, 'stack_overlay'):
            self.stack_overlay.hide()
            
        shelf = self.window()
        if hasattr(shelf, 'stop_auto_scroll'):
            shelf.stop_auto_scroll()
            
        mime = event.mimeData()
        source_id = None
        is_internal = False
        
        is_subitem = False
        
        # Check internal drags first
        if mime.hasFormat("edgedrop/internal-drag-item"):
            source_id = str(mime.data("edgedrop/internal-drag-item"), 'utf-8')
            is_internal = True
        elif mime.hasFormat("edgedrop/internal-drag-subitem"):
            source_id = str(mime.data("edgedrop/internal-drag-subitem"), 'utf-8')
            is_internal = True
            is_subitem = True
            
        if source_id == self.item_id:
            event.ignore()
            return
            
        source_data = None
        if mime.hasUrls():
            urls = [u.toLocalFile() for u in mime.urls() if u.isLocalFile()]
            if urls:
                source_data = urls if len(urls) > 1 else urls[0]
        elif mime.hasText():
            source_data = mime.text()
            
        if not source_data and mime.hasFormat("edgedrop/internal-drag-item"):
            # If it's an internal item drag but no urls (e.g. text/link item), we need to fetch its data
            source_item = next((x for x in shelf.clipboard_watcher.get_history() if x.get("id") == source_id), None)
            if source_item:
                source_data = source_item.get("content")
                
        if source_data and self._is_valid_grouping(event):
            if is_subitem:
                file_to_remove = source_data[0] if isinstance(source_data, list) else source_data
                shelf.clipboard_watcher.remove_file_from_group(source_id, file_to_remove)
                # Pass is_internal=False to stack_items so it doesn't delete the entire source group!
                shelf.clipboard_watcher.stack_items(self.item_id, source_data, source_id, False)
            else:
                shelf.clipboard_watcher.stack_items(self.item_id, source_data, source_id, is_internal)
            event.acceptProposedAction()
        else:
            event.ignore()

    def _on_preview_ready(self, item_dict):
        item_id = item_dict.get("item_id")
        title = item_dict.get("title")
        img_path = item_dict.get("image")
        
        if self.item_id != item_id:
            return
        
        # In-place UI update
        if title:
            self.item["link_title"] = title
            self.link_title_lbl.setText(title)
        else:
            self.link_title_lbl.setText("Link")
            
        if img_path and os.path.exists(img_path):
            self.item["link_image"] = img_path
            from PyQt6.QtGui import QPixmap
            img = QPixmap(img_path)
            if not img.isNull():
                self.link_img_lbl = QLabel()
                pixmap = img.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                self.link_img_lbl.setPixmap(pixmap)
                self.link_img_lbl.setFixedSize(64, 64)
                self.link_img_lbl.setStyleSheet("border-radius: 8px; background-color: #2a2a2a;")
                self.link_img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.link_img_lbl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                
                # Insert at the beginning of the horizontal layout
                self.content_layout.itemAt(self.content_layout.count() - 1).layout().insertWidget(0, self.link_img_lbl)
                
        # Persist the fetched data to history via the watcher
        shelf = self.window()
        if hasattr(shelf, 'clipboard_watcher'):
            shelf.clipboard_watcher.update_item(item_id, {
                "link_title": title,
                "link_image": img_path,
                "preview_fetched": True
            })

    def enterEvent(self, event):
        super().enterEvent(event)
        # Pre-stage drag data to make drag start instantly
        QTimer.singleShot(0, self._prestage_drag_data)

    def _prestage_drag_data(self):
        self._prestaged_mimedata = QMimeData()
        content = self.item.get("content")
        content_stripped = content.strip() if isinstance(content, str) else content
        
        if self.item.get("type") == "files":
            urls = [QUrl.fromLocalFile(p.strip()) for p in self.item.get("content", []) if os.path.exists(p.strip())]
            self._prestaged_mimedata.setUrls(urls)
        elif self.item.get("type") == "file" and os.path.exists(content_stripped):
            url = QUrl.fromLocalFile(content_stripped)
            self._prestaged_mimedata.setUrls([url])
        elif self.item.get("type") == "image" and os.path.exists(content_stripped):
            from PyQt6.QtGui import QImage
            img = QImage(content_stripped)
            if not img.isNull():
                self._prestaged_mimedata.setImageData(img)
            import struct
            filename = os.path.basename(content_stripped)
            if not filename.lower().endswith('.png'):
                filename += '.png'
            filename_encoded = filename.encode('utf-16-le')
            filename_padded = filename_encoded + b'\x00' * (520 - len(filename_encoded))
            try:
                with open(content_stripped, 'rb') as f:
                    file_bytes = f.read()
                fgd = struct.pack('<I I 16s 8s 8s I 8s 8s 8s I I 520s',
                                  1, 0, b'\x00'*16, b'\x00'*8, b'\x00'*8, 0x80,
                                  b'\x00'*8, b'\x00'*8, b'\x00'*8, 0, len(file_bytes), filename_padded)
                from PyQt6.QtCore import QByteArray
                self._prestaged_mimedata.setData("FileGroupDescriptorW", QByteArray(fgd))
                self._prestaged_mimedata.setData("FileContents", QByteArray(file_bytes))
            except Exception as e:
                pass
        else:
            self._prestaged_mimedata.setText(str(content))
            self._prestaged_mimedata.setHtml(f"<html><body>{content}</body></html>")
            
        from PyQt6.QtCore import QByteArray
        self._prestaged_mimedata.setData("edgedrop/internal-drag-item", QByteArray(self.item_id.encode('utf-8')))
        
        # Pre-stage pixmap
        original_pixmap = self.grab()
        from PyQt6.QtGui import QPixmap, QPainter
        transparent_pixmap = QPixmap(original_pixmap.size())
        transparent_pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(transparent_pixmap)
        painter.setOpacity(0.6)
        painter.drawPixmap(0, 0, original_pixmap)
        painter.end()
        self._prestaged_pixmap = transparent_pixmap

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        if getattr(self, "is_invalid", False):
            return
        drag = QDrag(self)
        
        # Build on demand if it wasn't prestaged (e.g. fast click before hover finished)
        if getattr(self, "_prestaged_mimedata", None) is None:
            self._prestage_drag_data()
            
        drag.setMimeData(self._prestaged_mimedata)
        drag.setPixmap(self._prestaged_pixmap)
        drag.setHotSpot(event.pos())
        
        # Clear references so C++ can take ownership safely
        self._prestaged_mimedata = None
        self._prestaged_pixmap = None
        
        shelf = self.window()
        shelf.is_dragging = True
        shelf.active_drag_is_top_level = True
        shelf.active_drag_source_id = self.item_id
        
        if hasattr(shelf, 'start_auto_scroll'):
            shelf.start_auto_scroll()
            
        drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.LinkAction | Qt.DropAction.MoveAction)
        
        if hasattr(shelf, 'stop_auto_scroll'):
            shelf.stop_auto_scroll()
            
        shelf.is_dragging = False
        shelf.active_drag_is_top_level = False
        shelf.active_drag_source_id = None
        shelf._check_close()
        self.check_validity()
        
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if hasattr(self, 'drag_start_position') and (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
                if getattr(self, "is_invalid", False): return
                if self.audio: self.audio.play_copy()
                self.setStyleSheet(f"#ItemCard {{ background-color: {self.get_darker(self.accent_color)}; border-radius: 8px; border: 1px solid {self.accent_color}; }}")
                self.copy_clicked.emit(self.item)
                QTimer.singleShot(300, lambda: self.setStyleSheet("""
                    #ItemCard {
                        background-color: rgba(26, 26, 26, 200);
                        border-radius: 8px;
                        border: 1px solid rgba(255, 255, 255, 10);
                    }
                    #ItemCard:hover {
                        background-color: rgba(40, 40, 40, 220);
                        border: 1px solid rgba(255, 255, 255, 30);
                    }
                """))
        elif event.button() == Qt.MouseButton.RightButton:
            if self.item.get("type") == "image":
                content = self.item.get("content")
                if os.path.exists(content):
                    if hasattr(self, 'preview_window') and self.preview_window is not None and not getattr(self.preview_window, 'is_closing', False):
                        self.preview_window.close_animated()
                        self.preview_window = None
                    else:
                        ImagePreviewWindow.close_all()
                        from PyQt6.QtCore import QRect, QPoint
                        source_rect = QRect(self.mapToGlobal(QPoint(0,0)), self.size())
                        self.preview_window = ImagePreviewWindow(content, source_rect)
                        self.preview_window.show()
                    if self.audio: self.audio.play_toggle()
                    return
                    
            if hasattr(self, 'expanded_widget'):
                if not hasattr(self, '_is_expanded'):
                    self._is_expanded = False
                
                if not self._is_expanded:
                    self._is_expanded = True
                    sum_target = self.summary_body_widget.size()
                    sum_height = sum_target.height() if sum_target.height() > 0 else self.summary_body_widget.sizeHint().height()
                    self.summary_body_widget.setVisible(False)
                    self.expanded_widget.setVisible(True)
                    exp_target = self.expanded_widget.sizeHint().height()
                    
                    self.expand_anim.setStartValue(sum_height)
                    self.expand_anim.setEndValue(exp_target)
                    
                    self.expand_anim.start()
                    
                    def on_expand_finish():
                        try: self.expand_anim.finished.disconnect(on_expand_finish)
                        except: pass
                        self.expanded_widget.setMaximumHeight(16777215)
                    self.expand_anim.finished.connect(on_expand_finish)
                    
                else:
                    self._is_expanded = False
                    exp_target = self.expanded_widget.size().height()
                    # Need to temporarily show summary to get correct height if it was hidden
                    was_visible = self.summary_body_widget.isVisible()
                    if not was_visible:
                        self.summary_body_widget.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
                        self.summary_body_widget.show()
                        
                    sum_target = self.summary_body_widget.sizeHint().height()
                    
                    if not was_visible:
                        self.summary_body_widget.hide()
                        self.summary_body_widget.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, False)
                    
                    self.expand_anim.setStartValue(exp_target)
                    self.expand_anim.setEndValue(sum_target)
                    
                    def on_finish():
                        try: self.expand_anim.finished.disconnect(on_finish)
                        except: pass
                        self.expanded_widget.setVisible(False)
                        self.summary_body_widget.setVisible(True)
                        self.expanded_widget.setMaximumHeight(0)
                    self.expand_anim.finished.connect(on_finish)
                    self.expand_anim.start()
                    
                if self.audio: self.audio.play_toggle()
        super().mouseReleaseEvent(event)

    def update_timestamp(self):
        if hasattr(self, 'time_lbl') and self.item.get("timestamp"):
            from src.utils import helpers as utils
            new_text = utils.format_relative_time(self.item.get("timestamp"))
            if self.time_lbl.text() != new_text:
                self.time_lbl.setText(new_text)


class CollapsibleSection(QFrame):
    toggled_state = pyqtSignal(bool)

    def set_accent_color(self, hex_color):
        from PyQt6.QtGui import QColor
        c = QColor(hex_color).darker(150)
        bg = f"rgba({c.red()}, {c.green()}, {c.blue()}, 150)"
        bd = f"rgba({c.red()}, {c.green()}, {c.blue()}, 200)"
        self.setStyleSheet(f"""
            #PinnedSection {{
                background-color: {bg};
                border-radius: 8px;
                border: 1px solid {bd};
            }}
        """)

    def __init__(self, title, parent=None, accent_color="#4CAF50", expanded=True):
        super().__init__(parent)
        self.setObjectName("PinnedSection")
        self.set_accent_color(accent_color)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(5)
        
        self.header_btn = QPushButton(f"▼ {title}")
        self.header_btn.setStyleSheet("text-align: left; font-weight: bold; color: #aaaaaa; background: transparent; border: none; padding: 5px;")
        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.layout.addWidget(self.header_btn)
        
        self.body_widget = QWidget()
        self.body_layout = QVBoxLayout(self.body_widget)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(10)
        self.layout.addWidget(self.body_widget)
        
        self.header_btn.clicked.connect(self.toggle)
        self.is_expanded = expanded
        self.body_widget.setVisible(self.is_expanded)
        self.set_title(title)
        
    def set_title(self, title):
        icon = "▼" if self.is_expanded else "▶"
        # If title already contains the icon, strip it
        if title.startswith("▼ ") or title.startswith("▶ "):
            title = title[2:]
        self.header_btn.setText(f"{icon} {title}")

    def toggle(self):
        self.is_expanded = not self.is_expanded
        self.body_widget.setVisible(self.is_expanded)
        title = self.header_btn.text().split(" ", 1)[1] if " " in self.header_btn.text() else self.header_btn.text()
        self.set_title(title)
        self.toggled_state.emit(self.is_expanded)


class ShelfContainer(QWidget):
    def __init__(self, parent_shelf):
        super().__init__(parent_shelf)
        self.shelf = parent_shelf
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        r = 15
        w = self.width()
        h = self.height()
        if getattr(self.shelf, "edge_side", "left") == "left":
            path.moveTo(w - r, r)
            path.arcTo(w - r*2, r, r*2, r*2, 90, -90)
            path.lineTo(w, h - r*2)
            path.arcTo(w - r*2, h - r*3, r*2, r*2, 0, -90)
            path.lineTo(r, h - r)
            path.quadTo(0, h - r, 0, h)
            path.lineTo(0, 0)
            path.quadTo(0, r, r, r)
            path.lineTo(w - r, r)
        else:
            path.moveTo(r, r)
            path.arcTo(0, r, r*2, r*2, 90, 90)
            path.lineTo(0, h - r*2)
            path.arcTo(0, h - r*3, r*2, r*2, 180, 90)
            path.lineTo(w - r, h - r)
            path.quadTo(w, h - r, w, h)
            path.lineTo(w, 0)
            path.quadTo(w, r, w - r, r)
            path.lineTo(r, r)
            
        is_translucent = self.shelf.config.get("translucent_background")
        if is_translucent:
            opacity_pct = self.shelf.config.get("bg_opacity_percent", 70)
            bg_alpha = int((opacity_pct / 100.0) * 255)
        else:
            bg_alpha = 255
            
        painter.fillPath(path, QColor(0, 0, 0, bg_alpha))
        
        header_path = QPainterPath()
        header_path.addRect(QRectF(0, 0, w, r + 45))
        intersected = path.intersected(header_path)
        painter.fillPath(intersected, QColor(17, 17, 17, bg_alpha))
        
        pen = painter.pen()
        pen.setColor(QColor(34, 34, 34, 255)) # #222
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)

class EdgeDropShelf(QWidget):
    def __init__(self, clipboard_watcher, config, audio=None):
        self.accent_color = config.get("accent_color")
        super().__init__()
        self.clipboard_watcher = clipboard_watcher
        self.config = config
        self.audio = audio
        self.hotkey_manager = None
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysShowToolTips, True)
        self.shelf_width = self.config.get("shelf_width")
        self.screen_x, self.screen_y, self.screen_width, self.screen_height = 0, 0, *utils.get_screen_size()
        self.shelf_height = int(self.screen_height * 0.8)
        self.y_pos = self.screen_y + int((self.screen_height - self.shelf_height) / 2)
        self.edge_side = self.config.get("edge_side")
        self.display_limit = 30
        self._calc_positions()
        self.is_open = False
        self.is_settings_view = False
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.finished.connect(self._on_animation_finished)
        self.setAcceptDrops(True)
        self.item_widgets = {}
        self._setup_ui()
        # Keep the window at the correct physical geometry on the correct screen,
        # but just use hide(). We will animate the container inside it.
        self.setGeometry(self.x_visible, self.y_pos, self.shelf_width, self.shelf_height)
        self.hide()
        self._update_app_stylesheet()
        self.load_history()
        self.clipboard_watcher.new_item.connect(lambda item: self.load_history())
        if hasattr(self.clipboard_watcher, 'history_changed'):
            self.clipboard_watcher.history_changed.connect(self.load_history)
            
        self.time_update_timer = QTimer(self)
        self.time_update_timer.timeout.connect(self._update_all_timestamps)
        self.time_update_timer.start(30000)

    def _update_all_timestamps(self):
        for card in self.item_widgets.values():
            if hasattr(card, 'update_timestamp'):
                card.update_timestamp()

    def _calc_positions(self):
        if self.edge_side == "left":
            self.x_visible = self.screen_x
        else:
            self.x_visible = self.screen_x + self.screen_width - self.shelf_width
            
    # paintEvent was moved to the container in _setup_ui
            
    def _rebuild_settings_view_delayed(self):
        was_settings = self.is_settings_view
        self.stacked.removeWidget(self.settings_view)
        self.settings_view.deleteLater()
        self.settings_view = QWidget()
        self._build_settings_view()
        self.stacked.addWidget(self.settings_view)
        if was_settings:
            self.stacked.setCurrentWidget(self.settings_view)

    def _retranslate_ui(self):
        self.search_input.setPlaceholderText(tr("Search..."))
        self.trash_btn.setToolTip(tr("Clear unpinned items"))
        self.pause_btn.setToolTip(tr("Pause/Resume capture"))
        self.settings_btn.setToolTip(tr("Settings"))
        self.pinned_section.set_title(tr("Pinned Items"))
        
        if self.search_input.text().strip():
            self._on_search(self.search_input.text())
        else:
            self.empty_lbl.setText(tr("The shelf is empty."))
            
        self.load_history(force_rebuild=True)
        
        QTimer.singleShot(0, self._rebuild_settings_view_delayed)

    def _setup_ui(self):
        self.container = ShelfContainer(self)
        self.container.resize(self.shelf_width, self.shelf_height)
        self.container.move(0, 0)
        
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(5, 15, 5, 15)
        main_layout.setSpacing(0)
        
        self.bg_frame = QFrame()
        self.bg_frame.setObjectName("BgFrame")
        self.bg_frame.setStyleSheet("background: transparent; border: none;")
        
        bg_layout = QVBoxLayout(self.bg_frame)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.setSpacing(0)
        
        # Header
        self.header = QFrame()
        self.header.setFixedHeight(45)
        self.header.setStyleSheet("background: transparent; border: none;")
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(5, 0, 5, 0)
        
        title = QLabel("Py-Drop")
        title.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        h_layout.addWidget(title)
        
        self.search_input = QLineEdit()
        self.search_input.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.search_input.setPlaceholderText(tr("Search..."))
        self.search_input.setStyleSheet("background: #222; color: white; border: none; border-radius: 4px; padding: 2px 5px;")
        self.search_input.textChanged.connect(self._on_search)
        h_layout.addWidget(self.search_input)
        
        self.trash_btn = SvgButton(PATH_TRASH, size=16, color="#888888", hover_color="#ff4444")
        self.trash_btn.setToolTip(tr("Clear unpinned items"))
        self.trash_btn.clicked.connect(self._clear_unpinned)
        h_layout.addWidget(self.trash_btn)
        
        self.pause_btn = SvgButton(PATH_PAUSE, size=16, color="#888888", hover_color="#ffffff")
        self.pause_btn.setToolTip(tr("Pause/Resume capture"))
        self.pause_btn.clicked.connect(self._toggle_pause)
        h_layout.addWidget(self.pause_btn)
        
        self.settings_btn = SvgButton(PATH_SETTINGS, size=16, color="#888888", hover_color="#ffffff")
        self.settings_btn.setToolTip(tr("Settings"))
        self.settings_btn.clicked.connect(self._toggle_settings)
        h_layout.addWidget(self.settings_btn)
        
        bg_layout.addWidget(self.header)
        
        self.stacked = QStackedWidget()
        bg_layout.addWidget(self.stacked)
        
        # Main View
        self.main_view = QWidget()
        v_layout = QVBoxLayout(self.main_view)
        v_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self._is_loading_more = False
        def on_scroll_moved(val):
            if self._is_loading_more: return
            sb = self.scroll.verticalScrollBar()
            if sb.maximum() > 0 and val >= sb.maximum() * 0.8:
                if self.display_limit < len(self.clipboard_watcher.history):
                    self._is_loading_more = True
                    self.display_limit += 30
                    self.load_history(force_rebuild=False)
                    self._is_loading_more = False
        
        self.scroll.verticalScrollBar().valueChanged.connect(on_scroll_moved)
        self.scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background: transparent; 
            }
            QScrollBar:vertical { 
                background: transparent; 
                width: 8px; 
                margin: 4px 0px 4px 0px; 
            }
            QScrollBar::handle:vertical { 
                background: #555555; 
                border-radius: 4px; 
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #777777;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.items_layout = QVBoxLayout(self.scroll_content)
        self.items_layout.setContentsMargins(0, 10, 10, 10)
        self.items_layout.setSpacing(10)
        
        is_expanded = self.config.get("pinned_section_expanded", True)
        self.pinned_section = CollapsibleSection(tr("Pinned Items"), accent_color=self.accent_color, expanded=is_expanded)
        self.pinned_section.toggled_state.connect(lambda expanded: self.config.set("pinned_section_expanded", expanded))
        self.pinned_section.hide()
        self.items_layout.addWidget(self.pinned_section)
        
        self.unpinned_layout = QVBoxLayout()
        self.unpinned_layout.setContentsMargins(10, 0, 10, 0)
        self.unpinned_layout.setSpacing(10)
        self.items_layout.addLayout(self.unpinned_layout)
        
        self.items_layout.addStretch()
        
        self.scroll.setWidget(self.scroll_content)
        v_layout.addWidget(self.scroll)
        
        self.empty_lbl = QLabel(tr("The shelf is empty."))
        self.empty_lbl.setStyleSheet("color: #666; font-size: 14px;")
        self.empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v_layout.addWidget(self.empty_lbl)
        
        self.stacked.addWidget(self.main_view)
        
        # Settings View
        self.settings_view = QWidget()
        self._build_settings_view()
        self.stacked.addWidget(self.settings_view)
        
        bg_layout.addWidget(self.stacked)
        main_layout.addWidget(self.bg_frame)
        
        # Drop overlay
        self.drop_overlay = QLabel(tr("Drop here"), self)
        self.drop_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_overlay.setStyleSheet("""
            QLabel {
                background: rgba(30, 100, 30, 200);
                color: white;
                font-size: 24px;
                font-weight: bold;
                border: 4px dashed #4CAF50;
                border-radius: 15px;
            }
        """)
        self.drop_overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.drop_overlay.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'drop_overlay'):
            self.drop_overlay.resize(self.size())
            
    def _handle_auto_scroll(self):
        from PyQt6.QtGui import QCursor
        pos = self.mapFromGlobal(QCursor.pos())
        y = pos.y()
        
        scroll_bar = self.scroll.verticalScrollBar()
        if not scroll_bar: return
        
        margin = 60
        speed = 0
        
        if y < margin:
            speed = -max(2, int((margin - y) / 2))
        elif y > self.height() - margin:
            speed = max(2, int((y - (self.height() - margin)) / 2))
            
        if speed != 0:
            scroll_bar.setValue(scroll_bar.value() + speed)
            
    def start_auto_scroll(self):
        if not hasattr(self, 'auto_scroll_timer'):
            self.auto_scroll_timer = QTimer(self)
            self.auto_scroll_timer.setInterval(16)
            self.auto_scroll_timer.timeout.connect(self._handle_auto_scroll)
        self.auto_scroll_timer.start()
        
    def stop_auto_scroll(self):
        if hasattr(self, 'auto_scroll_timer'):
            self.auto_scroll_timer.stop()

    def _apply_theme(self):
        # Update settings view by replacing it
        self.stacked.removeWidget(self.settings_view)
        self.settings_view.deleteLater()
        
        self.settings_view = QWidget()
        self._build_settings_view()
        self.stacked.addWidget(self.settings_view)
        if self.is_settings_view:
            self.stacked.setCurrentWidget(self.settings_view)
        
        # Update pinned section
        self.pinned_section.set_accent_color(self.accent_color)
        
        # Reload history to rebuild all cards with new color
        self.load_history()
        
        # Update drop overlay
        self.drop_overlay.setStyleSheet(f"""
            QLabel {{
                background: rgba(30, 100, 30, 200);
                color: white;
                font-size: 32px;
                font-weight: bold;
                border: 4px dashed {self.accent_color};
                border-radius: 15px;
            }}
        """)
        self._update_app_stylesheet()
        self.update()

    def _update_app_stylesheet(self):
        app = QApplication.instance()
        if app:
            app.setStyleSheet(f"""
                QToolTip {{ color: #ffffff; background-color: #2a2a2a; border: 1px solid #555555; padding: 4px; border-radius: 4px; }}
                QMenu {{
                    background-color: transparent;
                    color: #e0e0e0;
                    padding: 4px;
                }}
                QMenu::item {{
                    padding: 6px 24px 6px 12px;
                    border-radius: 4px;
                    margin: 2px 0px;
                }}
                QMenu::item:selected {{
                    background-color: {self.accent_color};
                    color: #ffffff;
                }}
                QMenu::separator {{
                    height: 1px;
                    background: #333333;
                    margin: 4px 0px;
                }}
            """)

    def _build_settings_view(self):
        # We need a main layout for settings_view itself
        outer_layout = QVBoxLayout(self.settings_view)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QWidget#ScrollContainer { background: transparent; }
            QScrollBar:vertical { background: #1a1a1a; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #555; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #777; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }
        """)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        container = QWidget()
        container.setObjectName("ScrollContainer")
        scroll.setWidget(container)
        outer_layout.addWidget(scroll)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)
        
        self.lbl_settings_title = QLabel(tr("Settings"))
        self.lbl_settings_title.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        main_layout.addWidget(self.lbl_settings_title)

        from src.ui.flow_layout import FlowLayout
        from PyQt6.QtWidgets import QButtonGroup, QStackedWidget

        def create_form():
            form = QFormLayout()
            form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
            form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
            form.setSpacing(15)
            # Add some margin at the top so the form isn't flush with the tabs
            form.setContentsMargins(0, 10, 0, 0)
            return form

        checkbox_style = f"""
            QCheckBox {{ color: white; }}
            QCheckBox::indicator {{ width: 14px; height: 14px; border-radius: 3px; border: 1px solid #777; background: #222; }}
            QCheckBox::indicator:hover {{ border: 1px solid #999; }}
            QCheckBox::indicator:checked {{ background: {self.accent_color}; border: 1px solid {self.accent_color}; image: url(data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIzIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwb2x5bGluZSBwb2ludHM9IjIwIDYgOSAxNyA0IDEyIj48L3BvbHlsaW5lPjwvc3ZnPg==); }}
        """

        combo_style = f"""
            QComboBox {{
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 4px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #2a2a2a;
                color: #ffffff;
                selection-background-color: {self.accent_color};
            }}
        """
        
        tab_style = f"""
            QPushButton {{
                background-color: transparent;
                color: #aaa;
                border: 1px solid #444;
                border-radius: 12px;
                padding: 4px 10px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #333;
                color: #fff;
            }}
            QPushButton:checked {{
                background-color: {self.accent_color};
                color: white;
                border: 1px solid {self.accent_color};
            }}
        """

        # Tabs Layout
        tabs_layout = FlowLayout(margin=0, hSpacing=8, vSpacing=8)
        main_layout.addLayout(tabs_layout)
        
        self.tab_group = QButtonGroup(container)
        self.tab_group.setExclusive(True)
        
        self.settings_stacked = QStackedWidget()
        main_layout.addWidget(self.settings_stacked)
        
        def add_tab(title, index, is_checked=False):
            btn = QPushButton(title)
            btn.setCheckable(True)
            btn.setChecked(is_checked)
            btn.setStyleSheet(tab_style)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            tabs_layout.addWidget(btn)
            self.tab_group.addButton(btn, index)
            return btn
            
        # ==========================================
        # SECTION: Appearance
        # ==========================================
        btn_appearance = add_tab(tr("Appearance"), 0, True)
        
        app_widget = QWidget()
        app_form = create_form()
        app_widget.setLayout(app_form)
        self.settings_stacked.addWidget(app_widget)
        
        # Language (Using QPushButton + QMenu to fix Windows 10 popup bugs)
        self.cb_lang = QPushButton()
        self.cb_lang.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb_lang.setMinimumWidth(100)
        from PyQt6.QtWidgets import QSizePolicy
        self.cb_lang.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        btn_combo_style = f"""
            QPushButton {{
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 4px;
                text-align: left;
            }}
            QPushButton:hover {{
                background-color: #333333;
            }}
            QPushButton::menu-indicator {{
                image: none;
            }}
        """
        self.cb_lang.setStyleSheet(btn_combo_style)
        
        self.lang_menu = QMenu(self.cb_lang)
        self.lang_menu.setStyleSheet(f"""
            QMenu {{
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444444;
            }}
            QMenu::item {{
                padding: 4px 24px 4px 8px;
            }}
            QMenu::item:selected {{
                background-color: {self.accent_color};
            }}
        """)
        
        self.cb_lang.setMenu(self.lang_menu)
        
        # Add actions
        act_pt = self.lang_menu.addAction("Português")
        act_pt.setData("pt_BR")
        act_en = self.lang_menu.addAction("English")
        act_en.setData("en_US")
        
        current_lang = self.config.get("language", "pt_BR")
        if current_lang == "en_US":
            self.cb_lang.setText("English")
        else:
            self.cb_lang.setText("Português")
            
        def on_lang_action(action):
            lang_code = action.data()
            if self.config.get("language", "pt_BR") != lang_code:
                self.config.set("language", lang_code)
                self.cb_lang.setText(action.text())
                from src.core.i18n import set_language
                set_language(lang_code)
                self._retranslate_ui()
                self.load_history()
                
        self.lang_menu.triggered.connect(on_lang_action)
        
        lbl_lang = QLabel(tr("Language"))
        lbl_lang.setStyleSheet("color: #cccccc;")
        app_form.addRow(lbl_lang, self.cb_lang)

        # Accent Color
        self.color_btn = QPushButton(self.accent_color)
        self.color_btn.setMinimumWidth(100)
        from PyQt6.QtWidgets import QSizePolicy
        self.color_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.color_btn.setStyleSheet(f"background: {self.accent_color}; color: white; border-radius: 4px; padding: 5px; font-weight: bold;")
        self.color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        def on_color_click():
            from PyQt6.QtWidgets import QColorDialog
            from PyQt6.QtGui import QColor
            color = QColorDialog.getColor(initial=QColor(self.accent_color), parent=self)
            if color.isValid():
                self.config.set("accent_color", color.name())
                self.accent_color = color.name()
                self._apply_theme()
        self.color_btn.clicked.connect(on_color_click)
        lbl_color = QLabel(tr("Accent Color"))
        lbl_color.setStyleSheet("color: #cccccc;")
        app_form.addRow(lbl_color, self.color_btn)

        # Translucent Background
        self.cb_translucent = QCheckBox()
        self.cb_translucent.setStyleSheet(checkbox_style)
        self.cb_translucent.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb_translucent.setChecked(self.config.get("translucent_background"))
        def on_translucent_change(state):
            self.config.set("translucent_background", bool(state))
            update_opacity_visibility()
            self._update_app_stylesheet()
            self.container.update()
        self.cb_translucent.stateChanged.connect(on_translucent_change)
        lbl_translucent = QLabel(tr("Translucent Background"))
        lbl_translucent.setStyleSheet("color: #cccccc;")
        app_form.addRow(lbl_translucent, self.cb_translucent)

        # Background Opacity
        self.slider_opacity = QSlider(Qt.Orientation.Horizontal)
        self.slider_opacity.setMinimumWidth(100)
        self.slider_opacity.setRange(10, 100)
        self.slider_opacity.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_opacity.setValue(self.config.get("bg_opacity_percent", 70))
        self.slider_opacity.setStyleSheet(f"QSlider::handle:horizontal {{ background: {self.accent_color}; border-radius: 5px; width: 10px; }}")
        
        self.lbl_opacity = QLabel(tr("Background Opacity (%)"))
        self.lbl_opacity.setStyleSheet("color: #cccccc;")
        
        def on_opacity_moved(val):
            from PyQt6.QtWidgets import QToolTip
            from PyQt6.QtGui import QCursor
            QToolTip.showText(QCursor.pos(), f"{val}%")
            
        def on_opacity_changed(val):
            self.config.set("bg_opacity_percent", val)
            self.container.update()
            
        self.slider_opacity.sliderMoved.connect(on_opacity_moved)
        self.slider_opacity.valueChanged.connect(on_opacity_changed)
        
        app_form.addRow(self.lbl_opacity, self.slider_opacity)
        
        def update_opacity_visibility():
            is_checked = self.cb_translucent.isChecked()
            self.slider_opacity.setVisible(is_checked)
            self.lbl_opacity.setVisible(is_checked)
            
        update_opacity_visibility()

        # Shelf Width
        slider_width = QSlider(Qt.Orientation.Horizontal)
        slider_width.setMinimumWidth(100)
        slider_width.setRange(200, 600)
        slider_width.setValue(self.config.get("shelf_width"))
        slider_width.setCursor(Qt.CursorShape.PointingHandCursor)
        slider_width.setTracking(False)
        slider_width.setStyleSheet(f"QSlider::handle:horizontal {{ background: {self.accent_color}; border-radius: 5px; width: 10px; }}")
        def on_width_moved(val):
            from PyQt6.QtWidgets import QToolTip
            from PyQt6.QtGui import QCursor
            QToolTip.showText(QCursor.pos(), f"{val} px")
            
        def on_width_changed(val):
            self.config.set("shelf_width", val)
            self.shelf_width = val
            self._calc_positions()
            self.container.resize(self.shelf_width, self.shelf_height)
            if self.is_open:
                self.setFixedSize(self.shelf_width, self.shelf_height)
                self.setGeometry(self.x_visible, self.y_pos, self.shelf_width, self.shelf_height)
            self.update()
            self.load_history(force_rebuild=True)
            
        slider_width.sliderMoved.connect(on_width_moved)
        slider_width.valueChanged.connect(on_width_changed)
        lbl_width = QLabel(tr("Shelf Width (pixels)"))
        lbl_width.setStyleSheet("color: #cccccc;")
        app_form.addRow(lbl_width, slider_width)

        # ==========================================
        # SECTION: Behavior
        # ==========================================
        btn_behavior = add_tab(tr("Behavior"), 1)
        beh_widget = QWidget()
        beh_form = create_form()
        beh_widget.setLayout(beh_form)
        self.settings_stacked.addWidget(beh_widget)

        # Max history items
        slider_history = QSlider(Qt.Orientation.Horizontal)
        slider_history.setMinimumWidth(100)
        # Using 1 to 10 for physical snapping (1=50, 2=100... 10=500)
        slider_history.setRange(1, 10)
        slider_history.setSingleStep(1)
        current_history_limit = self.config.get("max_history_items", 100)
        slider_history.setValue(current_history_limit // 50)
        slider_history.setCursor(Qt.CursorShape.PointingHandCursor)
        slider_history.setTracking(False)
        slider_history.setStyleSheet(f"QSlider::handle:horizontal {{ background: {self.accent_color}; border-radius: 5px; width: 10px; }}")
        
        def on_history_moved(val):
            real_val = val * 50
            from PyQt6.QtWidgets import QToolTip
            from PyQt6.QtGui import QCursor
            QToolTip.showText(QCursor.pos(), str(real_val))
            
        def on_history_changed(val):
            real_val = val * 50
            self.config.set("max_history_items", real_val)
            
        slider_history.sliderMoved.connect(on_history_moved)
        slider_history.valueChanged.connect(on_history_changed)
        lbl_history = QLabel(tr("History Limit"))
        lbl_history.setStyleSheet("color: #cccccc;")
        beh_form.addRow(lbl_history, slider_history)

        # Click behavior
        self.cb_click = QPushButton()
        self.cb_click.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb_click.setMinimumWidth(100)
        from PyQt6.QtWidgets import QSizePolicy
        self.cb_click.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cb_click.setStyleSheet(btn_combo_style)
        
        self.click_menu = QMenu(self.cb_click)
        self.click_menu.setStyleSheet(f"""
            QMenu {{
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444444;
            }}
            QMenu::item {{
                padding: 4px 24px 4px 8px;
            }}
            QMenu::item:selected {{
                background-color: {self.accent_color};
            }}
        """)
        self.cb_click.setMenu(self.click_menu)
        
        act_paste = self.click_menu.addAction(tr("Copy and Paste in Window"))
        act_paste.setData(True)
        act_copy = self.click_menu.addAction(tr("Copy Only"))
        act_copy.setData(False)
        
        current_click_val = self.config.get("click_to_paste", True)
        if current_click_val:
            self.cb_click.setText(tr("Copy and Paste in Window"))
        else:
            self.cb_click.setText(tr("Copy Only"))
            
        def on_click_action(action):
            val = action.data()
            if self.config.get("click_to_paste", True) != val:
                self.config.set("click_to_paste", val)
                self.cb_click.setText(action.text())
                
        self.click_menu.triggered.connect(on_click_action)
        
        lbl_click = QLabel(tr("Left-click behavior:"))
        lbl_click.setStyleSheet("color: #cccccc;")
        beh_form.addRow(lbl_click, self.cb_click)

        # Sound
        self.cb_sound = QCheckBox()
        self.cb_sound.setStyleSheet(checkbox_style)
        self.cb_sound.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb_sound.setChecked(self.config.get("sound_enabled"))
        self.cb_sound.stateChanged.connect(lambda state: self.config.set("sound_enabled", bool(state)))
        lbl_sound = QLabel(tr("Sound Effects"))
        lbl_sound.setStyleSheet("color: #cccccc;")
        beh_form.addRow(lbl_sound, self.cb_sound)

        # Hotkey
        self.hotkey_btn = QPushButton(self.config.get("hotkey"))
        self.hotkey_btn.setToolTip(tr("Click to redefine hotkey"))
        self.hotkey_btn.setStyleSheet("background: #222; color: white; border-radius: 4px; padding: 5px; font-weight: bold;")
        self.hotkey_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hotkey_btn.setMinimumWidth(100)
        from PyQt6.QtWidgets import QSizePolicy
        self.hotkey_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.is_capturing = False
        def on_hk_click():
            self.is_capturing = True
            self.hotkey_btn.setText(tr("Waiting for key..."))
            self.hotkey_btn.setStyleSheet(f"background: {self.accent_color}; color: white; border-radius: 4px; padding: 5px; font-weight: bold;")
            self.hotkey_btn.setFocus()
        self.hotkey_btn.clicked.connect(on_hk_click)
        lbl_hk = QLabel(tr("Global Hotkey (Click to capture)"))
        lbl_hk.setStyleSheet("color: #cccccc;")
        beh_form.addRow(lbl_hk, self.hotkey_btn)
        
        # Move to top on click
        self.cb_move_top = QCheckBox()
        self.cb_move_top.setStyleSheet(checkbox_style)
        self.cb_move_top.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cb_move_top.setChecked(self.config.get("move_to_top_on_click", True))
        self.cb_move_top.stateChanged.connect(lambda state: self.config.set("move_to_top_on_click", bool(state)))
        lbl_move_top = QLabel(tr("Move clicked item to top"))
        lbl_move_top.setStyleSheet("color: #cccccc;")
        beh_form.addRow(lbl_move_top, self.cb_move_top)

        # ==========================================
        # ==========================================
        # SECTION: Edge Zone
        # ==========================================
        btn_edge = add_tab(tr("Edge Zone"), 2)
        edge_widget = QWidget()
        edge_form = create_form()
        edge_widget.setLayout(edge_form)
        self.settings_stacked.addWidget(edge_widget)
        
        # Edge side
        side_layout = QVBoxLayout()
        radio_style = f"""
            QRadioButton {{ color: white; }}
            QRadioButton::indicator {{ width: 14px; height: 14px; border-radius: 7px; border: 1px solid #777; background: #222; }}
            QRadioButton::indicator:checked {{ background: {self.accent_color}; border: 3px solid #222; }}
            QRadioButton::indicator:hover {{ border: 1px solid #999; }}
        """
        self.rb_left = QRadioButton(tr("Left Edge"))
        self.rb_right = QRadioButton(tr("Right Edge"))
        self.rb_left.setStyleSheet(radio_style)
        self.rb_right.setStyleSheet(radio_style)
        self.rb_left.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rb_right.setCursor(Qt.CursorShape.PointingHandCursor)
        
        edge_sides = self.config.get("edge_sides", {})
        current_val = edge_sides.get(getattr(self, "current_screen_name", "default"), self.config.get("edge_side", "left"))
        
        if current_val == "left":
            self.rb_left.setChecked(True)
        else:
            self.rb_right.setChecked(True)
            
        def on_side_change():
            val = "left" if self.rb_left.isChecked() else "right"
            s_name = getattr(self, "current_screen_name", "default")
            edge_sides = dict(self.config.get("edge_sides", {}))
            edge_sides[s_name] = val
            self.config.set("edge_sides", edge_sides)
            self.edge_side = val
            self._calc_positions()
            if self.is_open:
                self.setFixedSize(self.shelf_width, self.shelf_height)
                self.setGeometry(self.x_visible, self.y_pos, self.shelf_width, self.shelf_height)
            self.update()
            
        self.rb_left.toggled.connect(on_side_change)
        self.rb_right.toggled.connect(on_side_change)
        side_layout.addWidget(self.rb_left)
        side_layout.addWidget(self.rb_right)
        
        from PyQt6.QtGui import QGuiApplication
        num_screens = len(QGuiApplication.screens())
        lbl_text = tr("Edge Side for this monitor") if num_screens > 1 else tr("Edge Side")
        lbl_side = QLabel(lbl_text)
        lbl_side.setWordWrap(True)
        lbl_side.setStyleSheet("color: #cccccc;")
        edge_form.addRow(lbl_side, side_layout)
        # Sensitivity / Width
        slider_sens = QSlider(Qt.Orientation.Horizontal)
        slider_sens.setMinimumWidth(100)
        slider_sens.setRange(1, 20)
        slider_sens.setValue(self.config.get("trigger_width"))
        slider_sens.setCursor(Qt.CursorShape.PointingHandCursor)
        slider_sens.setStyleSheet(f"QSlider::handle:horizontal {{ background: {self.accent_color}; border-radius: 5px; width: 10px; }}")
        
        def _update_preview():
            val = self.config.get("trigger_width")
            if not getattr(self, 'preview_win', None):
                self.preview_win = QWidget()
                self.preview_win.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.WindowTransparentForInput)
                self.preview_win.setWindowOpacity(0.5)
                self.preview_win.setStyleSheet(f"background-color: {self.accent_color};")
            x = self.screen_x if self.edge_side == "left" else self.screen_x + self.screen_width - val
            h_pct = self.config.get("trigger_height_percent", 50)
            area_height = int(self.screen_height * (h_pct / 100))
            y_pos = self.screen_y + int((self.screen_height - area_height) / 2)
            self.preview_win.setGeometry(x, y_pos, val, area_height)
            self.preview_win.show()

        def on_sens_changed(val):
            from PyQt6.QtWidgets import QToolTip
            from PyQt6.QtGui import QCursor
            QToolTip.showText(QCursor.pos(), f"{val} px")
            self.config.set("trigger_width", val)
            _update_preview()
            
        def on_sens_released():
            if getattr(self, 'preview_win', None):
                self.preview_win.hide()
                self.preview_win.deleteLater()
                self.preview_win = None
                
        slider_sens.valueChanged.connect(on_sens_changed)
        slider_sens.sliderReleased.connect(on_sens_released)
        lbl_sens = QLabel(tr("Trigger Area (pixels)"))
        lbl_sens.setStyleSheet("color: #cccccc;")
        edge_form.addRow(lbl_sens, slider_sens)

        # Sensitivity Height
        slider_height = QSlider(Qt.Orientation.Horizontal)
        slider_height.setMinimumWidth(100)
        slider_height.setRange(10, 100)
        slider_height.setCursor(Qt.CursorShape.PointingHandCursor)
        slider_height.setValue(self.config.get("trigger_height_percent"))
        slider_height.setStyleSheet(f"QSlider::handle:horizontal {{ background: {self.accent_color}; border-radius: 5px; width: 10px; }}")
        
        def on_height_changed(val):
            from PyQt6.QtWidgets import QToolTip
            from PyQt6.QtGui import QCursor
            QToolTip.showText(QCursor.pos(), f"{val}%")
            self.config.set("trigger_height_percent", val)
            _update_preview()
            
        slider_height.valueChanged.connect(on_height_changed)
        slider_height.sliderReleased.connect(on_sens_released)
        lbl_sens_height = QLabel(tr("Trigger Height (%)"))
        lbl_sens_height.setStyleSheet("color: #cccccc;")
        edge_form.addRow(lbl_sens_height, slider_height)

        # ==========================================
        # SECTION: System
        # ==========================================
        btn_system = add_tab(tr("System"), 3)
        sys_widget = QWidget()
        sys_layout = QVBoxLayout(sys_widget)
        sys_layout.setContentsMargins(0, 10, 0, 0)
        sys_layout.setSpacing(10)
        self.settings_stacked.addWidget(sys_widget)
        self.restart_btn = QPushButton(tr("Restart Application"))
        self.restart_btn.setToolTip(tr("Restart Py-Drop"))
        self.restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.restart_btn.setStyleSheet("QPushButton { background-color: #ff4444; color: white; border-radius: 4px; padding: 8px; font-weight: bold; } QPushButton:hover { background-color: #ff6666; }")
        def on_restart():
            import sys, subprocess
            subprocess.Popen([sys.executable] + sys.argv)
            QApplication.quit()
        self.restart_btn.clicked.connect(on_restart)
        sys_layout.addWidget(self.restart_btn)
        
        self.exit_btn = QPushButton(tr("Quit Application"))
        self.exit_btn.setToolTip(tr("Quit Py-Drop completely"))
        self.exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_btn.setStyleSheet("QPushButton { background-color: #ff4444; color: white; border-radius: 4px; padding: 8px; font-weight: bold; } QPushButton:hover { background-color: #ff6666; }")
        self.exit_btn.clicked.connect(QApplication.quit)
        sys_layout.addWidget(self.exit_btn)
        sys_layout.addStretch()
        
        # Ensure all labels wrap text to prevent horizontal overflow on narrow shelf widths
        for lbl in container.findChildren(QLabel):
            lbl.setWordWrap(True)
            
        def on_tab_clicked(id):
            self.settings_stacked.setCurrentIndex(id)
            
        self.tab_group.idClicked.connect(on_tab_clicked)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            if getattr(self, "is_capturing", False):
                self.is_capturing = False
                hk_str = self.config.get("hotkey", "Alt+Shift+A")
                self.hotkey_btn.setText(hk_str)
                self.hotkey_btn.setStyleSheet("background: #222; color: white; border-radius: 4px; padding: 5px; font-weight: bold;")
            elif self.is_settings_view:
                self._toggle_settings()
            else:
                self.close_shelf()
            return
            
        if getattr(self, "is_capturing", False):
            key = event.key()
            if key in (Qt.Key.Key_Shift, Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
                return
                
            mods = []
            m = event.modifiers()
            if m & Qt.KeyboardModifier.ControlModifier: mods.append("Ctrl")
            if m & Qt.KeyboardModifier.ShiftModifier: mods.append("Shift")
            if m & Qt.KeyboardModifier.AltModifier: mods.append("Alt")
            
            # Very basic key mapping for display
            from PyQt6.QtGui import QKeySequence
            key_str = QKeySequence(key).toString()
            hk_str = "+".join(mods + [key_str])
            
            self.config.set("hotkey", hk_str)
            self.hotkey_btn.setText(hk_str)
            self.hotkey_btn.setStyleSheet("background: #222; color: white; border-radius: 4px; padding: 5px; font-weight: bold;")
            self.is_capturing = False
            
            if self.hotkey_manager:
                from src.core.hotkey import parse_hotkey_string
                modifiers, vk = parse_hotkey_string(hk_str)
                if vk != 0:
                    self.hotkey_manager.start_hotkey(modifiers, vk)
                    
        super().keyPressEvent(event)

    def set_hotkey_manager(self, manager):
        self.hotkey_manager = manager

    def _toggle_settings(self):
        if self.audio: self.audio.play_toggle()
        if self.is_settings_view:
            self.stacked.setCurrentIndex(0)
            self.settings_btn.set_active(False)
        else:
            self.stacked.setCurrentIndex(1)
            self.settings_btn.set_active(True)
        self.is_settings_view = not self.is_settings_view

    def _toggle_pause(self):
        if self.audio: self.audio.play_toggle()
        self.clipboard_watcher.is_paused = not self.clipboard_watcher.is_paused
        if self.clipboard_watcher.is_paused:
            self.pause_btn.inner_html = PATH_PLAY
            self.pause_btn.set_active(True)
        else:
            self.pause_btn.inner_html = PATH_PAUSE
            self.pause_btn.set_active(False)

    def _clear_unpinned(self):
        if self.audio: self.audio.play_delete()
        self.clipboard_watcher.clear_unpinned()
        self.load_history()

    def _on_search(self, text):
        text = text.lower()
        visible = 0
        for item_id, card in self.item_widgets.items():
            if text and card.render_type == "image":
                card.hide()
                continue
                
            search_target = " ".join(card.full_content).lower() if isinstance(card.full_content, list) else card.full_content.lower()
            if text in search_target:
                card.show()
                visible += 1
            else:
                card.hide()
        
        if visible == 0 and self.item_widgets:
            self.empty_lbl.setText(tr("No matches found."))
            self.empty_lbl.show()
        elif not self.item_widgets:
            self.empty_lbl.setText(tr("The shelf is empty."))
            self.empty_lbl.show()
        else:
            self.empty_lbl.hide()

    def handle_edge_enter(self, screen_info=None):
        if screen_info:
            s_name, sx, sy, sw, sh, edge_side = screen_info
            # If already open on the exact same screen, ignore the teleport
            if self.is_open:
                pass
            else:
                self.current_screen_name = s_name
                self.edge_side = edge_side
                self.screen_x, self.screen_y, self.screen_width, self.screen_height = sx, sy, sw, sh
                self.shelf_height = int(self.screen_height * 0.8)
                self.y_pos = self.screen_y + int((self.screen_height - self.shelf_height) / 2)
                self._calc_positions()
                self.setFixedSize(self.shelf_width, self.shelf_height)
                self.load_history(force_rebuild=True)
            
        self.open_shelf()

    def handle_edge_leave(self):
        QTimer.singleShot(100, self._check_close)

    def enterEvent(self, event):
        self.open_shelf()
        super().enterEvent(event)

    def leaveEvent(self, event):
        QTimer.singleShot(100, self._check_close)
        super().leaveEvent(event)

    def _check_close(self):
        if getattr(self, "is_dragging", False):
            return
            
        cx, cy = utils.get_cursor_pos()
        
        # Use logical coordinates instead of self.geometry() because Windows DWM 
        # can temporarily alter physical geometry during show/hide operations
        geo_x = self.x_visible
        geo_y = self.y_pos
        geo_w = self.shelf_width
        geo_h = self.shelf_height
        buffer = 30
        
        is_inside_strict = (
            geo_x <= cx <= geo_x + geo_w and
            geo_y <= cy <= geo_y + geo_h
        )
        
        is_inside_buffer = (
            geo_x - buffer <= cx <= geo_x + geo_w + buffer and
            geo_y - buffer <= cy <= geo_y + geo_h + buffer
        )
        
        is_inside = is_inside_buffer
        
        if not is_inside:
            self.close_shelf()
        elif not is_inside_strict and self.is_open:
            # Mouse is in the buffer but outside the physical window, Qt won't fire leaveEvent again.
            # So we poll until they leave the buffer or re-enter the window.
            QTimer.singleShot(100, self._check_close)
    def open_shelf(self):
        if not self.is_open:
            self.setGeometry(self.x_visible, self.y_pos, self.shelf_width, self.shelf_height)
            self.show()
            self.raise_()
            self.activateWindow()
            self.setFocus()
            
            def run_checks():
                for card in self.item_widgets.values():
                    if hasattr(card, 'check_validity'):
                        card.check_validity()
            
            # Defer the checks until after the slide animation finishes (400ms)
            QTimer.singleShot(400, run_checks)
            
            self.is_open = True
            if self.audio: self.audio.play_toggle()
            
            # Animate the container sliding in from the edge
            start_x = self.shelf_width if self.edge_side == "right" else -self.shelf_width
            self.container.move(start_x, 0)
            
            self.animation.setTargetObject(self.container)
            self.animation.setPropertyName(b"pos")
            self.animation.setStartValue(QPoint(start_x, 0))
            self.animation.setEndValue(QPoint(0, 0))
            self.animation.start()

    def close_shelf(self):
        if self.is_open:
            self.is_open = False
            try:
                ImagePreviewWindow.close_all()
            except NameError:
                pass
            
            end_x = self.shelf_width if self.edge_side == "right" else -self.shelf_width
            
            self.animation.setTargetObject(self.container)
            self.animation.setPropertyName(b"pos")
            self.animation.setStartValue(self.container.pos())
            self.animation.setEndValue(QPoint(end_x, 0))
            self.animation.start()

    def _on_animation_finished(self):
        if not self.is_open:
            self.hide()

    def load_history(self, force_rebuild=False):
        history = self.clipboard_watcher.get_history()
        
        # 1. Identify which items to keep and which to delete
        current_history_map = {item.get("id"): item for item in history}
        
        # Remove widgets that no longer exist, or whose type/timestamp/content changed
        for w_id in list(self.item_widgets.keys()):
            w = self.item_widgets[w_id]
            h_item = current_history_map.get(w_id)
            # Compare basic attributes to see if we can reuse the widget
            if not h_item:
                w = self.item_widgets.pop(w_id)
                w.setParent(None)
                w.deleteLater()
                continue
                
            h_content_len = len(h_item.get("content")) if isinstance(h_item.get("content"), list) else 1
            if force_rebuild or w.render_timestamp != h_item.get("timestamp") or w.render_content_len != h_content_len or w.render_pinned != h_item.get("pinned") or w.render_type != h_item.get("type"):
                w = self.item_widgets.pop(w_id)
                w.setParent(None)
                w.deleteLater()
                
        # 2. Clear layouts (remove without deleting remaining widgets)
        while self.pinned_section.body_layout.count():
            item = self.pinned_section.body_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                
        while self.unpinned_layout.count():
            item = self.unpinned_layout.takeAt(0)
            if item.widget():
                w = item.widget()
                w.setParent(None)
                if isinstance(w, TimeDividerWidget):
                    w.deleteLater()
                    
        # 3. Rebuild UI
        has_pinned = False
        from src.utils.helpers import get_time_group
        current_group_id = None
        
        for item in history[:self.display_limit]:
            item_id = item.get("id")
            is_pinned = item.get("pinned")
            
            if is_pinned:
                has_pinned = True
                
            layout = self.pinned_section.body_layout if is_pinned else self.unpinned_layout
            
            if not is_pinned:
                grp_id, grp_name = get_time_group(item.get("timestamp"))
                if grp_id != current_group_id:
                    current_group_id = grp_id
                    divider = TimeDividerWidget(grp_name)
                    layout.addWidget(divider)
                    divider.show()
            
            if item_id in self.item_widgets:
                # Reuse existing widget
                card = self.item_widgets[item_id]
                layout.addWidget(card)
                card.show()
            else:
                # Create new widget (this will add it to the layout and self.item_widgets)
                self.add_clipboard_item(item, to_top=False)
                
        self.pinned_section.setVisible(has_pinned)
            
        if not history:
            self.empty_lbl.show()
        else:
            self.empty_lbl.hide()

    def delete_subitem(self, group_id, file_path):
        if self.audio: self.audio.play_delete()
        self.clipboard_watcher.remove_file_from_group(group_id, file_path, delete_physical=True)
        self.load_history()

    def _simulate_ctrl_v(self):
        import ctypes
        VK_CONTROL = 0x11
        VK_V = 0x56
        KEYEVENTF_KEYUP = 0x0002
        
        # Press Ctrl
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, 0, 0)
        # Press V
        ctypes.windll.user32.keybd_event(VK_V, 0, 0, 0)
        # Release V
        ctypes.windll.user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
        # Release Ctrl
        ctypes.windll.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

    def _animate_move_to_top(self, card, moved_item, on_complete=None):
        layout = self.pinned_section.body_layout if moved_item.get("pinned") else self.unpinned_layout
        current_idx = layout.indexOf(card)
        
        target_idx = 0
        temp_divider = None
        if not moved_item.get("pinned"):
            from src.utils.helpers import get_time_group
            import time
            grp_id, grp_name = get_time_group(time.time())
            
            has_hoje = False
            if layout.count() > 0:
                from src.ui.shelf import TimeDividerWidget
                first_item = layout.itemAt(0).widget()
                if isinstance(first_item, TimeDividerWidget):
                    lbl = first_item.findChild(QLabel)
                    if lbl and lbl.text() == grp_name:
                        has_hoje = True
                        
            if has_hoje:
                target_idx = 1
            else:
                from src.ui.shelf import TimeDividerWidget
                temp_divider = TimeDividerWidget(grp_name)
                layout.insertWidget(0, temp_divider)
                temp_divider.show()
                target_idx = 1
                # current_idx shifts down by 1 because we inserted before it
                current_idx += 1

        if current_idx <= target_idx:
            # Já está no topo
            if temp_divider:
                temp_divider.deleteLater()
            card.item = moved_item
            card.render_timestamp = moved_item.get("timestamp")
            card.update_timestamp()
            self.load_history()
            if on_complete: on_complete()
            return
            
        pixmap = card.grab()
        scroll_widget = self.scroll.widget()
        start_pos = card.mapTo(scroll_widget, QPoint(0, 0))
        
        flying = QLabel(scroll_widget)
        flying.setPixmap(pixmap)
        flying.move(start_pos)
        flying.resize(card.size())
        flying.show()
        flying.raise_()
        
        dummy_expand = QWidget()
        dummy_expand.setMinimumHeight(0)
        dummy_expand.setMaximumHeight(0)
        
        dummy_shrink = QWidget()
        dummy_shrink.setMinimumHeight(0)
        dummy_shrink.setMaximumHeight(card.height())
        
        layout.insertWidget(current_idx, dummy_shrink)
        dummy_shrink.show()
        card.hide()
        layout.insertWidget(target_idx, dummy_expand)
        dummy_expand.show()
        
        layout.invalidate()
        scroll_widget.layout().activate()
        target_pos = dummy_expand.mapTo(scroll_widget, QPoint(0, 0))
        
        from PyQt6.QtCore import QParallelAnimationGroup, QPropertyAnimation, QEasingCurve
        self._move_anim_group = QParallelAnimationGroup(self)
        
        anim_move = QPropertyAnimation(flying, b"pos")
        anim_move.setStartValue(start_pos)
        anim_move.setEndValue(target_pos)
        anim_move.setDuration(400)
        anim_move.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        anim_shrink = QPropertyAnimation(dummy_shrink, b"maximumHeight")
        anim_shrink.setStartValue(card.height())
        anim_shrink.setEndValue(0)
        anim_shrink.setDuration(400)
        anim_shrink.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        anim_expand = QPropertyAnimation(dummy_expand, b"maximumHeight")
        anim_expand.setStartValue(0)
        anim_expand.setEndValue(card.height())
        anim_expand.setDuration(400)
        anim_expand.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        target_scroll = 0
        if not moved_item.get("pinned"):
            divider = layout.itemAt(0).widget()
            if divider:
                target_scroll = divider.mapTo(scroll_widget, QPoint(0, 0)).y()
                
        scroll_bar = self.scroll.verticalScrollBar()
        current_scroll = scroll_bar.value()
        viewport_height = self.scroll.viewport().height()
        
        final_scroll = current_scroll
        if target_scroll < current_scroll:
            final_scroll = target_scroll
        elif target_scroll + card.height() + 50 > current_scroll + viewport_height:
            final_scroll = target_scroll
            
        final_scroll = max(0, min(final_scroll, scroll_bar.maximum()))
        
        anim_scroll = QPropertyAnimation(scroll_bar, b"value")
        anim_scroll.setStartValue(scroll_bar.value())
        anim_scroll.setEndValue(final_scroll)
        anim_scroll.setDuration(400)
        anim_scroll.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self._move_anim_group.addAnimation(anim_move)
        self._move_anim_group.addAnimation(anim_shrink)
        self._move_anim_group.addAnimation(anim_expand)
        self._move_anim_group.addAnimation(anim_scroll)
        
        def on_finish():
            flying.deleteLater()
            dummy_shrink.deleteLater()
            dummy_expand.deleteLater()
            if temp_divider:
                temp_divider.deleteLater()
            card.item = moved_item
            card.render_timestamp = moved_item.get("timestamp")
            card.update_timestamp()
            self.load_history()
            if on_complete: on_complete()
            
        self._move_anim_group.finished.connect(on_finish)
        self._move_anim_group.start()

    def _on_card_clicked_to_paste(self, item):
        item_id = item.get("id")
        self.clipboard_watcher.copy_to_clipboard(item)
        
        def do_paste():
            click_to_paste = self.config.get("click_to_paste")
            if click_to_paste is False:
                return
            self.hide()
            self.is_open = False
            end_x = self.shelf_width if self.edge_side == "right" else -self.shelf_width
            self.container.move(end_x, 0)
            QTimer.singleShot(100, self._simulate_ctrl_v)
        
        if self.config.get("move_to_top_on_click", True):
            moved_item = self.clipboard_watcher.move_to_top(item_id)
            if moved_item:
                card = self.item_widgets.get(item_id)
                if card:
                    self._animate_move_to_top(card, moved_item, on_complete=do_paste)
                    return
                        
        do_paste()

    def add_clipboard_item(self, item, to_top=True):
        self.empty_lbl.hide()
        item_id = item.get("id")
        
        if item_id in self.item_widgets:
            w = self.item_widgets[item_id]
            w.setParent(None)
            w.deleteLater()
            
        card = ItemCard(item, self.shelf_width, self.audio, accent_color=self.accent_color)
        card.copy_clicked.connect(self._on_card_clicked_to_paste)
        card.delete_clicked.connect(self.delete_item)
        card.delete_subitem_clicked.connect(self.delete_subitem)
        card.pin_clicked.connect(self.pin_item)
        
        if item.get("pinned"):
            if to_top:
                self.pinned_section.body_layout.insertWidget(0, card)
            else:
                self.pinned_section.body_layout.addWidget(card)
            self.pinned_section.show()
        else:
            if to_top:
                self.unpinned_layout.insertWidget(0, card)
            else:
                self.unpinned_layout.addWidget(card)
                
        self.item_widgets[item_id] = card
        card.show()
        
    def delete_item(self, item_id):
        self.clipboard_watcher.remove_item(item_id)
        if item_id in self.item_widgets:
            w = self.item_widgets[item_id]
            w.setParent(None)
            w.deleteLater()
            del self.item_widgets[item_id]
            
        has_pinned = any(item.get("pinned") for item in self.clipboard_watcher.get_history())
        self.pinned_section.setVisible(has_pinned)
            
        if not self.item_widgets:
            self.empty_lbl.setText(tr("The shelf is empty."))
            self.empty_lbl.show()

    def pin_item(self, item_id):
        self.clipboard_watcher.toggle_pin(item_id)
        self.load_history()

    def dragEnterEvent(self, event):
        if getattr(self, 'active_drag_is_top_level', False):
            event.ignore()
            return
            
        if event.mimeData().hasUrls() or event.mimeData().hasText() or event.mimeData().hasImage():
            if hasattr(self, 'drop_overlay'):
                if hasattr(self, 'active_drag_source_id') and self.active_drag_source_id:
                    self.drop_overlay.setText(tr("Drop here to ungroup"))
                else:
                    self.drop_overlay.setText(tr("Drop here"))
                self.drop_overlay.clearMask()
                self.drop_overlay.show()
                self.drop_overlay.raise_()
            if not getattr(self, 'is_dragging', False):
                self.start_auto_scroll()
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event):
        if getattr(self, 'active_drag_is_top_level', False):
            event.ignore()
            return
            
        if event.mimeData().hasUrls() or event.mimeData().hasText() or event.mimeData().hasImage():
            if hasattr(self, 'drop_overlay'):
                if hasattr(self, 'active_drag_source_id') and self.active_drag_source_id:
                    card_widget = self.item_widgets.get(self.active_drag_source_id)
                    if card_widget:
                        from PyQt6.QtGui import QRegion
                        from PyQt6.QtCore import QRect, QPoint
                        mapped_top_left = card_widget.mapTo(self, QPoint(0, 0))
                        mapped_rect = QRect(mapped_top_left, card_widget.size())
                        
                        if mapped_rect.contains(event.position().toPoint()):
                            self.drop_overlay.hide()
                        else:
                            region = QRegion(self.rect())
                            region -= QRegion(mapped_rect)
                            self.drop_overlay.setMask(region)
                            self.drop_overlay.show()
                else:
                    self.drop_overlay.clearMask()
                    self.drop_overlay.show()
            event.acceptProposedAction()
            
    def dragLeaveEvent(self, event):
        if hasattr(self, 'drop_overlay'):
            self.drop_overlay.hide()
        if not getattr(self, 'is_dragging', False):
            self.stop_auto_scroll()
        super().dragLeaveEvent(event)
        
    def _try_download_image(self, url_str):
        if not url_str.startswith(('http', 'https', 'data')):
            return False
            
        import urllib.request
        import time
        from PyQt6.QtGui import QImage
        try:
            req = urllib.request.Request(url_str, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            with urllib.request.urlopen(req, timeout=3) as response:
                content_type = response.headers.get('Content-Type', '')
                if content_type.startswith('image/'):
                    data = response.read()
                    img = QImage.fromData(data)
                    if not img.isNull():
                        images_dir = self.clipboard_watcher.storage.filepath.parent / "images"
                        images_dir.mkdir(exist_ok=True)
                        img_path = images_dir / f"image_{int(time.time()*1000)}.png"
                        if img.save(str(img_path), "PNG"):
                            self.clipboard_watcher.copy_to_clipboard({"type": "image", "content": str(img_path)}, add_to_shelf=True)
                            return True
        except Exception:
            pass
        return False

    def dropEvent(self, event):
        if not getattr(self, 'is_dragging', False):
            self.stop_auto_scroll()
        if hasattr(self, 'drop_overlay'):
            self.drop_overlay.hide()
            
        mime = event.mimeData()
        
        # 0. Internal sub-item drag extraction
        if mime.hasFormat("edgedrop/internal-drag-subitem"):
            parent_id = bytes(mime.data("edgedrop/internal-drag-subitem")).decode('utf-8')
            if mime.hasUrls():
                local_files = [url.toLocalFile() for url in mime.urls() if url.isLocalFile()]
                if local_files:
                    # Remove from original group
                    self.clipboard_watcher.remove_file_from_group(parent_id, local_files[0])
                    # Add as new top-level item
                    self.clipboard_watcher.copy_to_clipboard(local_files[0], add_to_shelf=True)
                    event.acceptProposedAction()
                    return
                    
        # 1. Local Files
        if mime.hasUrls():
            local_files = [url.toLocalFile() for url in mime.urls() if url.isLocalFile()]
            if local_files:
                if len(local_files) == 1:
                    self.clipboard_watcher.copy_to_clipboard(local_files[0], add_to_shelf=True)
                else:
                    self.clipboard_watcher.copy_to_clipboard(local_files, add_to_shelf=True)
                event.acceptProposedAction()
                return

        # 2. Try HTML to find an <img> tag if it's a browser drag
        if mime.hasHtml():
            html = mime.html()
            import re
            m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html)
            if m:
                img_src = m.group(1)
                if not img_src.startswith('/'): # Ignore relative
                    if self._try_download_image(img_src):
                        event.acceptProposedAction()
                        return
                        
        # 3. Try URLs if they are web links
        if mime.hasUrls():
            web_urls = [url.toString() for url in mime.urls() if url.scheme() in ('http', 'https', 'data')]
            for w_url in web_urls:
                if self._try_download_image(w_url):
                    event.acceptProposedAction()
                    return

        # 4. Try Text as URL
        if mime.hasText():
            text = mime.text().strip()
            if text.startswith(('http', 'https', 'data')):
                if self._try_download_image(text):
                    event.acceptProposedAction()
                    return

        # 5. Native Image (e.g. Snipping tool)
        if mime.hasImage():
            saved_path = self.clipboard_watcher.save_image_from_mime(mime)
            if saved_path:
                self.clipboard_watcher.copy_to_clipboard({"type": "image", "content": saved_path}, add_to_shelf=True)
                event.acceptProposedAction()
                return
                
        # 6. Fallback to raw text
        if mime.hasText():
            self.clipboard_watcher.copy_to_clipboard(mime.text(), add_to_shelf=True)
            event.acceptProposedAction()
