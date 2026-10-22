import tempfile
import unittest
from pathlib import Path

from soilclass import project_file
from soilclass.example_data import example_sample


class TestProjectFile(unittest.TestCase):
    def test_round_trip_preserves_data(self):
        sample = example_sample()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.soilpro"
            project_file.save_project(path, sample, mode="ASTM")
            loaded, mode = project_file.load_project(path)

        self.assertEqual(mode, "ASTM")
        self.assertEqual(loaded.name, sample.name)
        self.assertEqual(loaded.project, sample.project)
        self.assertEqual(loaded.liquid_limit, sample.liquid_limit)
        self.assertEqual(loaded.plastic_limit, sample.plastic_limit)
        self.assertEqual(loaded.organic, sample.organic)
        self.assertEqual(sorted(loaded.sieve_data), sorted(sample.sieve_data))

    def test_non_plastic_sample_round_trips(self):
        sample = example_sample()
        sample.liquid_limit = None
        sample.plastic_limit = None
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "np.soilpro"
            project_file.save_project(path, sample, mode="ALL")
            loaded, mode = project_file.load_project(path)
        self.assertIsNone(loaded.liquid_limit)
        self.assertIsNone(loaded.plastic_limit)
        self.assertEqual(mode, "ALL")

    def test_rejects_foreign_json_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "not_a_project.soilpro"
            path.write_text('{"hello": "world"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                project_file.load_project(path)

    def test_rejects_missing_file(self):
        with self.assertRaises(ValueError):
            project_file.load_project("/no/such/file.soilpro")


if __name__ == "__main__":
    unittest.main()
