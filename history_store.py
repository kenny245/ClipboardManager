import json
import os
import sys
import uuid
import time
from datetime import datetime, timedelta

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
LEGACY_IMAGES_SUBDIR = "images"
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
            return
        self._drop_legacy_images()

    def _drop_legacy_images(self):
        """One-time migration: image recording has been removed.
        Purge legacy image records and their cached PNG files."""
        legacy = [i for i in self._items if i.get("type") == "image"]
        if not legacy:
            return
        images_dir = os.path.join(self.base_dir, LEGACY_IMAGES_SUBDIR)
        for item in legacy:
            fname = item.get("image_file")
            if not fname:
                continue
            try:
                os.remove(os.path.join(images_dir, fname))
            except Exception:
                pass
        self._items = [i for i in self._items if i.get("type") != "image"]
        try:
            if os.path.isdir(images_dir) and not os.listdir(images_dir):
                os.rmdir(images_dir)
        except Exception:
            pass
        self._save()

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

    def remove(self, item_id):
        self._items = [i for i in self._items if i["id"] != item_id]
        self._save()

    def clear(self):
        self._items = []
        self._save()

    def get_all(self):
        return list(reversed(self._items))

    def search(self, query):
        if not query or not query.strip():
            return self.get_all()
        q = query.lower()
        return [i for i in reversed(self._items)
                if q in i.get("text", "").lower()]

    def count(self):
        return len(self._items)

    def set_max_items(self, max_items):
        self._max_items = max_items
        if len(self._items) > max_items:
            self._items = self._items[-max_items:]
            self._save()

    def get_max_items(self):
        return self._max_items

    def format_time(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        now = datetime.now()
        if dt.date() == now.date():
            return f"今天 {dt.strftime('%H:%M')}"
        elif dt.date() == (now - timedelta(days=1)).date():
            return f"昨天 {dt.strftime('%H:%M')}"
        else:
            return dt.strftime("%m-%d %H:%M")
