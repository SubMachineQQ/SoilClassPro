import csv
import io
import unittest

from soilclass.classifiers import classify_all
from soilclass.example_data import example_sample
from soilclass.report import build_ags4_text, export_ags4


def _parse_groups(text: str):
    reader = csv.reader(io.StringIO(text))
    groups = {}
    current = None
    for row in reader:
        if not row:
            continue
        tag, rest = row[0], row[1:]
        if tag == "GROUP":
            current = rest[0]
            groups[current] = {"heading": [], "rows": []}
        elif tag == "HEADING":
            groups[current]["heading"] = rest
        elif tag == "DATA":
            groups[current]["rows"].append(rest)
    return groups


class TestAGS4Export(unittest.TestCase):
    def test_produces_the_expected_groups(self):
        sample = example_sample()
        text = build_ags4_text(sample, classify_all(sample))
        groups = _parse_groups(text)
        for name in ("PROJ", "TRAN", "ABBR", "TYPE", "UNIT", "LOCA", "SAMP",
                     "GRAG", "GRAT", "LLPL"):
            self.assertIn(name, groups)

    def test_grat_has_one_row_per_sieve_point(self):
        sample = example_sample()
        groups = _parse_groups(build_ags4_text(sample))
        self.assertEqual(len(groups["GRAT"]["rows"]), len(sample.sieve_data))

    def test_llpl_carries_the_atterberg_limits(self):
        sample = example_sample()
        groups = _parse_groups(build_ags4_text(sample))
        heading = groups["LLPL"]["heading"]
        row = groups["LLPL"]["rows"][0]
        values = dict(zip(heading, row))
        self.assertAlmostEqual(float(values["LLPL_LL"]), sample.liquid_limit,
                               places=1)
        self.assertAlmostEqual(float(values["LLPL_PL"]), sample.plastic_limit,
                               places=1)

    def test_llpl_omitted_when_no_atterberg_limits(self):
        from soilclass.models import SoilSample
        sample = SoilSample("No plasticity", [(2.0, 100), (0.075, 40)])
        groups = _parse_groups(build_ags4_text(sample))
        self.assertNotIn("LLPL", groups)

    def test_export_ags4_writes_a_file(self):
        import os
        import tempfile
        sample = example_sample()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "sample.ags")
            export_ags4(path, sample, classify_all(sample))
            self.assertTrue(os.path.isfile(path))
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("GRAT", content)


if __name__ == "__main__":
    unittest.main()
