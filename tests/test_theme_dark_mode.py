import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from soilclass.gui import theme


class TestDarkModePersistence(unittest.TestCase):
    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self._orig_dir = theme.STORE_DIR
        self._orig_file = theme.STORE_FILE
        self._orig_dark = theme._dark_mode
        theme.STORE_DIR = Path(self._tmpdir.name) / ".soilclasspro"
        theme.STORE_FILE = theme.STORE_DIR / "settings.json"
        theme._dark_mode = None
        self.addCleanup(self._restore)

    def _restore(self):
        theme.STORE_DIR = self._orig_dir
        theme.STORE_FILE = self._orig_file
        theme._dark_mode = self._orig_dark

    def test_defaults_to_light(self):
        self.assertFalse(theme.get_dark_mode())

    def test_set_dark_mode_round_trips(self):
        theme.set_dark_mode(True)
        self.assertTrue(theme.get_dark_mode())
        theme._dark_mode = None
        self.assertTrue(theme.get_dark_mode())

    def test_set_dark_mode_false_round_trips(self):
        theme.set_dark_mode(True)
        theme.set_dark_mode(False)
        theme._dark_mode = None
        self.assertFalse(theme.get_dark_mode())

    def test_persists_alongside_other_settings(self):
        theme.STORE_DIR.mkdir(parents=True, exist_ok=True)
        theme.STORE_FILE.write_text('{"language": "tr"}', encoding="utf-8")
        theme.set_dark_mode(True)
        import json
        data = json.loads(theme.STORE_FILE.read_text(encoding="utf-8"))
        self.assertEqual(data["language"], "tr")
        self.assertTrue(data["dark_mode"])

    def test_missing_settings_file_defaults_to_light(self):
        self.assertFalse(theme.STORE_FILE.exists())
        self.assertFalse(theme.get_dark_mode())

    def test_corrupt_settings_file_defaults_to_light(self):
        theme.STORE_DIR.mkdir(parents=True, exist_ok=True)
        theme.STORE_FILE.write_text("not json", encoding="utf-8")
        self.assertFalse(theme.get_dark_mode())


if __name__ == "__main__":
    unittest.main()
