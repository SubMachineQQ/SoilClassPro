from __future__ import annotations

import sys
import tkinter as tk
from dataclasses import dataclass
from typing import Callable, List, Optional, Union

if sys.platform == "win32":
    import ctypes


class Separator:
    pass


@dataclass
class MenuItem:
    label: str
    command: Optional[Callable] = None
    accelerator: str = ""
    items: Optional[List["MenuEntry"]] = None
    checked: bool = False


MenuEntry = Union[MenuItem, Separator]

_POINTER_POLL_MS = 150
_CLOSE_GRACE_MS = 200
_HOVER_DEBOUNCE_MS = 80


class DropdownMenu(tk.Toplevel):
    def __init__(self, anchor: tk.Widget, entries: List[MenuEntry], palette):
        super().__init__(anchor.winfo_toplevel())
        self._entries = entries
        self._pal = palette
        self._expanded_path: List[int] = []
        self._row_y = {}
        self._x = anchor.winfo_rootx()
        self._y = anchor.winfo_rooty() + anchor.winfo_height() + 2
        self._anchor_rect = (anchor.winfo_rootx(), anchor.winfo_rooty(),
                             anchor.winfo_rootx() + anchor.winfo_width(),
                             anchor.winfo_rooty() + anchor.winfo_height())
        self._closed = False
        self._poll_job = None
        self._close_job = None
        self._hover_job = None
        self._tint_key = None
        self._tint_widgets = None
        self._tint_base_bg = None
        self._cur_w = 0
        self._cur_h = 0

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(background=palette["surface"])

        self._columns = tk.Frame(self, background=palette["surface"])
        self._columns.place(x=0, y=0)

        self._render()
        self.bind("<Escape>", lambda _e: self.close())
        self.bind("<FocusOut>", lambda _e: self.close())

        self.grab_set()
        self.focus_set()
        self._poll_job = self.after(_POINTER_POLL_MS, self._watch_pointer)

    def _render(self):
        self._tint_key = None
        self._tint_widgets = None
        self._tint_base_bg = None
        for child in self._columns.winfo_children():
            child.destroy()
        self._row_y = {}
        self._col_rects = []

        level_entries = self._entries
        x = y = 0
        col_w, col_h = self._add_column(level_entries, 0, x, y)
        total_w = x + col_w
        total_h = y + col_h

        depth = 0
        for key in self._expanded_path:
            entry = self._find(level_entries, key)
            if entry is None or not entry.items or key not in self._row_y:
                break
            y = self._row_y[key]
            x = x + col_w
            level_entries = entry.items
            depth += 1
            col_w, col_h = self._add_column(level_entries, depth, x, y)
            total_w = max(total_w, x + col_w)
            total_h = max(total_h, y + col_h)

        self._columns.configure(width=total_w, height=total_h)
        self._resize_to_content(total_w, total_h)
        self._apply_shape()

    @staticmethod
    def _find(entries, key):
        for e in entries:
            if not isinstance(e, Separator) and id(e) == key:
                return e
        return None

    def _resize_to_content(self, content_w, content_h):
        if (content_w, content_h) == (self._cur_w, self._cur_h):
            return
        self._cur_w, self._cur_h = content_w, content_h
        self.geometry(f"{content_w}x{content_h}+{self._x}+{self._y}")
        self.update_idletasks()

    def _apply_shape(self):
        if sys.platform != "win32":
            return
        try:
            hwnd = self.winfo_id()
            gdi32 = ctypes.windll.gdi32
            combined = gdi32.CreateRectRgn(0, 0, 0, 0)
            for x0, y0, x1, y1 in self._col_rects:
                piece = gdi32.CreateRectRgn(x0, y0, x1, y1)
                gdi32.CombineRgn(combined, combined, piece, 2)
                gdi32.DeleteObject(piece)
            ctypes.windll.user32.SetWindowRgn(hwnd, combined, True)
        except Exception:
            pass

    _SEP_PADY = 4
    _SEP_HEIGHT = 1
    _COL_BORDER = 1

    def _add_column(self, entries, depth, x, y):
        col = tk.Frame(self._columns, background=self._pal["surface"],
                       highlightthickness=self._COL_BORDER,
                       highlightbackground=self._pal["border"],
                       highlightcolor=self._pal["border"])
        active_key = (self._expanded_path[depth]
                     if depth < len(self._expanded_path) else None)
        cursor_y = 0
        for entry in entries:
            if isinstance(entry, Separator):
                tk.Frame(col, background=self._pal["border"],
                        height=self._SEP_HEIGHT).pack(
                        fill="x", padx=8, pady=self._SEP_PADY)
                cursor_y += self._SEP_HEIGHT + 2 * self._SEP_PADY
                continue
            key = id(entry)
            row = self._add_row(col, entry, key, depth, key == active_key)
            row.update_idletasks()
            self._row_y[key] = y + self._COL_BORDER + cursor_y
            cursor_y += row.winfo_reqheight()
        col.update_idletasks()
        w = col.winfo_reqwidth()
        h = cursor_y + 2 * self._COL_BORDER
        col.place(x=x, y=y, width=w, height=h)
        self._col_rects.append((x, y, x + w, y + h))
        return w, h

    def _add_row(self, col, entry, key, depth, active) -> tk.Frame:
        base_bg = self._pal["note_bg"] if active else self._pal["surface"]
        row = tk.Frame(col, background=base_bg, cursor="hand2")
        row.pack(fill="x")

        prefix = "✓  " if entry.checked else ""
        lbl = tk.Label(row, text=f"{prefix}{entry.label}", font=("Segoe UI", 11),
                       anchor="w", background=base_bg, foreground=self._pal["fg"],
                       padx=12, pady=7)
        lbl.pack(side="left", fill="x", expand=True)

        right_text = "›" if entry.items else entry.accelerator
        right = tk.Label(row, text=right_text, font=("Segoe UI", 9),
                         background=base_bg, foreground=self._pal["muted_fg"], padx=10)
        right.pack(side="right")

        widgets = (row, lbl, right)
        for w in widgets:
            w.bind("<Enter>", lambda _e, k=key, ws=widgets, b=base_bg:
                  self._on_row_enter_tint(k, ws, b))
            w.bind("<Leave>", lambda _e, k=key: self._on_row_leave_tint(k))
            w.bind("<Button-1>", lambda _e, en=entry, k=key, d=depth:
                  self._on_row_click(en, k, d))
            w.bind("<Enter>", lambda _e, en=entry, k=key, d=depth:
                  self._on_row_hover(en, k, d), add="+")
        return row

    def _on_row_enter_tint(self, key, widgets, base_bg):
        if self._tint_key == key:
            return
        if self._tint_widgets is not None:
            self._tint(self._tint_widgets, self._tint_base_bg, self._pal["fg"])
        self._tint(widgets, self._pal["note_bg"], self._pal["accent_dark"])
        self._tint_key = key
        self._tint_widgets = widgets
        self._tint_base_bg = base_bg

    def _on_row_leave_tint(self, key):
        if self._tint_key != key or self._tint_widgets is None:
            return
        self._tint(self._tint_widgets, self._tint_base_bg, self._pal["fg"])
        self._tint_key = None
        self._tint_widgets = None
        self._tint_base_bg = None

    @staticmethod
    def _tint(widgets, bg, fg):
        for w in widgets:
            try:
                w.configure(background=bg)
                if isinstance(w, tk.Label):
                    w.configure(foreground=fg)
            except tk.TclError:
                pass

    def _on_row_click(self, entry, key, depth):
        self._cancel_hover_job()
        if entry.items:
            self._set_expanded(depth, key)
            return
        self.close()
        if entry.command:
            entry.command()

    def _on_row_hover(self, entry, key, depth):
        self._cancel_hover_job()
        if entry.items:
            self._hover_job = self.after(
                _HOVER_DEBOUNCE_MS, lambda: self._set_expanded(depth, key))
        elif len(self._expanded_path) > depth:
            self._hover_job = self.after(
                _HOVER_DEBOUNCE_MS, lambda: self._collapse_to(depth))

    def _cancel_hover_job(self):
        if self._hover_job is not None:
            try:
                self.after_cancel(self._hover_job)
            except tk.TclError:
                pass
            self._hover_job = None

    def _collapse_to(self, depth):
        self._hover_job = None
        if len(self._expanded_path) > depth:
            self._expanded_path = self._expanded_path[:depth]
            self._render()

    def _set_expanded(self, depth, key):
        self._hover_job = None
        new_path = self._expanded_path[:depth] + [key]
        if new_path == self._expanded_path:
            return
        self._expanded_path = new_path
        self._render()

    def _pointer_inside(self) -> bool:
        px, py = self.winfo_pointerx(), self.winfo_pointery()
        rects = (
            self._anchor_rect,
            (self._x, self._y,
             self._x + self._cur_w, self._y + self._cur_h),
        )
        return any(l <= px < r and t <= py < b for l, t, r, b in rects)

    def _watch_pointer(self):
        if self._closed or not self.winfo_exists():
            return
        try:
            inside = self._pointer_inside()
        except tk.TclError:
            inside = True
        if inside:
            if self._close_job is not None:
                try:
                    self.after_cancel(self._close_job)
                except tk.TclError:
                    pass
                self._close_job = None
        elif self._close_job is None:
            self._close_job = self.after(_CLOSE_GRACE_MS, self.close)
        self._poll_job = self.after(_POINTER_POLL_MS, self._watch_pointer)

    def _cancel_jobs(self):
        for job in (self._poll_job, self._close_job, self._hover_job):
            if job is not None:
                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass
        self._poll_job = self._close_job = self._hover_job = None

    def destroy(self):
        self._cancel_jobs()
        super().destroy()

    def close(self):
        if self._closed:
            return
        self._closed = True
        self._cancel_jobs()
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()
