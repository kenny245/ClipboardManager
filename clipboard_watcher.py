from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication


class ClipboardWatcher(QObject):
    new_clipboard = Signal(str, object)  # (type, data) type: "text"

    def __init__(self, app=None):
        super().__init__()
        self._app = app or QApplication.instance()
        self._last_text = ""
        self._clip = self._app.clipboard()
        self._clip.dataChanged.connect(self._on_changed)

    def _on_changed(self):
        text = self._clip.text()
        if not text or not text.strip():
            return
        if text == self._last_text:
            return
        self._last_text = text
        self.new_clipboard.emit("text", text)

    def set_text(self, text):
        self._last_text = text
        self._clip.setText(text)
