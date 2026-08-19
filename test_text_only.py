import sys, os
sys.path.insert(0, r'D:\剪贴板')
os.chdir(r'D:\剪贴板')

# 图片记录功能已移除：验证 watcher / store 为纯文本实现，
# 并触发旧数据迁移（清除历史中的图片条目及缓存文件）

from clipboard_watcher import ClipboardWatcher
from history_store import HistoryStore

assert not hasattr(ClipboardWatcher, 'set_image'), 'watcher still has set_image'
assert not hasattr(HistoryStore, 'add_image'), 'store still has add_image'
assert not hasattr(HistoryStore, 'get_image_path'), 'store still has get_image_path'
print('API check OK: no image interfaces remain')

store = HistoryStore(r'D:\剪贴板', max_items=200)
items = store.get_all()
non_text = [i for i in items if i.get('type') != 'text']
print(f'Total items: {len(items)}, non-text items after migration: {len(non_text)}')
assert not non_text, f'legacy image items remain: {len(non_text)}'
assert not os.path.exists(os.path.join(r'D:\剪贴板', 'images')), 'images dir still exists'
print('Migration OK: history is text-only, images dir removed')

added = store.add_text('纯文本记录冒烟测试')
assert added is not None and added.get('type') == 'text'
store.remove(added['id'])
print('Add/remove text OK')

print('=== ALL TEXT-ONLY CHECKS PASSED ===')
