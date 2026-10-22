import os
import unittest

import matplotlib
matplotlib.use("Agg")

from soilclass.charts import (rscs_fines_ratio_figure,
                              rscs_fines_sensitivity_figure)
from soilclass.classifiers import RSCSClassifier
from soilclass.colors import THEME_LIGHT
from soilclass.models import SoilSample


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY"))


def _sample_with_fines_data():
    return SoilSample(name="BH-1",
                      sieve_data=[(19, 100), (4.75, 95), (2.0, 90),
                                  (0.425, 75), (0.075, 60), (0.002, 30)],
                      liquid_limit=60, plastic_limit=25,
                      ll_brine=48, ll_kerosene=30)


def _sample_without_fines_data():
    return SoilSample(name="BH-2",
                      sieve_data=[(19, 100), (4.75, 95), (0.075, 60)],
                      liquid_limit=40, plastic_limit=20)


class TestFinesChartsPlotTheSample(unittest.TestCase):
    def test_ratio_chart_marks_the_sample(self):
        fig = rscs_fines_ratio_figure(_sample_with_fines_data())
        ax = fig.axes[0]
        stars = [l for l in ax.get_lines() if l.get_marker() == "*"]
        self.assertEqual(len(stars), 1)

    def test_sensitivity_chart_marks_the_sample(self):
        fig = rscs_fines_sensitivity_figure(_sample_with_fines_data())
        ax = fig.axes[0]
        stars = [l for l in ax.get_lines() if l.get_marker() == "*"]
        self.assertEqual(len(stars), 1)

    def test_charts_note_missing_data_instead_of_plotting_nothing(self):
        for fn in (rscs_fines_ratio_figure, rscs_fines_sensitivity_figure):
            fig = fn(_sample_without_fines_data())
            ax = fig.axes[0]
            stars = [l for l in ax.get_lines() if l.get_marker() == "*"]
            notes = [t.get_text() for t in ax.texts
                    if "not\nmeasured" in t.get_text()
                    or "not measured" in t.get_text()]
            self.assertEqual(len(stars), 0, fn.__name__)
            self.assertEqual(len(notes), 1, fn.__name__)

    def test_sensitivity_chart_point_matches_the_classifier(self):
        s = _sample_with_fines_data()
        fc = RSCSClassifier.fines_classification(
            float(s.liquid_limit), float(s.ll_brine), float(s.ll_kerosene))
        fig = rscs_fines_sensitivity_figure(s)
        ax = fig.axes[0]
        star = [l for l in ax.get_lines() if l.get_marker() == "*"][0]
        x, y = star.get_xydata()[0]
        self.assertAlmostEqual(x, float(fc["LL_brine_corrected"]), places=3)
        self.assertAlmostEqual(y, float(fc["SE"]), places=3)

    def test_fines_symbol_reaches_the_classification_result(self):
        result = RSCSClassifier().classify(_sample_with_fines_data())
        self.assertIn("-", result.symbol)
        self.assertIn("Fines group", result.extras)
        self.assertIn("Electrical sensitivity, SE", result.extras)


class TestFinesChartsAreRegistered(unittest.TestCase):
    def test_both_charts_are_in_all_figures(self):
        from soilclass.charts import ALL_FIGURES
        labels = [label for label, _ in ALL_FIGURES]
        self.assertTrue(any("Ratio Plane" in l for l in labels))
        self.assertTrue(any("Sensitivity" in l for l in labels))

    def test_pdf_report_includes_them(self):
        from soilclass.charts import ALL_FIGURES
        self.assertEqual(len(ALL_FIGURES), 8)


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestWhiteThemeIsApplied(unittest.TestCase):
    def setUp(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from soilclass.gui import theme
        self._tmpdir = TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self._orig_dir = theme.STORE_DIR
        self._orig_file = theme.STORE_FILE
        self._orig_dark = theme._dark_mode
        theme.STORE_DIR = Path(self._tmpdir.name) / ".soilclasspro"
        theme.STORE_FILE = theme.STORE_DIR / "settings.json"
        theme._dark_mode = False
        self.addCleanup(self._restore_theme)

    def _restore_theme(self):
        from soilclass.gui import theme
        theme.STORE_DIR = self._orig_dir
        theme.STORE_FILE = self._orig_file
        theme._dark_mode = self._orig_dark

    def _make_app(self):
        from soilclass.gui.app import SoilClassApp
        from soilclass.example_data import example_sample
        app = SoilClassApp(mode="ALL")
        app.input_tab.load_sample(example_sample())
        app.classify()
        app.update()
        self.addCleanup(app._on_close)
        return app

    def test_window_background_is_white(self):
        app = self._make_app()
        self.assertEqual(app.cget("background").upper(),
                         THEME_LIGHT["bg"].upper())

    def test_hero_value_box_uses_the_light_palette(self):
        app = self._make_app()
        box = app.results_tab._hero_box
        self.assertEqual(box.value.cget("background").upper(),
                         THEME_LIGHT["card_bg"].upper())

    def test_metrics_rail_cells_use_the_light_palette(self):
        app = self._make_app()
        cell = app.input_tab._metric_cells["gravel"]
        self.assertEqual(cell.value.cget("background").upper(),
                         THEME_LIGHT["rail_bg"].upper())
        self.assertEqual(cell.value.cget("foreground").upper(),
                         THEME_LIGHT["value_fg"].upper())

    def test_dark_mode_toggle_is_in_the_toolbar(self):
        from soilclass.gui.theme_toggle import ThemeToggle
        app = self._make_app()

        def walk(w, acc):
            for ch in w.winfo_children():
                if isinstance(ch, ThemeToggle):
                    acc.append(ch)
                walk(ch, acc)
            return acc

        toggles = walk(app, [])
        self.assertEqual(len(toggles), 1)
        self.assertTrue(hasattr(app, "_toggle_theme"))


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestHeroBoxFitsLongSymbols(unittest.TestCase):
    def test_rscs_fines_symbol_is_not_clipped(self):
        from soilclass.gui.app import SoilClassApp
        app = SoilClassApp(mode="RSCS",
                           preset_sample=_sample_with_fines_data())
        self.addCleanup(app._on_close)
        app.classify()
        app.update()
        box = app.results_tab._hero_box
        symbol = app.results_tab.results[0].symbol
        self.assertIn("-", symbol)
        self.assertEqual(box.value.cget("text"), symbol)
        self.assertGreaterEqual(int(box.value.cget("width")), len(symbol))


if __name__ == "__main__":
    unittest.main()
