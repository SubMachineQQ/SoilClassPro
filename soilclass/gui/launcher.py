from __future__ import annotations

import threading
import tkinter as tk
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .. import __app_name__, __version__, project_file, recent_projects, updates
from ..colors import LAUNCHER, LAUNCHER_DARK
from ..i18n import LANGUAGES, get_language, set_language, t
from ..models import SoilSample
from ..standard_info import get_standard_info
from .icon_utils import set_window_icon
from .modes import MODE_TITLE
from .theme import get_dark_mode, set_dark_mode
from .theme_toggle import ThemeToggle
from .widgets import (MONO, UI, MetricCell, StatusPill, hairline,
                      micro_label)
from .scaling import fit_window, px, work_area


def _apply_palette_globals(dark: bool) -> None:
    pal = LAUNCHER_DARK if dark else LAUNCHER
    g = globals()
    g["_SIDEBAR_BG"] = pal["sidebar_bg"]
    g["_SIDEBAR_FG"] = pal["sidebar_fg"]
    g["_SIDEBAR_HOVER"] = pal["sidebar_hover"]
    g["_BORDER"] = pal["sidebar_border"]
    g["_SIDEBAR_HEADER_FG"] = pal["sidebar_header_fg"]
    g["_PANEL_BG"] = pal["panel_bg"]
    g["_PANEL_FG"] = pal["panel_fg"]
    g["_PANEL_MUTED"] = pal["panel_muted"]
    g["_PANEL_DIVIDER"] = pal["panel_divider"]
    g["_FIELD_BG"] = pal["field_bg"]
    g["_FIELD_BORDER"] = pal["field_border"]
    g["_CREATE_BG"] = pal["create_button_bg"]
    g["_CREATE_FG"] = pal["create_button_fg"]
    g["_ACCENT"] = pal["accent"]
    g["_CARD_BG"] = pal["card_bg"]
    g["_CARD_BORDER"] = pal["card_border"]
    g["_CARD_HOVER"] = pal["card_hover"]
    g["_MICRO_FG"] = pal["micro_fg"]
    g["_CHIP_BG"] = pal["chip_bg"]
    g["_STRIP_FG"] = pal["strip_fg"]
    g["_W_PAL"] = {
        "card_bg": g["_CARD_BG"],
        "card_border": g["_CARD_BORDER"],
        "micro_fg": g["_MICRO_FG"],
        "value_fg": g["_PANEL_FG"],
        "accent": g["_ACCENT"],
        "bg": g["_PANEL_BG"],
        "fg": g["_PANEL_FG"],
        "pill_active": pal["pill_active"],
        "pill_review": pal["pill_review"],
        "pill_signed": pal["pill_signed"],
    }


_apply_palette_globals(False)

BUTTON_ORDER = [
    ("New", "CTRL+N", None),
    ("Open", "CTRL+O", None),
    ("ASTM", "D2487", "ASTM"),
    ("BS", "5930", "BS"),
    ("AASHTO", "M 145", "AASHTO"),
    ("TS EN ISO 14688", "ISO 14688-2", "ISO14688"),
    ("RSCS", "REVISED", "RSCS"),
]

_GRID_COLUMNS = 3

_MONTH_ABBR = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "tr": ["Oca", "Şub", "Mar", "Nis", "May", "Haz",
           "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"],
}


def _month_abbr(dt: datetime) -> str:
    return _MONTH_ABBR.get(get_language(), _MONTH_ABBR["en"])[dt.month - 1]

_HOVER_PREVIEW_MS = 80


class LauncherWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        _apply_palette_globals(get_dark_mode())
        self.title(f"{__app_name__} v{__version__} \u2014 "
                  f"{t('launcher_window_title')}")
        fit_window(self, 880, 560, min_width=760, min_height=480)
        self.configure(background=_PANEL_BG)
        set_window_icon(self)

        self.result = None
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._panel_locked = False
        self._hover_preview_job = None
        self._update_release = None
        self._update_result = None
        self._update_done = False
        self._update_job = None
        self._compact = False

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_panel()
        self._show_default()
        self._fit_sidebar()
        self._start_update_check()

    def _sidebar_needed_height(self) -> int:
        self.update_idletasks()
        total = 4
        for child in self._sidebar.pack_slaves():
            pady = child.pack_info().get("pady", 0)
            if isinstance(pady, (tuple, list)):
                pad = sum(int(v) for v in pady)
            elif isinstance(pady, str):
                parts = [int(v) for v in pady.split()]
                pad = sum(parts) if len(parts) > 1 else 2 * parts[0]
            else:
                pad = 2 * int(pady)
            total += child.winfo_reqheight() + pad
        return total

    def _fit_sidebar(self):
        _, _, _, area_h = work_area(self)
        max_h = int(area_h * 0.94)
        needed = self._sidebar_needed_height()
        if needed > max_h and not self._compact:
            self._compact = True
            self._sidebar.destroy()
            self._build_sidebar()
            needed = self._sidebar_needed_height()
        target = min(needed, max_h)
        min_w, min_h = self.minsize()
        self.minsize(min_w, max(min_h, target))
        size, _, position = self.geometry().partition("+")
        width, _, height = size.partition("x")
        if int(height) < target:
            top = max(0, int(position.split("+")[-1]) - (target - int(height)) // 2)
            left = position.split("+")[0]
            self.geometry(f"{width}x{target}+{left}+{top}")

    def _start_update_check(self):
        if not updates.GITHUB_REPO:
            return

        def worker():
            self._update_result = updates.check_for_update()
            self._update_done = True

        threading.Thread(target=worker, daemon=True).start()
        self._update_job = self.after(500, self._poll_update, 0)

    def _poll_update(self, tries: int):
        self._update_job = None
        if not self._update_done:
            if tries < 40:
                self._update_job = self.after(500, self._poll_update, tries + 1)
            return
        self._update_release = self._update_result
        self._render_update_badge()

    def _render_update_badge(self):
        slot = getattr(self, "_update_slot", None)
        release = self._update_release
        if release is None or slot is None or not slot.winfo_exists():
            return
        for child in slot.winfo_children():
            child.destroy()
        badge = tk.Label(slot,
                         text=t("update_available").format(version=release.version),
                         font=(UI, 10, "bold"), background=_SIDEBAR_BG,
                         foreground=_ACCENT, cursor="hand2", anchor="w",
                         justify="left", wraplength=px(self, 190))
        badge.pack(fill="x", pady=(0, 8))
        badge.bind("<Button-1>", lambda _e: webbrowser.open(release.url))

    def _on_close(self):
        self.result = None
        self.destroy()

    def destroy(self):
        self._cancel_hover_preview()
        for name in ("_update_job", "_leave_job"):
            job = getattr(self, name, None)
            if job is not None:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass
                setattr(self, name, None)
        super().destroy()

    def _build_sidebar(self):
        sidebar = tk.Frame(self, width=px(self, 230), background=_SIDEBAR_BG,
                           highlightthickness=1,
                           highlightbackground=_BORDER)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)
        self._sidebar = sidebar

        header = tk.Frame(sidebar, background=_SIDEBAR_BG)
        header.pack(fill="x", padx=16, pady=(16, 12))
        tk.Label(header, text=__app_name__.upper(),
                 font=(UI, 13, "bold"), background=_SIDEBAR_BG,
                 foreground=_SIDEBAR_HEADER_FG, anchor="w").pack(anchor="w")
        tk.Label(header, text=f"v{__version__}  \u00b7  "
                              f"{t('launcher_workspace')}",
                 font=(MONO, 10), background=_SIDEBAR_BG,
                 foreground=_STRIP_FG, anchor="w").pack(anchor="w")

        hairline(sidebar, color=_BORDER, fill="x")

        self._buttons = {}

        actions = tk.Frame(sidebar, background=_SIDEBAR_BG)
        actions.pack(fill="x", pady=(2, 0))
        for label, hint, std_key in BUTTON_ORDER[:2]:
            self._sidebar_button(actions, label, hint, std_key,
                                 primary=True)

        hairline(sidebar, color=_BORDER, fill="x", pady=(10, 0))
        micro_label(sidebar, t("launcher_classification_standard"), bg=_SIDEBAR_BG,
                    fg=_STRIP_FG, anchor="w", fill="x", padx=16,
                    pady=(12, 6))

        self._hover_rows = []

        for label, hint, std_key in BUTTON_ORDER[2:]:
            self._sidebar_button(sidebar, label, hint, std_key)

        self._build_session_block(sidebar)

    def _sidebar_button(self, parent, label, hint, std_key, *,
                        primary=False):
        row = tk.Frame(parent, background=_SIDEBAR_BG, cursor="hand2")
        row.pack(fill="x")

        inner = tk.Frame(row, background=_SIDEBAR_BG)
        gap = 3 if self._compact else 8
        inner.pack(fill="x", padx=16, pady=(gap, gap))

        _DISPLAY = {"New": t("launcher_new"), "Open": t("launcher_open")}
        display_label = _DISPLAY.get(label, label)
        name = tk.Label(inner, text=display_label.upper() if primary else display_label,
                        font=(UI, 14, "bold") if primary else (UI, 13),
                        background=_SIDEBAR_BG,
                        foreground=_ACCENT if primary else _SIDEBAR_FG,
                        anchor="w")
        name.pack(anchor="w")
        kids = (row, inner, name)
        if not primary and not self._compact:
            sub = tk.Label(inner, text=hint, font=(MONO, 10),
                           background=_SIDEBAR_BG, foreground=_STRIP_FG,
                           anchor="w")
            sub.pack(anchor="w")
            kids = (row, inner, name, sub)
        for w in kids:
            w.bind("<Button-1>",
                   lambda _e, l=label, k=std_key: self._on_click(l, k))
            if std_key is not None:
                w.bind("<Enter>",
                       lambda _e, k=std_key, r=row: self._on_hover(k, r))
                w.bind("<Leave>", lambda _e, r=row: self._on_leave(r))
        row._tinted = kids
        self._buttons[label] = row
        if std_key is not None:
            self._hover_rows.append(row)

    def _build_session_block(self, sidebar):
        block = tk.Frame(sidebar, background=_SIDEBAR_BG)
        block.pack(side="bottom", fill="x", padx=16,
                   pady=6 if self._compact else 14)
        self._update_slot = tk.Frame(block, background=_SIDEBAR_BG)
        self._update_slot.pack(fill="x")
        self._render_update_badge()
        hairline(block, color=_BORDER, fill="x", pady=(0, 10))
        for caption, value in ((t("launcher_units"), "SI"),
                               (t("launcher_sieve_set"), "ASTM E11")):
            line = tk.Frame(block, background=_SIDEBAR_BG)
            line.pack(fill="x", pady=1)
            micro_label(line, caption, bg=_SIDEBAR_BG, fg=_STRIP_FG,
                        side="left")
            tk.Label(line, text=value, font=(MONO, 10),
                     background=_SIDEBAR_BG,
                     foreground=_SIDEBAR_FG).pack(side="right")

        self._build_language_row(block)
        self._build_theme_row(block)

    def _build_theme_row(self, block):
        line = tk.Frame(block, background=_SIDEBAR_BG)
        line.pack(fill="x", pady=(6, 0))
        micro_label(line, t("launcher_theme"), bg=_SIDEBAR_BG,
                    fg=_STRIP_FG, side="left")
        ThemeToggle(line, is_dark=get_dark_mode(), bg=_SIDEBAR_BG,
                   command=self._set_theme).pack(side="right")

    def _set_theme(self, dark: bool):
        set_dark_mode(dark)
        self.after_idle(self._rebuild_theme, bool(dark))

    def _rebuild_theme(self, dark: bool):
        if not self.winfo_exists():
            return
        self._cancel_hover_preview()
        _apply_palette_globals(dark)
        for w in self.winfo_children():
            w.destroy()
        self.configure(background=_PANEL_BG)
        self._panel_locked = False
        self._hover_preview_job = None
        self._build_sidebar()
        self._build_panel()
        self._show_default()

    def _build_language_row(self, block):
        line = tk.Frame(block, background=_SIDEBAR_BG)
        line.pack(fill="x", pady=1)
        micro_label(line, t("launcher_language"), bg=_SIDEBAR_BG,
                    fg=_STRIP_FG, side="left")

        values = tk.Frame(line, background=_SIDEBAR_BG)
        values.pack(side="right")
        current = get_language()
        codes = list(LANGUAGES.keys())
        for i, code in enumerate(codes):
            active = code == current
            lbl = tk.Label(values, text=code.upper(), font=(MONO, 10, "bold"),
                           background=_SIDEBAR_BG,
                           foreground=_ACCENT if active else _STRIP_FG,
                           cursor="arrow" if active else "hand2")
            lbl.pack(side="left")
            if not active:
                lbl.bind("<Button-1>", lambda _e, c=code: self._set_language(c))
            if i < len(codes) - 1:
                tk.Label(values, text=" / ", font=(MONO, 10),
                        background=_SIDEBAR_BG,
                        foreground=_STRIP_FG).pack(side="left")

    def _set_language(self, code: str):
        set_language(code)
        for w in self.winfo_children():
            w.destroy()
        self._panel_locked = False
        self._hover_preview_job = None
        self._build_sidebar()
        self._build_panel()
        self._show_default()

    def _build_panel(self):
        container = tk.Frame(self, background=_PANEL_BG)
        container.grid(row=0, column=1, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        canvas = tk.Canvas(container, background=_PANEL_BG,
                          highlightthickness=0, bd=0)
        vsb = ttk.Scrollbar(container, orient="vertical",
                           command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        self.panel = tk.Frame(canvas, background=_PANEL_BG)
        panel_window = canvas.create_window((0, 0), window=self.panel,
                                             anchor="nw")

        def _sync_scrollregion(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        self.panel.bind("<Configure>", _sync_scrollregion)

        def _sync_panel_width(event):
            canvas.itemconfig(panel_window, width=event.width)
        canvas.bind("<Configure>", _sync_panel_width)

        def _wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<MouseWheel>", _wheel)
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        self._panel_canvas = canvas

    def _clear_panel(self):
        for w in self.panel.winfo_children():
            w.destroy()
        self._panel_canvas.yview_moveto(0)

    def _show_default(self):
        self._panel_locked = False
        self._clear_panel()

        recents = recent_projects.get_recent()
        self._panel_header(len(recents))

        if not recents:
            empty = tk.Frame(self.panel, background=_PANEL_BG)
            empty.pack(fill="x", padx=28, pady=(4, 0))
            tk.Label(empty,
                     text=t("launcher_no_recent"),
                     font=(UI, 13, "bold"), background=_PANEL_BG,
                     foreground=_PANEL_FG).pack(anchor="w")
            tk.Label(empty,
                     text=t("launcher_no_recent_help"),
                     justify="left", wraplength=px(self, 460), font=(UI, 13),
                     background=_PANEL_BG,
                     foreground=_PANEL_MUTED).pack(anchor="w", pady=(4, 0))
            return

        self._card_grid(recents)

    def _panel_header(self, count: int):
        head = tk.Frame(self.panel, background=_PANEL_BG)
        head.pack(fill="x", padx=28, pady=(24, 0))

        now = datetime.now()
        tk.Label(head,
                 text=f"// {t('launcher_session_start')}  \u00b7  "
                      + now.strftime(f"%d {_month_abbr(now)} %Y  \u00b7  %H:%M").upper(),
                 font=(MONO, 10), background=_PANEL_BG,
                 foreground=_ACCENT, anchor="w").pack(anchor="w")

        tk.Label(head, text=t("launcher_recent_projects"),
                 font=(UI, 18, "bold"), background=_PANEL_BG,
                 foreground=_PANEL_FG, anchor="w").pack(anchor="w",
                                                        pady=(4, 0))

        noun = t("launcher_dossier") if count == 1 else t("launcher_dossiers")
        tk.Label(head, text=f"{count} {noun}  \u00b7  "
                            f"{t('launcher_resume_or_start')}",
                 font=(MONO, 10), background=_PANEL_BG,
                 foreground=_STRIP_FG, anchor="w").pack(anchor="w",
                                                        pady=(3, 0))

        hairline(self.panel, color=_PANEL_DIVIDER, fill="x",
                 padx=28, pady=(12, 14))

    def _card_grid(self, recents):
        grid = tk.Frame(self.panel, background=_PANEL_BG)
        grid.pack(fill="both", expand=True, padx=22)
        for col in range(_GRID_COLUMNS):
            grid.columnconfigure(col, weight=1, uniform="cards")

        for i, path in enumerate(recents):
            card = self._project_card(grid, path)
            card.grid(row=i // _GRID_COLUMNS, column=i % _GRID_COLUMNS,
                      sticky="nsew", padx=6, pady=6)

        self._panel_footer()

    def _project_card(self, parent, path: str):
        outer = tk.Frame(parent, background=_CARD_BORDER, padx=1, pady=1)
        body = tk.Frame(outer, background=_CARD_BORDER)
        body.pack(fill="both", expand=True)
        tk.Frame(body, background=LAUNCHER["card_accent_border"],
                width=4).pack(side="left", fill="y")
        card = tk.Frame(body, background=_CARD_BG, cursor="hand2")
        card.pack(side="left", fill="both", expand=True)

        meta = self._card_meta(path)

        top = tk.Frame(card, background=_CARD_BG)
        top.pack(fill="x", padx=12, pady=(10, 0))
        micro_label(top, meta["standard"], bg=_CARD_BG, fg=_MICRO_FG,
                    side="left")
        StatusPill(top, meta["state"], _W_PAL, bg=_CARD_BG).pack(side="right")

        title = tk.Label(card, text=meta["title"], font=(UI, 13, "bold"),
                         background=_CARD_BG, foreground=_PANEL_FG,
                         anchor="w", justify="left", wraplength=px(self, 190))
        title.pack(fill="x", padx=12, pady=(6, 0))
        sub = tk.Label(card, text=meta["subtitle"], font=(MONO, 10),
                       background=_CARD_BG, foreground=_MICRO_FG,
                       anchor="w", wraplength=px(self, 190), justify="left")
        sub.pack(fill="x", padx=12, pady=(2, 8))

        hairline(card, color=_CARD_BORDER, fill="x", padx=12)

        metrics = tk.Frame(card, background=_CARD_BG)
        metrics.pack(fill="x", padx=12, pady=8)
        metrics.columnconfigure(0, weight=1, uniform="m")
        metrics.columnconfigure(1, weight=1, uniform="m")
        MetricCell(metrics, t("launcher_group_caption"), meta["group"],
                   _W_PAL, accent=True).grid(row=0, column=0, sticky="w")
        MetricCell(metrics, t("launcher_samples_caption"), meta["samples"],
                   _W_PAL).grid(row=0, column=1, sticky="w")

        foot = tk.Frame(card, background=_CARD_BG)
        foot.pack(fill="x", padx=12, pady=(0, 10))
        tk.Label(foot, text=meta["opened"], font=(MONO, 10),
                 background=_CARD_BG, foreground=_STRIP_FG,
                 anchor="w").pack(side="left")
        tk.Label(foot, text=t("launcher_open_arrow"), font=(MONO, 10, "bold"),
                 background=_CARD_BG, foreground=_ACCENT,
                 anchor="e").pack(side="right")

        widgets = [card, title, sub, metrics, top, foot, *foot.winfo_children()]
        for w in widgets:
            w.bind("<Button-1>", lambda _e, p=path: self._open_path(p))
        return outer

    def _card_meta(self, path: str) -> dict:
        p = Path(path)
        meta = {
            "title": p.stem.replace("_", " ").replace("-", " ").title(),
            "subtitle": str(p.parent),
            "standard": t("launcher_standard_placeholder"),
            "group": "\u2014",
            "samples": "\u2014",
            "state": "ACTIVE",
            "opened": "",
        }
        try:
            stamp = datetime.fromtimestamp(p.stat().st_mtime)
            meta["opened"] = t("launcher_opened_prefix") + " " + stamp.strftime(
                f"%d {_month_abbr(stamp)} \u00b7 %H:%M").upper()
        except OSError:
            meta["opened"] = t("launcher_file_not_found")
            meta["state"] = "REVIEW"

        try:
            sample, mode = project_file.load_project(path)
        except Exception:
            return meta

        meta["standard"] = MODE_TITLE.get(mode, mode).upper()
        if getattr(sample, "project", ""):
            meta["title"] = sample.project
            meta["subtitle"] = sample.name or str(p.parent)
        meta["samples"] = str(len(sample.sieve_data)) if sample.sieve_data \
            else "0"
        if not sample.has_sieve_data:
            meta["state"] = "REVIEW"
            meta["group"] = t("launcher_group_no_data")
        else:
            meta["state"] = "SIGNED"
            meta["group"] = t("launcher_group_ready")
        return meta

    def _panel_footer(self):
        foot = tk.Frame(self.panel, background=_PANEL_BG)
        foot.pack(fill="x", padx=28, pady=(14, 18))
        hairline(foot, color=_PANEL_DIVIDER, fill="x", pady=(0, 8))
        tk.Label(foot,
                 text=t("launcher_moisture_footer"),
                 font=(MONO, 10), background=_PANEL_BG,
                 foreground=_STRIP_FG, anchor="w").pack(side="left")

    def _show_info(self, std_key: str):
        self._clear_panel()
        info = get_standard_info(std_key)
        tk.Label(self.panel, text=info["label"],
                font=("Segoe UI", 19, "bold"), background=_PANEL_BG,
                foreground=_PANEL_FG).pack(anchor="w", padx=28, pady=(28, 2))
        tk.Label(self.panel, text=info["standard"],
                font=("Segoe UI", 12, "italic"), background=_PANEL_BG,
                foreground=_PANEL_MUTED, wraplength=px(self, 480),
                justify="left").pack(anchor="w", padx=28, pady=(0, 18))

        tk.Label(self.panel, text=t("launcher_required_tests"),
                font=("Segoe UI", 13, "bold"), background=_PANEL_BG,
                foreground=_PANEL_FG).pack(anchor="w", padx=28)
        for test_item in info["tests"]:
            tk.Label(self.panel, text=f"\u2022  {test_item}", font=("Segoe UI", 12),
                    background=_PANEL_BG, foreground=_PANEL_FG,
                    wraplength=px(self, 480), justify="left").pack(
                    anchor="w", padx=40, pady=2)

        tk.Label(self.panel, text=t("launcher_required_inputs"),
                font=("Segoe UI", 13, "bold"), background=_PANEL_BG,
                foreground=_PANEL_FG).pack(anchor="w", padx=28, pady=(16, 0))
        for input_item in info["inputs"]:
            tk.Label(self.panel, text=f"\u2022  {input_item}", font=("Segoe UI", 12),
                    background=_PANEL_BG, foreground=_PANEL_FG,
                    wraplength=px(self, 480), justify="left").pack(
                    anchor="w", padx=40, pady=2)

        notes = info.get("notes")
        if notes:
            tk.Label(self.panel, text=t("launcher_worth_knowing"),
                    font=("Segoe UI", 13, "bold"), background=_PANEL_BG,
                    foreground=_PANEL_FG).pack(anchor="w", padx=28,
                                               pady=(16, 0))
            for n in notes:
                tk.Label(self.panel, text=f"\u2022  {n}",
                        font=("Segoe UI", 12, "italic"),
                        background=_PANEL_BG, foreground=_PANEL_MUTED,
                        wraplength=px(self, 480), justify="left").pack(
                        anchor="w", padx=40, pady=2)

    def _show_project_form(self, mode: str):
        self._panel_locked = True
        self._clear_panel()

        back = tk.Label(self.panel, text="\u2190  " + t("launcher_back_to_projects"),
                        font=("Segoe UI", 11, "bold"), background=_PANEL_BG,
                        foreground=_ACCENT, cursor="hand2")
        back.pack(anchor="w", padx=28, pady=(20, 0))
        back.bind("<Button-1>", lambda _e: self._cancel_form())

        title = (t("launcher_all_standards") if mode == "ALL"
                 else MODE_TITLE.get(mode, mode))
        tk.Label(self.panel,
                text=f"{t('launcher_new_project')} \u2014 {title}",
                font=("Segoe UI", 17, "bold"), background=_PANEL_BG,
                foreground=_PANEL_FG).pack(anchor="w", padx=28, pady=(10, 4))
        tk.Frame(self.panel, height=2, width=340,
                background=_PANEL_DIVIDER).pack(anchor="w", padx=28, pady=(0, 18))

        form = tk.Frame(self.panel, background=_PANEL_BG)
        form.pack(anchor="w", padx=28, fill="x")

        fields = [
            (t("launcher_project_name"), "project"),
            (t("launcher_sample_name"), "name"),
            (t("launcher_location"), "location"),
            (t("launcher_tested_by"), "operator"),
            (t("launcher_date"), "date"),
        ]
        entry_vars = {}
        for row, (label, key) in enumerate(fields):
            tk.Label(form, text=f"{label}:", font=("Segoe UI", 12, "bold"),
                    background=_PANEL_BG, foreground=_PANEL_FG,
                    anchor="w").grid(row=row, column=0, sticky="w",
                                     pady=6, padx=(0, 12))
            var = tk.StringVar()
            entry = tk.Entry(form, textvariable=var, font=("Segoe UI", 12),
                             width=34, relief="flat",
                             background=_FIELD_BG, foreground=_PANEL_FG,
                             highlightthickness=1,
                             highlightbackground=_FIELD_BORDER,
                             highlightcolor=_FIELD_BORDER)
            entry.grid(row=row, column=1, sticky="w", pady=6, ipady=4)
            entry_vars[key] = var

        tk.Label(self.panel,
                text=t("launcher_sieve_note"),
                font=("Segoe UI", 11, "italic"), background=_PANEL_BG,
                foreground=_PANEL_MUTED).pack(anchor="w", padx=28,
                                              pady=(14, 18))

        create_btn = tk.Label(self.panel, text=f"  {t('launcher_create_project')}  ",
                              font=("Segoe UI", 13, "bold"),
                              background=_CREATE_BG, foreground=_CREATE_FG,
                              cursor="hand2", padx=10, pady=8)
        create_btn.pack(anchor="w", padx=28)
        create_btn.bind(
            "<Button-1>",
            lambda _e: self._create_project(mode, entry_vars))

    def _cancel_form(self):
        self._panel_locked = False
        self._show_default()

    def _create_project(self, mode: str, entry_vars: dict):
        sample = SoilSample(
            name=entry_vars["name"].get().strip() or "Sample 1",
            project=entry_vars["project"].get().strip(),
            location=entry_vars["location"].get().strip(),
            operator=entry_vars["operator"].get().strip(),
            date=entry_vars["date"].get().strip(),
            sieve_data=[],
        )
        self._launch(mode, preset_sample=sample)

    def _tint_row(self, row, colour):
        for w in getattr(row, "_tinted", (row,)):
            try:
                w.configure(background=colour)
            except tk.TclError:
                pass

    def _on_hover(self, std_key, btn):
        self._tint_row(btn, _SIDEBAR_HOVER)
        if self._panel_locked:
            return
        self._cancel_hover_preview()
        self._hover_preview_job = self.after(
            _HOVER_PREVIEW_MS, lambda k=std_key: self._apply_hover_preview(k))

    def _apply_hover_preview(self, std_key):
        self._hover_preview_job = None
        if self._panel_locked:
            return
        if std_key is None:
            self._show_default()
        else:
            self._show_info(std_key)

    def _cancel_hover_preview(self):
        if self._hover_preview_job is not None:
            try:
                self.after_cancel(self._hover_preview_job)
            except tk.TclError:
                pass
            self._hover_preview_job = None

    def _on_leave(self, btn):
        self._tint_row(btn, _SIDEBAR_BG)
        if self._panel_locked:
            return
        self._leave_job = self.after(30, self._check_pointer_left_sidebar)

    def _check_pointer_left_sidebar(self):
        self._leave_job = None
        if self._panel_locked or not self.winfo_exists():
            return
        x, y = self.winfo_pointerxy()
        widget = self.winfo_containing(x, y)
        while widget is not None:
            if widget in self._hover_rows:
                return
            widget = widget.master if hasattr(widget, "master") else None
        self._cancel_hover_preview()
        self._show_default()

    def _on_click(self, label: str, std_key):
        if label == "Open":
            self._open_dialog()
        elif label == "New":
            self._show_project_form("ALL")
        else:
            self._show_project_form(std_key)

    def _open_dialog(self):
        path = filedialog.askopenfilename(
            title=t("dlg_open_project_title"),
            filetypes=[("SoilClass Pro project", "*.soilpro"),
                       ("All files", "*.*")])
        if path:
            self._open_path(path)

    def _open_path(self, path: str):
        try:
            sample, mode = project_file.load_project(path)
        except ValueError as exc:
            messagebox.showerror(t("dlg_open_failed"), str(exc))
            return
        recent_projects.add_recent(path)
        self._launch(mode, preset_sample=sample)

    def _launch(self, mode: str, preset_sample=None):
        self.result = (mode, preset_sample)
        self.destroy()
