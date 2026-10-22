import atexit
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

TEST_HOME = Path(tempfile.mkdtemp(prefix="soilclasspro-tests-"))
os.environ["USERPROFILE"] = str(TEST_HOME)
os.environ["HOME"] = str(TEST_HOME)
(TEST_HOME / ".soilclasspro").mkdir()
(TEST_HOME / ".soilclasspro" / "settings.json").write_text(
    json.dumps({"language": "en", "dark_mode": False}), encoding="utf-8")
atexit.register(shutil.rmtree, TEST_HOME, True)


class TestIsolation(unittest.TestCase):
    def test_user_files_point_to_the_temporary_home(self):
        from soilclass import consent, i18n, recent_projects
        from soilclass.gui import theme
        for path in (i18n.STORE_FILE, theme.STORE_FILE,
                     recent_projects.STORE_FILE, consent.CONSENT_FILE):
            self.assertTrue(Path(path).is_relative_to(TEST_HOME), path)


if __name__ == "__main__":
    unittest.main()
