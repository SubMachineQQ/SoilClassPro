from __future__ import annotations

import math
import tkinter as tk
from typing import Callable, Optional

from ..colors import THEME_TOGGLE as PAL

TRACK_W, TRACK_H = 64, 32
THUMB = 24
INSET = 4
TRAVEL = TRACK_W - THUMB - 2 * INSET

_DURATION_MS = 220
_STEP_MS = 15


def _smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


class ThemeToggle(tk.Canvas):
    def __init__(self, master, *, is_dark: bool, bg: str,
                command: Optional[Callable[[bool], None]] = None):
        super().__init__(master, width=TRACK_W, height=TRACK_H,
                         highlightthickness=0, background=bg,
                         cursor="hand2", takefocus=1)
        self._is_dark = is_dark
        self._command = command
        self._animating = False
        self._job = None
        self._frac = 1.0 if is_dark else 0.0
        self._thumb_fill = PAL["thumb_dark"] if is_dark else PAL["thumb_light"]

        self.bind("<Button-1>", self._on_click)
        self.bind("<Return>", self._on_click)
        self.bind("<space>", self._on_click)

        self._draw(self._frac)

    @property
    def is_dark(self) -> bool:
        return self._is_dark

    def _on_click(self, _event=None):
        if self._animating:
            return
        self._is_dark = not self._is_dark
        self._animate_to(1.0 if self._is_dark else 0.0)

    def _animate_to(self, target: float) -> None:
        start = self._frac
        steps = max(1, _DURATION_MS // _STEP_MS)
        self._animating = True

        def step(i: int = 0):
            self._job = None
            if i >= steps:
                self._frac = target
                self._draw(self._frac)
                self._animating = False
                if self._command is not None:
                    self._command(self._is_dark)
                return
            t = _smoothstep(i / steps)
            self._frac = start + (target - start) * t
            self._draw(self._frac)
            self._job = self.after(_STEP_MS, lambda: step(i + 1))

        step()

    def destroy(self):
        if self._job is not None:
            self.after_cancel(self._job)
            self._job = None
        super().destroy()

    def _lerp_color(self, c1: str, c2: str, t: float) -> str:
        r1, g1, b1 = self.winfo_rgb(c1)
        r2, g2, b2 = self.winfo_rgb(c2)
        r = int(r1 + (r2 - r1) * t) >> 8
        g = int(g1 + (g2 - g1) * t) >> 8
        b = int(b1 + (b2 - b1) * t) >> 8
        return f"#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}" \
               f"{max(0, min(255, b)):02x}"

    def _rounded_rect(self, x0, y0, x1, y1, r, **kw):
        points = [
            x0 + r, y0, x1 - r, y0, x1, y0, x1, y0 + r,
            x1, y1 - r, x1, y1, x1 - r, y1, x0 + r, y1,
            x0, y1, x0, y1 - r, x0, y0 + r, x0, y0,
        ]
        return self.create_polygon(points, smooth=True, **kw)

    def _draw(self, frac: float) -> None:
        self.delete("all")

        track = self._lerp_color(PAL["track_light"], PAL["track_dark"], frac)
        border = self._lerp_color(PAL["track_border_light"],
                                  PAL["track_border_dark"], frac)
        self._rounded_rect(1, 1, TRACK_W - 1, TRACK_H - 1, TRACK_H / 2,
                           fill=track, outline=border)

        cx0 = INSET + frac * TRAVEL
        cy0 = INSET

        shadow = self._lerp_color(PAL["thumb_shadow_light"],
                                  PAL["thumb_shadow_dark"], frac)
        self.create_oval(cx0 - 0.5, cy0 + 1.5, cx0 + THUMB - 0.5,
                         cy0 + THUMB + 1.5, fill=shadow, outline="")

        self._thumb_fill = self._lerp_color(PAL["thumb_light"],
                                            PAL["thumb_dark"], frac)
        self.create_oval(cx0, cy0, cx0 + THUMB, cy0 + THUMB,
                         fill=self._thumb_fill, outline="")

        icx, icy = cx0 + THUMB / 2, cy0 + THUMB / 2
        sun_scale = max(0.0, 1.0 - frac * 2.0)
        moon_scale = max(0.0, frac * 2.0 - 1.0)
        if sun_scale > 0.02:
            self._draw_sun(icx, icy, sun_scale)
        if moon_scale > 0.02:
            self._draw_moon(icx, icy, moon_scale)

    def _draw_sun(self, cx, cy, scale):
        r = 3.0 * scale
        color = PAL["sun"]
        self.create_oval(cx - r, cy - r, cx + r, cy + r, outline=color, width=2)
        inner, outer = r * 1.6, r * 2.7
        for i in range(8):
            a = math.radians(i * 45)
            x0, y0 = cx + inner * math.cos(a), cy + inner * math.sin(a)
            x1, y1 = cx + outer * math.cos(a), cy + outer * math.sin(a)
            self.create_line(x0, y0, x1, y1, fill=color, width=2,
                             capstyle="round")

    def _draw_moon(self, cx, cy, scale):
        r = 5.6 * scale
        color = PAL["moon"]
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         fill=color, outline="")
        off = r * 0.55
        self.create_oval(cx - r + off, cy - r - off * 0.3,
                         cx + r + off, cy + r - off * 0.3,
                         fill=self._thumb_fill, outline="")
