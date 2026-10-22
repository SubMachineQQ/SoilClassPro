import unittest
from datetime import date

from soilclass import __version__, about, i18n, updates


class TestVersion(unittest.TestCase):
    def test_release_version(self):
        self.assertEqual(__version__, "1.0.0")

    def test_installer_uses_the_same_version(self):
        from pathlib import Path
        iss = (Path(__file__).resolve().parent.parent / "installer"
               / "SoilClassPro.iss").read_text(encoding="utf-8")
        self.assertIn(f'#define MyAppVersion "{__version__}"', iss)


class TestAbout(unittest.TestCase):
    def test_developers_and_acknowledgement(self):
        self.assertEqual(len(about.AUTHORS), 3)
        self.assertNotIn(about.ACKNOWLEDGED, about.AUTHORS)
        self.assertEqual(about.ACKNOWLEDGED, "Nejan Huvaj")
        self.assertIn("Batuhan Barış Döğer", about.AUTHORS)
        self.assertIn("Erol Boz", about.AUTHORS)

    def test_format_date_turkish(self):
        self.assertEqual(about.format_date(date(2026, 10, 21), "tr"),
                         "21 Ekim 2026")

    def test_format_date_english(self):
        self.assertEqual(about.format_date(date(2026, 2, 3), "en"),
                         "3 February 2026")


class TestWelcomeTexts(unittest.TestCase):
    KEYS = ("welcome_title", "welcome_thanks", "welcome_thanks_body",
            "welcome_developers", "welcome_institution",
            "welcome_disclaimer_title", "welcome_disclaimer",
            "welcome_license", "welcome_accept", "welcome_exit",
            "about_menu", "about_close", "update_available",
            "pdf_disclaimer", "splash_thanks")

    def tearDown(self):
        i18n._current_language = None

    def test_keys_exist_in_both_languages(self):
        for lang in ("en", "tr"):
            i18n._current_language = lang
            for key in self.KEYS:
                self.assertNotEqual(i18n.t(key), key, f"{lang}:{key}")

    def test_disclaimer_states_no_liability(self):
        i18n._current_language = "tr"
        self.assertIn("hukuken sorumlu tutulamaz", i18n.t("welcome_disclaimer"))
        i18n._current_language = "en"
        self.assertIn("no legal liability", i18n.t("welcome_disclaimer"))

    def test_first_launch_follows_system_language(self):
        from unittest import mock
        with mock.patch.object(i18n, "STORE_FILE",
                               i18n.STORE_DIR / "missing-settings.json"):
            for system, expected in (("tr", "tr"), ("en", "en")):
                i18n._current_language = None
                with mock.patch.object(i18n, "system_language",
                                       return_value=system):
                    self.assertEqual(i18n.get_language(), expected)

    def test_saved_language_wins_over_system_language(self):
        import json
        import tempfile
        from pathlib import Path
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "settings.json"
            store.write_text(json.dumps({"language": "en"}), encoding="utf-8")
            with mock.patch.object(i18n, "STORE_FILE", store), \
                    mock.patch.object(i18n, "system_language",
                                      return_value="tr"):
                i18n._current_language = None
                self.assertEqual(i18n.get_language(), "en")

    def test_disclaimer_has_no_hedging_clause(self):
        i18n._current_language = "tr"
        self.assertNotIn("eksik olabilir", i18n.t("welcome_disclaimer"))
        i18n._current_language = "en"
        self.assertNotIn("incomplete", i18n.t("welcome_disclaimer"))

    def test_copyright_mentions_mit(self):
        for lang in ("en", "tr"):
            i18n._current_language = lang
            self.assertIn("MIT", i18n.t("splash_copyright"))


class TestUpdates(unittest.TestCase):
    def test_parse_version(self):
        self.assertEqual(updates.parse_version("v1.2"), (1, 2, 0))
        self.assertEqual(updates.parse_version("1.10.3"), (1, 10, 3))

    def test_is_newer(self):
        self.assertTrue(updates.is_newer("1.0.1", "1.0.0"))
        self.assertTrue(updates.is_newer("v1.10.0", "1.9.9"))
        self.assertFalse(updates.is_newer("1.0.0", "1.0.0"))
        self.assertFalse(updates.is_newer("0.9.0", "1.0.0"))

    def test_no_repository_means_no_network_call(self):
        self.assertIsNone(updates.fetch_latest(""))


if __name__ == "__main__":
    unittest.main()
