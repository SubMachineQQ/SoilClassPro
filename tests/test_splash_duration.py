import inspect
import os
import unittest
from unittest import mock


class TestSplashDuration(unittest.TestCase):
    def test_duration_is_random_between_limits(self):
        from soilclass.gui import splash
        self.assertEqual((splash.SPLASH_MIN_MS, splash.SPLASH_MAX_MS),
                         (2500, 3500))
        values = {splash.splash_duration() for _ in range(300)}
        self.assertTrue(all(2500 <= v <= 3500 for v in values))
        self.assertGreater(len(values), 50)

    def test_defaults_use_the_random_duration(self):
        from soilclass.gui.splash import SplashScreen, show_splash_then_launcher
        for func in (SplashScreen.__init__, show_splash_then_launcher):
            self.assertIsNone(
                inspect.signature(func).parameters["duration_ms"].default)

    def test_random_value_drives_the_splash(self):
        from soilclass.gui import splash
        with mock.patch.object(splash.random, "randint",
                               return_value=3100) as randint:
            self.assertEqual(splash.splash_duration(), 3100)
        randint.assert_called_once_with(2500, 3500)


@unittest.skipUnless(os.environ.get("DISPLAY"), "no DISPLAY available for a GUI test")
class TestSplashProgressBar(unittest.TestCase):
    def test_bar_follows_the_clock_and_is_full_when_closing(self):
        import time
        from soilclass.gui.splash import SplashScreen
        duration = 600
        splash = SplashScreen(duration)
        samples = []
        original = splash._animate_progress

        def tick():
            original()
            if splash._started is not None:
                elapsed = (time.perf_counter() - splash._started) * 1000.0
                width = int(splash._bar_fill.place_info().get("width", 0))
                samples.append((elapsed, width / splash._track_width))

        splash._animate_progress = tick
        splash.after_cancel(splash._anim_job)
        splash._anim_job = splash.after(0, splash._animate_progress)
        started = time.perf_counter()
        splash.mainloop()
        lifetime = (time.perf_counter() - started) * 1000.0

        self.assertGreater(len(samples), 10)
        for elapsed, fraction in samples:
            self.assertLessEqual(abs(fraction - min(1.0, elapsed / duration)),
                                 0.05)
        self.assertEqual(samples[-1][1], 1.0)
        self.assertGreaterEqual(lifetime, duration)
        self.assertLess(lifetime, duration + 400)


if __name__ == "__main__":
    unittest.main()
