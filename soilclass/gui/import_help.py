from __future__ import annotations

import os
import shutil
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from ..fonts import UI_FONT
from ..assets_path import EXAMPLES_DIR, IMPORT_HELP_DIR
from ..i18n import t
from .icon_utils import set_window_icon
from .scaling import fit_window, px
from .theme import LIGHT, Palette

LAYOUTS = (
    ("1_basit_iki_sutun", "xlsx"),
    ("2_laboratuvar_foyu", "xlsx"),
    ("3_sadece_kalan_kutle", "xlsx"),
    ("4_coklu_numune", "xlsx"),
    ("5_astm_elek_numarasi_en", "xlsx"),
    ("6_yatay_duzen", "xlsx"),
    ("7_noktali_virgul", "csv"),
    ("8_ags4_ornek", "ags"),
)

EXAMPLES_FOLDER = "SoilClassPro_ornek_dosyalar"


def save_examples(parent) -> Optional[Path]:
    target = filedialog.askdirectory(parent=parent,
                                     title=t("import_save_examples"))
    if not target:
        return None
    folder = Path(target) / EXAMPLES_FOLDER
    try:
        folder.mkdir(parents=True, exist_ok=True)
        for stem, ext in LAYOUTS:
            shutil.copy2(EXAMPLES_DIR / f"{stem}.{ext}", folder / f"{stem}.{ext}")
    except OSError as exc:
        messagebox.showerror(t("import_save_examples"), str(exc), parent=parent)
        return None
    messagebox.showinfo(t("import_save_examples"),
                        t("import_examples_saved").format(path=folder),
                        parent=parent)
    if hasattr(os, "startfile"):
        try:
            os.startfile(folder)
        except OSError:
            pass
    return folder


class ImportHelpDialog(tk.Toplevel):
    def __init__(self, master, palette: Palette = LIGHT):
        super().__init__(master)
        self._pal = pal = palette
        self.title(t("import_help_title"))
        self.configure(background=pal["bg"])
        set_window_icon(self)
        fit_window(self, 1040, 760, min_width=780, min_height=600,
                   parent=master)
        self.transient(master)
        self._images = {}

        frame = ttk.Frame(self, padding=(18, 14, 18, 14))
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

        ttk.Label(frame, text=t("import_help_title"),
                  font=(UI_FONT, 15, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w")
        self._intro = ttk.Label(frame, text=t("import_help_intro"),
                                justify="left", foreground=pal["muted_fg"])
        self._intro.grid(row=1, column=0, columnspan=2, sticky="ew",
                         pady=(4, 12))

        self._list = ttk.Treeview(frame, show="tree", selectmode="browse",
                                  height=len(LAYOUTS))
        self._list.column("#0", width=px(self, 250), stretch=False)
        for stem, ext in LAYOUTS:
            self._list.insert("", "end", iid=stem,
                              text=t(f"import_layout_{stem[2:]}"))
        self._list.grid(row=2, column=0, sticky="n", padx=(0, 16))
        self._list.bind("<<TreeviewSelect>>", lambda _e: self._show())

        right = ttk.Frame(frame)
        right.grid(row=2, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(2, weight=1)
        self._name = ttk.Label(right, font=(UI_FONT, 12, "bold"))
        self._name.grid(row=0, column=0, sticky="w")
        self._desc = ttk.Label(right, justify="left")
        self._desc.grid(row=1, column=0, sticky="ew", pady=(2, 10))

        view = tk.Frame(right, background=pal["border"])
        view.grid(row=2, column=0, sticky="nsew")
        view.columnconfigure(0, weight=1)
        view.rowconfigure(0, weight=1)
        self._canvas = tk.Canvas(view, background=pal["bg"],
                                 highlightthickness=0, borderwidth=0)
        ys = ttk.Scrollbar(view, orient="vertical", command=self._canvas.yview)
        xs = ttk.Scrollbar(view, orient="horizontal",
                           command=self._canvas.xview)
        self._canvas.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        self._canvas.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")
        self._image_id = self._canvas.create_image(0, 0, anchor="nw")

        self._tips = ttk.Label(frame, text=t("import_help_tips"),
                               justify="left", font=(UI_FONT, 10))
        self._tips.grid(row=3, column=0, columnspan=2, sticky="ew",
                        pady=(12, 0))

        btns = ttk.Frame(frame)
        btns.grid(row=4, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(btns, text=t("about_close"),
                   command=self.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(btns, text=t("import_save_examples"),
                   style="Action.TButton",
                   command=lambda: save_examples(self)).pack(side="right")

        frame.bind("<Configure>", self._on_resize)
        right.bind("<Configure>", self._on_right_resize)
        self.bind("<Escape>", lambda _e: self.destroy())
        self._list.selection_set(LAYOUTS[0][0])
        self._list.focus(LAYOUTS[0][0])
        self._show()
        self.focus_set()

    def _on_resize(self, event):
        wrap = max(300, event.width - px(self, 40))
        self._intro.configure(wraplength=wrap)
        self._tips.configure(wraplength=wrap)

    def _on_right_resize(self, event):
        self._desc.configure(wraplength=max(240, event.width - px(self, 8)))

    def _image(self, stem: str):
        if stem not in self._images:
            try:
                self._images[stem] = tk.PhotoImage(
                    master=self, file=str(IMPORT_HELP_DIR / f"{stem}.png"))
            except tk.TclError:
                self._images[stem] = None
        return self._images[stem]

    def _show(self):
        selection = self._list.selection()
        if not selection:
            return
        stem = selection[0]
        ext = dict(LAYOUTS)[stem]
        key = stem[2:]
        self._name.configure(text=f"{t(f'import_layout_{key}')}  ·  {stem}.{ext}")
        self._desc.configure(text=t(f"import_layout_{key}_desc"))
        image = self._image(stem)
        self._canvas.itemconfigure(self._image_id, image=image or "")
        if image is not None:
            self._canvas.configure(scrollregion=(0, 0, image.width(),
                                                 image.height()))
        self._canvas.xview_moveto(0)
        self._canvas.yview_moveto(0)
