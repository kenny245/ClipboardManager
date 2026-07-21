from PySide6.QtCore import QObject, Signal, QByteArray, QBuffer, QIODevice
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QApplication


class ClipboardWatcher(QObject):
    new_clipboard = Signal(str, object)  # (type, data) type: "text" or "image"

    def __init__(self, app=None):
        super().__init__()
        self._app = app or QApplication.instance()
        self._last_text = ""
        self._last_image_id = ""
        self._clip = self._app.clipboard()
        self._clip.dataChanged.connect(self._on_changed)

    def _on_changed(self):
        # Check for image first
        image = self._clip.image()
        if image and not image.isNull():
            # Generate a simple ID based on image content to detect duplicates
            img_id = f"{image.width()}x{image.height()}_{image.sizeInBytes()}"
            if img_id != self._last_image_id:
                self._last_image_id = img_id
                self._last_text = ""
                self.new_clipboard.emit("image", image)
            return

        # Fallback to text
        text = self._clip.text()
        if not text or not text.strip():
            return
        if text == self._last_text:
            return
        self._last_text = text
        self._last_image_id = ""
        self.new_clipboard.emit("text", text)

    def set_text(self, text):
        self._last_text = text
        self._last_image_id = ""
        self._clip.setText(text)

    def set_image(self, image):
        self._last_image_id = f"{image.width()}x{image.height()}_{image.sizeInBytes()}"
        self._last_text = ""
        self._clip.setPixmap(QPixmap.fromImage(image))
