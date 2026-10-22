from __future__ import annotations

import sys
import tkinter as tk
from tkinter import font as tkfont
from typing import Optional, Tuple

_BASE_DPI = 96.0
_SCREEN_MARGIN = 0.94


def enable_dpi_awareness() -> None:
    if sys.platform != "win32":
        return
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        return
    except (AttributeError, OSError):
        pass
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except (AttributeError, OSError):
        pass


def factor(widget: tk.Misc) -> float:
    try:
        return max(1.0, float(widget.winfo_fpixels("1i")) / _BASE_DPI)
    except tk.TclError:
        return 1.0


def px(widget: tk.Misc, value: float) -> int:
    return int(round(value * factor(widget)))


def work_area(widget: tk.Misc) -> Tuple[int, int, int, int]:
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes
        rect = wintypes.RECT()
        try:
            if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0,
                                                          ctypes.byref(rect), 0):
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                if width > 0 and height > 0:
                    return rect.left, rect.top, width, height
        except (AttributeError, OSError):
            pass
    return 0, 0, widget.winfo_screenwidth(), widget.winfo_screenheight()


def row_height(widget: tk.Misc, font_spec, padding: float = 1.6) -> int:
    try:
        linespace = tkfont.Font(root=widget, font=font_spec).metrics("linespace")
    except tk.TclError:
        linespace = 18
    return max(20, int(round(linespace * padding)))


def fit_window(window: tk.Misc, width: float, height: float, *,
               min_width: float = 0, min_height: float = 0,
               parent: Optional[tk.Misc] = None) -> Tuple[int, int]:
    left, top, area_w, area_h = work_area(window)
    max_w = int(area_w * _SCREEN_MARGIN)
    max_h = int(area_h * _SCREEN_MARGIN)
    w = min(px(window, width), max_w)
    h = min(px(window, height), max_h)
    window.minsize(min(px(window, min_width), w), min(px(window, min_height), h))

    if parent is not None:
        try:
            parent.update_idletasks()
            x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
            y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
        except tk.TclError:
            parent = None
    if parent is None:
        x = left + (area_w - w) // 2
        y = top + (area_h - h) // 2
    x = max(left, min(x, left + area_w - w))
    y = max(top, min(y, top + area_h - h))
    window.geometry(f"{w}x{h}+{x}+{y}")
    return w, h


def lock_min_to_content(window: tk.Misc) -> None:
    window.update_idletasks()
    _, _, area_w, area_h = work_area(window)
    min_w, min_h = window.minsize()
    window.minsize(max(min_w, min(window.winfo_reqwidth(), int(area_w * _SCREEN_MARGIN))),
                   max(min_h, min(window.winfo_reqheight(), int(area_h * _SCREEN_MARGIN))))
