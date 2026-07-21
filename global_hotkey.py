import sys
import threading


class GlobalHotkeyBase:
    def __init__(self):
        self._callbacks = {}
        self._id_counter = 1
        self._running = False

    def register(self, key_code, modifiers, callback):
        hotkey_id = self._id_counter
        self._id_counter += 1
        self._callbacks[hotkey_id] = (key_code, modifiers, callback)
        self._do_register(hotkey_id, key_code, modifiers, callback)
        if not self._running:
            self._start()
        return hotkey_id

    def unregister(self, hotkey_id):
        if hotkey_id in self._callbacks:
            self._do_unregister(hotkey_id)
            del self._callbacks[hotkey_id]

    def stop(self):
        self._running = False
        self._do_stop()

    def _do_register(self, hid, key, mod, cb): pass
    def _do_unregister(self, hid): pass
    def _do_stop(self): pass
    def _start(self): self._running = True


# ==================== Windows ====================
if sys.platform == "win32":
    import ctypes
    import ctypes.wintypes as wintypes

    WM_HOTKEY = 0x0312
    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002
    MOD_SHIFT = 0x0004
    MOD_WIN = 0x0008

    class GlobalHotkey(GlobalHotkeyBase):
        def _start(self):
            self._running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

        def _loop(self):
            user32 = ctypes.windll.user32
            msg = wintypes.MSG()
            while self._running:
                if user32.GetMessageA(ctypes.byref(msg), None, 0, 0) > 0:
                    if msg.message == WM_HOTKEY:
                        hid = msg.wParam
                        if hid in self._callbacks:
                            _, _, cb = self._callbacks[hid]
                            cb()
                else:
                    break

        def _do_register(self, hid, key, mod, cb):
            ctypes.windll.user32.RegisterHotKey(None, hid, mod | 0x4000, key)

        def _do_unregister(self, hid):
            try:
                ctypes.windll.user32.UnregisterHotKey(None, hid)
            except Exception:
                pass

        def _do_stop(self):
            for hid in list(self._callbacks.keys()):
                self._do_unregister(hid)
            try:
                ctypes.windll.user32.PostThreadMessageA(
                    self._thread.ident if hasattr(self, '_thread') else 0,
                    0x0012, 0, 0
                )
            except Exception:
                pass


# ==================== macOS ====================
elif sys.platform == "darwin":
    class GlobalHotkey(GlobalHotkeyBase):
        def __init__(self):
            super().__init__()
            self._listener = None
            self._handler_map = {}

        def _start(self):
            self._running = True

        def _do_register(self, hid, key, mod, cb):
            from pynput import keyboard as kb

            VK_MAP = {
                0x56: kb.KeyCode.from_char('v'),
                0x43: kb.KeyCode.from_char('c'),
                0x58: kb.KeyCode.from_char('x'),
                0x41: kb.KeyCode.from_char('a'),
                0x5A: kb.KeyCode.from_char('z'),
            }

            keys = set()
            if mod & 0x0004:
                keys.add(kb.Key.shift)
            if mod & 0x0002:
                keys.add(kb.Key.ctrl)
            if mod & 0x0001:
                keys.add(kb.Key.alt)
            if mod & 0x0008:
                keys.add(kb.Key.cmd)

            vk = VK_MAP.get(key)
            if vk is None:
                if 0x30 <= key <= 0x39:
                    vk = kb.KeyCode.from_char(str(key - 0x30))
                elif 0x41 <= key <= 0x5A:
                    vk = kb.KeyCode.from_char(chr(key).lower())
                else:
                    return
            keys.add(vk)

            def make_cb(cb):
                def handler():
                    cb()
                return handler

            handler = make_cb(cb)
            self._handler_map[hid] = (keys, handler)

            self._rebuild_listener()

        def _rebuild_listener(self):
            if self._listener:
                try:
                    self._listener.stop()
                except Exception:
                    pass

            from pynput import keyboard as kb
            combos = {}
            for hid, (keys, handler) in self._handler_map.items():
                key_list = frozenset(keys)
                combos[key_list] = handler

            try:
                self._listener = kb.GlobalHotKeys(combos)
                self._listener.start()
            except Exception:
                pass

        def _do_unregister(self, hid):
            if hid in self._handler_map:
                del self._handler_map[hid]
                self._rebuild_listener()

        def _do_stop(self):
            if self._listener:
                try:
                    self._listener.stop()
                except Exception:
                    pass


# ==================== Fallback ====================
else:
    class GlobalHotkey(GlobalHotkeyBase):
        def _start(self):
            self._running = True


# Convenience constants (same as Windows VK codes for cross-platform use)
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
VK_V = 0x56
VK_C = 0x43
VK_X = 0x58
