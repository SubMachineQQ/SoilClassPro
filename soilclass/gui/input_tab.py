from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Tuple

from ..example_data import example_sample
from ..i18n import t
from ..models import ASTM_SIZES, SoilSample
from .icon_utils import set_window_icon
from .theme import LIGHT
from .widgets import MONO, MetricCell, hairline, micro_label
from .scaling import px


class InputTab(ttk.Frame):
    def __init__(self, master, on_change=None):
        super().__init__(master, padding=12)
        self.on_change = on_change
        self._undo_stack: List[List[Tuple[float, float]]] = []

        self.meta_vars = {key: tk.StringVar() for key in
                          ("name", "project", "location", "operator",
                           "date")}

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._pal = dict(LIGHT)

        self._build_entry_row()
        self._build_table()
        self._build_atterberg()
        self._build_rscs()
        self._build_metrics_rail()

    def _build_entry_row(self):
        ctrl = ttk.Frame(self)
        ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        fields = ttk.Frame(ctrl)
        ttk.Label(fields, text=f"{t('input_sieve_size')} (mm):",
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        self.size_var = tk.StringVar()
        e1 = ttk.Entry(fields, textvariable=self.size_var, width=10)
        e1.pack(side="left", padx=(6, 16))
        ttk.Label(fields, text=f"{t('input_cumulative_passing')} (%):",
                 font=("Segoe UI", 12, "bold")).pack(side="left")
        self.pass_var = tk.StringVar()
        e2 = ttk.Entry(fields, textvariable=self.pass_var, width=10)
        e2.pack(side="left", padx=(6, 16))
        e2.bind("<Return>", lambda _e: self.add_row())

        buttons = ttk.Frame(ctrl)
        ttk.Button(buttons, text=t("input_add"), style="Add.TButton",
                   command=self.add_row).pack(side="left", padx=3)
        ttk.Button(buttons, text=t("input_remove"), style="Remove.TButton",
                   command=self.remove_selected).pack(side="left", padx=3)
        ttk.Button(buttons, text=t("input_clear"), style="Clear.TButton",
                   command=self.clear_table).pack(side="left", padx=3)

        self._entry_fields = fields
        self._entry_buttons = buttons
        self._entry_stacked = None
        self._layout_entry_row(stacked=False)
        ctrl.bind("<Configure>", self._on_entry_row_resize)

    def _layout_entry_row(self, stacked: bool) -> None:
        if stacked == self._entry_stacked:
            return
        self._entry_stacked = stacked
        self._entry_fields.pack_forget()
        self._entry_buttons.pack_forget()
        if stacked:
            self._entry_fields.pack(side="top", anchor="w")
            self._entry_buttons.pack(side="top", anchor="w", pady=(6, 0))
        else:
            self._entry_fields.pack(side="left")
            self._entry_buttons.pack(side="left")

    def _on_entry_row_resize(self, event) -> None:
        needed = (self._entry_fields.winfo_reqwidth()
                  + self._entry_buttons.winfo_reqwidth())
        self._layout_entry_row(stacked=event.width < needed)

    def _build_table(self):
        box = ttk.Frame(self)
        box.grid(row=1, column=0, sticky="nsew")
        box.columnconfigure(0, weight=1)
        box.rowconfigure(0, weight=1)

        cols = ("size", "passing")
        self.tree = ttk.Treeview(box, columns=cols, show="headings",
                                 height=12)
        self.tree.heading("size", text=f"{t('input_particle_size')} (mm)")
        self.tree.heading("passing", text=f"{t('input_percent_passing')} (%)")
        self.tree.column("size", width=170, anchor="center")
        self.tree.column("passing", width=170, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(box, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        self.tree.bind("<Double-1>", self._edit_cell)

    def _build_atterberg(self):
        box = ttk.LabelFrame(self, text=f" {t('input_atterberg_box_title')} ",
                             padding=10)
        box.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.ll_var = tk.StringVar()
        self.pl_var = tk.StringVar()
        self.organic_var = tk.BooleanVar(value=False)
        self.np_var = tk.BooleanVar(value=False)

        ttk.Label(box, text=f"{t('input_liquid_limit')} LL (%):").grid(
            row=0, column=0, sticky="e", padx=4)
        self.ll_entry = ttk.Entry(box, textvariable=self.ll_var, width=10)
        self.ll_entry.grid(row=0, column=1, padx=(0, 16))
        ttk.Label(box, text=f"{t('input_plastic_limit')} PL (%):").grid(
            row=0, column=2, sticky="e", padx=4)
        self.pl_entry = ttk.Entry(box, textvariable=self.pl_var, width=10)
        self.pl_entry.grid(row=0, column=3, padx=(0, 16))
        for entry in (self.ll_entry, self.pl_entry):
            entry.bind("<KeyPress>", self._untick_np_on_typing, add="+")
        ttk.Checkbutton(box, text=f"{t('input_non_plastic')} (NP)",
                        variable=self.np_var).grid(row=0, column=4, padx=8)
        ttk.Checkbutton(box, text=t("input_organic_soil"),
                        variable=self.organic_var).grid(row=0, column=5,
                                                        padx=8)

        self.pi_var = tk.StringVar(value="PI \u2014")
        self.aline_var = tk.StringVar(value="")
        info = ttk.Frame(box)
        info.grid(row=1, column=0, columnspan=6, sticky="w", padx=4,
                  pady=(8, 0))
        ttk.Label(info, textvariable=self.pi_var,
                  font=(MONO, 12, "bold")).pack(side="left")
        ttk.Label(info, textvariable=self.aline_var,
                  font=(MONO, 10)).pack(side="left", padx=(14, 0))

        for var in (self.ll_var, self.pl_var):
            var.trace_add("write", lambda *_a: self._refresh_plasticity())
        self.np_var.trace_add("write",
                              lambda *_a: self._refresh_plasticity())
        self._refresh_plasticity()

    def _untick_np_on_typing(self, event):
        if event.keysym in ("Tab", "ISO_Left_Tab", "Shift_L", "Shift_R",
                            "Control_L", "Control_R", "Alt_L", "Alt_R",
                            "Left", "Right", "Home", "End", "Return"):
            return
        if self.np_var.get():
            self.np_var.set(False)

    def _refresh_plasticity(self):
        if self.np_var.get():
            self.pi_var.set(t("input_non_plastic_tag"))
            self.aline_var.set("")
            return
        try:
            ll = float(self.ll_var.get().strip().replace(",", "."))
            pl = float(self.pl_var.get().strip().replace(",", "."))
        except ValueError:
            self.pi_var.set("PI \u2014")
            self.aline_var.set("")
            return
        pi = max(ll - pl, 0.0)
        self.pi_var.set(f"PI {pi:.1f}")
        a_line = 0.73 * (ll - 20.0)
        position = (t("input_above_a_line") if pi > a_line
                   else t("input_below_a_line"))
        self.aline_var.set(f"{t('input_a_line_pi')} {a_line:.1f}  \u00b7  {position}")

    @property
    def _FRACTION_ROWS(self):
        return [
            (t("rail_gravel"), "gravel"),
            (t("rail_sand"), "sand"),
            (t("rail_fines"), "fines"),
        ]
    _GRADATION_ROWS = [
        ("D60 mm", "d60"),
        ("D30 mm", "d30"),
        ("D10 mm", "d10"),
        ("Cu", "cu"),
        ("Cc", "cc"),
    ]

    def _build_metrics_rail(self):
        pal = self._pal
        rail = tk.Frame(self, background=pal["rail_bg"], width=px(self, 230))
        rail.grid(row=0, column=1, rowspan=5, sticky="ns", padx=(12, 0))
        rail.grid_propagate(False)
        rail.pack_propagate(False)
        self._rail = rail

        head = tk.Frame(rail, background=pal["rail_bg"])
        head.pack(fill="x", padx=12, pady=(12, 0))
        micro_label(head, t("rail_points_logged"), bg=pal["rail_bg"],
                    fg=pal["micro_fg"], anchor="w", fill="x")
        self._rows_lbl = tk.Label(head, text="0", font=(MONO, 16, "bold"),
                                  background=pal["rail_bg"],
                                  foreground=pal["value_fg"], anchor="w")
        self._rows_lbl.pack(anchor="w")

        self._metric_cells = {}
        for title, rows in ((t("rail_fractions"), self._FRACTION_ROWS),
                            (t("rail_gradation"), self._GRADATION_ROWS)):
            hairline(rail, color=pal["card_border"], fill="x",
                     padx=12, pady=(12, 8))
            micro_label(rail, title, bg=pal["rail_bg"], fg=pal["accent"],
                        anchor="w", fill="x", padx=12)
            for caption, key in rows:
                cell = MetricCell(rail, caption, "\u2014",
                                  {**pal, "card_bg": pal["rail_bg"]},
                                  value_size=10, inline=True)
                cell.pack(fill="x", padx=12, pady=(7, 0))
                self._metric_cells[key] = cell

        self.refresh_metrics()

    def refresh_metrics(self):
        if not hasattr(self, "_metric_cells"):
            return
        rows = self._preview_rows()
        self._rows_lbl.configure(text=str(len(rows)))

        values = {k: "\u2014" for k in self._metric_cells}
        try:
            sample = SoilSample(name="preview", sieve_data=rows)
            if sample.has_sieve_data:
                frac = sample.fractions(ASTM_SIZES)
                if frac is not None:
                    values["gravel"] = f"{frac.gravel:.1f}"
                    values["sand"] = f"{frac.sand:.1f}"
                    values["fines"] = f"{frac.fines:.1f}"
                for key in ("d60", "d30", "d10", "cu", "cc"):
                    val = getattr(sample, key, None)
                    if val is not None:
                        values[key] = f"{val:.3f}" if key.startswith("d") \
                            else f"{val:.2f}"
        except (ValueError, ZeroDivisionError):
            pass

        for key, cell in self._metric_cells.items():
            cell.set(values[key])

    def _preview_rows(self):
        out = []
        for item in self.tree.get_children():
            try:
                size, passing = self.tree.item(item, "values")
                out.append((float(size), float(passing)))
            except (ValueError, TypeError):
                continue
        return out

    def apply_palette(self, palette) -> None:
        self._pal = dict(palette)
        if hasattr(self, "_rscs_summary_label"):
            self._rscs_summary_label.configure(foreground=palette["muted_fg"])
        if not hasattr(self, "_rail"):
            return
        bg = palette["rail_bg"]
        cell_pal = {**palette, "card_bg": bg}

        def paint(widget):
            try:
                widget.configure(background=bg)
            except tk.TclError:
                pass
            for child in widget.winfo_children():
                if isinstance(child, MetricCell):
                    child.apply_palette(cell_pal)
                    continue
                paint(child)

        paint(self._rail)
        self._rows_lbl.configure(foreground=palette["value_fg"])
        for lbl, fg in self._rail_captions():
            try:
                lbl.configure(foreground=fg)
            except tk.TclError:
                pass

    def _rail_captions(self):
        pal = self._pal
        out = []
        for child in self._rail.winfo_children():
            if isinstance(child, MetricCell):
                continue
            if isinstance(child, tk.Label):
                out.append((child, pal["accent"]))
            elif isinstance(child, tk.Frame):
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Label) and sub is not self._rows_lbl:
                        out.append((sub, pal["micro_fg"]))
        return out

    @property
    def RSCS_FIELDS(self):
        return [
            ("e_min_gravel", t("rscs_field_gravel_emin"), 0, 0),
            ("e_max_gravel", "e_max", 2, 0),
            ("roundness_gravel", t("rscs_field_or"), 4, 0),
            ("cu_gravel", "Cu", 6, 0),
            ("e_min_sand", t("rscs_field_sand_emin"), 0, 1),
            ("e_max_sand", "e_max", 2, 1),
            ("roundness_sand", t("rscs_field_or"), 4, 1),
            ("cu_sand", "Cu", 6, 1),
            ("ll_brine", t("rscs_field_fines_ll_brine"), 0, 2),
            ("ll_kerosene", "LL_kerosene", 2, 2),
        ]

    def _build_rscs(self):
        self.rscs_vars = {key: tk.StringVar() for key, _, _, _ in
                          self.RSCS_FIELDS}
        self.rscs_shown = tk.BooleanVar(value=False)
        self.rscs_summary = tk.StringVar()

        outer = ttk.Frame(self)
        outer.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        ttk.Checkbutton(
            outer, text=t("rscs_checkbox_label"),
            variable=self.rscs_shown,
            command=self._on_rscs_toggled).pack(side="left")
        self.rscs_button = ttk.Button(outer, text=t("rscs_params_button"),
                                      command=self.open_rscs_parameters)
        self.rscs_button.pack(side="left", padx=(12, 0))
        ttk.Label(outer, textvariable=self.rscs_summary, width=1,
                  foreground=LIGHT["muted_fg"]).pack(
            side="left", fill="x", expand=True, padx=(12, 0))
        self._rscs_summary_label = outer.winfo_children()[-1]
        for var in self.rscs_vars.values():
            var.trace_add("write", lambda *_a: self._toggle_rscs())
        self._toggle_rscs()

    def set_rscs_enabled(self, enabled: bool) -> None:
        if bool(self.rscs_shown.get()) != bool(enabled):
            self.rscs_shown.set(bool(enabled))
        self._toggle_rscs()

    def _on_rscs_toggled(self):
        self._toggle_rscs()
        self._changed()

    def _toggle_rscs(self):
        enabled = bool(self.rscs_shown.get())
        self.rscs_button.state(["!disabled"] if enabled else ["disabled"])
        filled = sum(1 for var in self.rscs_vars.values() if var.get().strip())
        if not enabled:
            text = t("rscs_summary_off")
        elif filled:
            text = t("rscs_summary_count").format(count=filled)
        else:
            text = t("rscs_summary_defaults")
        self.rscs_summary.set(text)

    def open_rscs_parameters(self):
        root = self.winfo_toplevel()
        palette = getattr(root, "palette", None) or LIGHT
        dialog = RscsParametersDialog(root, self.RSCS_FIELDS, self.rscs_vars,
                                      palette)
        self.wait_window(dialog)
        self._toggle_rscs()
        self._changed()

    def _rscs_kwargs(self) -> dict:
        out = {"rscs_enabled": bool(self.rscs_shown.get())}
        for key, label, _, _ in self.RSCS_FIELDS:
            if not out["rscs_enabled"]:
                out[key] = None
                continue
            txt = self.rscs_vars[key].get().strip().replace(",", ".")
            if not txt:
                out[key] = None
                continue
            try:
                value = float(txt)
            except ValueError:
                raise ValueError(t("msg_rscs_must_be_number").format(label=label))
            if value <= 0:
                raise ValueError(t("msg_rscs_must_be_positive").format(label=label))
            if key.startswith("roundness") and not 0.05 <= value <= 1.0:
                raise ValueError(t("msg_rscs_roundness_range"))
            out[key] = value
        return out

    def _edit_cell(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell":
            return
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if not item or col not in ("#1", "#2"):
            return
        bbox = self.tree.bbox(item, col)
        if not bbox:
            return
        x, y, w, h = bbox
        idx = 0 if col == "#1" else 1
        old_value = self.tree.item(item, "values")[idx]

        var = tk.StringVar(value=old_value)
        entry = ttk.Entry(self.tree, textvariable=var, justify="center")
        entry.place(x=x, y=y, width=w, height=h)
        entry.focus_set()
        entry.select_range(0, "end")

        done = []

        def finish(_e=None):
            if done:
                return
            done.append(True)
            txt = var.get().strip().replace(",", ".")
            try:
                val = float(txt)
                if idx == 0 and val <= 0:
                    raise ValueError
                if idx == 1 and not 0 <= val <= 100:
                    raise ValueError
            except ValueError:
                entry.destroy()
                messagebox.showerror(
                    t("msg_invalid_value_title"),
                    t("msg_enter_size") if idx == 0 else
                    t("msg_enter_passing"))
                return
            entry.destroy()
            formatted = f"{val:g}"
            if formatted == old_value:
                return
            self._snapshot()
            vals = list(self.tree.item(item, "values"))
            vals[idx] = formatted
            self.tree.item(item, values=vals)
            self._sort_rows()
            self._changed()

        def cancel(_e=None):
            done.append(True)
            entry.destroy()

        entry.bind("<Return>", finish)
        entry.bind("<FocusOut>", finish)
        entry.bind("<Escape>", cancel)

    def add_row(self):
        try:
            size = float(self.size_var.get().replace(",", "."))
            passing = float(self.pass_var.get().replace(",", "."))
            if size <= 0:
                raise ValueError
            if not 0 <= passing <= 100:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                t("msg_invalid_point_title"),
                t("msg_enter_size_and_passing"))
            return
        self._snapshot()
        self.tree.insert("", "end", values=(f"{size:g}", f"{passing:g}"))
        self._sort_rows()
        self.size_var.set("")
        self.pass_var.set("")
        self._changed()

    def remove_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        self._snapshot()
        for item in selected:
            self.tree.delete(item)
        self._changed()

    def clear_table(self):
        if self.tree.get_children():
            self._snapshot()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._changed()

    def _snapshot(self):
        self._undo_stack.append(self._table_rows())
        if len(self._undo_stack) > 20:
            self._undo_stack.pop(0)

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        rows = self._undo_stack.pop()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for d, p in rows:
            self.tree.insert("", "end", values=(f"{d:g}", f"{p:g}"))
        self._sort_rows()
        self._changed()
        return True

    def load_example(self):
        self.load_sample(example_sample())

    def load_sample(self, sample: SoilSample) -> None:
        self.clear_table()
        for d, p in sample.sieve_data:
            self.tree.insert("", "end", values=(f"{d:g}", f"{p:g}"))
        if sample.liquid_limit is not None:
            self.ll_var.set(f"{sample.liquid_limit:g}")
        else:
            self.ll_var.set("")
        if sample.plastic_limit is not None:
            self.pl_var.set(f"{sample.plastic_limit:g}")
        else:
            self.pl_var.set("")
        self.np_var.set(sample.liquid_limit is None
                        and sample.plastic_limit is None)
        self.organic_var.set(sample.organic)
        for key, var in self.meta_vars.items():
            var.set(getattr(sample, key))

        for key in self.rscs_vars:
            value = getattr(sample, key, None)
            self.rscs_vars[key].set("" if value is None else f"{value:g}")
        self.set_rscs_enabled(getattr(sample, "rscs_enabled", True))

        self._sort_rows()
        self._changed()

    def import_csv(self):
        from ..importers import csv_import
        path = filedialog.askopenfilename(
            title=t("dlg_import_file_title"),
            filetypes=[(t("dlg_import_filetypes"),
                        "*.xlsx *.xlsm *.xls *.csv *.txt *.tsv *.ags"),
                       ("Excel", "*.xlsx *.xlsm *.xls"),
                       ("CSV", "*.csv *.txt *.tsv"),
                       ("AGS", "*.ags"),
                       (t("dlg_all_files"), "*.*")])
        if path:
            self._review_and_apply(csv_import.import_file(path))

    def _review_and_apply(self, data):
        from .import_dialog import ImportReviewDialog
        if not data.ok and not data.others:
            message = "\n\n".join(data.warnings) or t("import_warn_too_few")
            messagebox.showwarning(t("msg_import_title"),
                                   message + "\n\n" + t("import_help_hint"))
            if not data.sieve:
                return
        root = self.winfo_toplevel()
        palette = getattr(root, "palette", None)
        dlg = ImportReviewDialog(root, data,
                                 **({"palette": palette} if palette else {}))
        self.wait_window(dlg)
        if dlg.result is None:
            return
        res = dlg.result
        self.clear_table()
        for d, p in res.sieve:
            self.tree.insert("", "end", values=(f"{d:g}", f"{p:g}"))
        self.ll_var.set("" if res.liquid_limit is None
                        else f"{res.liquid_limit:g}")
        self.pl_var.set("" if res.plastic_limit is None
                        else f"{res.plastic_limit:g}")
        self.np_var.set(bool(res.meta.get("non_plastic")))
        if "organic" in res.meta:
            self.organic_var.set(bool(res.meta["organic"]))
        for key, var in self.meta_vars.items():
            value = res.meta.get(key)
            if value:
                var.set(str(value))
        rscs_found = False
        for key, var in self.rscs_vars.items():
            value = res.meta.get(key)
            if value is not None:
                var.set(f"{float(value):g}")
                rscs_found = True
        if rscs_found:
            self.set_rscs_enabled(True)
        self._sort_rows()
        self._changed()

    def _sort_rows(self):
        rows = self._table_rows()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for d, p in sorted(rows, key=lambda x: -x[0]):
            self.tree.insert("", "end", values=(f"{d:g}", f"{p:g}"))

    def _table_rows(self) -> List[Tuple[float, float]]:
        rows = []
        for item in self.tree.get_children():
            d, p = self.tree.item(item, "values")
            rows.append((float(d), float(p)))
        return rows

    def _changed(self):
        self.refresh_metrics()
        if self.on_change:
            self.on_change()

    def build_sample(self) -> SoilSample:
        rows = self._table_rows()
        if len(rows) < 2:
            raise ValueError(t("msg_need_two_points"))

        sorted_rows = sorted(rows, key=lambda x: -x[0])
        for (d1, p1), (d2, p2) in zip(sorted_rows, sorted_rows[1:]):
            if p2 > p1 + 1e-9:
                raise ValueError(t("msg_sieve_contradiction").format(
                    p1=p1, d1=d1, p2=p2, d2=d2))

        def parse(var, label):
            txt = var.get().strip().replace(",", ".")
            if not txt:
                return None
            try:
                v = float(txt)
            except ValueError:
                raise ValueError(t("msg_number_or_blank").format(label=label))
            if not 0 <= v <= 600:
                raise ValueError(t("msg_out_of_range").format(label=label))
            return v

        if self.np_var.get():
            ll = pl = None
        else:
            ll = parse(self.ll_var, t("input_liquid_limit"))
            pl = parse(self.pl_var, t("input_plastic_limit"))
            if ll is not None and pl is not None and pl > ll:
                raise ValueError(t("msg_pl_exceeds_ll"))

        return SoilSample(
            name=self.meta_vars["name"].get() or "Sample 1",
            sieve_data=rows,
            liquid_limit=ll,
            plastic_limit=pl,
            organic=self.organic_var.get(),
            project=self.meta_vars["project"].get(),
            location=self.meta_vars["location"].get(),
            operator=self.meta_vars["operator"].get(),
            date=self.meta_vars["date"].get(),
            **self._rscs_kwargs(),
        )

class RscsParametersDialog(tk.Toplevel):
    def __init__(self, master, fields, variables, palette):
        super().__init__(master)
        self.title(t("rscs_dialog_title"))
        self.configure(background=palette["bg"])
        set_window_icon(self)
        self.resizable(False, False)
        self.transient(master)
        self._variables = variables

        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="RSCS \u2014 Park & Santamarina (2017)",
                  font=("Segoe UI", 13, "bold")).grid(
            row=0, column=0, columnspan=8, sticky="w", pady=(0, 10))
        first = None
        for key, label, col, row in fields:
            ttk.Label(frame, text=f"{label}:").grid(
                row=row + 1, column=col, sticky="e", padx=(8, 3), pady=4)
            entry = ttk.Entry(frame, textvariable=variables[key], width=9)
            entry.grid(row=row + 1, column=col + 1, sticky="w", padx=(0, 6),
                       pady=4)
            first = first or entry
        ttk.Label(frame, text=t("rscs_help_text"), font=("Segoe UI", 10),
                  foreground=palette["muted_fg"], wraplength=px(self, 600),
                  justify="left").grid(row=5, column=0, columnspan=8,
                                       sticky="w", padx=8, pady=(12, 0))
        buttons = ttk.Frame(frame)
        buttons.grid(row=6, column=0, columnspan=8, sticky="e", pady=(16, 0))
        ttk.Button(buttons, text=t("about_close"), style="Action.TButton",
                   command=self.destroy).pack(side="right")
        ttk.Button(buttons, text=t("rscs_clear"),
                   command=self._clear).pack(side="right", padx=(0, 8))

        self.bind("<Escape>", lambda _e: self.destroy())
        self.bind("<Return>", lambda _e: self.destroy())
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width()
                                    - self.winfo_reqwidth()) // 2
        y = master.winfo_rooty() + (master.winfo_height()
                                    - self.winfo_reqheight()) // 3
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.grab_set()
        if first is not None:
            first.focus_set()

    def _clear(self):
        for var in self._variables.values():
            var.set("")

