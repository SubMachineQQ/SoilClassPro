from __future__ import annotations

import sys
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from typing import Optional

import matplotlib.pyplot as plt

from .. import __app_name__, __version__
from ..charts import classifiable_chart_defs
from ..classifiers import classify_selected, short_system_name
from ..i18n import t, upper
from ..models import SoilSample
from .. import project_file
from ..report import build_pdf, export_ags4
from . import theme
from .dropdown_menu import DropdownMenu, MenuItem, Separator
from .icon_utils import set_window_icon
from .input_tab import InputTab
from .modes import MODE_CHARTS, MODE_CLASSIFIERS, MODE_TITLE
from .results_window import ResultsWindow
from .scaling import fit_window, lock_min_to_content, tk_scaling
from .theme_toggle import ThemeToggle
from .widgets import MONO


class SoilClassApp(tk.Tk):
    def __init__(self, mode: str = "ALL",
                preset_sample: Optional[SoilSample] = None):
        super().__init__()
        tk_scaling(self)
        self.mode = mode if mode in MODE_TITLE else "ALL"
        self.classifiers = MODE_CLASSIFIERS[self.mode]
        self.chart_defs = MODE_CHARTS[self.mode]

        fit_window(self, 1260, 780, min_width=1040, min_height=640)
        self.sample: Optional[SoilSample] = None
        self.project_path: Optional[str] = None
        self._dirty = False
        self._dark = theme.get_dark_mode()
        self.palette = theme.DARK if self._dark else theme.LIGHT
        self.results_window: Optional[ResultsWindow] = None
        self.results_tab = None

        self.next_screen = None

        self._clock_job = None

        self._set_window_icon()
        self._init_style()
        self._build_header()
        self._build_toolbar()
        self._build_statusbar()
        self._build_main_area()
        self.protocol("WM_DELETE_WINDOW", self.close_requested)
        modifier = "Command" if sys.platform == "darwin" else "Control"
        self.bind_all(f"<{modifier}-s>", lambda _e: self.save_project())
        self.bind_all(f"<{modifier}-S>", lambda _e: self.save_project_as())
        self.bind_all(f"<{modifier}-o>", lambda _e: self.open_project())
        self.bind_all(f"<{modifier}-z>", lambda _e: self._undo())

        lock_min_to_content(self)

        if preset_sample is not None:
            self.input_tab.load_sample(preset_sample)
            self.sample = preset_sample
            self._dirty = False
        self._refresh_title()

    def close_requested(self):
        if self.next_screen is None and not self._confirm_discard(t("confirm_closing")):
            return
        self._on_close()

    def destroy(self):
        if self._clock_job is not None:
            try:
                self.after_cancel(self._clock_job)
            except tk.TclError:
                pass
            self._clock_job = None
        super().destroy()

    def _on_close(self):
        if self._clock_job is not None:
            try:
                self.after_cancel(self._clock_job)
            except tk.TclError:
                pass
            self._clock_job = None
        if self.results_window is not None and self.results_window.winfo_exists():
            self.results_window._on_close()
        plt.close("all")
        self.destroy()

    def _init_style(self):
        self.palette = theme.apply_theme(self, dark=self._dark)

    def _set_window_icon(self):
        set_window_icon(self)

    def _refresh_title(self, sample: Optional[SoilSample] = None):
        sample = sample or self.sample
        project_name = (sample.project.strip() if sample and sample.project
                        else "") or t("title_untitled")
        marker = "*" if self._dirty else ""
        if self.project_path:
            from pathlib import Path
            where = f" [{Path(self.project_path).name}]"
        else:
            where = f" [{t('title_not_saved')}]"
        self.title(f"{marker}{__app_name__} v{__version__} \u2014 "
                   f"{project_name}{where} \u2014 {MODE_TITLE[self.mode]}")
        if hasattr(self, "breadcrumb"):
            self._refresh_breadcrumb(sample)

    def _build_header(self):
        pal = self.palette
        strip = tk.Frame(self, background=pal["header_strip_bg"])
        strip.pack(side="top", fill="x")

        self.breadcrumb = tk.StringVar()
        tk.Label(strip, textvariable=self.breadcrumb, font=(MONO, 10),
                 background=pal["header_strip_bg"],
                 foreground=pal["micro_fg"], anchor="w").pack(
                     side="left", padx=10, pady=4)

        self.header_std = tk.StringVar(value=upper(MODE_TITLE[self.mode]))
        tk.Label(strip, textvariable=self.header_std, font=(MONO, 10),
                 background=pal["header_strip_bg"],
                 foreground=pal["accent"], anchor="e").pack(
                     side="right", padx=10, pady=4)
        self._header_widgets = strip
        self._refresh_breadcrumb()

    def _refresh_breadcrumb(self, sample: Optional[SoilSample] = None):
        sample = sample or self.sample
        name = (sample.name.strip() if sample and sample.name else "") \
            or "NO SAMPLE"
        self.breadcrumb.set(
            f"{__app_name__.upper()} {__version__}  \u2014  {upper(name)}")

    def _build_toolbar(self):
        bar = ttk.Frame(self, padding=(8, 6))
        bar.pack(side="top", fill="x")

        menu_btn = ttk.Button(bar, text="\u2630  " + t("file_menu"),
                              style="Icon.TButton", command=self._open_main_menu)
        menu_btn.pack(side="left", padx=(0, 4))
        self._menu_btn = menu_btn

        ttk.Button(bar, text="\u25b6  " + t("classify_button"),
                   style="Classify.TButton",
                   command=self.classify).pack(side="right", padx=(8, 4))

        pal = self.palette
        ThemeToggle(bar, is_dark=self._dark, bg=pal["bg"],
                   command=self._toggle_theme).pack(side="right", padx=(4, 8))

        self._toolbar_bar = bar

    def _open_main_menu(self):
        entries = [
            MenuItem(t("tt_home"), command=self._go_home),
            Separator(),
            MenuItem(t("save_project"), command=self.save_project,
                    accelerator="Ctrl+S"),
            MenuItem(t("save_as"), command=self.save_project_as,
                    accelerator="Ctrl+Shift+S"),
            MenuItem(t("open_project"), command=self.open_project,
                    accelerator="Ctrl+O"),
            MenuItem(t("tt_undo"), command=self._undo, accelerator="Ctrl+Z"),
            Separator(),
            MenuItem(t("import_menu"), items=[
                MenuItem(t("import_csv"),
                        command=lambda: self.input_tab.import_csv()),
                Separator(),
                MenuItem(t("import_example"), command=self._load_example),
                Separator(),
                MenuItem(t("import_help_menu"), command=self.show_import_help),
                MenuItem(t("import_save_examples"),
                        command=self.save_import_examples),
            ]),
            MenuItem(t("export_menu"), items=[
                MenuItem(t("export_ags4"), command=self.export_ags4),
            ]),
            Separator(),
            MenuItem(t("tt_compare"), command=self.open_comparison),
            Separator(),
            MenuItem(t("methods_menu"), command=self.show_methods),
            MenuItem(t("about_menu"), command=self.show_about),
        ]
        return DropdownMenu(self._menu_btn, entries, self.palette)

    def show_import_help(self):
        from .import_help import ImportHelpDialog
        ImportHelpDialog(self, self.palette)

    def save_import_examples(self):
        from .import_help import save_examples
        save_examples(self)

    def show_methods(self):
        from .methods_window import MethodsWindow
        window = getattr(self, "_methods_window", None)
        if window is not None and window.winfo_exists():
            window.deiconify()
            window.lift()
            window.focus_set()
            return
        self._methods_window = MethodsWindow(self, self.palette)

    def show_about(self):
        from .welcome import AboutDialog
        AboutDialog(self)

    def _build_main_area(self):
        self.input_tab = InputTab(self, on_change=self._data_changed)
        self.input_tab.pack(fill="both", expand=True, padx=8, pady=(0, 4))
        if self.mode == "RSCS":
            self.input_tab.set_rscs_enabled(True)
        if self._dark:
            self.input_tab.apply_palette(self.palette)

    def _build_statusbar(self):
        pal = self.palette
        bar = tk.Frame(self, background=pal["status_bg"])
        bar.pack(side="bottom", fill="x")

        self.session_info = tk.StringVar()
        tk.Label(bar, textvariable=self.session_info, font=(MONO, 10),
                 background=pal["status_bg"], foreground=pal["micro_fg"],
                 anchor="e").pack(side="right", padx=10, pady=3)

        self.status = tk.StringVar(value=t("status_ready"))
        tk.Label(bar, textvariable=self.status, font=(MONO, 10),
                 background=pal["status_bg"], foreground=pal["muted_fg"],
                 anchor="w", width=1).pack(side="left", fill="x", expand=True,
                                           padx=10, pady=3)
        self._statusbar = bar
        self._tick_clock()

    def _tick_clock(self):
        self.session_info.set(
            f"{t('status_units_si')}  |  {upper(MODE_TITLE[self.mode])}  |  "
            + datetime.now().strftime("%Y-%m-%d %H:%M"))
        self._clock_job = self.after(60_000, self._tick_clock)

    def _data_changed(self):
        self._dirty = True
        self._refresh_title()
        self.status.set(t("status_data_changed"))

    def _load_example(self):
        self.input_tab.load_example()
        self.classify()

    def _undo(self):
        if self.input_tab.undo():
            self.status.set(t("status_undo_done"))
        else:
            self.status.set(t("status_undo_none"))

    def classify(self):
        try:
            self.sample = self.input_tab.build_sample()
        except ValueError as exc:
            messagebox.showerror(t("msg_input_error"), str(exc))
            return
        results = classify_selected(self.sample, self.classifiers)
        shown = [r for r in results if r.ok]
        if not shown:
            message = (t("msg_rscs_not_selected")
                       if self.mode == "RSCS" and not self.sample.rscs_enabled
                       else t("msg_no_classification"))
            messagebox.showinfo(t("tt_classify"), message)
            return

        chart_defs = classifiable_chart_defs(self.chart_defs, self.sample)
        if self.results_window is None or not self.results_window.winfo_exists():
            self.results_window = ResultsWindow(self, self.palette,
                                                on_export_pdf=self.export_pdf)
            self.results_window.transient(self)
        self.results_window.refresh(self.sample, shown, chart_defs)
        self.results_tab = self.results_window.results_tab

        symbols = "  |  ".join(f"{short_system_name(r.system)}: {r.symbol}"
                               for r in results if r.ok)
        self.status.set(t("status_classified").format(
            name=self.sample.name, symbols=symbols))
        self._refresh_title(self.sample)

    def _current_sample_or_error(self) -> Optional[SoilSample]:
        if self.sample is not None:
            return self.sample
        try:
            self.sample = self.input_tab.build_sample()
        except ValueError as exc:
            messagebox.showerror(t("msg_input_error"), str(exc))
            return None
        return self.sample

    def _go_home(self):
        if not self._confirm_discard(t("confirm_returning_home")):
            return
        self.next_screen = ("launcher", None, None)
        self._on_close()

    def _toggle_theme(self, dark: bool):
        theme.set_dark_mode(dark)
        self._dark = bool(dark)
        self.after_idle(self._rebuild_for_theme)

    def _rebuild_for_theme(self):
        if not self.winfo_exists():
            return
        try:
            sample = self.input_tab.build_sample()
        except ValueError:
            sample = self.sample
        dirty = self._dirty
        project_path = self.project_path
        results_open = (self.results_window is not None
                        and self.results_window.winfo_exists())

        if self._clock_job is not None:
            try:
                self.after_cancel(self._clock_job)
            except tk.TclError:
                pass
            self._clock_job = None
        if results_open:
            self.results_window._on_close()
        self.results_window = None
        self.results_tab = None
        for child in self.winfo_children():
            child.destroy()

        self.palette = theme.DARK if self._dark else theme.LIGHT
        self._init_style()
        self._build_header()
        self._build_toolbar()
        self._build_statusbar()
        self._build_main_area()

        if sample is not None:
            self.input_tab.load_sample(sample)
            self.sample = sample
        self.project_path = project_path
        self._dirty = dirty
        self._refresh_title(self.sample)
        self.lift()
        self.focus_force()
        if results_open:
            self.classify()

    def open_comparison(self):
        from .compare_window import ComparisonWindow
        seed = []
        try:
            current = self.input_tab.build_sample()
            if current.has_sieve_data or current.liquid_limit is not None:
                seed.append(current)
        except ValueError:
            pass
        win = ComparisonWindow(self, samples=seed, palette=self.palette)
        win.transient(self)

    def open_project(self):
        path = filedialog.askopenfilename(
            title=t("dlg_open_project_title"),
            filetypes=[("SoilClass Pro project", "*.soilpro"),
                       ("All files", "*.*")])
        if not path:
            return
        try:
            sample, mode = project_file.load_project(path)
        except ValueError as exc:
            messagebox.showerror(t("dlg_open_failed"), str(exc))
            return

        from .. import recent_projects
        recent_projects.add_recent(path)

        if mode == self.mode:
            self.input_tab.load_sample(sample)
            self.project_path = path
            self._dirty = False
            self._refresh_title(sample)
            self.status.set(t("status_opened_project").format(path=path))
        else:
            self.next_screen = ("app", mode, sample)
            self._on_close()

    def save_project(self, save_as: bool = False) -> bool:
        sample = self._current_sample_or_error()
        if sample is None:
            return False

        path = self.project_path
        if save_as or not path:
            path = filedialog.asksaveasfilename(
                title=t("dlg_save_project_title"),
                defaultextension=".soilpro",
                initialfile=f"{sample.name}".replace("/", "-")
                            .replace(" ", "_") + ".soilpro",
                filetypes=[("SoilClass Pro project", "*.soilpro")],
            )
            if not path:
                return False
        try:
            project_file.save_project(path, sample, self.mode)
        except OSError as exc:
            messagebox.showerror(t("dlg_save_failed"), str(exc))
            return False

        from .. import recent_projects
        recent_projects.add_recent(path)
        self.project_path = path
        self._dirty = False
        self._refresh_title()
        self.status.set(t("status_project_saved").format(path=path))
        return True

    def save_project_as(self) -> bool:
        return self.save_project(save_as=True)

    def _confirm_discard(self, what: str) -> bool:
        if not self._dirty:
            return True
        answer = messagebox.askyesnocancel(
            t("dlg_unsaved_changes"),
            t("msg_unsaved_body").format(what=what))
        if answer is None:
            return False
        if answer:
            return self.save_project()
        return True

    def export_pdf(self):
        sample = self._current_sample_or_error()
        if sample is None:
            return
        path = filedialog.asksaveasfilename(
            title=t("dlg_save_pdf_title"),
            defaultextension=".pdf",
            initialfile=f"SoilClassification_{sample.name}"
                        .replace("/", "-").replace(" ", "_") + ".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not path:
            return
        try:
            build_pdf(sample, path, classifiers=self.classifiers,
                     figures=self.chart_defs)
        except OSError as exc:
            messagebox.showerror(t("msg_export_failed"), str(exc))
            return
        self.status.set(t("status_pdf_saved").format(path=path))
        messagebox.showinfo(t("msg_report_created_title"),
                            t("msg_report_created_body").format(path=path))

    def export_ags4(self):
        sample = self._current_sample_or_error()
        if sample is None:
            return
        path = filedialog.asksaveasfilename(
            title=t("dlg_export_ags4_title"),
            defaultextension=".ags",
            initialfile=f"{sample.name}".replace("/", "-")
                        .replace(" ", "_") + ".ags",
            filetypes=[("AGS4 data file", "*.ags"), ("All files", "*.*")],
        )
        if not path:
            return
        results = classify_selected(sample, self.classifiers)
        try:
            export_ags4(path, sample, results)
        except OSError as exc:
            messagebox.showerror(t("msg_export_failed"), str(exc))
            return
        self.status.set(t("status_ags4_saved").format(path=path))
        messagebox.showinfo(
            t("msg_ags4_created_title"),
            t("msg_ags4_created_body").format(path=path))
