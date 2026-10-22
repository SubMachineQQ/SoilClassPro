import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from soilclass import i18n


class TestI18n(unittest.TestCase):
    def setUp(self):
        self._tmpdir = TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self._orig_dir = i18n.STORE_DIR
        self._orig_file = i18n.STORE_FILE
        self._orig_lang = i18n._current_language
        i18n.STORE_DIR = Path(self._tmpdir.name) / ".soilclasspro"
        i18n.STORE_FILE = i18n.STORE_DIR / "settings.json"
        i18n._current_language = None
        self.addCleanup(self._restore)

    def _restore(self):
        i18n.STORE_DIR = self._orig_dir
        i18n.STORE_FILE = self._orig_file
        i18n._current_language = self._orig_lang

    def test_defaults_to_english(self):
        self.assertEqual(i18n.get_language(), "en")

    def test_set_language_round_trips(self):
        i18n.set_language("tr")
        self.assertEqual(i18n.get_language(), "tr")
        i18n._current_language = None
        self.assertEqual(i18n.get_language(), "tr")

    def test_translated_key_differs_by_language(self):
        i18n.set_language("en")
        en_text = i18n.t("save_project")
        i18n.set_language("tr")
        tr_text = i18n.t("save_project")
        self.assertNotEqual(en_text, tr_text)
        self.assertEqual(en_text, "Save Project")

    def test_unknown_key_falls_back_to_the_key_itself(self):
        self.assertEqual(i18n.t("this_key_does_not_exist"),
                         "this_key_does_not_exist")

    def test_unknown_language_code_raises(self):
        with self.assertRaises(ValueError):
            i18n.set_language("fr")


if __name__ == "__main__":
    unittest.main()
