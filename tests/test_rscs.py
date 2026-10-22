import math
import unittest

from soilclass.classifiers.rscs import (ALPHA_COARSE_FINES,
                                        ALPHA_GRAVEL_SAND, GROUP_POLYGONS,
                                        RSCSClassifier, emax_from_R_Cu,
                                        emin_from_R_Cu)
from soilclass.models import SoilSample

EKICI = dict(e_max_gravel=0.8353, e_min_gravel=0.4674,
             e_max_sand=0.4053, e_min_sand=0.1984)


def sample(pass4, pass200, ll=None, **kw):
    return SoilSample(name="T",
                      sieve_data=[(75.0, 100.0), (4.75, pass4),
                                  (0.075, pass200)],
                      liquid_limit=ll, **kw)


class TestPackingCorrelations(unittest.TestCase):
    def test_youd_cho_correlations(self):
        self.assertAlmostEqual(emax_from_R_Cu(0.3, 2.0), 0.80633, places=4)
        self.assertAlmostEqual(emin_from_R_Cu(0.3, 2.0), 0.44683, places=4)

    def test_emax_always_exceeds_emin(self):
        for R in (0.2, 0.35, 0.5, 0.9):
            for cu in (1.5, 3.0, 10.0):
                self.assertGreater(emax_from_R_Cu(R, cu),
                                   emin_from_R_Cu(R, cu))

    def test_measured_values_take_priority_over_R_and_Cu(self):
        s = sample(60, 10, ll=40, e_max_gravel=0.9, e_min_gravel=0.5,
                   roundness_gravel=0.3, cu_gravel=2.0,
                   e_max_sand=0.7, e_min_sand=0.4)
        pk = RSCSClassifier().packing(s)
        self.assertAlmostEqual(pk.e_max_gravel, 0.9)
        self.assertAlmostEqual(pk.e_min_gravel, 0.5)

    def test_R_and_Cu_used_when_void_ratios_absent(self):
        s = sample(60, 10, ll=40, roundness_sand=0.3, cu_sand=2.0)
        pk = RSCSClassifier().packing(s)
        self.assertAlmostEqual(pk.e_max_sand, emax_from_R_Cu(0.3, 2.0),
                               places=6)


class TestFinesVoidRatios(unittest.TestCase):
    def test_correlations(self):
        fv = RSCSClassifier().fines_void_ratios(40.0)
        self.assertAlmostEqual(fv.e_ll, 2.65 / 100 * 40.0, places=6)
        self.assertAlmostEqual(fv.e_10kpa, 0.026 * 40.0 + 0.07, places=6)
        self.assertAlmostEqual(fv.e_1mpa, 0.011 * 40.0 + 0.21, places=6)

    def test_lambda_is_clamped_at_one(self):
        for ll in (10.0, 20.0, 25.0, 26.0, 27.5, 28.0):
            self.assertAlmostEqual(
                RSCSClassifier().fines_void_ratios(ll).lam, 1.0, places=9,
                msg=f"lambda should be clamped to 1 at LL = {ll}")

    def test_lambda_follows_the_correlation_for_plastic_fines(self):
        for ll in (40.0, 60.0, 100.0):
            self.assertAlmostEqual(
                RSCSClassifier().fines_void_ratios(ll).lam,
                2.0 * math.log10(ll - 25.0), places=9)

    def test_flow_void_ratio_never_below_the_soft_mechanical_one(self):
        for ll in (15.0, 25.0, 30.0, 50.0, 90.0):
            fv = RSCSClassifier().fines_void_ratios(ll)
            self.assertGreaterEqual(fv.e_flow, fv.e_10kpa - 1e-12)


class TestNotableMixtures(unittest.TestCase):
    def setUp(self):
        self.clf = RSCSClassifier()
        self.pk = self.clf.packing(sample(60, 10, ll=44, **EKICI))
        self.fv = self.clf.fines_void_ratios(44.0)
        self.m = self.clf.notable_mixtures(self.pk, self.fv)

    def test_there_are_thirteen(self):
        self.assertEqual(sorted(self.m), list(range(1, 14)))

    def test_every_mixture_sums_to_100_percent(self):
        for i, (g, s, f) in self.m.items():
            self.assertAlmostEqual(g + s + f, 100.0, places=6,
                                   msg=f"mixture {i}")

    def test_alpha_factors(self):
        self.assertEqual(ALPHA_GRAVEL_SAND, 2.5)
        self.assertEqual(ALPHA_COARSE_FINES, 1.3)

    def test_binary_mixtures_have_a_zero_fraction(self):
        for i in (1, 7, 10):
            self.assertAlmostEqual(self.m[i][1], 0.0, places=9)
        for i in (4, 8, 13):
            self.assertAlmostEqual(self.m[i][0], 0.0, places=9)
        for i in (2, 5):
            self.assertAlmostEqual(self.m[i][2], 0.0, places=9)

    def test_flow_boundary_sits_below_the_mechanical_one(self):
        for flow, mech in ((10, 1), (11, 3), (12, 6), (13, 4)):
            self.assertLessEqual(self.m[flow][2], self.m[mech][2] + 1e-9,
                                 msg=f"mixture {flow} vs {mech}")

    def test_fines_carry_the_load_last(self):
        self.assertGreater(self.m[7][2], self.m[1][2])
        self.assertGreater(self.m[8][2], self.m[4][2])


class TestGroupsAndGeometry(unittest.TestCase):
    def test_ten_groups(self):
        self.assertEqual(len(GROUP_POLYGONS), 10)
        self.assertEqual(
            set(GROUP_POLYGONS),
            {"G(G)", "GS(S)", "S(S)", "G(F)", "GS(F)", "S(F)",
             "GF(F)", "GSF(F)", "SF(F)", "F(F)"})

    def test_every_group_is_reachable(self):
        clf = RSCSClassifier()
        found = set()
        for fines in range(0, 101, 2):
            for gravel in range(0, 101 - fines, 2):
                s = sample(100 - gravel, fines, ll=44, **EKICI)
                r = clf.classify(s)
                if r.ok:
                    found.add(r.symbol)
        self.assertEqual(found, set(GROUP_POLYGONS),
                         f"unreachable groups: {set(GROUP_POLYGONS) - found}")

    def test_non_plastic_fines_remove_three_groups(self):
        clf = RSCSClassifier()
        found = set()
        for fines in range(0, 101, 2):
            for gravel in range(0, 101 - fines, 2):
                s = sample(100 - gravel, fines, ll=20, **EKICI)
                r = clf.classify(s)
                if r.ok:
                    found.add(r.symbol)
        for gone in ("G(F)", "GS(F)", "S(F)"):
            self.assertNotIn(gone, found)
        self.assertIn("G(G)", found)
        self.assertIn("F(F)", found)


class TestClassification(unittest.TestCase):
    def sym(self, s):
        return RSCSClassifier().classify(s).symbol

    def test_clean_gravel(self):
        self.assertEqual(self.sym(sample(8, 1, **EKICI)), "G(G)")

    def test_clean_sand(self):
        self.assertEqual(self.sym(sample(100, 1, **EKICI)), "S(S)")

    def test_pure_fines(self):
        self.assertEqual(self.sym(sample(100, 95, ll=62, **EKICI)), "F(F)")

    def test_ekici_2022_s12_5(self):
        self.assertEqual(self.sym(sample(63.5, 12.0, ll=34.0, **EKICI)),
                         "GSF(F)")

    def test_no_sieve_data_is_reported_as_insufficient(self):
        r = RSCSClassifier().classify(SoilSample(name="x", sieve_data=[]))
        self.assertFalse(r.ok)

    def test_decision_trail_records_the_assumed_liquid_limit(self):
        r = RSCSClassifier().classify(sample(60, 10, **EKICI))
        self.assertTrue(any("not measured" in n for n in r.notes))

    def test_extras_expose_the_two_controlling_fractions(self):
        r = RSCSClassifier().classify(sample(63.5, 12.0, ll=34.0, **EKICI))
        self.assertEqual(r.extras["Mechanical control"], "GSF")
        self.assertEqual(r.extras["Fluid flow control"], "F")


class TestFinesClassification(unittest.TestCase):
    def test_twelve_groups_are_all_letters(self):
        fc = RSCSClassifier().fines_classification(60.0, 70.0, 55.0)
        self.assertIn(fc["plasticity"], "NLIH")
        self.assertIn(fc["sensitivity"], "LIH")

    def test_a_non_sensitive_clay_sits_at_the_origin(self):
        clf = RSCSClassifier()
        ll_brine = 40.0
        salt = 1.0 - 0.11688 * ll_brine / 100.0
        ll_dw = ll_brine / salt
        ll_ker = ll_brine * 0.78 / salt
        fc = clf.fines_classification(ll_dw, ll_brine, ll_ker)
        self.assertAlmostEqual(fc["SE"], 0.0, places=6)
        self.assertEqual(fc["sensitivity"], "L")

    def test_sensitivity_grows_with_the_liquid_limit_spread(self):
        clf = RSCSClassifier()
        low = clf.fines_classification(45.0, 40.0, 32.0)["SE"]
        high = clf.fines_classification(120.0, 40.0, 32.0)["SE"]
        self.assertGreater(high, low)

    def test_full_symbol_appends_the_fines_group(self):
        s = sample(100, 95, ll=62, ll_brine=70.0, ll_kerosene=55.0, **EKICI)
        r = RSCSClassifier().classify(s)
        self.assertTrue(r.symbol.startswith("F(F)-"))
        self.assertIn("Electrical sensitivity, SE", r.extras)

    def test_symbol_stays_short_without_the_extra_limits(self):
        s = sample(100, 95, ll=62, **EKICI)
        self.assertEqual(RSCSClassifier().classify(s).symbol, "F(F)")


class TestSimplifiedThresholds(unittest.TestCase):
    def test_ordering(self):
        th = RSCSClassifier().thresholds(40.0)
        self.assertLess(th.ff_flow, th.ff_low)
        self.assertLess(th.ff_low, th.ff_high)

    def test_thresholds_drop_as_the_fines_become_more_plastic(self):
        clf = RSCSClassifier()
        self.assertGreater(clf.thresholds(30.0).ff_high,
                           clf.thresholds(90.0).ff_high)

    def test_accepts_a_specific_coarse_packing(self):
        th = RSCSClassifier().thresholds(40.0, e_max=0.9, e_min=0.5)
        self.assertTrue(0.0 < th.ff_flow < th.ff_low < th.ff_high < 1.0)


if __name__ == "__main__":
    unittest.main()
