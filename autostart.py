import os
import sys
import json
import plistlib

APP_NAME = "ClipboardManager"


def _get_command():
    if getattr(sys, 'frozen', False):
        return sys.executable
    script = os.path.abspath(sys.argv[0])
    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable
    return f'"{pythonw}" "{script}"'


# ==================== Windows ====================
if sys.platform == "win32":
    import winreg

    RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

    def enable():
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _get_command())
            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    def disable():
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return True
        except Exception:
            return False

    def is_enabled():
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False


# ==================== macOS ====================
elif sys.platform == "darwin":
    LAUNCH_AGENT_DIR = os.path.expanduser("~/Library/LaunchAgents")
    PLIST_PATH = os.path.join(LAUNCH_AGENT_DIR, f"com.{APP_NAME.lower()}.plist")
    LABEL = f"com.{APP_NAME.lower()}"

    def _get_app_path():
        if getattr(sys, 'frozen', False):
            return sys.executable
        script = os.path.abspath(sys.argv[0])
        return f'"{sys.executable}" "{script}"'

    def enable():
        try:
            os.makedirs(LAUNCH_AGENT_DIR, exist_ok=True)
            plist = {
                "Label": LABEL,
                "ProgramArguments": _get_app_path().strip('"').split('" "'),
                "RunAtLoad": True,
                "KeepAlive": False,
                "StandardErrorPath": os.path.expanduser(f"~/.{APP_NAME.lower()}.err.log"),
                "StandardOutPath": os.path.expanduser(f"~/.{APP_NAME.lower()}.out.log"),
            }
            with open(PLIST_PATH, "wb") as f:
                plistlib.dump(plist, f)
            os.system(f'launchctl load "{PLIST_PATH}" 2>/dev/null')
            return True
        except Exception:
            return False

    def disable():
        try:
            os.system(f'launchctl unload "{PLIST_PATH}" 2>/dev/null')
            if os.path.exists(PLIST_PATH):
                os.remove(PLIST_PATH)
            return True
        except Exception:
            return False

    def is_enabled():
        return os.path.exists(PLIST_PATH)


# ==================== Fallback ====================
else:
    def enable():
        return False

    def disable():
        return True

    def is_enabled():
        return False
