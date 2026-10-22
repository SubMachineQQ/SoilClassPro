from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk
from typing import List, Optional

from ..classifiers import ClassificationResult
from ..i18n import t
from ..models import SoilSample, conventions_for_systems
from .theme import LIGHT, UI_BODY, UI_FACE, Palette
from .scaling import px
from .widgets import MONO, UI, ValueBox, micro_label


class ResultsTab(ttk.Frame):
    def __init__(self, master, palette: Palette = LIGHT):
        super().__init__(master, padding=12)
        self.results: List[ClassificationResult] = []
        self._pal = palette

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(4, weight=1)

        self._build_hero()

        ttk.Label(self, text=t("results_classification_summary"),
                  font=("Segoe UI", 13, "bold")).grid(row=1, column=0,
                                                      sticky="w")

        cols = ("system", "symbol", "name")
        self.tree = ttk.Treeview(self, columns=cols, show="headings",
                                 height=6)
        for cid, text, w in (("system", t("results_system"), 240),
                             ("symbol", t("results_group_symbol"), 140),
                             ("name", t("results_group_name"), 420)):
            self.tree.heading(cid, text=text)
            self.tree.column(cid, width=px(self, w), anchor="w",
                             stretch=cid == "name")
        self.tree.grid(row=2, column=0, sticky="nsew", pady=(4, 10))
        self.tree.bind("<<TreeviewSelect>>", self._show_detail)

        ttk.Label(self, text=t("results_decision_trail"),
                  font=("Segoe UI", 13, "bold")).grid(row=3, column=0,
                                                      sticky="w")
        detail_box = ttk.Frame(self)
        detail_box.grid(row=4, column=0, sticky="nsew", pady=(4, 0))
        detail_box.columnconfigure(0, weight=1)
        detail_box.rowconfigure(0, weight=1)
        self.detail = tk.Text(detail_box, height=12, wrap="word",
                              font=("Consolas", 12), relief="flat")
        detail_scroll = ttk.Scrollbar(detail_box, orient="vertical",
                                      command=self.detail.yview)
        self.detail.configure(yscrollcommand=detail_scroll.set)
        self.detail.grid(row=0, column=0, sticky="nsew")
        detail_scroll.grid(row=0, column=1, sticky="ns")
        self.detail.configure(state="disabled")

        self._apply_widget_colors()

    def _build_hero(self):
        pal = self._pal
        self._hero = tk.Frame(self, background=pal["bg"])
        self._hero.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        self._hero_box = ValueBox(self._hero, "\u2014", pal, size=26,
                                  accent=True, outline=True, width=5)
        self._hero_box.pack(side="left")

        side = tk.Frame(self._hero, background=pal["bg"])
        side.pack(side="left", fill="both", padx=14)
        self._hero_caption = micro_label(side, t("results_hero_primary"),
                                         bg=pal["bg"], fg=pal["micro_fg"],
                                         anchor="w", fill="x")
        self._hero_name = tk.Label(side, text=t("results_hero_placeholder"),
                                   font=(UI, 13, "bold"),
                                   background=pal["bg"], foreground=pal["fg"],
                                   anchor="w", justify="left")
        self._hero_name.pack(anchor="w", pady=(2, 6))
        self._hero_others = tk.Label(side, text="", font=(MONO, 10),
                                     background=pal["bg"],
                                     foreground=pal["micro_fg"], anchor="w",
                                     justify="left")
        self._hero_others.pack(anchor="w")
        self._hero.bind("<Configure>", lambda event: self._hero_others.configure(
            wraplength=max(240, event.width - self._hero_box.winfo_reqwidth()
                           - px(self, 40))))

    def _fit_columns(self, results: List[ClassificationResult]) -> None:
        body = tkfont.Font(self, font=(UI_FACE, UI_BODY))
        head = tkfont.Font(self, font=(UI_FACE, UI_BODY, "bold"))
        pad = px(self, 28)
        for cid, title, attr in (("system", t("results_system"), "system"),
                                 ("symbol", t("results_group_symbol"), "symbol")):
            width = max([head.measure(title)]
                        + [body.measure(getattr(r, attr) or "") for r in results])
            self.tree.column(cid, width=width + pad, minwidth=width + pad)

    def _update_hero(self) -> None:
        if not self.results:
            self._hero_box.set("\u2014")
            self._hero_name.configure(text=t("results_hero_placeholder"))
            self._hero_others.configure(text="")
            return
        primary = self.results[0]
        self._hero_box.set(primary.symbol or "\u2014")
        self._hero_name.configure(text=primary.name or primary.system)
        others = "   ".join(
            f"{r.system.upper()}: {r.symbol}".replace(" ", " ")
            for r in self.results[1:] if r.symbol)
        self._hero_others.configure(text=others)

    def apply_palette(self, palette: Palette) -> None:
        self._pal = palette
        self._apply_widget_colors()

    def _apply_widget_colors(self) -> None:
        pal = self._pal
        self.detail.configure(background=pal["surface"],
                              foreground=pal["fg"],
                              insertbackground=pal["fg"])
        if hasattr(self, "_hero"):
            for widget, fg in ((self._hero_name, pal["fg"]),
                               (self._hero_others, pal["micro_fg"])):
                widget.configure(background=pal["bg"], foreground=fg)
            self._hero.configure(background=pal["bg"])
            for child in self._hero.winfo_children():
                if isinstance(child, tk.Frame) and child is not self._hero_box:
                    child.configure(background=pal["bg"])
            self._hero_box.apply_palette(pal)
            if hasattr(self, "_hero_caption"):
                self._hero_caption.configure(background=pal["bg"],
                                             foreground=pal["micro_fg"])

    def show(self, sample: SoilSample,
             results: List[ClassificationResult]) -> None:
        self.results = results
        for item in self.tree.get_children():
            self.tree.delete(item)
        for r in results:
            self.tree.insert("", "end",
                             values=(r.system, r.symbol, r.name))
        self._fit_columns(results)
        self._update_hero()
        self._set_detail(self._all_text(sample))

    def clear(self) -> None:
        self.results = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._update_hero()
        self._set_detail(t("results_hero_placeholder"))

    def _all_text(self, sample: Optional[SoilSample]) -> str:
        parts = []
        if sample is not None:
            parts.append(t("pdf_index_properties"))
            parts.append("-" * 60)
            for k, v in sample.summary_rows(conventions_for_systems(
                    [r.system for r in self.results])):
                parts.append(f"  {k:<38} {v}")
            parts.append("")
        for r in self.results:
            parts.append(r.as_text())
            parts.append("")
        return "\n".join(parts)

    def _show_detail(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        idx = self.tree.index(sel[0])
        if 0 <= idx < len(self.results):
            self._set_detail(self.results[idx].as_text())

    def _set_detail(self, text: str):
        self.detail.configure(state="normal")
        self.detail.delete("1.0", "end")
        self.detail.insert("1.0", text)
        self.detail.configure(state="disabled")
