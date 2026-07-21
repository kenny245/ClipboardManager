import json
import os
import sys

if sys.platform == "win32":
    DEFAULT_DIR = r"D:\剪贴板"
    CONFIG_DIR = os.path.join(os.environ.get("APPDATA", ""), "ClipboardManager")
elif sys.platform == "darwin":
    DEFAULT_DIR = os.path.expanduser("~/Documents/ClipboardManager")
    CONFIG_DIR = os.path.expanduser("~/Library/Application Support/ClipboardManager")
else:
    DEFAULT_DIR = os.path.expanduser("~/.clipboard-manager")
    CONFIG_DIR = os.path.expanduser("~/.clipboard-manager")

CONFIG_FILE = "config.json"

DEFAULTS = {
    "max_items": 200,
    "storage_dir": DEFAULT_DIR,
    "autostart": True,
    "show_close": False,
}


class Config:
    _instance = None

    def __init__(self):
        self._data = dict(DEFAULTS)
        self._ensure_dir()
        self._load()

    def _ensure_dir(self):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
        except Exception:
            pass

    @property
    def path(self):
        return os.path.join(CONFIG_DIR, CONFIG_FILE)

    def _load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                for k in DEFAULTS:
                    if k in saved:
                        self._data[k] = saved[k]
        except Exception:
            pass

    def save(self):
        try:
            self._ensure_dir()
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def get(self, key, fallback=None):
        return self._data.get(key, fallback if fallback is not None else DEFAULTS.get(key))

    def set(self, key, value):
        self._data[key] = value

    def to_dict(self):
        return dict(self._data)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = Config()
        return cls._instance
