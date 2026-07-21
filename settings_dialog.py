import os
import sys

from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QLineEdit, QPushButton, QCheckBox, QFileDialog, QFrame,
    QGridLayout
)
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QLinearGradient

from config import Config
from autostart import enable as autostart_enable, disable as autostart_disable


STYLE_DIALOG = """
QDialog {
    background: rgba(245, 245, 248, 0.98);
}
QLabel {
    color: rgba(40, 40, 50, 0.8);
    font-size: 12px;
    background: transparent;
    border: none;
}
QLabel#title {
    color: rgba(30, 30, 40, 0.9);
    font-size: 14px;
    font-weight: bold;
}
QLabel#hint {
    color: rgba(80, 80, 90, 0.4);
    font-size: 10px;
}
QSpinBox, QLineEdit {
    background: rgba(255, 255, 255, 0.7);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 6px;
    padding: 6px 10px;
    color: rgba(30, 30, 40, 0.9);
    font-size: 12px;
    selection-background-color: rgba(100, 180, 255, 0.25);
}
QSpinBox:focus, QLineEdit:focus {
    border: 1px solid rgba(80, 160, 255, 0.5);
}
QCheckBox {
    color: rgba(40, 40, 50, 0.8);
    font-size: 12px;
    spacing: 8px;
    background: transparent;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1.5px solid rgba(0, 0, 0, 0.15);
    background: rgba(255, 255, 255, 0.6);
}
QCheckBox::indicator:checked {
    border: 1.5px solid rgba(80, 160, 255, 0.7);
    background: rgba(100, 180, 255, 0.2);
}
QPushButton {
    background: rgba(255, 255, 255, 0.6);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 6px;
    padding: 7px 18px;
    color: rgba(40, 40, 50, 0.75);
    font-size: 12px;
}
QPushButton:hover {
    background: rgba(100, 180, 255, 0.1);
    border: 1px solid rgba(80, 160, 255, 0.3);
    color: rgba(30, 30, 40, 0.9);
}
QPushButton#primary {
    background: rgba(80, 160, 255, 0.15);
    border: 1px solid rgba(80, 160, 255, 0.3);
    color: rgba(30, 60, 120, 0.85);
}
QPushButton#primary:hover {
    background: rgba(80, 160, 255, 0.25);
}
"""

RADIUS = 14


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setWindowFlags(
            Qt.Dialog |
            Qt.FramelessWindowHint |
            Qt.WindowCloseButtonHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(360, 340)
        self.setStyleSheet(STYLE_DIALOG)

        self._cfg = Config.instance()
        self._build_ui()
        self._load_values()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(0)

        container = QFrame()
        container.setObjectName("container")
        container.setStyleSheet("""
            QFrame#container {
                background: rgba(248, 248, 252, 0.97);
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.06);
            }
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        title = QLabel("设置")
        title.setObjectName("title")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(1, 1)

        row = 0

        label_max = QLabel("最大储存条数")
        grid.addWidget(label_max, row, 0)
        self.spin_max = QSpinBox()
        self.spin_max.setRange(10, 10000)
        self.spin_max.setSingleStep(50)
        self.spin_max.setFixedWidth(120)
        grid.addWidget(self.spin_max, row, 1, 1, 2)
        row += 1

        label_dir = QLabel("储存位置")
        grid.addWidget(label_dir, row, 0)
        dir_row = QHBoxLayout()
        dir_row.setSpacing(6)
        self.edit_dir = QLineEdit()
        self.edit_dir.setReadOnly(False)
        self.btn_browse = QPushButton("浏览")
        self.btn_browse.setFixedWidth(60)
        self.btn_browse.clicked.connect(self._on_browse)
        dir_row.addWidget(self.edit_dir)
        dir_row.addWidget(self.btn_browse)
        grid.addLayout(dir_row, row, 1, 1, 2)
        row += 1

        hint = QLabel("更改储存位置后需重启程序生效")
        hint.setObjectName("hint")
        grid.addWidget(hint, row, 1, 1, 2)
        row += 1

        layout.addLayout(grid)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: rgba(0,0,0,0.06); background: rgba(0,0,0,0.06); max-height: 1px; border: none;")
        layout.addWidget(sep)

        self.chk_autostart = QCheckBox("开机自启动")
        layout.addWidget(self.chk_autostart)

        self.chk_close = QCheckBox("显示关闭按钮（点击退出程序）")
        layout.addWidget(self.chk_close)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_save = QPushButton("保存")
        self.btn_save.setObjectName("primary")
        self.btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_save)
        layout.addLayout(btn_row)

        outer.addWidget(container)

    def _load_values(self):
        self.spin_max.setValue(self._cfg.get("max_items", 200))
        self.edit_dir.setText(self._cfg.get("storage_dir", ""))
        self.chk_autostart.setChecked(self._cfg.get("autostart", True))
        self.chk_close.setChecked(self._cfg.get("show_close", False))

    def _on_browse(self):
        cur = self.edit_dir.text() or os.path.expanduser("~")
        path = QFileDialog.getExistingDirectory(self, "选择储存位置", cur)
        if path:
            self.edit_dir.setText(path)

    def _on_save(self):
        old_autostart = self._cfg.get("autostart", True)
        new_autostart = self.chk_autostart.isChecked()
        self._cfg.set("max_items", self.spin_max.value())
        self._cfg.set("storage_dir", self.edit_dir.text().strip())
        self._cfg.set("autostart", new_autostart)
        self._cfg.set("show_close", self.chk_close.isChecked())
        self._cfg.save()
        if new_autostart != old_autostart:
            if new_autostart:
                autostart_enable()
            else:
                autostart_disable()
        self.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h), RADIUS, RADIUS)
        painter.setClipPath(path)
        painter.fillRect(QRectF(0, 0, w, h), QColor(235, 235, 240, 30))
        painter.setPen(QPen(QColor(0, 0, 0, 15), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(QRectF(0.5, 0.5, w - 1, h - 1), RADIUS, RADIUS)
        painter.end()
