"""Windows-only niceties, written to fail softly everywhere.

Two things live here: the DWM backdrop used by the optional "desktop glass"
mode, and the system animation preference that drives reduced motion.
"""

from __future__ import annotations

import ctypes
import platform
import sys

DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_WINDOW_CORNER_PREFERENCE = 33
DWMWA_SYSTEMBACKDROP_TYPE = 38

DWMSBT_AUTO = 0
DWMSBT_NONE = 1
DWMSBT_MICA = 2
DWMSBT_ACRYLIC = 3
DWMSBT_TABBED = 4

DWMWCP_ROUND = 2

SPI_GETCLIENTAREAANIMATION = 0x1042


def is_windows() -> bool:
    return sys.platform.startswith("win")


def windows_build() -> int:
    if not is_windows():
        return 0
    try:
        return int(platform.version().split(".")[-1])
    except (ValueError, IndexError):
        return 0


def glass_supported() -> bool:
    """Mica/Acrylic backdrops need Windows 11 (build 22000+)."""
    return is_windows() and windows_build() >= 22000


class _Margins(ctypes.Structure):
    _fields_ = [
        ("cxLeftWidth", ctypes.c_int),
        ("cxRightWidth", ctypes.c_int),
        ("cyTopHeight", ctypes.c_int),
        ("cyBottomHeight", ctypes.c_int),
    ]


def _set_attr(hwnd: int, attribute: int, value: int) -> bool:
    try:
        dwmapi = ctypes.windll.dwmapi  # type: ignore[attr-defined]
        data = ctypes.c_int(value)
        result = dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd), ctypes.c_uint(attribute), ctypes.byref(data), ctypes.sizeof(data)
        )
        return result == 0
    except Exception:
        return False


def apply_chrome(hwnd: int, *, dark: bool, rounded: bool = True) -> dict[str, bool]:
    """Dark titlebar and rounded corners for the frameless window."""
    applied = {"dark": False, "rounded": False}
    if not is_windows() or not hwnd:
        return applied
    applied["dark"] = _set_attr(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, 1 if dark else 0)
    if rounded:
        applied["rounded"] = _set_attr(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, DWMWCP_ROUND)
    return applied


def set_backdrop(hwnd: int, kind: str | None) -> bool:
    """``"mica"``, ``"acrylic"`` or ``None``.  False when the OS says no."""
    if not glass_supported():
        return False
    value = {"mica": DWMSBT_MICA, "acrylic": DWMSBT_ACRYLIC}.get((kind or "").lower(), DWMSBT_NONE)
    ok = _set_attr(hwnd, DWMWA_SYSTEMBACKDROP_TYPE, value)
    try:  # the frame has to reach the glass for acrylic to show
        margins = _Margins(-1, -1, -1, -1)
        ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(  # type: ignore[attr-defined]
            ctypes.c_void_p(hwnd), ctypes.byref(margins)
        )
    except Exception:
        pass
    return ok


def animations_enabled() -> bool:
    """False when the user turned off Windows animations."""
    if not is_windows():
        return True
    try:
        enabled = ctypes.c_int(1)
        ok = ctypes.windll.user32.SystemParametersInfoW(  # type: ignore[attr-defined]
            SPI_GETCLIENTAREAANIMATION, 0, ctypes.byref(enabled), 0
        )
        return bool(enabled.value) if ok else True
    except Exception:
        return True
