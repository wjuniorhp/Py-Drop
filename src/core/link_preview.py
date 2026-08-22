import os
import re
import urllib.request
from PyQt6.QtCore import QThread, pyqtSignal

class LinkPreviewWorker(QThread):
    preview_ready = pyqtSignal(dict)
    
    def __init__(self, url, item_id, cache_dir):
        super().__init__()
        self.url = url
        self.item_id = item_id
        self.cache_dir = cache_dir
        
    def run(self):
        try:
            req = urllib.request.Request(self.url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            with urllib.request.urlopen(req, timeout=3) as response:
                html = response.read().decode('utf-8', errors='ignore')
                
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else ""
            
            og_image_match = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
            if not og_image_match:
                og_image_match = re.search(r'<meta[^>]*content=["\'](.*?)["\'][^>]*property=["\']og:image["\']', html, re.IGNORECASE)
                
            image_url = og_image_match.group(1).strip() if og_image_match else ""
            
            image_path = ""
            if image_url:
                if not image_url.startswith('http'):
                    from urllib.parse import urljoin
                    image_url = urljoin(self.url, image_url)
                    
                import hashlib
                ext = image_url.split('.')[-1].split('?')[0]
                if ext not in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                    ext = 'jpg'
                
                hash_name = hashlib.md5(image_url.encode()).hexdigest()
                
                os.makedirs(self.cache_dir, exist_ok=True)
                image_path = os.path.join(self.cache_dir, f"{hash_name}.{ext}")
                image_path = os.path.normpath(image_path).replace('\\', '/')
                
                if not os.path.exists(image_path):
                    img_req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(img_req, timeout=3) as img_resp:
                        with open(image_path, 'wb') as f:
                            f.write(img_resp.read())
                            
            if title or image_path:
                self.preview_ready.emit({
                    "item_id": self.item_id,
                    "title": title,
                    "image": image_path
                })
        except Exception as e:
            pass
