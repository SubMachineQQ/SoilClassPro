from __future__ import annotations

import tkinter as tk

from ..fonts import UI_FONT
from .. import __app_name__, __version__
from ..about import ACKNOWLEDGED, AUTHORS, format_date
from ..assets_path import LOGO_PNG
from ..colors import SPLASH, SPLASH_DARK
from ..i18n import t, upper
from .icon_utils import set_window_icon
from .theme import get_dark_mode
from .scaling import px, work_area

_FONT = UI_FONT
_LOGO_PX = 56
_WIDTH = 790
_WIDTHS = (790, 960, 1140)


def _palette() -> dict:
    return SPLASH_DARK if get_dark_mode() else SPLASH


def _load_logo():
    try:
        img = tk.PhotoImage(file=str(LOGO_PNG))
    except tk.TclError:
        return None
    factor = max(1, round(max(img.width(), img.height()) / _LOGO_PX))
    return img.subsample(factor, factor) if factor > 1 else img


def _build_body(window, pal: dict, wrap: int) -> tk.Frame:
    bg, fg, muted = pal["background"], pal["text"], pal["muted_text"]
    body = tk.Frame(window, background=bg)
    body.pack(fill="both", expand=True, padx=28, pady=(16, 4))

    head = tk.Frame(body, background=bg)
    head.pack(fill="x")
    window._welcome_logo = _load_logo()
    if window._welcome_logo is not None:
        tk.Label(head, image=window._welcome_logo,
                 background=bg).pack(side="left", padx=(0, 16))
    titles = tk.Frame(head, background=bg)
    titles.pack(side="left", fill="x")
    tk.Label(titles, text=__app_name__, font=(_FONT, 20, "bold"),
             fg=fg, background=bg, anchor="w").pack(anchor="w")
    tk.Label(titles,
             text=f"{t('splash_version').format(version=__version__)}"
                  f"   ·   {format_date()}",
             font=(_FONT, 12), fg=muted, background=bg,
             anchor="w").pack(anchor="w")

    tk.Frame(body, height=1, background=pal["accent"]).pack(fill="x",
                                                            pady=(12, 10))

    tk.Label(body, text=t("welcome_thanks"), font=(_FONT, 15, "bold"),
             fg=fg, background=bg, anchor="w",
             justify="left", wraplength=wrap).pack(anchor="w")
    tk.Label(body, text=t("welcome_thanks_body"), font=(_FONT, 11),
             fg=fg, background=bg, anchor="w", justify="left",
             wraplength=wrap).pack(anchor="w", pady=(2, 10))

    tk.Label(body, text=upper(t("welcome_developers")),
             font=(_FONT, 9, "bold"), fg=muted, background=bg,
             anchor="w").pack(anchor="w")
    tk.Label(body, text="  ·  ".join(AUTHORS), font=(_FONT, 11, "bold"),
             fg=fg, background=bg, anchor="w", justify="left",
             wraplength=wrap).pack(anchor="w", pady=(2, 0))
    tk.Label(body, text=t("welcome_institution"), font=(_FONT, 10),
             fg=muted, background=bg, anchor="w", justify="left",
             wraplength=wrap).pack(anchor="w")
    tk.Label(body, text=t("research_program"), font=(_FONT, 10),
             fg=muted, background=bg, anchor="w", justify="left",
             wraplength=wrap).pack(anchor="w")
    tk.Label(body, text=t("research_tribute"), font=(_FONT, 10),
             fg=muted, background=bg, anchor="w", justify="left",
             wraplength=wrap).pack(anchor="w")
    tk.Label(body, text=t("acknowledgement").format(name=ACKNOWLEDGED),
             font=(_FONT, 10, "italic"), fg=muted, background=bg, anchor="w",
             justify="left", wraplength=wrap).pack(anchor="w", pady=(4, 10))

    frame = tk.Frame(body, background=pal["border"])
    frame.pack(fill="x")
    inner = tk.Frame(frame, background=bg)
    inner.pack(fill="both", padx=1, pady=1)
    tk.Label(inner, text=t("welcome_disclaimer_title"),
             font=(_FONT, 11, "bold"), fg=pal["accent"], background=bg,
             anchor="w").pack(anchor="w", padx=14, pady=(10, 2))
    tk.Label(inner, text=t("welcome_disclaimer"), font=(_FONT, 10),
             fg=fg, background=bg, anchor="w", justify="left",
             wraplength=wrap - px(window, 30)).pack(anchor="w", padx=14, pady=(0, 10))

    tk.Label(body, text=t("welcome_license"), font=(_FONT, 9),
             fg=muted, background=bg, anchor="w", justify="left",
             wraplength=wrap).pack(anchor="w", pady=(8, 0))
    return body


def _button(parent, text, command, pal, primary):
    bg = pal["accent"] if primary else pal["background"]
    fg = pal["background"] if primary else pal["text"]
    return tk.Button(parent, text=text, command=command,
                     font=(_FONT, 11, "bold" if primary else "normal"),
                     background=bg, foreground=fg, activebackground=bg,
                     activeforeground=fg, relief="flat", bd=0,
                     highlightthickness=1,
                     highlightbackground=pal["border"],
                     padx=18, pady=7, cursor="hand2")


def _layout(window, pal: dict, add_buttons) -> None:
    buttons = tk.Frame(window, background=pal["background"])
    buttons.pack(side="bottom", fill="x", padx=28, pady=(6, 16))
    add_buttons(buttons)

    left, top, area_w, area_h = work_area(window)
    max_w = int(area_w * 0.94)
    max_h = int(area_h * 0.94)
    body = None
    width = px(window, _WIDTH)
    for width in (px(window, w) for w in _WIDTHS):
        width = min(width, max_w)
        if body is not None:
            body.destroy()
        body = _build_body(window, pal, width - px(window, 70))
        window.update_idletasks()
        if window.winfo_reqheight() <= max_h or width >= max_w:
            break
    height = min(window.winfo_reqheight(), max_h)
    x = left + (area_w - width) // 2
    y = top + max(0, (area_h - height) // 2 - px(window, 20))
    window.geometry(f"{width}x{height}+{x}+{y}")


class WelcomeWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        pal = _palette()
        self.accepted = False
        self.title(f"{__app_name__} — {t('welcome_title')}")
        self.configure(background=pal["background"])
        self.resizable(False, False)
        set_window_icon(self)
        self.protocol("WM_DELETE_WINDOW", self._decline)

        def add_buttons(bar):
            _button(bar, t("welcome_accept"), self._accept, pal,
                    True).pack(side="right")
            _button(bar, t("welcome_exit"), self._decline, pal,
                    False).pack(side="right", padx=(0, 10))

        _layout(self, pal, add_buttons)
        self.bind("<Return>", lambda _e: self._accept())
        self.bind("<Escape>", lambda _e: self._decline())
        self.lift()
        self.attributes("-topmost", True)
        self._topmost_job = self.after(300, self._release_topmost)
        self.focus_force()

    def _release_topmost(self):
        self._topmost_job = None
        self.attributes("-topmost", False)

    def destroy(self):
        if self._topmost_job is not None:
            self.after_cancel(self._topmost_job)
            self._topmost_job = None
        super().destroy()

    def _accept(self):
        self.accepted = True
        self.destroy()

    def _decline(self):
        self.accepted = False
        self.destroy()


class AboutDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        pal = _palette()
        self.title(f"{__app_name__} — {t('about_menu')}")
        self.configure(background=pal["background"])
        self.resizable(False, False)
        set_window_icon(self)
        self.transient(master)

        _layout(self, pal, lambda bar: _button(
            bar, t("about_close"), self.destroy, pal, True).pack(side="right"))
        self.bind("<Escape>", lambda _e: self.destroy())
        self.grab_set()
        self.focus_set()


def ask_acceptance() -> bool:
    window = WelcomeWindow()
    window.mainloop()
    return window.accepted
