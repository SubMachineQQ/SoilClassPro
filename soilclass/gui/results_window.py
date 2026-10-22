from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import List, Sequence, Tuple

from matplotlib import pyplot as plt

from .. import __app_name__
from ..charts import gsd_figure
from ..charts.gsd import BOUNDARY_SETS, DEFAULT_BOUNDARIES
from ..classifiers import ClassificationResult
from ..i18n import t
from ..models import SoilSample
from .chart_tab import ChartTab
from .icon_utils import enable_maximize_button, set_window_icon
from .results_tab import ResultsTab
from .scaling import fit_window
from .theme import LIGHT, Palette


class ResultsWindow(tk.Toplevel):
    def __init__(self, master, palette: Palette = LIGHT, *, on_export_pdf=None):
        super().__init__(master)
        self.palette = palette
        self._on_export_pdf = on_export_pdf
        self.title(f"{__app_name__} — {t('tab_results')}")
        fit_window(self, 1180, 820, min_width=900, min_height=560,
                   parent=master)
        self.configure(background=palette["bg"])
        set_window_icon(self)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Map>", lambda _e: enable_maximize_button(self))

        footer = tk.Frame(self, background=palette["bg"])
        footer.pack(side="bottom", fill="x", padx=12, pady=(0, 12))
        tk.Frame(footer, height=1,
                 background=palette["border"]).pack(fill="x", pady=(0, 10))
        ttk.Button(footer, text=t("results_export_pdf"),
                   style="Action.TButton",
                   command=self._export_pdf).pack(side="right")

        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=12, pady=(12, 10))

        self.results_tab = ResultsTab(self.nb, palette)
        self.nb.add(self.results_tab, text=t("tab_results"))
        self.chart_tabs: List[Tuple[str, ChartTab]] = []

    def refresh(self, sample: SoilSample, results: List[ClassificationResult],
               chart_defs: Sequence[Tuple[str, object]]) -> None:
        for _, tab in self.chart_tabs:
            tab.reset()
            self.nb.forget(tab)
        self.chart_tabs = []

        placeholder = ""
        for label, builder in chart_defs:
            if builder is gsd_figure:
                tab = ChartTab(self.nb, builder, placeholder,
                              boundary_options=list(BOUNDARY_SETS.keys()),
                              default_boundary=DEFAULT_BOUNDARIES,
                              boundary_label=t("compare_boundaries"))
            else:
                tab = ChartTab(self.nb, builder, placeholder)
            self.nb.add(tab, text=label)
            tab.draw(sample)
            self.chart_tabs.append((label, tab))

        self.results_tab.show(sample, results)
        self.nb.select(self.results_tab)

        self.deiconify()
        self.lift()
        self.focus_set()

    def _export_pdf(self) -> None:
        if self._on_export_pdf is not None:
            self._on_export_pdf()

    def _on_close(self) -> None:
        for _, tab in self.chart_tabs:
            tab.reset()
        plt.close("all")
        self.destroy()
