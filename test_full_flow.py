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
store = HistoryStore(cfg.get('storage_dir') or r'D:\剪贴板', max_items=cfg.get('max_items', 200))
watcher = ClipboardWatcher(app)
window = SearchWindow(store, watcher)
window.show()
window.refresh_settings()

sc = cfg.get('show_close')
cv = window.close_btn.isVisible()
cw = window.close_btn.width()
ch = window.close_btn.height()
print(f'After refresh_settings: show_close={sc}, visible={cv}, size={cw}x{ch}')

window._expand()

def check_after_expand():
    cv = window.close_btn.isVisible()
    cw = window.close_btn.width()
    sm = window.status_row.maximumHeight()
    print(f'After expand: visible={cv}, w={cw}, status_row maxH={sm}')

    def test_off():
        cfg.set('show_close', False)
        cfg.save()
        window._set_close_btn_visible(False)
        cv = window.close_btn.isVisible()
        cw = window.close_btn.width()
        print(f'After toggle OFF: visible={cv}, w={cw}')

    def test_on():
        cfg.set('show_close', True)
        cfg.save()
        window._set_close_btn_visible(True)
        cv = window.close_btn.isVisible()
        cw = window.close_btn.width()
        print(f'After toggle ON: visible={cv}, w={cw}')
        app.quit()

    QTimer.singleShot(500, test_off)
    QTimer.singleShot(1000, test_on)

QTimer.singleShot(300, check_after_expand)
app.exec()
print('Done')
