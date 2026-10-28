from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..fonts import UI_FONT, MONO_FONT
from .. import __app_name__
from ..i18n import t
from ..methods_text import method_sections
from .icon_utils import set_window_icon
from .scaling import fit_window, px
from .theme import LIGHT, Palette

_FONT = UI_FONT
_MONO = MONO_FONT


def _table_lines(rows):
    rows = [[str(c) for c in row if c != ""] or [""] for row in rows]
    count = max(len(r) for r in rows)
    rows = [r + [""] * (count - len(r)) for r in rows]
    widths = [max(len(r[i]) for r in rows) for i in range(count)]

    def line(row):
        return "   ".join(cell.ljust(widths[i]) for i, cell in
                          enumerate(row)).rstrip()

    rule = "   ".join("─" * w for w in widths)
    return [line(rows[0]), rule] + [line(r) for r in rows[1:]]


class MethodsWindow(tk.Toplevel):
    def __init__(self, master, palette: Palette = LIGHT):
        super().__init__(master)
        self._pal = pal = palette
        self.title(f"{__app_name__} — {t('methods_menu')}")
        self.configure(background=pal["bg"])
        set_window_icon(self)
        fit_window(self, 1000, 760, min_width=720, min_height=500,
                   parent=master)

        frame = ttk.Frame(self, padding=(14, 12, 14, 12))
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=t("methods_intro"), justify="left",
                  foreground=pal["muted_fg"]).pack(anchor="w", fill="x")
        self._intro = frame.winfo_children()[-1]
        frame.bind("<Configure>", lambda e: self._intro.configure(
            wraplength=max(300, e.width - px(self, 30))))

        bar = ttk.Frame(frame)
        bar.pack(side="bottom", fill="x", pady=(10, 0))
        ttk.Button(bar, text=t("about_close"), style="Action.TButton",
                   command=self.destroy).pack(side="right")

        self.nb = ttk.Notebook(frame)
        self.nb.pack(fill="both", expand=True, pady=(10, 0))
        self.texts = []
        for title, blocks in method_sections():
            self.nb.add(self._page(blocks), text=title)
        self.bind("<Escape>", lambda _e: self.destroy())
        self.focus_set()

    def _page(self, blocks):
        pal = self._pal
        page = ttk.Frame(self.nb)
        page.columnconfigure(0, weight=1)
        page.rowconfigure(0, weight=1)
        text = tk.Text(page, wrap="word", relief="flat", borderwidth=0,
                       padx=px(self, 20), pady=px(self, 14),
                       background=pal["surface"], foreground=pal["fg"],
                       font=(_FONT, 11), spacing1=2, spacing3=2,
                       cursor="arrow", highlightthickness=0)
        scroll = ttk.Scrollbar(page, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        indent = px(self, 18)
        text.tag_configure("h1", font=(_FONT, 16, "bold"),
                           foreground=pal["accent"], spacing3=px(self, 8))
        text.tag_configure("h2", font=(_FONT, 12, "bold"),
                           foreground=pal["fg"], spacing1=px(self, 14),
                           spacing3=px(self, 4))
        text.tag_configure("p", spacing3=px(self, 6))
        text.tag_configure("b", lmargin1=indent, lmargin2=indent + px(self, 14),
                           spacing3=px(self, 3))
        text.tag_configure("f", font=(_MONO, 11), lmargin1=indent,
                           lmargin2=indent, background=pal["note_bg"],
                           foreground=pal["fg"], spacing1=px(self, 2),
                           spacing3=px(self, 2))
        text.tag_configure("t", font=(_MONO, 11), lmargin1=indent,
                           lmargin2=indent)
        text.tag_configure("th", font=(_MONO, 11, "bold"), lmargin1=indent,
                           lmargin2=indent, foreground=pal["accent"])

        for kind, content in blocks:
            if kind == "b":
                text.insert("end", "•  " + content + "\n", "b")
            elif kind == "f":
                text.insert("end", "\n", "p")
                for line in str(content).split("\n"):
                    text.insert("end", "  " + line + "  \n", "f")
                text.insert("end", "\n", "p")
            elif kind == "t":
                lines = _table_lines(content)
                text.insert("end", "\n", "p")
                text.insert("end", lines[0] + "\n", "th")
                for line in lines[1:]:
                    text.insert("end", line + "\n", "t")
                text.insert("end", "\n", "p")
            else:
                text.insert("end", str(content) + "\n", kind)
        text.configure(state="disabled")
        self.texts.append(text)
        return page
