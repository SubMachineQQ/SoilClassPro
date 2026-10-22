from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)

from .. import project_file
from ..i18n import t
from ..charts.gsd import BOUNDARY_SETS, DEFAULT_BOUNDARIES, gsd_multi_figure
from ..charts.plasticity import (astm_plasticity_multi_figure,
                                 bs_plasticity_multi_figure)
from ..charts.iso14688_chart import iso14688_plasticity_multi_figure
from ..classifiers import classify_all
from ..models import SoilSample
from .icon_utils import enable_maximize_button, set_window_icon
from .theme import LIGHT, Palette
from .scaling import fit_window

_CHARTS = [
    ("compare_chart_gsd", "gsd"),
    ("compare_chart_astm", "astm"),
    ("compare_chart_bs", "bs"),
    ("compare_chart_iso", "iso"),
]


_PLACEHOLDER_NAMES = {"", "sample 1", "sample", "untitled", "soil",
                      "new sample"}


def _display_label(sample: SoilSample, path: Optional[str],
                   taken: set) -> str:
    stem = Path(path).stem if path else ""
    name = (sample.name or "").strip()
    if name.lower() in _PLACEHOLDER_NAMES:
        label = stem or name or "Soil"
    else:
        label = name

    if label in taken:
        if stem and stem not in taken:
            label = stem
        else:
            base, n = label, 2
            while f"{base} ({n})" in taken:
                n += 1
            label = f"{base} ({n})"
    taken.add(label)
    return label


class ComparisonWindow(tk.Toplevel):
    def __init__(self, master, samples: Optional[List[SoilSample]] = None,
                 palette: Palette = LIGHT):
        super().__init__(master)
        self._pal = palette
        self._taken_labels: set = set()
        self.samples: List[SoilSample] = []
        for s in (samples or []):
            s.name = _display_label(s, getattr(s, "source_path", None),
                                    self._taken_labels)
            self.samples.append(s)
        self._canvases = []

        self.title(f"SoilClass Pro \u2014 {t('compare_title')}")
        fit_window(self, 1180, 820, min_width=900, min_height=560,
                   parent=master)
        self.configure(background=palette["bg"])
        set_window_icon(self)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Map>", lambda _e: enable_maximize_button(self))

        self.boundary_var = tk.StringVar(value=DEFAULT_BOUNDARIES)
        self._build_toolbar()
        self._build_body()
        self.refresh()

    def _build_toolbar(self):
        bar = ttk.Frame(self, padding=(10, 8))
        bar.pack(side="top", fill="x")

        ttk.Button(bar, text=t("compare_add_soils"), style="Add.TButton",
                   command=self.add_files).pack(side="left", padx=(0, 6))
        ttk.Button(bar, text=t("compare_remove_selected"), style="Remove.TButton",
                   command=self.remove_selected).pack(side="left", padx=4)
        ttk.Button(bar, text=t("compare_clear"), style="Clear.TButton",
                   command=self.clear_all).pack(side="left", padx=4)

        ttk.Label(bar, text=f"   {t('compare_boundaries')}").pack(side="left")
        combo = ttk.Combobox(bar, textvariable=self.boundary_var,
                             values=list(BOUNDARY_SETS.keys()),
                             state="readonly", width=10)
        combo.pack(side="left", padx=6)
        combo.bind("<<ComboboxSelected>>", lambda _e: self.refresh())

        ttk.Button(bar, text=f"\U0001F4C4  {t('compare_export_pdf')}",
                   style="Toolbar.TButton",
                   command=self.export_pdf).pack(side="right")

    def _build_body(self):
        paned = ttk.Panedwindow(self, orient="vertical")
        paned.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self.nb = ttk.Notebook(paned)
        paned.add(self.nb, weight=3)

        table_frame = ttk.Frame(paned)
        paned.add(table_frame, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(1, weight=1)

        ttk.Label(table_frame, text=t("compare_soils_in_comparison"),
                  font=("Segoe UI", 12, "bold")).grid(row=0, column=0,
                                                      sticky="w", pady=(6, 4))
        cols = ("name", "uscs", "bs", "iso", "aashto", "rscs", "source")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                 height=6)
        for cid, text, w in (("name", t("compare_col_soil"), 190),
                             ("uscs", "USCS", 110),
                             ("bs", "BS 5930", 110), ("iso", "TS EN ISO 14688", 140),
                             ("aashto", "AASHTO", 110),
                             ("rscs", "RSCS", 150),
                             ("source", t("compare_col_source"), 300)):
            self.tree.heading(cid, text=text)
            self.tree.column(cid, width=w, anchor="w")
        self.tree.grid(row=1, column=0, sticky="nsew")
        vsb = ttk.Scrollbar(table_frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

    def add_files(self):
        paths = filedialog.askopenfilenames(
            parent=self,
            title=t("compare_add_dialog_title"),
            filetypes=[("SoilClass Pro project", "*.soilpro"),
                       ("All files", "*.*")])
        added, failed = 0, []
        for path in paths:
            try:
                sample, _mode = project_file.load_project(path)
            except ValueError as exc:
                failed.append(f"{Path(path).name}: {exc}")
                continue
            sample.source_path = path
            sample.name = _display_label(sample, path, self._taken_labels)
            self.samples.append(sample)
            added += 1
        if failed:
            messagebox.showwarning(t("compare_some_failed_title"),
                                   "\n".join(failed), parent=self)
        if added:
            self.refresh()

    def remove_selected(self):
        idx = [self.tree.index(i) for i in self.tree.selection()]
        if not idx:
            return
        for i in sorted(idx, reverse=True):
            if 0 <= i < len(self.samples):
                self._taken_labels.discard(self.samples[i].name)
                self.samples.pop(i)
        self.refresh()

    def clear_all(self):
        self.samples = []
        self._taken_labels.clear()
        self.refresh()

    def _figures(self, *, figsize=(9.4, 6.0)):
        b = self.boundary_var.get()
        return [
            (t("compare_chart_gsd"),
             gsd_multi_figure(self.samples, boundaries=b, figsize=figsize)),
            (t("compare_chart_astm"),
             astm_plasticity_multi_figure(self.samples, figsize=figsize)),
            (t("compare_chart_bs"),
             bs_plasticity_multi_figure(self.samples, figsize=figsize)),
            (t("compare_chart_iso"),
             iso14688_plasticity_multi_figure(self.samples, figsize=figsize)),
        ]

    def _clear_canvases(self):
        for canvas in self._canvases:
            fig = canvas.figure
            canvas.get_tk_widget().destroy()
            plt.close(fig)
        self._canvases = []
        for tab in self.nb.tabs():
            self.nb.forget(tab)

    def refresh(self):
        self._clear_canvases()

        for label, fig in self._figures():
            frame = ttk.Frame(self.nb)
            self.nb.add(frame, text=f"  {label}  ")
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            toolbar = NavigationToolbar2Tk(canvas, frame, pack_toolbar=False)
            toolbar.update()
            toolbar.pack(side="bottom", fill="x")
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
            self._canvases.append(canvas)

        for item in self.tree.get_children():
            self.tree.delete(item)
        for s in self.samples:
            syms = {}
            try:
                for r in classify_all(s):
                    key = r.system.split(" ")[0].lower()
                    syms[key] = r.symbol
            except Exception:
                pass
            self.tree.insert(
                "", "end",
                values=(s.name or t("compare_unnamed"),
                        syms.get("uscs", "-"), syms.get("british", "-"),
                        syms.get("ts", "-"), syms.get("aashto", "-"),
                        syms.get("rscs", "-"),
                        Path(getattr(s, "source_path", "")).name
                        or t("compare_current_project")))

    def export_pdf(self):
        if not self.samples:
            messagebox.showinfo(t("compare_nothing_to_export_title"),
                                t("compare_nothing_to_export_body"),
                                parent=self)
            return
        path = filedialog.asksaveasfilename(
            parent=self, title=t("compare_save_charts_title"),
            defaultextension=".pdf",
            initialfile="SoilClassPro_comparison.pdf",
            filetypes=[("PDF files", "*.pdf")])
        if not path:
            return
        from matplotlib.backends.backend_pdf import PdfPages
        from ..report.pdf_report import PAGE_LANDSCAPE, _finalize_page
        try:
            with PdfPages(path) as pdf:
                for _label, fig in self._figures(figsize=PAGE_LANDSCAPE):
                    fig.subplots_adjust(top=0.85)
                    _finalize_page(fig, page=PAGE_LANDSCAPE)
                    pdf.savefig(fig)
                    plt.close(fig)
        except OSError as exc:
            messagebox.showerror(t("compare_export_failed_title"), str(exc),
                                 parent=self)
            return
        messagebox.showinfo(t("compare_charts_exported_title"),
                            t("compare_charts_exported_body").format(path=path),
                            parent=self)

    def _on_close(self):
        self._clear_canvases()
        plt.close("all")
        self.destroy()
