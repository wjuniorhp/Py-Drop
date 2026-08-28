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
        
        # Corrige caminhos absolutos de imagens internas caso o projeto tenha sido movido ou rodado de outro drive (ex: Y:)
        images_dir = self.storage.filepath.parent / "images"
        changed = False
        for item in self.history:
            content = item.get("content")
            if isinstance(content, str) and "data" in content and "images" in content and "image_" in content:
                filename = os.path.basename(content.replace("\\", "/"))
                new_path = str(images_dir / filename)
                if new_path != content:
                    item["content"] = new_path
                    changed = True
            elif isinstance(content, list):
                for i, path in enumerate(content):
                    if isinstance(path, str) and "data" in path and "images" in path and "image_" in path:
                        filename = os.path.basename(path.replace("\\", "/"))
                        new_path = str(images_dir / filename)
                        if new_path != path:
                            content[i] = new_path
                            changed = True
        # Cleanup missing external files so they don't stay crossed-out forever
        valid_history = []
        for item in self.history:
            item_type = item.get("type", "text")
            content = item.get("content")
            
            if item_type in ["file", "image"] and isinstance(content, str):
                if not os.path.exists(content):
                    changed = True
                    continue # Skip this item (it's missing)
            elif item_type == "files" and isinstance(content, list):
                existing_files = [p for p in content if isinstance(p, str) and os.path.exists(p)]
                if len(existing_files) != len(content):
                    changed = True
                    if len(existing_files) == 0:
                        continue # All missing, remove the group
                    elif len(existing_files) == 1:
                        path_str = str(existing_files[0]).replace('\\', '/')
                        if "/images/image_" in path_str and path_str.endswith(".png"):
                            item["type"] = "image"
                        else:
                            item["type"] = "file"
                        item["content"] = existing_files[0]
                    else:
                        item["content"] = existing_files
            valid_history.append(item)
            
        self.history = valid_history

        if changed:
            self.storage.save(self.history)
        # Cleanup orphaned images that might have been left behind due to previous bugs
        if images_dir.exists():
            active_paths = set()
            for item in self.history:
                content = item.get("content")
                if item.get("type") == "image" and isinstance(content, str):
                    active_paths.add(os.path.normcase(os.path.normpath(content)))
                elif item.get("type") == "files" and isinstance(content, list):
                    for p in content:
                        if isinstance(p, str):
                            active_paths.add(os.path.normcase(os.path.normpath(p)))
            
            for f in images_dir.glob("image_*.png"):
                norm_f = os.path.normcase(os.path.normpath(str(f)))
                if norm_f not in active_paths:
                    try:
                        os.remove(f)
                    except Exception:
                        pass
            
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
            text_stripped = text.strip() if isinstance(text, str) else text
            if isinstance(text, str) and os.path.exists(text_stripped):
                mime.setUrls([QUrl.fromLocalFile(text_stripped)])
                if item_type == "image":
                    from PyQt6.QtGui import QImage
                    img = QImage(text_stripped)
                    if not img.isNull():
                        mime.setImageData(img)
            else:
                mime.setText(str(text))
            
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
                self.add_from_text(text, force_type=item_type)

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
            
            formats = mime.formats()
            if "image/png" in formats:
                ext = "png"
                save_fmt = "PNG"
                quality = -1
            elif "image/webp" in formats:
                ext = "webp"
                save_fmt = "WEBP"
                quality = -1
            else:
                ext = "jpg"
                save_fmt = "JPEG"
                quality = 95
                
            img_path = images_dir / f"image_{int(time.time()*1000)}.{ext}"
            if img.save(str(img_path), save_fmt, quality):
                return str(img_path)
        return None

    def _process_clipboard(self):
        if self.is_paused:
            return
            
        clipboard = QGuiApplication.clipboard()
        mime = clipboard.mimeData()
        
        current_text = ""
        current_list = None
        current_type = None
        
        # Ignora imagens geradas pelo próprio Py-Drop sendo copiadas (evita duplicações)
        if mime.hasUrls() and mime.urls():
            local_files = [u.toLocalFile() for u in mime.urls() if u.isLocalFile()]
            if len(local_files) == 1:
                path_str = local_files[0].replace('\\', '/')
                if "/images/image_" in path_str and path_str.endswith(".png"):
                    self.last_content = os.path.normcase(os.path.normpath(local_files[0]))
                    return
        
        if mime.hasImage():
            img = mime.imageData()
            # Ignora imagens muito pequenas (como imagens transparentes 1x1 colocadas por alguns editores de texto na área de transferência)
            if img and not img.isNull() and img.width() > 5 and img.height() > 5:
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
                    current_type = "file"
                else:
                    current_list = local_files
        
        if not current_list and not current_text:
            if mime.hasText():
                raw_text = mime.text()
                if raw_text.strip():
                    current_text = raw_text
                    current_type = "text"
            elif mime.hasUrls() and mime.urls():
                current_text = mime.urls()[0].toString()
                current_type = "text"
            
        if current_list:
            norm_list = [os.path.normcase(os.path.normpath(p)) for p in current_list]
            if norm_list == self.last_content:
                return
            self.last_content = norm_list
            self.add_from_files(current_list)
        else:
            norm_text = os.path.normcase(os.path.normpath(current_text)) if (current_type == "file" or os.path.exists(current_text)) else current_text
            if not current_text or norm_text == self.last_content:
                return
            self.last_content = norm_text
            self.add_from_text(current_text, force_type=current_type)
            
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
        
    def add_from_text(self, current_text, force_type=None):
        if force_type:
            item_type = force_type
            if force_type == "text" and (re.match(r'^https?://', current_text) or re.match(r'^www\.', current_text)):
                item_type = "link"
        else:
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
        max_items = self.config.get("max_history_items", 100)
        if len(self.history) > max_items and unpinned:
            oldest_unpinned = unpinned[-1]
            self._delete_physical_file(oldest_unpinned)
            self.history.remove(oldest_unpinned)

        self.storage.save(self.history)
        self.new_item.emit(item)
            
    def move_to_top(self, item_id):
        import time
        for i, item in enumerate(self.history):
            if item.get("id") == item_id:
                item["timestamp"] = time.time()
                self.history.pop(i)
                self.history.insert(0, item)
                self.storage.save(self.history)
                return item
        return None

    def remove_item(self, item_id):
        for x in self.history:
            if x.get("id") == item_id:
                self._delete_physical_file(x)
                break
                
        self.history = [x for x in self.history if x.get("id") != item_id]
        self.storage.save(self.history)
        
    def update_item(self, item_id, updates):
        for x in self.history:
            if x.get("id") == item_id:
                x.update(updates)
                break
        self.storage.save(self.history)
        
    def remove_file_from_group(self, group_id, file_path, delete_physical=False):
        for x in self.history:
            if x.get("id") == group_id and x.get("type") == "files":
                content = x.get("content", [])
                
                norm_file_path = os.path.normcase(os.path.normpath(file_path))
                norm_content = [os.path.normcase(os.path.normpath(p)) for p in content]
                
                if norm_file_path in norm_content:
                    idx = norm_content.index(norm_file_path)
                    original_path = content[idx]
                    content.pop(idx)
                    
                    if delete_physical:
                        # Check if it was an internal image and delete it
                        path_str = str(original_path).replace('\\', '/')
                        if os.path.exists(original_path) and "/images/image_" in path_str and path_str.endswith(".png"):
                            try:
                                os.remove(original_path)
                            except Exception:
                                pass
                                
                if len(content) == 1:
                    path_str = str(content[0]).replace('\\', '/')
                    if "/images/image_" in path_str and path_str.endswith(".png"):
                        x["type"] = "image"
                    else:
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
        paths_to_check = []
        if item.get("type") == "image":
            paths_to_check.append(item.get("content"))
        elif item.get("type") == "files":
            content = item.get("content")
            if isinstance(content, list):
                paths_to_check.extend(content)
                
        for path in paths_to_check:
            if not path:
                continue
            path_str = str(path).replace('\\', '/')
            if os.path.exists(path) and "/images/image_" in path_str and path_str.endswith(".png"):
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
