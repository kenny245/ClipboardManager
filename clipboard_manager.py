import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PySide6.QtCore import QObject, Qt, Signal

from history_store import HistoryStore
from clipboard_watcher import ClipboardWatcher
from search_window import SearchWindow
from global_hotkey import GlobalHotkey, MOD_CONTROL, MOD_SHIFT, VK_V
from autostart import enable as autostart_enable, disable as autostart_disable, is_enabled as autostart_is_enabled
from config import Config, DEFAULT_DIR

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"


def make_tray_icon():
    pix = QPixmap(64, 64)
    pix.fill(QColor(0, 0, 0, 0))
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(100, 200, 255, 200))
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(12, 18, 40, 40, 6, 6)
    p.setBrush(QColor(255, 255, 255, 230))
    p.drawRoundedRect(18, 24, 28, 4, 2, 2)
    p.drawRoundedRect(18, 32, 28, 4, 2, 2)
    p.drawRoundedRect(18, 40, 20, 4, 2, 2)
    p.setBrush(QColor(80, 160, 220, 200))
    p.drawRoundedRect(22, 12, 20, 10, 3, 3)
    p.end()
    return QIcon(pix)


class App(QObject):
    # 热键回调来自后台消息线程，通过 Qt 信号自动排队转发到主线程，
    # 避免在非 GUI 线程中直接操作窗口控件
    _hotkey_triggered = Signal()

    def __init__(self):
        super().__init__()
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.app.setApplicationName("静默剪贴板管理器")
        self.app.setQuitOnLastWindowClosed(False)

        if IS_MAC:
            self.app.setQuitOnLastWindowClosed(True)

        self.cfg = Config.instance()

        self.store = HistoryStore(self.cfg.get("storage_dir") or DEFAULT_DIR,
                                  max_items=self.cfg.get("max_items", 200))
        self.watcher = ClipboardWatcher(self.app)
        self.watcher.new_clipboard.connect(self._on_new_clip)

        self.window = SearchWindow(self.store, self.watcher)
        self.window.show()
        self.window.refresh_settings()

        app = QApplication.instance()
        app._clipboard_app = self

        self._setup_tray()
        self._setup_hotkey()

        if self.cfg.get("autostart", True) and not autostart_is_enabled():
            autostart_enable()
        elif not self.cfg.get("autostart", True) and autostart_is_enabled():
            autostart_disable()

    def _on_new_clip(self, clip_type, data):
        self.store.add_text(data)
        if self.window._expanded:
            self.window._refresh_list()

    def _setup_tray(self):
        self.tray = QSystemTrayIcon(make_tray_icon(), self.app)
        self.tray.setToolTip("静默剪贴板管理器")

        menu = QMenu()
        act_show = QAction("显示/隐藏搜索框", menu)
        act_show.triggered.connect(self._toggle_window)
        menu.addAction(act_show)

        act_clear = QAction("清空全部历史", menu)
        act_clear.triggered.connect(self._clear_history)
        menu.addAction(act_clear)

        menu.addSeparator()

        self.act_autostart = QAction("开机自启动", menu)
        self.act_autostart.setCheckable(True)
        self.act_autostart.setChecked(autostart_is_enabled())
        self.act_autostart.triggered.connect(self._toggle_autostart)
        menu.addAction(self.act_autostart)

        menu.addSeparator()

        act_quit = QAction("退出", menu)
        act_quit.triggered.connect(self._quit)
        menu.addAction(act_quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _toggle_window(self):
        if self.window.isVisible():
            self.window.hide()
        else:
            self.window.show()
            self.window.activate_search()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.window.show()
            self.window.activate_search()

    def _clear_history(self):
        reply = QMessageBox.question(
            None, "确认", "确定清空全部剪贴板历史？此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.store.clear()
            if self.window._expanded:
                self.window._refresh_list()
            self.tray.showMessage("已清空", "剪贴板历史已全部清除", QSystemTrayIcon.Information, 2000)

    def _toggle_autostart(self):
        if self.act_autostart.isChecked():
            ok = autostart_enable()
            msg = "开机将自动启动" if ok else "设置失败，请手动添加"
        else:
            ok = autostart_disable()
            msg = "开机自启动已关闭" if ok else "取消失败，请手动移除"
        self.cfg.set("autostart", self.act_autostart.isChecked())
        self.cfg.save()
        self.tray.showMessage("自启动", msg, QSystemTrayIcon.Information, 2000)

    def _sync_autostart(self):
        self.act_autostart.setChecked(autostart_is_enabled())

    def _setup_hotkey(self):
        self.hotkey = GlobalHotkey()
        self._hotkey_triggered.connect(self._on_hotkey)
        self.hotkey.register(VK_V, MOD_CONTROL | MOD_SHIFT, self._hotkey_triggered.emit)

    def _on_hotkey(self):
        if self.window._expanded and self.window.input.hasFocus():
            self.window.deactivate_search()
        else:
            self.window.show()
            self.window.activate_search()

    def _quit(self):
        self.hotkey.stop()
        try:
            self.store.flush()  # 落盘防抖窗口内尚未写入的历史
        except Exception:
            pass
        self.tray.hide()
        self.app.quit()

    def run(self):
        return self.app.exec()


def main():
    app = App()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
