import sys, os
sys.path.insert(0, r'D:\剪贴板')
os.chdir(r'D:\剪贴板')

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

app = QApplication(sys.argv)

from config import Config
from history_store import HistoryStore
from clipboard_watcher import ClipboardWatcher
from search_window import SearchWindow

cfg = Config.instance()
print(f"Config show_close = {cfg.get('show_close')}")

store = HistoryStore(cfg.get("storage_dir"))
watcher = ClipboardWatcher(app)
win = SearchWindow(store, watcher)
win.show()

# Test 1: check initial state
print(f"close_btn isVisible = {win.close_btn.isVisible()}")
print(f"close_btn minimumWidth = {win.close_btn.minimumWidth()}")
print(f"close_btn maximumWidth = {win.close_btn.maximumWidth()}")

# Test 2: expand window to see status row
win._expand()

# Test 3: toggle close btn on
def test_toggle_on():
    print("\n--- Toggling show_close ON ---")
    cfg.set("show_close", True)
    cfg.save()
    win._set_close_btn_visible(True)
    print(f"close_btn isVisible = {win.close_btn.isVisible()}")
    print(f"close_btn minimumWidth = {win.close_btn.minimumWidth()}")
    print(f"close_btn maximumWidth = {win.close_btn.maximumWidth()}")
    print(f"close_btn width = {win.close_btn.width()}")

def test_toggle_off():
    print("\n--- Toggling show_close OFF ---")
    cfg.set("show_close", False)
    cfg.save()
    win._set_close_btn_visible(False)
    print(f"close_btn isVisible = {win.close_btn.isVisible()}")
    print(f"close_btn minimumWidth = {win.close_btn.minimumWidth()}")
    print(f"close_btn maximumWidth = {win.close_btn.maximumWidth()}")
    print(f"close_btn width = {win.close_btn.width()}")

def test_toggle_on_again():
    test_toggle_on()
    QTimer.singleShot(1000, app.quit)

QTimer.singleShot(500, test_toggle_on)
QTimer.singleShot(1500, test_toggle_off)
QTimer.singleShot(2500, test_toggle_on_again)

app.exec()
