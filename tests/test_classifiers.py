import unittest

from soilclass.classifiers import (AASHTOClassifier, BS5930Classifier,
                                   RSCSClassifier, USCSClassifier)
from soilclass.example_data import example_sample
from soilclass.models import SoilSample


def make(sieve, ll=None, pl=None, organic=False):
    return SoilSample("T", sieve, ll, pl, organic)


class TestUSCS(unittest.TestCase):
    def sym(self, s):
        return USCSClassifier().classify(s).symbol

    def test_fat_clay(self):
        s = make([(4.75, 100), (0.075, 92), (0.005, 60)], ll=62, pl=24)
        self.assertEqual(self.sym(s), "CH")

    def test_lean_clay(self):
        s = make([(0.075, 85), (0.005, 40)], ll=35, pl=18)
        self.assertEqual(self.sym(s), "CL")

    def test_cl_ml(self):
        s = make([(2.0, 100), (0.075, 75)], ll=24, pl=18.5)
        self.assertEqual(self.sym(s), "CL-ML")

    def test_well_graded_gravel(self):
        s = make([(75, 100), (19, 70), (9.5, 50), (4.75, 35), (2, 22),
                  (0.85, 14), (0.425, 9), (0.075, 2)])
        self.assertEqual(self.sym(s), "GW")

    def test_dual_symbol(self):
        s = make([(19, 100), (4.75, 88), (2, 70), (0.85, 50), (0.425, 34),
                  (0.25, 24), (0.106, 12), (0.075, 8)], ll=22, pl=18)
        self.assertEqual(self.sym(s), "SW-SM")

    def test_clayey_sand(self):
        self.assertEqual(self.sym(example_sample()), "SC")

    def test_organic_high(self):
        s = make([(2.0, 100), (0.075, 90)], ll=70, pl=35, organic=True)
        self.assertEqual(self.sym(s), "OH")


class TestBS(unittest.TestCase):
    def sym(self, s):
        return BS5930Classifier().classify(s).symbol

    def test_high_plasticity_clay(self):
        s = make([(2.0, 100), (0.063, 92)], ll=62, pl=24)
        self.assertEqual(self.sym(s), "CH")

    def test_intermediate_silt(self):
        s = make([(2.0, 100), (0.063, 90)], ll=42, pl=32)
        self.assertEqual(self.sym(s), "MI")

    def test_extremely_high(self):
        s = make([(2.0, 100), (0.063, 95)], ll=105, pl=40)
        self.assertEqual(self.sym(s), "CE")


class TestAASHTO(unittest.TestCase):
    def res(self, s):
        return AASHTOClassifier().classify(s)

    def test_a3(self):
        s = make([(2, 99), (0.425, 85), (0.25, 40), (0.075, 3)])
        self.assertTrue(self.res(s).symbol.startswith("A-3"))

    def test_a76_group_index(self):
        s = make([(0.425, 98), (0.075, 92)], ll=62, pl=24)
        r = self.res(s)
        self.assertTrue(r.symbol.startswith("A-7-6"))
        self.assertEqual(r.extras["Group Index"], "20")

    def test_a2_gi_zero(self):
        s = make([(2, 60), (0.425, 40), (0.075, 20)], ll=30, pl=22)
        self.assertTrue(self.res(s).symbol.startswith("A-2-4 (0)"))


class TestRSCS(unittest.TestCase):
    def test_fines_control(self):
        s = make([(2.0, 100), (0.075, 92)], ll=62, pl=24)
        r = RSCSClassifier().classify(s)
        self.assertEqual(r.symbol, "F(F)")

    def test_clean_gravel(self):
        s = make([(75, 100), (19, 60), (4.75, 15), (2, 8), (0.075, 1)])
        r = RSCSClassifier().classify(s)
        self.assertEqual(r.symbol, "G(G)")

    def test_thresholds_ordering(self):
        th = RSCSClassifier().thresholds(40.0)
        self.assertLess(th.ff_flow, th.ff_low)
        self.assertLess(th.ff_low, th.ff_high)


if __name__ == "__main__":
    unittest.main()
