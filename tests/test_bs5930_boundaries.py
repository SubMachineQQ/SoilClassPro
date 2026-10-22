import unittest

from soilclass.classifiers import BS5930Classifier
from soilclass.models import SoilSample


def make(sieve, ll=None, pl=None, organic=False):
    return SoilSample("T", sieve, ll, pl, organic)


class TestBS5930CoarseFineBoundary(unittest.TestCase):
    def sym(self, s):
        return BS5930Classifier().classify(s).symbol

    def test_exactly_35_percent_fines_is_a_fine_soil(self):
        s = make([(2.0, 100.0), (0.063, 35.0)], ll=40, pl=20)
        result = BS5930Classifier().classify(s)
        self.assertTrue(result.ok)
        self.assertTrue(any(c in result.symbol for c in "LIHVE"))
        self.assertIn("35.0", " ".join(result.notes))

    def test_just_under_35_percent_fines_is_a_coarse_soil(self):
        s = make([(2.0, 100.0), (0.063, 34.9)], ll=40, pl=20)
        result = BS5930Classifier().classify(s)
        self.assertTrue(result.ok)
        self.assertTrue(result.symbol[0] in "GS")

    def test_exactly_5_percent_fines_is_slightly_silty_or_clayey(self):
        s = make([(2.0, 100.0), (0.063, 5.0)])
        result = BS5930Classifier().classify(s)
        self.assertIn("-", result.symbol)
        self.assertIn("Slightly", result.name)

    def test_just_under_5_percent_fines_is_clean(self):
        s = make([(2.0, 100.0), (0.063, 4.9)])
        result = BS5930Classifier().classify(s)
        self.assertNotIn("-", result.symbol)

    def test_exactly_15_percent_fines_is_still_slightly(self):
        s = make([(2.0, 100.0), (0.063, 15.0)])
        result = BS5930Classifier().classify(s)
        self.assertIn("-", result.symbol)
        self.assertIn("Slightly", result.name)

    def test_well_above_15_percent_fines_is_very(self):
        s = make([(2.0, 100.0), (0.063, 20.0)])
        result = BS5930Classifier().classify(s)
        self.assertNotIn("-", result.symbol)
        self.assertIn("Very", result.name)


class TestBS5930WellGradedThreshold(unittest.TestCase):
    def test_gravel_with_cu_4_is_well_graded(self):
        s = make([(10, 100), (4, 60), (2, 30), (1, 10), (0.063, 2)])
        result = BS5930Classifier().classify(s)
        self.assertAlmostEqual(s.cu, 4.0, places=2)
        self.assertEqual(result.symbol, "GW")

    def test_sand_with_cu_below_6_is_not_well_graded(self):
        s = make([(4.75, 100), (2.0, 95), (1.0, 75), (0.5, 45),
                  (0.25, 20), (0.125, 8), (0.063, 2)])
        self.assertLess(s.cu, 6.0)
        self.assertGreaterEqual(s.cu, 4.0)
        self.assertTrue(1.0 <= s.cc <= 3.0)
        result = BS5930Classifier().classify(s)
        self.assertEqual(result.symbol, "SP")

    def test_sand_with_cu_above_6_is_well_graded(self):
        s = make([(4.75, 100), (2.0, 90), (1.0, 74), (0.5, 52),
                  (0.25, 30), (0.125, 15), (0.075, 6), (0.063, 3)])
        self.assertGreaterEqual(s.cu, 6.0)
        self.assertTrue(1.0 <= s.cc <= 3.0)
        result = BS5930Classifier().classify(s)
        self.assertEqual(result.symbol, "SW")


class TestBS5930FinesNatureConsistency(unittest.TestCase):
    def test_non_plastic_fines_in_a_coarse_soil_are_never_clayey(self):
        s = make([(2.0, 100), (0.85, 60), (0.425, 30), (0.075, 10)],
                 ll=15, pl=15)
        letter, word = BS5930Classifier()._fines_nature(s, [])
        self.assertEqual(letter, "M")
        self.assertEqual(word, "silty")


if __name__ == "__main__":
    unittest.main()
