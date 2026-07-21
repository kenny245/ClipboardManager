import json
import os
import sys
import uuid
import time
from datetime import datetime

if sys.platform == "win32":
    DEFAULT_DIR = r"D:\剪贴板"
    FALLBACK_DIR = os.path.join(os.environ.get("APPDATA", ""), "ClipboardManager")
elif sys.platform == "darwin":
    DEFAULT_DIR = os.path.expanduser("~/Documents/ClipboardManager")
    FALLBACK_DIR = os.path.expanduser("~/.clipboard-manager")
else:
    DEFAULT_DIR = os.path.expanduser("~/.clipboard-manager")
    FALLBACK_DIR = "/tmp/clipboard-manager"

HISTORY_FILE = "history.json"
IMAGES_SUBDIR = "images"
MAX_ITEMS = 200
PREVIEW_LEN = 80


class HistoryStore:
    def __init__(self, base_dir=None, max_items=None):
        if base_dir is None:
            base_dir = DEFAULT_DIR
        if not self._ensure_writable(base_dir):
            base_dir = FALLBACK_DIR
            self._ensure_writable(base_dir)
        self.base_dir = base_dir
        self.history_path = os.path.join(base_dir, HISTORY_FILE)
        self.images_dir = os.path.join(base_dir, IMAGES_SUBDIR)
        self._max_items = max_items if max_items else MAX_ITEMS
        self._items = []
        self._load()

    def _ensure_writable(self, path):
        try:
            os.makedirs(path, exist_ok=True)
            test = os.path.join(path, ".write_test")
            with open(test, "w") as f:
                f.write("ok")
            os.remove(test)
            return True
        except Exception:
            return False

    def _load(self):
        if not os.path.exists(self.history_path):
            self._items = []
            return
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                self._items = json.load(f)
            if not isinstance(self._items, list):
                raise ValueError("not a list")
        except Exception:
            corrupt = self.history_path + ".corrupt"
            try:
                os.replace(self.history_path, corrupt)
            except Exception:
                pass
            self._items = []

    def _save(self):
        try:
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(self._items, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _make_preview(self, text):
        preview = text.replace("\n", " ").replace("\r", " ")
        if len(preview) > PREVIEW_LEN:
            return preview[:PREVIEW_LEN] + "..."
        return preview

    def add_text(self, text):
        if not text or not text.strip():
            return None
        if self._items and self._items[-1].get("text") == text:
            return None
        item = {
            "id": str(uuid.uuid4()),
            "type": "text",
            "text": text,
            "timestamp": int(time.time()),
            "preview": self._make_preview(text),
        }
        self._items.append(item)
        if len(self._items) > self._max_items:
            self._items = self._items[-self._max_items:]
        self._save()
        return item

    def add_image(self, image):
        from PySide6.QtCore import QByteArray, QBuffer, QIODevice
        from PySide6.QtGui import QImage

        os.makedirs(self.images_dir, exist_ok=True)
        img_id = str(uuid.uuid4())
        filename = f"{img_id}.png"
        filepath = os.path.join(self.images_dir, filename)

        # Save as PNG
        image.save(filepath, "PNG")

        w = image.width()
        h = image.height()

        item = {
            "id": img_id,
            "type": "image",
            "image_file": filename,
            "width": w,
            "height": h,
            "timestamp": int(time.time()),
            "preview": f"图片 {w}x{h}",
        }
        self._items.append(item)
        if len(self._items) > self._max_items:
            removed = self._items[:-self._max_items]
            self._items = self._items[-self._max_items:]
            # Clean up removed image files
            for r in removed:
                if r.get("type") == "image":
                    try:
                        os.remove(os.path.join(self.images_dir, r["image_file"]))
                    except Exception:
                        pass
        self._save()
        return item

    def remove(self, item_id):
        item = None
        for i in self._items:
            if i["id"] == item_id:
                item = i
                break
        self._items = [i for i in self._items if i["id"] != item_id]
        if item and item.get("type") == "image":
            try:
                os.remove(os.path.join(self.images_dir, item["image_file"]))
            except Exception:
                pass
        self._save()

    def clear(self):
        # Clean up image files
        for item in self._items:
            if item.get("type") == "image":
                try:
                    os.remove(os.path.join(self.images_dir, item["image_file"]))
                except Exception:
                    pass
        self._items = []
        self._save()

    def get_all(self):
        return list(reversed(self._items))

    def search(self, query):
        if not query or not query.strip():
            return self.get_all()
        q = query.lower()
        return [i for i in reversed(self._items)
                if i.get("type") == "image" or q in i.get("text", "").lower()]

    def count(self):
        return len(self._items)

    def get_image_path(self, item_id):
        for item in self._items:
            if item["id"] == item_id and item.get("type") == "image":
                return os.path.join(self.images_dir, item["image_file"])
        return None

    def set_max_items(self, max_items):
        self._max_items = max_items
        if len(self._items) > max_items:
            removed = self._items[:-max_items]
            self._items = self._items[-max_items:]
            for r in removed:
                if r.get("type") == "image":
                    try:
                        os.remove(os.path.join(self.images_dir, r["image_file"]))
                    except Exception:
                        pass
            self._save()

    def get_max_items(self):
        return self._max_items

    def format_time(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        now = datetime.now()
        if dt.date() == now.date():
            return f"今天 {dt.strftime('%H:%M')}"
        elif dt.date().strftime("%Y-%m-%d") == (now.replace(day=now.day-1)).strftime("%Y-%m-%d"):
            return f"昨天 {dt.strftime('%H:%M')}"
        else:
            return dt.strftime("%m-%d %H:%M")
