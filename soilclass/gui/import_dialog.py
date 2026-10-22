from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Optional

from ..i18n import t
from ..importers.table_parser import ParsedData
from ..importers.universal import method_label
from .theme import LIGHT, Palette
from .scaling import fit_window, px


class ImportReviewDialog(tk.Toplevel):
    def __init__(self, master, data: ParsedData, palette: Palette = LIGHT):
        super().__init__(master)
        self._pal = pal = palette
        self.configure(background=pal["bg"])
        self.title(t("import_review_title").format(
            source=data.source or t("import_review_source_default")))
        fit_window(self, 600, 600, min_width=500, min_height=460,
                   parent=master)
        self.transient(master)
        self.grab_set()
        self.result: Optional[ParsedData] = None
        self._samples: List[ParsedData] = [data] + list(data.others)
        self._data = data

        frame = ttk.Frame(self, padding=14)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(4, weight=1)

        ttk.Label(frame, text=t("import_review_instructions"),
                  font=("Segoe UI", 12, "bold"), wraplength=px(self, 520),
                  justify="left").grid(row=0, column=0, sticky="w")

        top = ttk.Frame(frame)
        top.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        if len(self._samples) > 1:
            ttk.Label(top, text=t("import_samples_found").format(
                count=len(self._samples))).pack(anchor="w")
            row = ttk.Frame(top)
            row.pack(anchor="w", pady=(4, 0))
            ttk.Label(row, text=t("import_sample")).pack(side="left")
            self._sample_var = tk.StringVar()
            names = [self._sample_name(s, i) for i, s in enumerate(self._samples)]
            combo = ttk.Combobox(row, textvariable=self._sample_var,
                                 values=names, state="readonly", width=32)
            combo.current(0)
            combo.pack(side="left", padx=(6, 0))
            combo.bind("<<ComboboxSelected>>",
                       lambda _e: self._show(self._samples[combo.current()]))
        self._method_var = tk.StringVar()
        ttk.Label(top, textvariable=self._method_var, foreground=pal["muted_fg"],
                  wraplength=px(self, 520), justify="left").pack(anchor="w", pady=(6, 0))

        self._warn = tk.Text(frame, height=3, wrap="word",
                             background=pal["warn_bg"], foreground=pal["fg"],
                             relief="flat", font=("Segoe UI", 11))
        self._warn_row = 2

        cols = ("size", "passing")
        box = ttk.Frame(frame)
        box.grid(row=4, column=0, sticky="nsew", pady=(8, 0))
        box.columnconfigure(0, weight=1)
        box.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(box, columns=cols, show="headings")
        self.tree.heading("size", text=t("import_review_size_col"))
        self.tree.heading("passing", text=t("import_review_passing_col"))
        self.tree.column("size", width=180, anchor="center")
        self.tree.column("passing", width=180, anchor="center")
        scroll = ttk.Scrollbar(box, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<Double-1>", self._edit_cell)

        ttk.Button(frame, text=t("import_review_delete_rows"),
                   command=self._delete_rows).grid(row=5, column=0,
                                                   sticky="w", pady=(6, 10))

        att = ttk.Frame(frame)
        att.grid(row=6, column=0, sticky="w")
        ttk.Label(att, text=t("import_review_ll")).pack(side="left")
        self.ll_var = tk.StringVar()
        ttk.Entry(att, textvariable=self.ll_var, width=8).pack(
            side="left", padx=(4, 16))
        ttk.Label(att, text=t("import_review_pl")).pack(side="left")
        self.pl_var = tk.StringVar()
        ttk.Entry(att, textvariable=self.pl_var, width=8).pack(
            side="left", padx=4)

        btns = ttk.Frame(frame)
        btns.grid(row=7, column=0, sticky="e", pady=(12, 0))
        ttk.Button(btns, text=t("import_review_cancel"),
                   command=self.destroy).pack(side="right", padx=4)
        ttk.Button(btns, text=t("import_review_apply"), style="Action.TButton",
                   command=self._apply).pack(side="right", padx=4)

        self._show(data)
        self.bind("<Escape>", lambda _e: self.destroy())
        self.wait_visibility()
        self.focus_set()

    @staticmethod
    def _sample_name(sample: ParsedData, index: int) -> str:
        name = str(sample.meta.get("name") or "").strip()
        return name or f"{t('chart_sample')} {index + 1}"

    def _show(self, sample: ParsedData) -> None:
        self._data = sample
        for item in self.tree.get_children():
            self.tree.delete(item)
        for d, p in sample.sieve:
            self.tree.insert("", "end", values=(f"{d:g}", f"{p:g}"))
        self.ll_var.set("" if sample.liquid_limit is None
                        else f"{sample.liquid_limit:g}")
        self.pl_var.set("" if sample.plastic_limit is None
                        else f"{sample.plastic_limit:g}")
        self._method_var.set(method_label(sample.meta.get("_method")))
        self._warn.configure(state="normal")
        self._warn.delete("1.0", "end")
        if sample.warnings:
            self._warn.insert("1.0", "\n".join("⚠  " + w
                                                for w in sample.warnings))
            self._warn.configure(height=min(6, len(sample.warnings) * 2))
            self._warn.grid(row=self._warn_row, column=0, sticky="ew",
                            pady=(8, 0))
        else:
            self._warn.grid_remove()
        self._warn.configure(state="disabled")

    def _delete_rows(self):
        for item in self.tree.selection():
            self.tree.delete(item)

    def _edit_cell(self, event):
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not item or col not in ("#1", "#2"):
            return
        x, y, w, h = self.tree.bbox(item, col)
        idx = 0 if col == "#1" else 1
        old = self.tree.item(item, "values")[idx]
        var = tk.StringVar(value=old)
        entry = ttk.Entry(self.tree, textvariable=var, justify="center")
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus_set()
        entry.select_range(0, "end")

        def finish(_e=None):
            txt = var.get().strip().replace(",", ".")
            try:
                val = float(txt)
                vals = list(self.tree.item(item, "values"))
                vals[idx] = f"{val:g}"
                self.tree.item(item, values=vals)
            except ValueError:
                pass
            entry.destroy()

        entry.bind("<Return>", finish)
        entry.bind("<FocusOut>", finish)
        entry.bind("<Escape>", lambda _e: entry.destroy())

    def _apply(self):
        rows = []
        for item in self.tree.get_children():
            d, p = self.tree.item(item, "values")
            try:
                d, p = float(d), float(p)
            except ValueError:
                continue
            if d > 0 and 0 <= p <= 100:
                rows.append((d, p))
        if len(rows) < 2:
            messagebox.showerror(t("import_review_not_enough_title"),
                                 t("import_review_not_enough_body"),
                                 parent=self)
            return

        def parse(var):
            txt = var.get().strip().replace(",", ".")
            if not txt:
                return None
            try:
                return float(txt)
            except ValueError:
                return None

        self.result = ParsedData(sieve=sorted(rows, key=lambda x: -x[0]),
                                 liquid_limit=parse(self.ll_var),
                                 plastic_limit=parse(self.pl_var),
                                 source=self._data.source,
                                 meta=dict(self._data.meta))
        self.destroy()
