import ast
import unittest
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

from soilclass.charts import astm_plasticity_figure, bs_plasticity_figure
from soilclass.charts import aashto_figure, gsd_figure, iso14688_plasticity_figure
from soilclass.example_data import example_sample
from soilclass.models import SoilSample


def _fully_non_plastic_sample():
    return SoilSample(name="Sample 1",
                      sieve_data=[(10, 100), (6, 81), (2, 58),
                                  (0.5, 35), (0.15, 11)],
                      liquid_limit=None, plastic_limit=None)


class TestGsdHasNoStar(unittest.TestCase):
    def test_no_star_marker_on_gsd_chart(self):
        fig = gsd_figure(example_sample())
        ax = fig.axes[0]
        stars = [l for l in ax.get_lines() if l.get_marker() == "*"]
        self.assertEqual(len(stars), 0)


class TestNonPlasticSampleGetsANote(unittest.TestCase):
    def test_astm_shows_note_not_nothing(self):
        s = _fully_non_plastic_sample()
        fig = astm_plasticity_figure(s)
        ax = fig.axes[0]
        stars = [l for l in ax.get_lines() if l.get_marker() == "*"]
        notes = [t.get_text() for t in ax.texts
                if "nothing to plot" in t.get_text()]
        self.assertEqual(len(stars), 0)
        self.assertEqual(len(notes), 1)

    def test_bs_shows_note_not_nothing(self):
        s = _fully_non_plastic_sample()
        fig = bs_plasticity_figure(s)
        ax = fig.axes[0]
        notes = [t.get_text() for t in ax.texts
                if "nothing to plot" in t.get_text()]
        self.assertEqual(len(notes), 1)

    def test_iso14688_shows_note_not_nothing(self):
        s = _fully_non_plastic_sample()
        fig = iso14688_plasticity_figure(s)
        ax = fig.axes[0]
        notes = [t.get_text() for t in ax.texts
                if "nothing to plot" in t.get_text()]
        self.assertEqual(len(notes), 1)

    def test_aashto_shows_note_not_nothing(self):
        s = _fully_non_plastic_sample()
        fig = aashto_figure(s)
        ax = fig.axes[0]
        notes = [t.get_text() for t in ax.texts
                if "nothing to plot" in t.get_text()]
        self.assertEqual(len(notes), 1)

    def test_plastic_sample_still_gets_a_star_not_a_note(self):
        s = SoilSample(name="A", sieve_data=[(4.75, 100), (0.075, 40)],
                      liquid_limit=38, plastic_limit=19)
        fig = astm_plasticity_figure(s)
        ax = fig.axes[0]
        stars = [l for l in ax.get_lines() if l.get_marker() == "*"]
        notes = [t.get_text() for t in ax.texts
                if "nothing to plot" in t.get_text()]
        self.assertEqual(len(stars), 1)
        self.assertEqual(len(notes), 0)

    def test_ll_only_sample_gets_a_star_at_pi_zero_not_a_note(self):
        s = SoilSample(name="B", sieve_data=[(4.75, 100), (0.075, 20)],
                      liquid_limit=30, plastic_limit=None)
        fig = astm_plasticity_figure(s)
        ax = fig.axes[0]
        stars = [l for l in ax.get_lines() if l.get_marker() == "*"]
        notes = [t.get_text() for t in ax.texts
                if "nothing to plot" in t.get_text()]
        self.assertEqual(len(stars), 1)
        self.assertEqual(len(notes), 0)


class TestNoScipyDependency(unittest.TestCase):
    def test_curve_module_does_not_import_scipy(self):
        curve_path = (Path(__file__).resolve().parent.parent
                     / "soilclass" / "curve.py")
        tree = ast.parse(curve_path.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertNotIn("scipy", imported)

    def test_requirements_do_not_mention_scipy(self):
        req_path = Path(__file__).resolve().parent.parent / "requirements.txt"
        self.assertNotIn("scipy", req_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
