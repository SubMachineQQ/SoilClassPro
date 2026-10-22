import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from soilclass import consent


class ConsentFileTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.path = self.dir / "sub" / "consent.json"

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def write(self, text):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(text, encoding="utf-8")

    def test_missing_file_is_not_accepted(self):
        self.assertFalse(consent.is_accepted(self.path))

    def test_empty_file_is_not_accepted(self):
        self.write("")
        self.assertFalse(consent.is_accepted(self.path))

    def test_corrupt_file_is_not_accepted(self):
        self.write("{not json")
        self.assertFalse(consent.is_accepted(self.path))

    def test_non_object_json_is_not_accepted(self):
        for text in ("[]", "true", "1", '"yes"', "null"):
            self.write(text)
            self.assertFalse(consent.is_accepted(self.path), text)

    def test_missing_fields_are_not_accepted(self):
        self.write(json.dumps({"disclaimer_version": consent.DISCLAIMER_VERSION}))
        self.assertFalse(consent.is_accepted(self.path))
        self.write(json.dumps({"accepted_at": "2026-10-21T10:00:00"}))
        self.assertFalse(consent.is_accepted(self.path))

    def test_wrong_or_mistyped_version_is_not_accepted(self):
        for version in (consent.DISCLAIMER_VERSION + 1, 0, "1", 1.0, True, None):
            self.write(json.dumps({"disclaimer_version": version,
                                   "accepted_at": "2026-10-21T10:00:00"}))
            self.assertFalse(consent.is_accepted(self.path), repr(version))

    def test_record_then_accepted(self):
        self.assertTrue(consent.record_acceptance(self.path))
        self.assertTrue(consent.is_accepted(self.path))
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(data["disclaimer_version"], consent.DISCLAIMER_VERSION)
        self.assertTrue(data["accepted_at"])

    def test_record_leaves_no_temporary_files(self):
        consent.record_acceptance(self.path)
        self.assertEqual(sorted(p.name for p in self.path.parent.iterdir()),
                         ["consent.json"])

    def test_failed_write_reports_false_and_stays_not_accepted(self):
        with mock.patch("soilclass.consent.os.replace",
                        side_effect=OSError("disk full")):
            self.assertFalse(consent.record_acceptance(self.path))
        self.assertFalse(consent.is_accepted(self.path))
        self.assertEqual(list(self.path.parent.iterdir()), [])

    def test_broken_settings_file_does_not_affect_consent(self):
        consent.record_acceptance(self.path)
        settings = self.path.parent / "settings.json"
        settings.write_text("{broken", encoding="utf-8")
        self.assertTrue(consent.is_accepted(self.path))

    def test_default_location_is_the_user_settings_folder(self):
        self.assertEqual(consent.CONSENT_FILE.name, "consent.json")
        self.assertEqual(consent.CONSENT_FILE.parent.name, ".soilclasspro")


class GateTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.path = self.dir / "consent.json"
        self.patch = mock.patch.object(consent, "CONSENT_FILE", self.path)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_first_launch_always_asks(self):
        from soilclass.gui.splash import ensure_disclaimer_accepted
        ask = mock.Mock(return_value=True)
        self.assertTrue(ensure_disclaimer_accepted(ask))
        ask.assert_called_once()
        self.assertTrue(consent.is_accepted())

    def test_second_launch_does_not_ask(self):
        from soilclass.gui.splash import ensure_disclaimer_accepted
        consent.record_acceptance()
        ask = mock.Mock(return_value=True)
        self.assertTrue(ensure_disclaimer_accepted(ask))
        ask.assert_not_called()

    def test_decline_blocks_and_is_not_remembered(self):
        from soilclass.gui.splash import ensure_disclaimer_accepted
        ask = mock.Mock(return_value=False)
        self.assertFalse(ensure_disclaimer_accepted(ask))
        self.assertFalse(consent.is_accepted())
        self.assertFalse(ensure_disclaimer_accepted(ask))
        self.assertEqual(ask.call_count, 2)

    def test_unsaved_acceptance_asks_again_next_time(self):
        from soilclass.gui.splash import ensure_disclaimer_accepted
        ask = mock.Mock(return_value=True)
        with mock.patch("soilclass.consent.os.replace",
                        side_effect=OSError("read-only")):
            self.assertTrue(ensure_disclaimer_accepted(ask))
        self.assertTrue(ensure_disclaimer_accepted(ask))
        self.assertEqual(ask.call_count, 2)

    def test_dialog_error_stops_the_program(self):
        from soilclass.gui.splash import ensure_disclaimer_accepted
        ask = mock.Mock(side_effect=RuntimeError("no display"))
        with self.assertRaises(RuntimeError):
            ensure_disclaimer_accepted(ask)
        self.assertFalse(consent.is_accepted())

    def test_launcher_loop_never_opens_without_acceptance(self):
        from soilclass.gui import splash
        with mock.patch.object(splash, "ensure_disclaimer_accepted",
                               return_value=False), \
                mock.patch("soilclass.gui.launcher.LauncherWindow") as window:
            splash.run_launcher_loop()
        window.assert_not_called()


if __name__ == "__main__":
    unittest.main()
