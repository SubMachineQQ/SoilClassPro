from __future__ import annotations

import tkinter as tk

from ..fonts import UI_FONT, MONO_FONT
from ..i18n import t, upper

__all__ = [
    "MONO", "UI",
    "micro_label", "MetricCell", "ValueBox", "StatusPill",
    "hairline",
]

MONO = MONO_FONT
UI = UI_FONT


def micro_label(parent, text: str, *, bg: str, fg: str, **pack_kw):
    lbl = tk.Label(parent, text=upper(text), font=(MONO, 10),
                   background=bg, foreground=fg, anchor="w")
    if pack_kw:
        lbl.pack(**pack_kw)
    return lbl


def hairline(parent, *, color: str, height: int = 1, **pack_kw):
    line = tk.Frame(parent, height=height, background=color)
    if pack_kw:
        line.pack(**pack_kw)
    return line


class MetricCell(tk.Frame):
    def __init__(self, master, caption: str, value: str, palette,
                 *, accent: bool = False, value_size: int = 10,
                 inline: bool = False):
        bg = palette["card_bg"]
        super().__init__(master, background=bg)
        self._pal = palette
        self._accent = accent
        fg = palette["accent"] if accent else palette["value_fg"]
        if inline:
            self._caption = micro_label(self, caption, bg=bg,
                                        fg=palette["micro_fg"], side="left")
            self.value = tk.Label(self, text=value,
                                  font=(MONO, value_size, "bold"),
                                  background=bg, foreground=fg, anchor="e")
            self.value.pack(side="right")
            return
        self._caption = micro_label(self, caption, bg=bg,
                                    fg=palette["micro_fg"],
                                    anchor="w", fill="x")
        self.value = tk.Label(self, text=value, font=(MONO, value_size, "bold"),
                              background=bg, foreground=fg, anchor="w")
        self.value.pack(anchor="w", fill="x")

    def set(self, value: str) -> None:
        self.value.configure(text=value)

    def apply_palette(self, palette) -> None:
        self._pal = palette
        bg = palette["card_bg"]
        self.configure(background=bg)
        fg = palette["accent"] if self._accent else palette["value_fg"]
        self.value.configure(background=bg, foreground=fg)
        if self._caption is not None:
            self._caption.configure(background=bg,
                                    foreground=palette["micro_fg"])


class ValueBox(tk.Frame):
    def __init__(self, master, value: str, palette,
                 *, size: int = 18, accent: bool = True,
                 outline: bool = False, width: int = 6):
        self._pal = palette
        self._accent = accent
        self._outline = outline
        border = palette["accent"] if outline else palette["card_border"]
        super().__init__(master, background=border, padx=1, pady=1)
        self._inner = tk.Frame(self, background=palette["card_bg"])
        self._inner.pack(fill="both", expand=True)
        fg = palette["accent"] if accent else palette["value_fg"]
        self.value = tk.Label(self._inner, text=value,
                              font=(MONO, size, "bold"),
                              background=palette["card_bg"], foreground=fg,
                              width=width, anchor="center", pady=8)
        self.value.pack(fill="both", expand=True)

    def set(self, value: str) -> None:
        if len(value) > int(self.value.cget("width")):
            self.value.configure(width=len(value))
        self.value.configure(text=value)

    def apply_palette(self, palette) -> None:
        self._pal = palette
        border = palette["accent"] if self._outline else palette["card_border"]
        self.configure(background=border)
        self._inner.configure(background=palette["card_bg"])
        fg = palette["accent"] if self._accent else palette["value_fg"]
        self.value.configure(background=palette["card_bg"], foreground=fg)


class StatusPill(tk.Frame):
    _KEYS = {
        "ACTIVE": "pill_active",
        "REVIEW": "pill_review",
        "SIGNED": "pill_signed",
    }

    def __init__(self, master, state: str, palette, *, bg: str | None = None):
        bg = bg or palette["card_bg"]
        super().__init__(master, background=bg)
        state = state.upper()
        key = self._KEYS.get(state, "pill_active")
        colour = palette[key]
        display = t(key)
        tk.Frame(self, background=colour, width=6, height=6).pack(
            side="left", pady=(1, 0))
        tk.Label(self, text=" " + display, font=(MONO, 9),
                 background=bg, foreground=colour).pack(side="left")
