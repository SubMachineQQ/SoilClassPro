import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from soilclass import project_file
from soilclass.example_data import example_sample


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestNavigation(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch("soilclass.recent_projects.add_recent")
        patcher.start()
        self.addCleanup(patcher.stop)

    def _run_with_watchdog(self, app, timeout_ms=5000):
        timed_out = {"flag": False}

        def watchdog():
            timed_out["flag"] = True
            app.quit()

        watchdog_id = app.after(timeout_ms, watchdog)
        app.mainloop()
        if not timed_out["flag"]:
            app.after_cancel(watchdog_id)
        self.assertFalse(timed_out["flag"], "mainloop() did not return")

    def test_home_button_sets_next_screen_and_closes(self):
        from soilclass.gui.app import SoilClassApp

        app = SoilClassApp(mode="ASTM")

        def click_home():
            with mock.patch("soilclass.gui.app.messagebox.askyesno",
                            return_value=True):
                app._go_home()

        app.after(100, click_home)
        self._run_with_watchdog(app)
        self.assertEqual(app.next_screen, ("launcher", None, None))

    def test_home_with_no_unsaved_changes_goes_straight_home(self):
        from soilclass.gui.app import SoilClassApp

        app = SoilClassApp(mode="ASTM")
        app._dirty = False
        app.after(100, app._go_home)
        self._run_with_watchdog(app)
        self.assertEqual(app.next_screen, ("launcher", None, None))

    def test_home_cancelled_with_unsaved_changes_keeps_window_open(self):
        from soilclass.gui.app import SoilClassApp

        app = SoilClassApp(mode="ASTM")

        def click_home_then_close():
            app._dirty = True
            with mock.patch("soilclass.gui.app.messagebox.askyesnocancel",
                            return_value=None):
                app._go_home()
            self.assertIsNone(app.next_screen)
            app._dirty = False
            app._on_close()

        app.after(100, click_home_then_close)
        self._run_with_watchdog(app)

    def test_home_discarding_unsaved_changes_proceeds(self):
        from soilclass.gui.app import SoilClassApp

        app = SoilClassApp(mode="ASTM")

        def click_home():
            app._dirty = True
            with mock.patch("soilclass.gui.app.messagebox.askyesnocancel",
                            return_value=False):
                app._go_home()

        app.after(100, click_home)
        self._run_with_watchdog(app)
        self.assertEqual(app.next_screen, ("launcher", None, None))

    def test_open_same_mode_loads_in_place(self):
        from soilclass.gui.app import SoilClassApp

        app = SoilClassApp(mode="BS")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "same_mode.soilpro"
            project_file.save_project(path, example_sample(), "BS")

            def do_open():
                with mock.patch(
                        "soilclass.gui.app.filedialog.askopenfilename",
                        return_value=str(path)):
                    app.open_project()
                self.assertIsNone(app.next_screen)
                self.assertIsNone(app.results_tab)
                app.classify()
                self.assertEqual(len(app.results_tab.results), 1)
                app._on_close()

            app.after(100, do_open)
            self._run_with_watchdog(app)

    def test_open_different_mode_schedules_reopen_and_closes(self):
        from soilclass.gui.app import SoilClassApp

        app = SoilClassApp(mode="ASTM")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "different_mode.soilpro"
            project_file.save_project(path, example_sample(), "RSCS")

            def do_open():
                with mock.patch(
                        "soilclass.gui.app.filedialog.askopenfilename",
                        return_value=str(path)):
                    app.open_project()

            app.after(100, do_open)
            self._run_with_watchdog(app)
            self.assertIsNotNone(app.next_screen)
            kind, mode, sample = app.next_screen
            self.assertEqual(kind, "app")
            self.assertEqual(mode, "RSCS")
            self.assertIsNotNone(sample)

    def test_window_title_defaults_to_untitled(self):
        from soilclass.gui.app import SoilClassApp
        from soilclass.models import SoilSample

        app = SoilClassApp(mode="ASTM",
                           preset_sample=SoilSample(project="", sieve_data=[]))
        self.assertIn("Untitled", app.title())
        app._on_close()

    def test_window_title_uses_project_name(self):
        from soilclass.gui.app import SoilClassApp
        from soilclass.models import SoilSample

        app = SoilClassApp(
            mode="ASTM",
            preset_sample=SoilSample(project="Riverside Embankment",
                                     sieve_data=[]))
        self.assertIn("Riverside Embankment", app.title())
        app._on_close()


if __name__ == "__main__":
    unittest.main()
