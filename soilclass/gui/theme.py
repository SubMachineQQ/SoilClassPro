from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from ..colors import THEME_DARK as DARK
from ..colors import THEME_LIGHT as LIGHT
from ..colors import Palette
from .scaling import row_height

__all__ = ["LIGHT", "DARK", "Palette", "apply_theme", "UI_FACE", "UI_BODY",
          "get_dark_mode", "set_dark_mode"]

UI_FACE = "Segoe UI"
UI_BODY = 12

STORE_DIR = Path.home() / ".soilclasspro"
STORE_FILE = STORE_DIR / "settings.json"

_dark_mode: bool | None = None


def get_dark_mode() -> bool:
    global _dark_mode
    if _dark_mode is None:
        try:
            data = json.loads(STORE_FILE.read_text(encoding="utf-8"))
            _dark_mode = bool(data.get("dark_mode", False))
        except (OSError, ValueError):
            _dark_mode = False
    return _dark_mode


def set_dark_mode(dark: bool) -> None:
    global _dark_mode
    _dark_mode = bool(dark)
    try:
        STORE_DIR.mkdir(parents=True, exist_ok=True)
        existing = {}
        try:
            existing = json.loads(STORE_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
        existing["dark_mode"] = _dark_mode
        STORE_FILE.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    except OSError:
        pass


def apply_theme(root: tk.Misc, dark: bool = False) -> Palette:
    pal = DARK if dark else LIGHT
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    if hasattr(root, "configure"):
        try:
            root.configure(background=pal["bg"])
        except tk.TclError:
            pass

    style.configure(".", background=pal["bg"], foreground=pal["fg"],
                    fieldbackground=pal["entry_bg"],
                    bordercolor=pal["border"],
                    darkcolor=pal["border"], lightcolor=pal["border"])

    style.configure("TFrame", background=pal["bg"])
    style.configure("TLabel", background=pal["bg"], foreground=pal["fg"],
                    font=(UI_FACE, UI_BODY))

    style.configure("TLabelframe", background=pal["bg"],
                    bordercolor=pal["border"])
    style.configure("TLabelframe.Label", background=pal["bg"],
                    foreground=pal["muted_fg"], font=("Segoe UI", 12, "bold"))

    style.configure("TCheckbutton", background=pal["bg"],
                    foreground=pal["fg"], font=(UI_FACE, UI_BODY))
    style.map("TCheckbutton",
              background=[("active", pal["bg"])],
              foreground=[("active", pal["fg"])])

    style.configure("TButton", background=pal["surface"],
                    foreground=pal["fg"], bordercolor=pal["border"],
                    font=(UI_FACE, 11), padding=(12, 4))
    style.map("TButton", background=[("active", pal["border"])])

    style.configure("Icon.TButton", padding=(6, 4),
                    font=("Segoe UI", 13), background=pal["surface"],
                    foreground=pal["fg"], borderwidth=0, relief="flat")
    style.map("Icon.TButton",
              background=[("active", pal["bg"]), ("pressed", pal["bg"])])

    style.configure("Classify.TButton", padding=(18, 10),
                    font=("Segoe UI", 14, "bold"),
                    background=pal["accent"], foreground=pal["on_accent_fg"],
                    borderwidth=0)
    style.map("Classify.TButton",
              background=[("active", pal["accent_dark"]),
                         ("pressed", pal["accent_dark"])])

    style.configure("Add.TButton", padding=(12, 6),
                    font=("Segoe UI", 11, "bold"),
                    background=pal["add_bg"], foreground=pal["on_accent_fg"],
                    borderwidth=0)
    style.map("Add.TButton", background=[("active", pal["add_bg"])])

    style.configure("Remove.TButton", padding=(12, 6),
                    font=("Segoe UI", 11, "bold"),
                    background=pal["remove_bg"],
                    foreground=pal["on_accent_fg"], borderwidth=0)
    style.map("Remove.TButton", background=[("active", pal["remove_bg"])])

    style.configure("Clear.TButton", padding=(12, 6),
                    font=("Segoe UI", 11, "bold"),
                    background=pal["clear_bg"],
                    foreground=pal["on_accent_fg"], borderwidth=0)
    style.map("Clear.TButton", background=[("active", pal["clear_bg"])])

    style.configure("Toolbar.TButton", padding=(12, 6),
                    font=("Segoe UI", 12, "bold"),
                    background=pal["surface"], foreground=pal["fg"],
                    bordercolor=pal["border"])
    style.map("Toolbar.TButton", background=[("active", pal["border"])])

    style.configure("TEntry", font=(UI_FACE, UI_BODY),
                    fieldbackground=pal["entry_bg"],
                    foreground=pal["fg"], insertcolor=pal["fg"],
                    bordercolor=pal["border"])

    style.configure("TCombobox", fieldbackground=pal["entry_bg"],
                    background=pal["surface"], foreground=pal["fg"],
                    arrowcolor=pal["fg"], bordercolor=pal["border"],
                    lightcolor=pal["border"], darkcolor=pal["border"],
                    selectbackground=pal["entry_bg"],
                    selectforeground=pal["fg"], padding=(6, 3))
    style.map("TCombobox",
              fieldbackground=[("readonly", pal["entry_bg"])],
              foreground=[("readonly", pal["fg"])],
              background=[("readonly", pal["surface"]),
                          ("active", pal["surface"])],
              selectbackground=[("readonly", pal["entry_bg"])],
              selectforeground=[("readonly", pal["fg"])])
    try:
        root.option_add("*TEntry.font", (UI_FACE, UI_BODY))
        root.option_add("*TCombobox.font", (UI_FACE, UI_BODY))
        root.option_add("*TCombobox*Listbox.font", (UI_FACE, UI_BODY))
        root.option_add("*TCombobox*Listbox.background", pal["entry_bg"])
        root.option_add("*TCombobox*Listbox.foreground", pal["fg"])
        root.option_add("*TCombobox*Listbox.selectBackground",
                        pal["select_bg"])
        root.option_add("*TCombobox*Listbox.selectForeground",
                        pal["select_fg"])
    except (AttributeError, tk.TclError):
        pass

    style.configure("TNotebook", background=pal["tab_strip_bg"],
                    bordercolor=pal["border"], tabmargins=(0, 0, 0, 0))
    style.configure("TNotebook.Tab", background=pal["tab_bg_inactive"],
                    foreground=pal["tab_fg_inactive"], padding=(14, 8),
                    bordercolor=pal["border"],
                    font=("Segoe UI", 11, "bold"))
    style.map(
        "TNotebook.Tab",
        background=[("selected", pal["tab_bg_active"]),
                    ("active", pal["tab_bg_hover"])],
        foreground=[("selected", pal["accent_dark"])],
        padding=[("selected", (14, 8)), ("!selected", (14, 8))],
        expand=[("selected", (0, 0, 0, 0)), ("!selected", (0, 0, 0, 0))],
    )

    style.configure("Action.TButton", padding=(18, 8),
                    font=("Segoe UI", 11, "bold"),
                    background=pal["action_bg"], foreground=pal["action_fg"],
                    bordercolor=pal["action_bg"], borderwidth=0,
                    focuscolor=pal["action_bg"], relief="flat")
    style.map("Action.TButton",
             background=[("pressed", pal["action_bg_hover"]),
                        ("active", pal["action_bg_hover"])],
             foreground=[("active", pal["action_fg"]),
                        ("pressed", pal["action_fg"])])

    style.configure("Treeview", font=(UI_FACE, UI_BODY),
                    rowheight=row_height(root, (UI_FACE, UI_BODY)),
                    background=pal["tree_bg"],
                    fieldbackground=pal["tree_bg"], foreground=pal["fg"],
                    bordercolor=pal["border"])
    style.map("Treeview",
              background=[("selected", pal["select_bg"])],
              foreground=[("selected", pal["select_fg"])])
    style.configure("Treeview.Heading", background=pal["tree_header"],
                    foreground=pal["tree_heading_fg"],
                    bordercolor=pal["border"], font=("Segoe UI", 11, "bold"))
    style.map("Treeview.Heading", background=[("active", pal["accent_tint"])])

    style.configure("TScrollbar", background=pal["surface"],
                    troughcolor=pal["bg"], bordercolor=pal["border"],
                    arrowcolor=pal["fg"])
    style.configure("Vertical.TScrollbar", background=pal["surface"])
    style.configure("Horizontal.TScrollbar", background=pal["surface"])

    return pal
