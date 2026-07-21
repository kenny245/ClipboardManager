import json
import os
import sys
from PySide6.QtCore import Qt, QPoint, QRect, QRectF, QTimer, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup

if sys.platform == "win32":
    POS_FILE = os.path.join(os.environ.get("APPDATA", ""), "ClipboardManager", "window_pos.json")
elif sys.platform == "darwin":
    POS_FILE = os.path.expanduser("~/Library/Application Support/ClipboardManager/window_pos.json")
else:
    POS_FILE = os.path.expanduser("~/.clipboard-manager/window_pos.json")
from PySide6.QtGui import (
    QColor, QPainter, QPainterPath, QPixmap, QRegion,
    QPen, QImage, QBrush, QLinearGradient, QIcon
)
from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QVBoxLayout, QHBoxLayout, QMenu, QApplication, QGraphicsScene,
    QGraphicsPixmapItem, QGraphicsBlurEffect, QDialog
)

from history_store import HistoryStore
from config import Config
from settings_dialog import SettingsDialog

STYLE_LIST = """
QListWidget {
    background: transparent;
    border: none;
    outline: none;
    padding: 4px 0px;
}
QListWidget::item {
    color: rgba(40, 40, 50, 0.65);
    padding: 7px 14px;
    border-left: 2px solid transparent;
    font-size: 11px;
}
QListWidget::item:selected {
    color: rgba(20, 30, 50, 0.95);
    border-left: 2px solid rgba(80, 160, 255, 0.6);
    background: rgba(100, 180, 255, 0.12);
}
QListWidget::item:hover {
    background: rgba(0, 0, 0, 0.03);
}
QScrollBar:vertical {
    background: transparent;
    width: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(0, 0, 0, 0.12);
    border-radius: 2px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
    background: none;
    border: none;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""

STYLE_INPUT = """
QLineEdit {
    background: transparent;
    border: none;
    color: rgba(30, 30, 40, 0.9);
    font-size: 12px;
    selection-background-color: rgba(100, 180, 255, 0.25);
}
QLineEdit::placeholder {
    color: rgba(80, 80, 90, 0.4);
}
"""

STYLE_HANDLE = """
QLabel {
    color: rgba(80, 80, 90, 0.3);
    font-size: 13px;
    border: none;
    background: transparent;
}
"""

STYLE_TOGGLE = """
QPushButton {
    color: rgba(80, 80, 90, 0.35);
    border: none;
    background: transparent;
    font-size: 12px;
    padding: 0px;
}
QPushButton:hover {
    color: rgba(80, 160, 255, 0.7);
}
"""

STYLE_GEAR = """
QPushButton {
    color: rgba(80, 80, 90, 0.3);
    border: none;
    background: transparent;
    font-size: 12px;
    padding: 0px;
}
QPushButton:hover {
    color: rgba(80, 160, 255, 0.7);
}
"""

STYLE_CLOSE = """
QPushButton {
    color: rgba(80, 80, 90, 0.3);
    border: none;
    background: transparent;
    font-size: 12px;
    padding: 0px;
}
QPushButton:hover {
    color: rgba(255, 80, 80, 0.7);
}
"""

STYLE_STATUS = """
QLabel {
    color: rgba(80, 80, 90, 0.3);
    font-size: 9px;
    border: none;
    background: transparent;
    padding: 0 14px;
}
"""

STYLE_SEARCH_ROW = "QWidget { background: transparent; border: none; }"

STYLE_MENU = """
QMenu {
    background: rgba(250, 250, 252, 0.95);
    color: rgba(30, 30, 40, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 6px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
    border-radius: 4px;
}
QMenu::item:selected {
    background: rgba(100, 180, 255, 0.12);
}
"""


def blur_pixmap(pixmap, radius=25):
    if pixmap.isNull():
        return pixmap
    scene = QGraphicsScene()
    item = QGraphicsPixmapItem(pixmap)
    blur = QGraphicsBlurEffect()
    blur.setBlurRadius(radius)
    blur.setBlurHints(QGraphicsBlurEffect.QualityHint)
    item.setGraphicsEffect(blur)
    scene.addItem(item)
    img = QImage(pixmap.size(), QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    p = QPainter(img)
    scene.render(p)
    p.end()
    return QPixmap.fromImage(img)


def make_rounded_region(w, h, radius):
    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, w, h), radius, radius)
    region = QRegion()
    for poly in path.toFillPolygons():
        region = region.united(QRegion(poly.toPolygon()))
    return region


class DragHandle(QLabel):
    def __init__(self, parent=None):
        super().__init__("⠿", parent)
        self.setFixedWidth(20)
        self.setAlignment(Qt.AlignCenter)
        self.setCursor(Qt.SizeAllCursor)
        self.setStyleSheet(STYLE_HANDLE)


class SearchWindow(QWidget):
    COLLAPSED_W = 300
    COLLAPSED_H = 36
    LIST_MAX_H = 280
    STATUS_H = 24
    RADIUS = 14
    SHADOW = 2  # minimal margin, no shadow

    def __init__(self, store: HistoryStore, watcher=None):
        super().__init__()
        self.store = store
        self.watcher = watcher
        self._dragging = False
        self._drag_offset = QPoint()
        self._expanded = False
        self._filter_items = []
        self._blurred_bg = None
        self._blur_timer = None
        self._anim_group = None

        self._init_ui()
        self._load_position()

    def _init_ui(self):
        self.setObjectName("main")
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        s = self.SHADOW
        self.setFixedWidth(self.COLLAPSED_W + s * 2)
        self.setFixedHeight(self.COLLAPSED_H + s * 2)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(s, s, s, s)
        layout.setSpacing(0)

        search_row = QWidget()
        search_row.setFixedHeight(self.COLLAPSED_H)
        search_row.setStyleSheet(STYLE_SEARCH_ROW)
        row_layout = QHBoxLayout(search_row)
        row_layout.setContentsMargins(12, 0, 8, 0)
        row_layout.setSpacing(6)

        self.handle = DragHandle()
        self.input = QLineEdit()
        self.input.setPlaceholderText("搜索剪贴板历史...")
        self.input.setStyleSheet(STYLE_INPUT)
        self.input.textChanged.connect(self._on_search_changed)
        self.input.returnPressed.connect(self._on_enter)

        self.toggle_btn = QPushButton("▾")
        self.toggle_btn.setFixedSize(20, 20)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setStyleSheet(STYLE_TOGGLE)
        self.toggle_btn.clicked.connect(self._toggle_expand)

        row_layout.addWidget(self.handle)
        row_layout.addWidget(self.input)
        row_layout.addWidget(self.toggle_btn)
        layout.addWidget(search_row)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(STYLE_LIST)
        self.list_widget.setMaximumHeight(0)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._on_right_click)
        self.list_widget.setFrameShape(QListWidget.NoFrame)
        self.list_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.list_widget)

        self.status_row = QWidget()
        self.status_row.setMaximumHeight(0)
        self.status_row.setMinimumHeight(0)
        self.status_row.setStyleSheet("QWidget { background: transparent; border: none; }")
        status_layout = QHBoxLayout(self.status_row)
        status_layout.setContentsMargins(14, 0, 10, 0)
        status_layout.setSpacing(6)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.setStyleSheet(STYLE_STATUS)
        status_layout.addWidget(self.status_label, 1)

        self.gear_btn = QPushButton("⚙")
        self.gear_btn.setFixedSize(20, 20)
        self.gear_btn.setCursor(Qt.PointingHandCursor)
        self.gear_btn.setStyleSheet(STYLE_GEAR)
        self.gear_btn.clicked.connect(self._on_settings)
        status_layout.addWidget(self.gear_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(0, 20)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet(STYLE_CLOSE)
        self.close_btn.clicked.connect(self._on_close_app)
        self.close_btn.setVisible(False)
        status_layout.addWidget(self.close_btn)

        layout.addWidget(self.status_row)

        self._apply_region()
        self._update_status()

        # Capture background after window is shown
        QTimer.singleShot(100, self._capture_blur)

    def _capture_blur(self):
        screen = QApplication.primaryScreen()
        if not screen:
            return
        s = self.SHADOW
        geo = self.geometry()
        screen_geo = screen.geometry()
        x = geo.x() + s - screen_geo.x()
        y = geo.y() + s - screen_geo.y()
        w = self.width() - s * 2
        h = self.height() - s * 2
        if w <= 0 or h <= 0:
            return
        full = screen.grabWindow(0, x, y, w, h)
        if full.isNull():
            return
        self._blurred_bg = blur_pixmap(full, radius=30)
        self.update()

    def _schedule_capture(self):
        if self._blur_timer:
            self._blur_timer.stop()
        self._blur_timer = QTimer(self)
        self._blur_timer.setSingleShot(True)
        self._blur_timer.timeout.connect(self._capture_blur)
        self._blur_timer.start(150)

    def _apply_region(self):
        pass  # paintEvent handles clipping; no mask needed

    def _load_position(self):
        s = self.SHADOW
        try:
            if os.path.exists(POS_FILE):
                with open(POS_FILE, "r") as f:
                    pos = json.load(f)
                    self.move(pos.get("x", 100) - s, pos.get("y", 100) - s)
            else:
                screen = QApplication.primaryScreen().geometry()
                self.move(screen.width() - 360 - s, screen.height() - 120 - s)
        except Exception:
            self.move(100, 100)

    def _save_position(self):
        s = self.SHADOW
        try:
            os.makedirs(os.path.dirname(POS_FILE), exist_ok=True)
            with open(POS_FILE, "w") as f:
                json.dump({"x": self.x() + s, "y": self.y() + s}, f)
        except Exception:
            pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        s = self.SHADOW
        w = self.width()
        h = self.height()
        r = self.RADIUS

        cx = s
        cy = s
        cw = w - s * 2
        ch = h - s * 2

        content_path = QPainterPath()
        content_path.addRoundedRect(QRectF(cx, cy, cw, ch), r, r)

        # === 1. Content area ===
        painter.save()
        painter.setClipPath(content_path)

        # 1a. Blurred background capture
        if self._blurred_bg and not self._blurred_bg.isNull():
            painter.drawPixmap(cx, cy, self._blurred_bg)
        else:
            painter.fillRect(QRectF(cx, cy, cw, ch), QColor(240, 240, 245, 200))

        # 1b. Translucent white frost overlay (lowered opacity)
        painter.fillRect(QRectF(cx, cy, cw, ch), QColor(255, 255, 255, 65))

        # 1c. Top highlight gradient — light from above
        top_grad = QLinearGradient(0, cy, 0, cy + ch * 0.4)
        top_grad.setColorAt(0, QColor(255, 255, 255, 50))
        top_grad.setColorAt(1, QColor(255, 255, 255, 0))
        painter.fillRect(QRectF(cx, cy, cw, ch), top_grad)

        # 1d. Inner glow on edges
        inner_path = QPainterPath()
        inner_path.addRoundedRect(QRectF(cx + 1, cy + 1, cw - 2, ch - 2), r - 1, r - 1)
        painter.setPen(QPen(QColor(255, 255, 255, 45), 1.5))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(inner_path)

        painter.restore()

        # === 2. Outer border ===
        painter.setPen(QPen(QColor(0, 0, 0, 18), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(QRectF(cx + 0.5, cy + 0.5, cw - 1, ch - 1), r, r)

        # === 3. Top edge specular highlight ===
        top_edge = QPainterPath()
        top_edge.moveTo(cx + r, cy + 1)
        top_edge.lineTo(cx + cw - r, cy + 1)
        painter.setPen(QPen(QColor(255, 255, 255, 80), 1))
        painter.drawPath(top_edge)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            widget = self.childAt(event.pos())
            if isinstance(widget, DragHandle):
                self._dragging = True
                self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self._dragging:
            self._dragging = False
            self._save_position()
            self._schedule_capture()
            event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_region()
        self._schedule_capture()

    def _toggle_expand(self):
        if self._expanded:
            self._collapse()
        else:
            self._expand()

    def _expand(self):
        if self._expanded:
            return
        self._expanded = True
        self.toggle_btn.setText("▴")
        self._refresh_list()
        self._animate_height(True)

    def _collapse(self):
        if not self._expanded:
            return
        self._expanded = False
        self.toggle_btn.setText("▾")
        self._animate_height(False)

    def _animate_height(self, expanding):
        if self._anim_group:
            self._anim_group.stop()

        s = self.SHADOW
        collapsed_h = self.COLLAPSED_H + s * 2
        expanded_h = self.COLLAPSED_H + self.LIST_MAX_H + self.STATUS_H + s * 2

        if expanding:
            win_start, win_end = collapsed_h, expanded_h
            list_start, list_end = 0, self.LIST_MAX_H
            status_start, status_end = 0, self.STATUS_H
            easing = QEasingCurve.OutCubic
        else:
            win_start, win_end = expanded_h, collapsed_h
            list_start, list_end = self.LIST_MAX_H, 0
            status_start, status_end = self.STATUS_H, 0
            easing = QEasingCurve.InCubic

        duration = 280
        group = QParallelAnimationGroup(self)

        anim_min = QPropertyAnimation(self, b"minimumHeight", self)
        anim_min.setDuration(duration)
        anim_min.setStartValue(win_start)
        anim_min.setEndValue(win_end)
        anim_min.setEasingCurve(easing)

        anim_max = QPropertyAnimation(self, b"maximumHeight", self)
        anim_max.setDuration(duration)
        anim_max.setStartValue(win_start)
        anim_max.setEndValue(win_end)
        anim_max.setEasingCurve(easing)
        anim_max.valueChanged.connect(self._schedule_capture)

        anim_list = QPropertyAnimation(self.list_widget, b"maximumHeight", self)
        anim_list.setDuration(duration)
        anim_list.setStartValue(list_start)
        anim_list.setEndValue(list_end)
        anim_list.setEasingCurve(easing)

        anim_status = QPropertyAnimation(self.status_row, b"maximumHeight", self)
        anim_status.setDuration(duration)
        anim_status.setStartValue(status_start)
        anim_status.setEndValue(status_end)
        anim_status.setEasingCurve(easing)

        group.addAnimation(anim_min)
        group.addAnimation(anim_max)
        group.addAnimation(anim_list)
        group.addAnimation(anim_status)
        group.finished.connect(self._schedule_capture)

        self._anim_group = group
        group.start()

    def _on_search_changed(self, text):
        if not self._expanded:
            self._expand()
        self._refresh_list()

    def _refresh_list(self):
        query = self.input.text().strip()
        items = self.store.search(query) if query else self.store.get_all()
        self._filter_items = items
        self.list_widget.clear()
        for item in items:
            if item.get("type") == "image":
                li = self._make_image_item(item)
            else:
                li = QListWidgetItem(item.get("preview", ""))
            li.setData(Qt.UserRole, item)
            self.list_widget.addItem(li)
            # If image item has a pending widget, attach it now
            widget_data = li.data(Qt.UserRole + 1)
            if widget_data and isinstance(widget_data, tuple) and widget_data[0] == "__image_widget__":
                self.list_widget.setItemWidget(li, widget_data[1])
        if items:
            self.list_widget.setCurrentRow(0)
        self._update_status()

    def _make_image_item(self, item):
        li = QListWidgetItem()
        # Load thumbnail from file
        img_path = self.store.get_image_path(item["id"])
        thumb = QPixmap(img_path)
        if thumb.isNull():
            li.setText(f"图片 {item.get('width','?')}x{item.get('height','?')} (无法加载)")
            return li

        # Scale to thumbnail height
        THUMB_H = 40
        scaled = thumb.scaledToHeight(THUMB_H, Qt.SmoothTransformation)
        THUMB_W = scaled.width()

        # Build a custom widget with thumbnail + label
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(14, 4, 14, 4)
        row_layout.setSpacing(10)

        thumb_label = QLabel()
        thumb_label.setPixmap(scaled)
        thumb_label.setFixedSize(THUMB_W, THUMB_H)
        row_layout.addWidget(thumb_label)

        info_label = QLabel(f"图片 {item.get('width')}x{item.get('height')}")
        info_label.setStyleSheet("color: rgba(40, 40, 50, 0.65); font-size: 11px; background: transparent; border: none;")
        row_layout.addWidget(info_label, 1)

        li.setSizeHint(row_widget.sizeHint())
        li.setData(Qt.UserRole + 1, ("__image_widget__", row_widget))
        return li

    def _update_status(self):
        total = self.store.count()
        shown = self.list_widget.count()
        query = self.input.text().strip()
        if query:
            self.status_label.setText(f"{shown} / {total} 匹配  ·  Enter恢复  ·  Esc清空")
        else:
            self.status_label.setText(f"{total} 条  ·  点击恢复  ·  右键删除  ·  Ctrl+Shift+V")

    def _on_enter(self):
        row = self.list_widget.currentRow()
        if row >= 0 and row < len(self._filter_items):
            self._restore_item(self._filter_items[row])

    def _on_item_clicked(self, list_item):
        item = list_item.data(Qt.UserRole)
        if item:
            self._restore_item(item)

    def _restore_item(self, item):
        if item.get("type") == "image":
            img_path = self.store.get_image_path(item["id"])
            if img_path and os.path.exists(img_path):
                pixmap = QPixmap(img_path)
                if self.watcher:
                    self.watcher.set_image(pixmap.toImage())
                else:
                    QApplication.clipboard().setPixmap(pixmap)
        else:
            if self.watcher:
                self.watcher.set_text(item.get("text", ""))
            else:
                QApplication.clipboard().setText(item.get("text", ""))
        self.input.clear()
        self._collapse()

    def _on_right_click(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        data = item.data(Qt.UserRole)
        if not data:
            return
        menu = QMenu(self)
        menu.setStyleSheet(STYLE_MENU)
        act_del = menu.addAction("删除")
        act_copy = menu.addAction("恢复到剪贴板")
        chosen = menu.exec(self.list_widget.mapToGlobal(pos))
        if chosen == act_del:
            self.store.remove(data["id"])
            self._refresh_list()
        elif chosen == act_copy:
            self._restore_item(data)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.input.clear()
            self._collapse()
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event):
        self.input.setFocus()
        super().focusInEvent(event)

    def activate_search(self):
        if not self._expanded:
            self._expand()
        self.input.setFocus()
        self.raise_()
        self.activateWindow()

    def deactivate_search(self):
        self.input.clear()
        self._collapse()

    def _set_close_btn_visible(self, visible):
        if visible:
            self.close_btn.setFixedSize(20, 20)
            self.close_btn.setVisible(True)
        else:
            self.close_btn.setFixedSize(0, 20)
            self.close_btn.setVisible(False)
        parent = self.close_btn.parentWidget()
        if parent:
            parent.layout().invalidate()
            parent.layout().activate()
        self.update()

    def _on_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.Accepted:
            cfg = Config.instance()
            self.store.set_max_items(cfg.get("max_items", 200))
            self._set_close_btn_visible(cfg.get("show_close", False))
            self._refresh_list()
            self._update_status()
            app = QApplication.instance()
            if hasattr(app, '_clipboard_app'):
                app._clipboard_app._sync_autostart()

    def _on_close_app(self):
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if hasattr(app, '_clipboard_app'):
            app._clipboard_app._quit()
        else:
            app.quit()

    def refresh_settings(self):
        cfg = Config.instance()
        self._set_close_btn_visible(cfg.get("show_close", False))
