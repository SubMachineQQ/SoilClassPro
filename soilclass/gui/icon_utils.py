from __future__ import annotations

import sys
import tkinter as tk

from ..assets_path import LOGO_ICO, LOGO_PNG

_TARGET_PX = 128

if sys.platform == "win32":
    import ctypes

_GWL_STYLE = -16
_WS_MINIMIZEBOX = 0x00020000
_WS_MAXIMIZEBOX = 0x00010000
_SWP_FLAGS = 0x0001 | 0x0002 | 0x0004 | 0x0020


def enable_maximize_button(window: tk.Misc) -> None:
    if sys.platform != "win32":
        return
    try:
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        style = ctypes.windll.user32.GetWindowLongW(hwnd, _GWL_STYLE)
        style |= _WS_MINIMIZEBOX | _WS_MAXIMIZEBOX
        ctypes.windll.user32.SetWindowLongW(hwnd, _GWL_STYLE, style)
        ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, _SWP_FLAGS)
    except Exception:
        pass


def set_window_icon(window: tk.Misc) -> None:
    if sys.platform.startswith("win") and LOGO_ICO.exists():
        try:
            window.iconbitmap(str(LOGO_ICO))
            return
        except tk.TclError:
            pass

    if LOGO_PNG.exists():
        try:
            img = tk.PhotoImage(file=str(LOGO_PNG))
            largest = max(img.width(), img.height())
            factor = max(1, round(largest / _TARGET_PX))
            if factor > 1:
                img = img.subsample(factor, factor)
            window.iconphoto(True, img)
            window._soilclasspro_icon_ref = img
        except tk.TclError:
            pass
