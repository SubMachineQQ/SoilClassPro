import inspect
import unittest


class TestSplashDuration(unittest.TestCase):
    def test_splashscreen_default_duration(self):
        from soilclass.gui.splash import SplashScreen
        sig = inspect.signature(SplashScreen.__init__)
        self.assertEqual(sig.parameters["duration_ms"].default, 4000)

    def test_show_splash_then_launcher_default_duration(self):
        from soilclass.gui.splash import show_splash_then_launcher
        sig = inspect.signature(show_splash_then_launcher)
        self.assertEqual(sig.parameters["duration_ms"].default, 4000)


if __name__ == "__main__":
    unittest.main()
