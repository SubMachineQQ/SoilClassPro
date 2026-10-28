from __future__ import annotations

import random
import time
import tkinter as tk
from typing import Optional

from ..fonts import UI_FONT
from .. import __app_name__, __version__, consent
from ..about import ACKNOWLEDGED, AUTHORS, format_date
from ..assets_path import LOGO_PNG
from ..colors import SPLASH, SPLASH_DARK
from ..i18n import t
from .theme import get_dark_mode
from .scaling import px, tk_scaling, work_area


def _apply_palette_globals(dark: bool) -> None:
    pal = SPLASH_DARK if dark else SPLASH
    g = globals()
    g["_BG"] = pal["background"]
    g["_BORDER"] = pal["border"]
    g["_FG"] = pal["text"]
    g["_MUTED"] = pal["muted_text"]
    g["_ACCENT"] = pal["accent"]
    g["_PROGRESS_TRACK"] = pal["progress_track"]


_apply_palette_globals(False)

_LOGO_TARGET_PX = 128


def _load_scaled_logo():
    try:
        img = tk.PhotoImage(file=str(LOGO_PNG))
    except tk.TclError:
        return None
    largest = max(img.width(), img.height())
    factor = max(1, round(largest / _LOGO_TARGET_PX))
    if factor > 1:
        img = img.subsample(factor, factor)
    return img


SPLASH_MIN_MS = 2500
SPLASH_MAX_MS = 3500
_FRAME_MS = 15
_FINAL_FRAME_MS = 60


def splash_duration() -> int:
    return random.randint(SPLASH_MIN_MS, SPLASH_MAX_MS)


class SplashScreen(tk.Tk):
    def __init__(self, duration_ms: Optional[int] = None):
        if duration_ms is None:
            duration_ms = splash_duration()
        super().__init__()
        tk_scaling(self)
        _apply_palette_globals(get_dark_mode())
        self.overrideredirect(True)
        self.configure(background=_BORDER)

        width, height = px(self, 600), px(self, 470)
        left, top, area_w, area_h = work_area(self)
        x, y = left + (area_w - width) // 2, top + (area_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        content = tk.Frame(self, background=_BG)
        content.pack(fill="both", expand=True, padx=2, pady=2)

        tk.Frame(content, background=_BG).pack(fill="both", expand=True)

        self._logo_img = _load_scaled_logo()
        if self._logo_img is not None:
            tk.Label(content, image=self._logo_img,
                    background=_BG).pack(pady=(0, 16))

        tk.Label(content, text=__app_name__, font=(UI_FONT, 26, "bold"),
                fg=_FG, background=_BG).pack()
        tk.Label(content,
                text=f"{t('splash_version').format(version=__version__)}"
                     f"   ·   {format_date()}",
                font=(UI_FONT, 13), fg=_MUTED,
                background=_BG).pack(pady=(4, 14))

        tk.Frame(content, height=1, width=180,
                background=_ACCENT).pack(pady=(0, 14))

        tk.Label(content,
                text="USCS  \u00b7  BS 5930  \u00b7  TS EN ISO 14688  \u00b7  "
                     "AASHTO  \u00b7  RSCS",
                font=(UI_FONT, 12), fg=_MUTED,
                background=_BG).pack()

        tk.Frame(content, background=_BG).pack(fill="both", expand=True)

        track_width = px(self, 360)
        track = tk.Frame(content, background=_PROGRESS_TRACK,
                        height=4,
                         width=track_width)
        track.pack(pady=(0, 10))
        track.pack_propagate(False)
        self._bar_fill = tk.Frame(track, background=_ACCENT, height=4)
        self._bar_fill.place(x=0, y=0, relheight=1, width=0)
        self._track_width = track_width

        tk.Label(content, text=t("splash_thanks"),
                font=(UI_FONT, 11, "italic"), fg=_FG,
                background=_BG).pack(pady=(0, 2))
        tk.Label(content, text="  \u00b7  ".join(AUTHORS),
                font=(UI_FONT, 10), fg=_MUTED,
                background=_BG).pack(pady=(0, 2))
        tk.Label(content, text=t("acknowledgement").format(name=ACKNOWLEDGED),
                font=(UI_FONT, 9, "italic"), fg=_MUTED,
                background=_BG).pack(pady=(0, 2))
        tk.Label(content,
                text=t("splash_copyright"),
                font=(UI_FONT, 11), fg=_MUTED,
                background=_BG).pack(pady=(0, 18))

        self._duration = max(duration_ms, 200)
        self._started = None
        self._close_job = None
        self._anim_job = self.after(0, self._animate_progress)

    def progress(self) -> float:
        if self._started is None:
            return 0.0
        elapsed_ms = (time.perf_counter() - self._started) * 1000.0
        return min(1.0, elapsed_ms / self._duration)

    def _animate_progress(self):
        self._anim_job = None
        if self._started is None:
            self._started = time.perf_counter()
        frac = self.progress()
        self._bar_fill.place_configure(width=round(self._track_width * frac))
        if frac >= 1.0:
            self._close_job = self.after(_FINAL_FRAME_MS, self._finish)
            return
        self._anim_job = self.after(_FRAME_MS, self._animate_progress)

    def _finish(self):
        self._close_job = None
        self.quit()
        self.destroy()

    def destroy(self):
        for name in ("_anim_job", "_close_job"):
            job = getattr(self, name, None)
            if job is not None:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass
                setattr(self, name, None)
        super().destroy()


def ensure_disclaimer_accepted(ask=None) -> bool:
    if consent.is_accepted():
        return True
    if ask is None:
        from .welcome import ask_acceptance as ask
    if not ask():
        return False
    consent.record_acceptance()
    return True


def run_launcher_loop() -> None:
    if not ensure_disclaimer_accepted():
        return

    from .launcher import LauncherWindow

    pending = ("launcher", None, None)
    while True:
        kind, mode, preset_sample = pending

        if kind == "launcher":
            launcher = LauncherWindow()
            launcher.mainloop()
            if launcher.result is None:
                return
            mode, preset_sample = launcher.result
            pending = ("app", mode, preset_sample)
            continue

        if kind == "app":
            from .app import SoilClassApp
            app = SoilClassApp(mode=mode, preset_sample=preset_sample)
            app.mainloop()
            pending = getattr(app, "next_screen", None)
            if pending is None:
                return
            continue

        return


def show_splash_then_launcher(duration_ms: Optional[int] = None) -> None:
    splash = SplashScreen(duration_ms)
    splash.mainloop()
    run_launcher_loop()
