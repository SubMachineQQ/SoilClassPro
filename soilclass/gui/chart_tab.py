from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Sequence

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib import pyplot as plt

from ..colors import CHART
from ..i18n import t
from ..models import SoilSample


_TOOLTIP_KEYS = {"Home": "tb_home", "Back": "tb_back", "Forward": "tb_forward",
                 "Pan": "tb_pan", "Zoom": "tb_zoom", "Subplots": "tb_subplots",
                 "Save": "tb_save"}


class _Toolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, window, **kwargs):
        self.toolitems = [
            (name, t(_TOOLTIP_KEYS[name]) if name in _TOOLTIP_KEYS else tip,
             image, callback)
            for name, tip, image, callback in NavigationToolbar2Tk.toolitems]
        super().__init__(canvas, window, **kwargs)


def _flatten_toolbar(toolbar: tk.Widget, background: str) -> None:
    widgets = [toolbar]
    while widgets:
        widget = widgets.pop()
        for option, value in (("background", background),
                              ("activebackground", background),
                              ("highlightthickness", 0),
                              ("relief", "flat"),
                              ("borderwidth", 0)):
            try:
                widget.configure(**{option: value})
            except tk.TclError:
                pass
        widgets.extend(widget.winfo_children())


class ChartTab(ttk.Frame):
    def __init__(self, master, builder: Callable, placeholder: str, *,
                boundary_options: Optional[Sequence[str]] = None,
                default_boundary: str = "",
                boundary_label: str = "",
                toolbar_extra: Optional[Callable[[tk.Widget], None]] = None):
        super().__init__(master)
        self.builder = builder
        self.placeholder = placeholder
        self.canvas: Optional[FigureCanvasTkAgg] = None
        self.toolbar: Optional[NavigationToolbar2Tk] = None
        self._sample: Optional[SoilSample] = None
        self._toolbar_extra = toolbar_extra

        self.boundary_var: Optional[tk.StringVar] = None
        self._chart_area: tk.Widget = self
        if boundary_options:
            self.boundary_var = tk.StringVar(value=default_boundary)
            bar = ttk.Frame(self, padding=(8, 6, 8, 0))
            bar.pack(side="top", fill="x")
            ttk.Label(bar, text=boundary_label).pack(side="left")
            combo = ttk.Combobox(bar, textvariable=self.boundary_var,
                                 values=list(boundary_options),
                                 state="readonly", width=10)
            combo.pack(side="left", padx=6)
            combo.bind("<<ComboboxSelected>>", lambda _e: self._redraw())
            self._chart_area = ttk.Frame(self)
            self._chart_area.pack(side="top", fill="both", expand=True)

        self._show_placeholder()

    def _clear(self):
        if self.toolbar is not None:
            self.toolbar.destroy()
            self.toolbar = None
        if self.canvas is not None:
            fig = self.canvas.figure
            self.canvas.get_tk_widget().destroy()
            plt.close(fig)
            self.canvas = None
        for child in self._chart_area.winfo_children():
            child.destroy()

    def _show_placeholder(self):
        self._clear()
        ttk.Label(self._chart_area, text=self.placeholder,
                 foreground=CHART["placeholder_text"],
                  font=("Segoe UI", 13)).pack(expand=True)

    def draw(self, sample: SoilSample) -> None:
        self._sample = sample
        self._redraw()

    def _redraw(self):
        if self._sample is None:
            return
        self._clear()
        if self.boundary_var is not None:
            fig = self.builder(self._sample, boundaries=self.boundary_var.get())
        else:
            fig = self.builder(self._sample)
        self.canvas = FigureCanvasTkAgg(fig, master=self._chart_area)
        self.canvas.draw()
        self.toolbar = _Toolbar(self.canvas, self._chart_area,
                                            pack_toolbar=False)
        self.toolbar.update()
        _flatten_toolbar(self.toolbar, CHART["toolbar_bg"])
        self.toolbar.update_idletasks()
        self.toolbar.configure(height=max(
            [50] + [child.winfo_reqheight() + 6
                    for child in self.toolbar.winfo_children()]))
        self.toolbar.pack(side="bottom", fill="x", pady=(4, 0))
        if self._toolbar_extra is not None:
            self._toolbar_extra(self.toolbar)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

    def reset(self) -> None:
        self._sample = None
        self._show_placeholder()
