import tempfile
import unittest
from pathlib import Path

from soilclass import recent_projects as rp


class TestRecentProjects(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._orig_dir = rp.STORE_DIR
        self._orig_file = rp.STORE_FILE
        rp.STORE_DIR = Path(self._tmp.name)
        rp.STORE_FILE = rp.STORE_DIR / "recent_projects.json"

    def tearDown(self):
        rp.STORE_DIR = self._orig_dir
        rp.STORE_FILE = self._orig_file
        self._tmp.cleanup()

    def _touch(self, name: str) -> str:
        p = Path(self._tmp.name) / name
        p.write_text("{}", encoding="utf-8")
        return str(p)

    def test_empty_by_default(self):
        self.assertEqual(rp.get_recent(), [])

    def test_add_and_get(self):
        a = self._touch("a.soilpro")
        b = self._touch("b.soilpro")
        rp.add_recent(a)
        rp.add_recent(b)
        recents = rp.get_recent()
        self.assertEqual(recents[0], str(Path(b).resolve()))
        self.assertIn(str(Path(a).resolve()), recents)

    def test_reopening_moves_to_front(self):
        a = self._touch("a.soilpro")
        b = self._touch("b.soilpro")
        rp.add_recent(a)
        rp.add_recent(b)
        rp.add_recent(a)
        self.assertEqual(rp.get_recent()[0], str(Path(a).resolve()))

    def test_deleted_files_are_filtered_out(self):
        a = self._touch("a.soilpro")
        rp.add_recent(a)
        Path(a).unlink()
        self.assertEqual(rp.get_recent(), [])

    def test_caps_at_max_items(self):
        for i in range(rp.MAX_ITEMS + 3):
            rp.add_recent(self._touch(f"p{i}.soilpro"))
        self.assertEqual(len(rp.get_recent()), rp.MAX_ITEMS)


if __name__ == "__main__":
    unittest.main()
