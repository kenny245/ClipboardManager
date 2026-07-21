import ctypes
import sys
from ctypes import Structure, c_int, c_uint, c_void_p, byref, sizeof

ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
WCA_ACCENT_POLICY = 19

DWMWA_USE_IMMERSIVE_DARK_MODE = 20


class _ACCENTPOLICY(Structure):
    _fields_ = [
        ("nAccentState", c_int),
        ("nFlags", c_int),
        ("nColor", c_uint),
        ("nAnimationId", c_int),
    ]


class _WINCOMPATTRDATA(Structure):
    _fields_ = [
        ("nAttribute", c_int),
        ("pData", c_void_p),
        ("ulDataSize", c_uint),
    ]


def enable_acrylic(hwnd, tint_color=(255, 255, 255), tint_alpha=80):
    if sys.platform != "win32":
        return False
    user32 = ctypes.windll.user32
    dwmapi = ctypes.windll.dwmapi

    # Disable dark mode so acrylic tint renders correctly with light color
    try:
        dark = c_int(0)
        dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd), DWMWA_USE_IMMERSIVE_DARK_MODE,
            byref(dark), sizeof(dark)
        )
    except Exception:
        pass

    r, g, b = tint_color
    accent = _ACCENTPOLICY()
    accent.nAccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
    accent.nFlags = 0
    accent.nAnimationId = 0
    accent.nColor = (tint_alpha << 24) | (b << 16) | (g << 8) | r

    data = _WINCOMPATTRDATA()
    data.nAttribute = WCA_ACCENT_POLICY
    data.pData = ctypes.cast(byref(accent), c_void_p)
    data.ulDataSize = sizeof(accent)

    try:
        result = user32.SetWindowCompositionAttribute(ctypes.c_void_p(hwnd), byref(data))
        return bool(result)
    except Exception:
        return False
