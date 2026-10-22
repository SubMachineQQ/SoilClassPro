import os
import unittest

import matplotlib
matplotlib.use("Agg")
import numpy as np
from matplotlib import pyplot as plt

from soilclass.charts.gsd import (BOUNDARY_SETS, gsd_figure,
                                  gsd_multi_figure)
from soilclass.charts.plasticity import (_A_AT_PI4, astm_plasticity_figure,
                                         astm_plasticity_multi_figure,
                                         bs_plasticity_figure,
                                         bs_plasticity_multi_figure)
from soilclass.charts.style import FONTS
from soilclass.charts import iso14688_plasticity_figure
from soilclass.colors import CHART, THEME_LIGHT
from soilclass.example_data import example_sample
from soilclass.models import SoilSample


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY"))


def _soils(n):
    base = [(75, 100), (19, 98), (9.5, 92), (4.75, 83), (2, 65), (0.85, 54),
            (0.425, 45), (0.25, 38), (0.106, 31), (0.075, 28), (0.02, 18),
            (0.005, 10), (0.001, 4)]
    out = []
    for i in range(n):
        f = 1 + (i - n // 2) * 0.12
        sd = [(d, max(0.5, min(100.0, p * f))) for d, p in base]
        out.append(SoilSample(name=f"Soil {i + 1}", sieve_data=sd,
                              liquid_limit=22 + i * 4,
                              plastic_limit=14 + i * 2))
    return out


class TestGrainSizeChartFeedback(unittest.TestCase):
    def tearDown(self):
        plt.close("all")
    """Figure 2 comments."""

    def setUp(self):
        self.fig = gsd_figure(example_sample())
        self.ax = self.fig.axes[0]

    def test_particle_size_axis_increases_to_the_right(self):
        lo, hi = self.ax.get_xlim()
        self.assertLess(lo, hi)

    def test_vertical_axis_says_cumulative(self):
        self.assertIn("Cumulative", self.ax.get_ylabel())

    def test_no_interpolation_dash_line_is_drawn(self):
        dashed = [l for l in self.ax.get_lines()
                  if l.get_linestyle() in ("--", "-.")]
        self.assertEqual(dashed, [])

    def test_d_value_construction_lines_are_off_by_default(self):
        dotted = [l for l in self.ax.get_lines() if l.get_linestyle() == ":"]
        self.assertEqual(dotted, [])

    def test_d_values_are_still_reported_in_a_box(self):
        blob = " ".join(t.get_text() for t in self.ax.texts)
        for token in ("D60", "D30", "D10", "Cu", "Cc"):
            self.assertIn(token, blob)

    def test_d_value_text_stays_inside_the_axes(self):
        for t in self.ax.texts:
            if t.get_transform() == self.ax.transAxes:
                _x, y = t.get_position()
                self.assertGreaterEqual(y, 0.0)
                self.assertLessEqual(y, 1.0)

    def test_y_axis_has_ten_unit_major_and_two_unit_minor_ticks(self):
        major = [t for t in self.ax.get_yticks() if 0 <= t <= 100]
        self.assertEqual(major, [float(v) for v in range(0, 101, 10)])
        minor = [t for t in self.ax.get_yticks(minor=True) if 0 <= t <= 100]
        self.assertIn(2.0, minor)
        self.assertIn(98.0, minor)

    def test_boundary_system_is_named_on_the_chart(self):
        blob = " ".join(t.get_text() for t in self.ax.texts)
        self.assertIn("particle size boundaries", blob)
        self.assertIn("USCS", blob)

    def test_boundary_system_is_selectable(self):
        for key, expect in (("BS", "BS 5930"), ("ISO14688", "TS EN ISO 14688"),
                            ("RSCS", "RSCS")):
            fig = gsd_figure(example_sample(), boundaries=key)
            blob = " ".join(t.get_text() for t in fig.axes[0].texts)
            self.assertIn(expect, blob)

    def test_every_boundary_set_defines_its_bands(self):
        for key, spec in BOUNDARY_SETS.items():
            self.assertTrue(spec["label_prefix"])
            self.assertGreaterEqual(len(spec["bands"]), 3)


class TestPlasticityChartFeedback(unittest.TestCase):
    def tearDown(self):
        plt.close("all")
    """Figure 3 comments."""

    def setUp(self):
        self.fig = astm_plasticity_figure(
            SoilSample(name="Z1", sieve_data=[(4.75, 100), (0.075, 60)],
                       liquid_limit=28, plastic_limit=20))
        self.ax = self.fig.axes[0]

    def test_u_line_is_drawn_all_the_way_down_to_the_axis(self):
        dashed = [l for l in self.ax.get_lines()
                  if l.get_linestyle() == "--" and len(l.get_ydata()) > 5]
        self.assertTrue(dashed)
        self.assertAlmostEqual(float(np.min(dashed[0].get_ydata())), 0.0,
                               places=2)

    def test_a_line_stops_at_the_cl_ml_boundary(self):
        solid = [l for l in self.ax.get_lines()
                if l.get_linestyle() == "-" and len(l.get_xdata()) > 5]
        self.assertTrue(solid)
        self.assertAlmostEqual(float(np.min(solid[0].get_ydata())), 4.0,
                               places=2)
        self.assertAlmostEqual(float(np.min(solid[0].get_xdata())),
                               _A_AT_PI4, places=2)

    def test_chart_has_no_zone_shading(self):
        self.assertEqual(len(self.ax.collections), 0)

    def test_low_ll_low_pi_region_is_named(self):
        blob = " ".join(t.get_text() for t in self.ax.texts)
        self.assertIn("ML  or  OL", blob)

    def test_ml_is_not_labelled_twice(self):
        labels = [t.get_text() for t in self.ax.texts]
        ml_like = [t for t in labels if t.strip().startswith("ML")]
        self.assertEqual(len(ml_like), 1, f"duplicate ML labels: {ml_like}")

    def test_all_regions_are_named(self):
        blob = " ".join(t.get_text() for t in self.ax.texts)
        for token in ("CL", "CH", "MH  or  OH", "ML  or  OL", "CL-ML"):
            self.assertIn(token, blob)


class TestIso14688ChartAlineStopsAtIntersection(unittest.TestCase):
    def tearDown(self):
        plt.close("all")

    def setUp(self):
        self.fig = iso14688_plasticity_figure(
            SoilSample(name="Z1", sieve_data=[(4.75, 100), (0.075, 60)],
                       liquid_limit=28, plastic_limit=20))
        self.ax = self.fig.axes[0]

    def test_a_line_does_not_reach_the_axis(self):
        solid = [l for l in self.ax.get_lines()
                if l.get_linestyle() == "-" and len(l.get_xdata()) > 5]
        self.assertTrue(solid)
        self.assertAlmostEqual(float(np.min(solid[0].get_ydata())), 4.0,
                               places=2)

    def test_a_line_starts_at_the_pi4_boundary(self):
        from soilclass.charts.plasticity import _A_AT_PI4
        solid = [l for l in self.ax.get_lines()
                if l.get_linestyle() == "-" and len(l.get_xdata()) > 5]
        self.assertAlmostEqual(float(np.min(solid[0].get_xdata())),
                               _A_AT_PI4, places=2)


class TestChartsArePrintReady(unittest.TestCase):
    def tearDown(self):
        plt.close("all")
    """"Everything black, nothing grey, and larger fonts.\""""

    def _figs(self):
        s = example_sample()
        return [gsd_figure(s), astm_plasticity_figure(s),
                bs_plasticity_figure(s), iso14688_plasticity_figure(s)]

    def test_axes_frame_and_ticks_are_black(self):
        self.assertEqual(CHART["spine"].upper(), "#000000")
        self.assertEqual(CHART["tick"].upper(), "#000000")
        self.assertEqual(CHART["ink"].upper(), "#000000")

    def test_plot_area_is_white(self):
        for fig in self._figs():
            ax = fig.axes[0]
            self.assertEqual(ax.get_facecolor()[:3], (1.0, 1.0, 1.0))

    def test_axis_titles_and_ticks_use_the_enlarged_scale(self):
        for fig in self._figs():
            ax = fig.axes[0]
            self.assertGreaterEqual(ax.xaxis.label.get_fontsize(), 12)
            self.assertGreaterEqual(ax.yaxis.label.get_fontsize(), 12)
            self.assertGreaterEqual(ax.title.get_fontsize(), 14)

    def test_font_scale_is_defined_centrally(self):
        for key in ("title", "axis_label", "tick", "legend"):
            self.assertGreaterEqual(FONTS[key], 11)


class TestMultiSampleCharts(unittest.TestCase):
    def tearDown(self):
        plt.close("all")
    """"Show these five soils on one grain-size chart", "these ten on
    the plasticity chart\"."""

    def test_five_soils_on_one_grain_size_chart(self):
        fig = gsd_multi_figure(_soils(5))
        legend = fig.axes[0].get_legend()
        self.assertEqual(len(legend.get_texts()), 5)

    def test_ten_soils_on_the_astm_plasticity_chart(self):
        fig = astm_plasticity_multi_figure(_soils(10))
        legend = fig.axes[0].get_legend()
        self.assertEqual(len(legend.get_texts()), 10)

    def test_ten_soils_on_the_bs_plasticity_chart(self):
        fig = bs_plasticity_multi_figure(_soils(10))
        legend = fig.axes[0].get_legend()
        self.assertEqual(len(legend.get_texts()), 10)

    def test_more_soils_than_colours_still_draws(self):
        fig = gsd_multi_figure(_soils(13))
        self.assertEqual(len(fig.axes[0].get_legend().get_texts()), 13)

    def test_empty_comparison_says_so_instead_of_crashing(self):
        fig = gsd_multi_figure([])
        blob = " ".join(t.get_text() for t in fig.axes[0].texts)
        self.assertIn("No sieve data", blob)


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestSingleWhiteTheme(unittest.TestCase):
    def test_theme_is_white_with_black_text(self):
        self.assertEqual(THEME_LIGHT["bg"].upper(), "#FFFFFF")
        self.assertEqual(THEME_LIGHT["fg"].upper(), "#000000")

    def test_launcher_is_light_too(self):
        from soilclass.colors import LAUNCHER
        self.assertEqual(LAUNCHER["panel_bg"].upper(), "#FFFFFF")

    def test_gui_body_font_is_enlarged(self):
        from soilclass.gui.theme import UI_BODY
        self.assertGreaterEqual(UI_BODY, 11)


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestSaveAndReopenFlow(unittest.TestCase):
    def _app(self, **kw):
        from soilclass.gui.app import SoilClassApp
        app = SoilClassApp(mode="ALL", **kw)
        self.addCleanup(app._on_close)
        app.update()
        return app

    def test_editing_marks_the_project_unsaved(self):
        app = self._app()
        self.assertFalse(app._dirty)
        app.input_tab.load_sample(example_sample())
        app.update()
        self.assertTrue(app._dirty)
        self.assertTrue(app.title().startswith("*"))

    def test_save_then_reopen_round_trip(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        from soilclass import project_file

        app = self._app()
        app.input_tab.load_sample(example_sample())
        app.classify()

        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch("soilclass.recent_projects.add_recent"):
            target = str(Path(tmp) / "p.soilpro")
            with mock.patch("soilclass.gui.app.filedialog.asksaveasfilename",
                            return_value=target):
                self.assertTrue(app.save_project())
            self.assertEqual(app.project_path, target)
            self.assertFalse(app._dirty)
            self.assertNotIn("*", app.title()[:1])

            with mock.patch("soilclass.gui.app.filedialog.asksaveasfilename",
                            side_effect=AssertionError("should not re-ask")):
                app._dirty = True
                self.assertTrue(app.save_project())

            sample, mode = project_file.load_project(target)
            self.assertEqual(mode, "ALL")
            self.assertEqual(len(sample.sieve_data),
                             len(example_sample().sieve_data))

    def test_closing_with_unsaved_work_asks_first(self):
        from unittest import mock
        app = self._app()
        app._dirty = True
        with mock.patch("soilclass.gui.app.messagebox.askyesnocancel",
                        return_value=None) as ask:
            app.close_requested()
            self.assertTrue(ask.called)
        self.assertTrue(app.winfo_exists())
        app._dirty = False


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestComparisonWindow(unittest.TestCase):
    def test_window_builds_four_charts_and_a_table(self):
        from soilclass.gui.app import SoilClassApp
        from soilclass.gui.compare_window import ComparisonWindow

        app = SoilClassApp(mode="ALL")
        self.addCleanup(app._on_close)
        win = ComparisonWindow(app, samples=_soils(5))
        self.addCleanup(win._on_close)
        app.update()

        self.assertEqual(len(win.nb.tabs()), 4)
        self.assertEqual(len(win.tree.get_children()), 5)

    def test_export_pdf_pages_are_landscape_with_letterhead(self):
        if __import__("importlib").util.find_spec("pypdfium2") is None:
            self.skipTest("pypdfium2 not installed")
        import os
        import tempfile
        from unittest import mock
        import pypdfium2 as pdfium
        from soilclass import __app_name__
        from soilclass.gui.app import SoilClassApp
        from soilclass.gui.compare_window import ComparisonWindow
        from soilclass.report.pdf_report import PAGE_LANDSCAPE

        app = SoilClassApp(mode="ALL")
        self.addCleanup(app._on_close)
        win = ComparisonWindow(app, samples=_soils(3))
        self.addCleanup(win._on_close)
        app.update()

        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "comparison.pdf")
            with mock.patch(
                    "soilclass.gui.compare_window.filedialog."
                    "asksaveasfilename", return_value=path), \
                mock.patch("soilclass.gui.compare_window.messagebox."
                          "showinfo"):
                win.export_pdf()

            pdf = pdfium.PdfDocument(path)
            try:
                self.assertGreater(len(pdf), 0)
                expected = (PAGE_LANDSCAPE[0] * 72.0, PAGE_LANDSCAPE[1] * 72.0)
                for i in range(len(pdf)):
                    size = pdf[i].get_size()
                    for got, want in zip(size, expected):
                        self.assertAlmostEqual(got, want, delta=1.0)
                    page_text = pdf[i].get_textpage().get_text_range()
                    self.assertIn(__app_name__, page_text,
                                 f"page {i} is missing the letterhead")
            finally:
                pdf.close()

    def test_soils_get_unique_labels_not_all_sample_1(self):
        import tempfile
        from pathlib import Path
        from unittest import mock
        from soilclass import project_file
        from soilclass.gui.app import SoilClassApp
        from soilclass.gui.compare_window import ComparisonWindow

        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for i, s in enumerate(_soils(4)):
                s.name = "Sample 1"
                path = Path(tmp) / f"soil_{i + 1}.soilpro"
                project_file.save_project(path, s, "ALL")
                paths.append(str(path))

            app = SoilClassApp(mode="ALL")
            self.addCleanup(app._on_close)
            win = ComparisonWindow(app, samples=[])
            self.addCleanup(win._on_close)
            with mock.patch(
                    "soilclass.gui.compare_window.filedialog."
                    "askopenfilenames", return_value=tuple(paths)):
                win.add_files()
            app.update()

            labels = [win.tree.item(i, "values")[0]
                      for i in win.tree.get_children()]
            self.assertEqual(len(labels), 4)
            self.assertEqual(len(set(labels)), 4, f"not unique: {labels}")
            self.assertNotIn("Sample 1", labels)
            self.assertIn("soil_1", labels)

    def test_toolbar_exposes_the_comparison_window(self):
        from soilclass.gui.app import SoilClassApp
        app = SoilClassApp(mode="ALL")
        self.addCleanup(app._on_close)
        self.assertTrue(hasattr(app, "open_comparison"))


if __name__ == "__main__":
    unittest.main()
