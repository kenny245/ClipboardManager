import sys, os
sys.path.insert(0, r'D:\剪贴板')
os.chdir(r'D:\剪贴板')

results = []

# Test 1: config import
print('[1/7] Testing config import...')
from config import Config
cfg = Config.instance()
mi = cfg.get("max_items")
sd = cfg.get("storage_dir")
au = cfg.get("autostart")
print(f'  max_items={mi}, storage_dir={sd}, autostart={au}')
results.append(True)

# Test 2: history_store with dynamic max_items
print('[2/7] Testing history_store set_max_items...')
from history_store import HistoryStore
store = HistoryStore(r'D:\剪贴板', max_items=200)
store.set_max_items(50)
assert store.get_max_items() == 50, 'max_items not updated'
store.set_max_items(200)
cnt = store.count()
print(f'  max_items={store.get_max_items()}, count={cnt}')
results.append(True)

# Test 3: settings_dialog import
print('[3/7] Testing settings_dialog import...')
from settings_dialog import SettingsDialog
print('  SettingsDialog class loaded OK')
results.append(True)

# Test 4: search_window methods
print('[4/7] Testing search_window settings integration...')
from search_window import SearchWindow
assert hasattr(SearchWindow, '_on_settings'), 'missing _on_settings'
assert hasattr(SearchWindow, '_on_close_app'), 'missing _on_close_app'
assert hasattr(SearchWindow, 'refresh_settings'), 'missing refresh_settings'
print('  _on_settings, _on_close_app, refresh_settings all present')
results.append(True)

# Test 5: clipboard_manager import
print('[5/7] Testing clipboard_manager config integration...')
import clipboard_manager
print('  clipboard_manager loaded OK')
results.append(True)

# Test 6: autostart functions
print('[6/7] Testing autostart functions...')
from autostart import is_enabled, enable, disable
state = is_enabled()
print(f'  autostart currently enabled: {state}')
results.append(True)

# Test 7: config save/load roundtrip
print('[7/7] Testing config save/load roundtrip...')
cfg.set('max_items', 300)
cfg.set('show_close', True)
cfg.save()
# Force fresh load (bypass singleton)
import importlib
import config as cfgmod
importlib.reload(cfgmod)
cfg2 = cfgmod.Config()
cfg2._load()
mi2 = cfg2.get('max_items')
sc2 = cfg2.get('show_close')
print(f'  Read back: max_items={mi2}, show_close={sc2}')
assert mi2 == 300, f'max_items mismatch: {mi2}'
assert sc2 == True, f'show_close mismatch: {sc2}'
# Restore defaults
cfg2.set('max_items', 200)
cfg2.set('show_close', False)
cfg2.save()
print('  Save/load roundtrip verified, defaults restored')
results.append(True)

print()
if all(results):
    print('=== ALL 7 TESTS PASSED ===')
else:
    failed = [i+1 for i, r in enumerate(results) if not r]
    print(f'=== FAILED: tests {failed} ===')
