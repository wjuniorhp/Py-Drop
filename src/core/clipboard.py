import time
import os
import re
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QGuiApplication

class ClipboardWatcher(QObject):
    new_item = pyqtSignal(dict)
    history_changed = pyqtSignal()

    def __init__(self, storage, audio=None):
        super().__init__()
        self.storage = storage
        self.audio = audio
        self.history = self.storage.load()
        self.is_paused = False
        self.last_content = ""
        
        # Connect to the global clipboard signals!
        clipboard = QGuiApplication.clipboard()
        clipboard.dataChanged.connect(self._on_clipboard_change)
        
        from PyQt6.QtCore import QTimer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(150)
        self.debounce_timer.timeout.connect(self._process_clipboard)

    def start(self):
        pass # No polling needed in PyQt6!

    def stop(self):
        pass

    def copy_to_clipboard(self, item_or_text, add_to_shelf=False):
        clipboard = QGuiApplication.clipboard()
        from PyQt6.QtCore import QMimeData, QUrl
        mime = QMimeData()
        
        if isinstance(item_or_text, dict):
            text = item_or_text.get("content", "")
            item_type = item_or_text.get("type", "text")
        else:
            text = item_or_text
            item_type = "text"
            if isinstance(text, list):
                item_type = "files"
            elif os.path.exists(text):
                text_str = str(text).replace('\\', '/')
                if "/images/image_" in text_str and text_str.endswith(".png"):
                    item_type = "image"
                else:
                    item_type = "file"
        
        if item_type == "files" or isinstance(text, list):
            mime.setUrls([QUrl.fromLocalFile(p.strip()) for p in text if os.path.exists(p.strip())])
        else:
            text = text.strip()
            if os.path.exists(text):
                mime.setUrls([QUrl.fromLocalFile(text)])
                if item_type == "image":
                    from PyQt6.QtGui import QImage
                    img = QImage(text)
                    if not img.isNull():
                        mime.setImageData(img)
            else:
                mime.setText(text)
            
        clipboard.blockSignals(True)
        clipboard.setMimeData(mime)
        
        # Normalize for last_content comparison to avoid duplicates from slash mismatch
        if isinstance(text, list):
            self.last_content = [os.path.normcase(os.path.normpath(p)) for p in text]
        elif os.path.exists(text):
            self.last_content = os.path.normcase(os.path.normpath(text))
        else:
            self.last_content = text
            
        clipboard.blockSignals(False)
        
        if add_to_shelf:
            if item_type == "image":
                self.add_from_image(text)
            elif item_type == "files" or isinstance(text, list):
                self.add_from_files(text)
            else:
                self.add_from_text(text)

    def _on_clipboard_change(self):
        # On Windows, the clipboard might be locked by the source application for a few milliseconds,
        # and some tools like Snipping Tool fire dataChanged multiple times rapidly.
        # We debounce the signal by restarting a 150ms timer.
        self.debounce_timer.start()

    def save_image_from_mime(self, mime):
        img = mime.imageData()
        if img and not img.isNull():
            import time
            images_dir = self.storage.filepath.parent / "images"
            images_dir.mkdir(exist_ok=True)
            img_path = images_dir / f"image_{int(time.time()*1000)}.png"
            if img.save(str(img_path), "PNG"):
                return str(img_path)
        return None

    def _process_clipboard(self):
        if self.is_paused:
            return
            
        clipboard = QGuiApplication.clipboard()
        mime = clipboard.mimeData()
        
        current_text = ""
        current_list = None
        
        if mime.hasImage():
            img = mime.imageData()
            if img and not img.isNull():
                import hashlib
                ptr = img.constBits()
                ptr.setsize(img.sizeInBytes())
                img_hash = hashlib.md5(ptr.asstring()).hexdigest()
                if img_hash == self.last_content:
                    return
                self.last_content = img_hash
                
                saved_path = self.save_image_from_mime(mime)
                if saved_path:
                    self.add_from_image(saved_path)
                return

        if mime.hasUrls() and mime.urls():
            local_files = [u.toLocalFile() for u in mime.urls() if u.isLocalFile()]
            if local_files:
                if len(local_files) == 1:
                    current_text = local_files[0]
                else:
                    current_list = local_files
        
        if not current_list and not current_text:
            if not current_text:
                if mime.hasText():
                    current_text = mime.text()
                elif mime.hasUrls() and mime.urls():
                    current_text = mime.urls()[0].toString()
            
        if current_list:
            norm_list = [os.path.normcase(os.path.normpath(p)) for p in current_list]
            if norm_list == self.last_content:
                return
            self.last_content = norm_list
            self.add_from_files(current_list)
        else:
            norm_text = os.path.normcase(os.path.normpath(current_text)) if os.path.exists(current_text) else current_text
            if not current_text or norm_text == self.last_content:
                return
            self.last_content = norm_text
            self.add_from_text(current_text)
            
    def add_from_image(self, saved_path):
        item = {
            "id": str(time.time()),
            "type": "image", 
            "content": saved_path, 
            "timestamp": time.time(),
            "pinned": False
        }
        self.add_item(item)
        if self.audio:
            self.audio.play_copy()
        
    def add_from_text(self, current_text):
        item_type = "text"
        
        if os.path.exists(current_text):
            item_type = "file"
        elif re.match(r'^https?://', current_text) or re.match(r'^www\.', current_text):
            item_type = "link"
            
        item = {
            "id": str(time.time()),
            "type": item_type, 
            "content": current_text, 
            "timestamp": time.time(),
            "pinned": False
        }
        
        self.add_item(item)
        if self.audio:
            self.audio.play_copy()
            
    def add_from_files(self, files_list):
        item = {
            "id": str(time.time()),
            "type": "files",
            "content": files_list,
            "timestamp": time.time(),
            "pinned": False
        }
        
        self.add_item(item)
        if self.audio:
            self.audio.play_copy()

    def add_item(self, item):
        for i, existing in enumerate(self.history):
            if existing["content"] == item["content"]:
                item["id"] = existing.get("id")
                if existing.get("pinned"):
                    item["pinned"] = True
                self.history.pop(i)
                break
                
        self.history.insert(0, item)
        
        unpinned = [x for x in self.history if not x.get("pinned")]
        if len(self.history) > 50 and unpinned:
            oldest_unpinned = unpinned[-1]
            self._delete_physical_file(oldest_unpinned)
            self.history.remove(oldest_unpinned)

        self.storage.save(self.history)
        self.new_item.emit(item)
            
    def remove_item(self, item_id):
        for x in self.history:
            if x.get("id") == item_id:
                self._delete_physical_file(x)
                break
                
        self.history = [x for x in self.history if x.get("id") != item_id]
        self.storage.save(self.history)
        
    def remove_file_from_group(self, group_id, file_path):
        for x in self.history:
            if x.get("id") == group_id and x.get("type") == "files":
                content = x.get("content", [])
                if file_path in content:
                    content.remove(file_path)
                if len(content) == 1:
                    x["type"] = "file"
                    x["content"] = content[0]
                elif len(content) == 0:
                    self.history.remove(x)
                self.storage.save(self.history)
                break
                
    def stack_items(self, target_id, source_data, source_id=None, is_internal=False):
        target_item = next((x for x in self.history if x.get("id") == target_id), None)
        if not target_item: return
        
        # Determine source items to add
        new_items = []
        if isinstance(source_data, list):
            new_items = source_data
        else:
            new_items = [source_data]
            
        # If target is not already a 'files' group, convert it
        if target_item.get("type") != "files":
            target_item["type"] = "files"
            target_item["content"] = [target_item["content"]]
            
        # Append new items avoiding duplicates
        for item in new_items:
            if item not in target_item["content"]:
                target_item["content"].append(item)
                
        target_item["timestamp"] = time.time()
        
        # Remove source if internal
        if is_internal and source_id:
            if source_id != target_id:
                self.history = [x for x in self.history if x.get("id") != source_id]
                
        self.storage.save(self.history)
        
        # Re-insert target at the top to refresh UI
        self.history.remove(target_item)
        self.history.insert(0, target_item)
        
        # We don't emit new_item because that adds a duplicate card.
        # Instead, we emit a new signal 'history_changed' or we rely on the caller to refresh.
        if hasattr(self, 'history_changed'):
            self.history_changed.emit()
        
    def clear_unpinned(self):
        for x in self.history:
            if not x.get("pinned"):
                self._delete_physical_file(x)
                
        self.history = [x for x in self.history if x.get("pinned")]
        self.storage.save(self.history)
        
    def _delete_physical_file(self, item):
        if item.get("type") == "image":
            path = item.get("content")
            if path and os.path.exists(path) and "data" in path and "images" in path:
                try:
                    os.remove(path)
                except Exception:
                    pass
                    
    def toggle_pin(self, item_id):
        for x in self.history:
            if x.get("id") == item_id:
                x["pinned"] = not x.get("pinned", False)
                break
        self.storage.save(self.history)

    def get_history(self):
        return self.history
