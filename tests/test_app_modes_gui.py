import os
import unittest

from soilclass.charts import classifiable_chart_defs
from soilclass.example_data import example_sample
from soilclass.gui.modes import MODE_CHARTS
from soilclass.models import SoilSample


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestModeRestrictedTabs(unittest.TestCase):
    def _make(self, mode):
        from soilclass.gui.app import SoilClassApp
        app = SoilClassApp(mode=mode)
        app.update()
        return app

    def _classify(self, app, sample=None):
        app.input_tab.load_sample(sample or example_sample())
        app.classify()
        app.update()
        return app.results_window

    def test_main_window_has_no_tab_strip(self):
        app = self._make("ALL")
        try:
            self.assertFalse(hasattr(app, "nb"))
            self.assertFalse(hasattr(app, "chart_tabs"))
        finally:
            app.destroy()

    def test_all_mode_popup_has_expected_tabs(self):
        app = self._make("ALL")
        try:
            win = self._classify(app)
            expected = classifiable_chart_defs(MODE_CHARTS["ALL"],
                                               app.sample)
            self.assertEqual(len(win.nb.tabs()), 1 + len(expected))
        finally:
            app.destroy()

    def test_astm_mode_popup_has_expected_tabs(self):
        app = self._make("ASTM")
        try:
            win = self._classify(app)
            texts = [win.nb.tab(i, "text") for i in win.nb.tabs()]
            self.assertTrue(any("Plasticity (ASTM)" in txt for txt in texts))
            self.assertFalse(any("RSCS" in txt for txt in texts))
            self.assertFalse(any("AASHTO" in txt for txt in texts))
            self.assertFalse(any("ISO 14688" in txt for txt in texts))
        finally:
            app.destroy()

    def test_rscs_mode_popup_only_shows_rscs_chart(self):
        app = self._make("RSCS")
        try:
            win = self._classify(app)
            texts = [win.nb.tab(i, "text") for i in win.nb.tabs()]
            self.assertTrue(any("RSCS Ternary" in txt for txt in texts))
            self.assertFalse(any("Plasticity" in txt for txt in texts))
            self.assertFalse(any("AASHTO" in txt for txt in texts))
        finally:
            app.destroy()

    def test_no_reference_guide_tab_anywhere(self):
        for mode in ("ALL", "ASTM", "BS", "ISO14688", "RSCS"):
            app = self._make(mode)
            try:
                win = self._classify(app)
                texts = [win.nb.tab(i, "text") for i in win.nb.tabs()]
                self.assertFalse(any("Reference" in txt for txt in texts))
            finally:
                app.destroy()

    def test_classify_only_runs_selected_classifier(self):
        app = self._make("BS")
        try:
            self._classify(app)
            self.assertEqual(len(app.results_tab.results), 1)
            self.assertIn("BS 5930", app.results_tab.results[0].system)
        finally:
            app.destroy()

    def test_repeated_classify_reuses_the_same_popup(self):
        app = self._make("ALL")
        try:
            win1 = self._classify(app)
            win2 = self._classify(app)
            self.assertIs(win1, win2)
        finally:
            app.destroy()

    def test_non_plastic_sample_hides_plasticity_tabs(self):
        sample = SoilSample("Clean sand", [(4.75, 100), (0.075, 2)])
        app = self._make("ALL")
        try:
            win = self._classify(app, sample)
            texts = [win.nb.tab(i, "text") for i in win.nb.tabs()]
            self.assertFalse(any("Plasticity" in txt for txt in texts))
            self.assertFalse(any("AASHTO" in txt for txt in texts))
            self.assertTrue(any("Grain Size" in txt for txt in texts))
        finally:
            app.destroy()

    def test_sample_without_extra_lls_hides_rscs_fines_tabs(self):
        app = self._make("ALL")
        try:
            win = self._classify(app)
            texts = [win.nb.tab(i, "text") for i in win.nb.tabs()]
            self.assertFalse(any("RSCS Fines" in txt for txt in texts))
        finally:
            app.destroy()

    @staticmethod
    def _find_button(widget, text_substr):
        for child in widget.winfo_children():
            if (child.winfo_class() == "TButton"
                    and text_substr in child.cget("text")):
                return child
            found = TestModeRestrictedTabs._find_button(child, text_substr)
            if found is not None:
                return found
        return None

    def test_single_export_button_sits_below_the_tabs(self):
        app = self._make("ALL")
        try:
            win = self._classify(app)
            buttons = []

            def collect(widget):
                for child in widget.winfo_children():
                    if (child.winfo_class() == "TButton"
                            and "Generate PDF Report" in child.cget("text")):
                        buttons.append(child)
                    collect(child)

            collect(win)
            self.assertEqual(len(buttons), 1)
            button = buttons[0]
            notebook_bottom = win.nb.winfo_rooty() + win.nb.winfo_height()
            for label, tab in [("Results", win.results_tab)] + list(win.chart_tabs):
                win.nb.select(tab)
                win.update()
                self.assertTrue(button.winfo_ismapped(), label)
                self.assertGreaterEqual(button.winfo_rooty(), notebook_bottom,
                                        f"export button overlaps {label!r}")
                self.assertLessEqual(
                    button.winfo_rootx() + button.winfo_width(),
                    win.winfo_rootx() + win.winfo_width(), label)
        finally:
            app.destroy()

    def test_export_button_triggers_the_export_callback(self):
        calls = []
        app = self._make("ALL")
        try:
            win = self._classify(app)
            win._on_export_pdf = lambda: calls.append(1)
            self._find_button(win, "Generate PDF Report").invoke()
            self.assertEqual(calls, [1])
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
