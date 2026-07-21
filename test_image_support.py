import sys, os
sys.path.insert(0, r'D:\剪贴板')
os.chdir(r'D:\剪贴板')

from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)

from config import Config
from history_store import HistoryStore
from clipboard_watcher import ClipboardWatcher
from search_window import SearchWindow

cfg = Config.instance()
store = HistoryStore(cfg.get('storage_dir'), max_items=cfg.get('max_items', 200))
watcher = ClipboardWatcher(app)
win = SearchWindow(store, watcher)
win.show()
win._expand()

items = store.get_all()
print(f'Total items: {len(items)}')
for item in items[:5]:
    t = item.get('type', 'text')
    p = item.get('preview', '')
    print(f'  type={t}, preview={p}')

print('All OK')
app.quit()
