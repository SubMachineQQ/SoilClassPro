import os
import unittest

import matplotlib.pyplot as plt


def _has_display() -> bool:
    return bool(os.environ.get("DISPLAY"))


@unittest.skipUnless(_has_display(), "no DISPLAY available for a GUI test")
class TestCleanShutdown(unittest.TestCase):
    def _run_with_watchdog(self, app, timeout_ms=5000):
        timed_out = {"flag": False}

        def watchdog():
            timed_out["flag"] = True
            app.quit()

        watchdog_id = app.after(timeout_ms, watchdog)
        app.mainloop()
        if not timed_out["flag"]:
            app.after_cancel(watchdog_id)
        self.assertFalse(
            timed_out["flag"],
            "mainloop() did not return within the timeout - the window "
            "close handler is not cleaning up properly (regression of "
            "the matplotlib-figures-keep-the-process-alive bug).")

    def test_closing_after_classify_returns_from_mainloop(self):
        from soilclass.gui.app import SoilClassApp
        from soilclass.example_data import example_sample

        app = SoilClassApp(mode="ALL")

        def classify_and_close():
            app.input_tab.load_sample(example_sample())
            app.classify()
            self.assertGreater(len(plt.get_fignums()), 0,
                               "test setup: expected some open figures")
            app._on_close()

        app.after(100, classify_and_close)
        self._run_with_watchdog(app)
        self.assertEqual(plt.get_fignums(), [],
                         "matplotlib figures were left open after close")

    def test_two_sequential_windows_both_close_cleanly(self):
        from soilclass.gui.app import SoilClassApp
        from soilclass.example_data import example_sample

        for mode in ("RSCS", "BS"):
            app = SoilClassApp(mode=mode, preset_sample=example_sample())

            def classify_and_close(app=app):
                app.classify()
                app._on_close()

            app.after(100, classify_and_close)
            self._run_with_watchdog(app)
        self.assertEqual(plt.get_fignums(), [])


if __name__ == "__main__":
    unittest.main()
