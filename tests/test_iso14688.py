import os
import tempfile
import unittest

from soilclass.classifiers import ALL_CLASSIFIERS, ISO14688Classifier
from soilclass.classifiers.iso14688 import (fine_kind, grading_letter,
                                            plasticity_class)
from soilclass.i18n import set_language, translate_domain_text
from soilclass.models import ISO14688_SIZES, SoilSample

Z4 = [(75, 100), (19, 100), (4.75, 98), (2.0, 90), (0.85, 70), (0.425, 60),
      (0.25, 50), (0.106, 30), (0.075, 25)]
S2 = [(4.75, 100), (2.0, 96), (0.425, 88), (0.075, 62), (0.02, 45),
      (0.002, 26)]


def make(sieve, ll=None, pl=None, organic=False):
    return SoilSample("T", sieve, ll, pl, organic)


def classify(s):
    return ISO14688Classifier().classify(s)


class TestRegistry(unittest.TestCase):
    def test_five_systems_aashto_back_ts1500_still_gone(self):
        names = [c.system_name for c in (cls() for cls in ALL_CLASSIFIERS)]
        self.assertEqual(len(names), 5)
        self.assertIn("TS EN ISO 14688", names)
        self.assertTrue(any("AASHTO" in n for n in names))
        self.assertFalse(any("1500" in n for n in names))


class TestWorkedExamples(unittest.TestCase):
    def test_z4_is_clayey_sand(self):
        r = classify(make(Z4, ll=25, pl=20))
        self.assertEqual(r.symbol, "clSa")
        self.assertEqual(r.name, "clayey SAND")

    def test_s2_is_sandy_medium_plasticity_clay(self):
        r = classify(make(S2, ll=45, pl=22))
        self.assertEqual(r.symbol, "saClM")
        self.assertEqual(r.name, "sandy medium plasticity CLAY")

    def test_missing_limits_gives_provisional_silty_result(self):
        r = classify(make(Z4))
        self.assertTrue(r.ok)
        self.assertEqual(r.symbol, "siSa")
        self.assertIn("provisional", r.name)
        self.assertIn("WARNING", r.notes[0])

    def test_fine_soil_without_limits_is_insufficient(self):
        r = classify(make([(2.0, 100), (0.063, 80)]))
        self.assertFalse(r.ok)


class TestPlasticityAndFineKind(unittest.TestCase):
    def test_plasticity_class_limits(self):
        for ll, letter in ((10, "L"), (34.9, "L"), (35, "M"), (49.9, "M"),
                           (50, "H"), (69.9, "H"), (70, "V"), (120, "V")):
            self.assertEqual(plasticity_class(ll)[0], letter, ll)

    def test_clay_silt_and_silty_clay(self):
        self.assertEqual(fine_kind(45, 23), "clay")
        self.assertEqual(fine_kind(45, 8), "silt")
        self.assertEqual(fine_kind(25, 3), "silt")
        self.assertEqual(fine_kind(25, 5), "silty clay")
        self.assertEqual(fine_kind(25, 7), "silty clay")
        self.assertEqual(fine_kind(25, 7.1), "clay")

    def test_fine_soil_symbols(self):
        cases = ((60, 30, "ClH"), (80, 50, "ClV"), (30, 3, "SiL"),
                 (55, 12, "SiH"), (25, 5, "ClL-SiL"))
        for ll, pi, sym in cases:
            r = classify(make([(2.0, 100), (0.063, 90)], ll=ll, pl=ll - pi))
            self.assertEqual(r.symbol, sym, (ll, pi))


class TestCoarseFineBoundary(unittest.TestCase):
    def test_exactly_50_percent_fines_is_fine(self):
        r = classify(make([(2.0, 100.0), (0.063, 50.0)], ll=40, pl=20))
        self.assertIn("Cl", r.symbol)
        self.assertTrue(r.symbol.endswith("ClM"))

    def test_just_under_50_percent_fines_is_coarse(self):
        r = classify(make([(2.0, 100.0), (0.063, 49.9)], ll=40, pl=20))
        self.assertTrue(r.symbol.endswith("Sa") or "Sa" in r.symbol)

    def test_uses_iso_sizes_not_astm(self):
        s = make([(4.75, 100), (2.0, 80), (0.075, 30), (0.063, 20)],
                 ll=30, pl=20)
        fr = s.fractions(ISO14688_SIZES)
        self.assertAlmostEqual(fr.fines, 20.0, places=1)
        self.assertAlmostEqual(fr.gravel, 20.0, places=1)


class TestGrading(unittest.TestCase):
    def test_letters(self):
        self.assertEqual(grading_letter(20, 2), "W")
        self.assertEqual(grading_letter(10, 0.5), "M")
        self.assertEqual(grading_letter(4, 0.8), "P")
        self.assertEqual(grading_letter(2, 0.9), "U")
        self.assertEqual(grading_letter(20, 0.3), "G")

    def test_uncovered_combination_is_poorly_graded(self):
        self.assertEqual(grading_letter(10, 2), "P")

    def test_unknown_cu_cc(self):
        self.assertIsNone(grading_letter(None, None))

    def test_well_graded_gravel_symbol(self):
        s = make([(63, 100), (19, 70), (9.5, 50), (2.0, 35), (0.85, 22),
                  (0.425, 14), (0.106, 9), (0.063, 2)])
        r = classify(s)
        self.assertRegex(r.symbol, r"^Gr[WMPUG]$")


class TestPrefixes(unittest.TestCase):
    def test_tertiary_coarse_fraction_prefix_not_applied(self):
        s = make([(63, 100), (2.0, 40), (0.063, 3)])
        self.assertRegex(classify(s).symbol, r"^Gr[WMPUG]$")

    def test_fines_between_5_and_15_keep_grading_letter(self):
        s = make([(4.75, 100), (2.0, 80), (0.85, 60), (0.425, 40),
                  (0.25, 30), (0.106, 18), (0.063, 10)], ll=30, pl=15)
        r = classify(s)
        self.assertRegex(r.symbol, r"^(si|cl)Sa[WMPUG]$")

    def test_fines_above_15_have_no_grading_letter(self):
        r = classify(make(Z4, ll=25, pl=20))
        self.assertFalse(r.symbol[-1] in "WMPUG")

    def test_organic_prefix(self):
        r = classify(make(S2, ll=45, pl=22, organic=True))
        self.assertEqual(r.symbol, "orsaClM")
        self.assertTrue(r.name.startswith("organic"))


class TestTurkishText(unittest.TestCase):
    def setUp(self):
        from pathlib import Path
        from soilclass import i18n
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._orig = (i18n.STORE_DIR, i18n.STORE_FILE,
                      i18n._current_language)
        i18n.STORE_DIR = Path(self._tmp.name) / ".soilclasspro"
        i18n.STORE_FILE = i18n.STORE_DIR / "settings.json"
        self.addCleanup(self._restore)
        set_language("tr")

    def _restore(self):
        from soilclass import i18n
        (i18n.STORE_DIR, i18n.STORE_FILE,
         i18n._current_language) = self._orig

    def test_notes_and_name_are_translated(self):
        r = classify(make(S2, ll=45, pl=22))
        name = translate_domain_text(r.name)
        self.assertIn("kumlu", name)
        self.assertIn("KİL", name)
        blob = " ".join(translate_domain_text(n) for n in r.notes)
        self.assertNotIn("Fines", blob)
        self.assertIn("İnce dane", blob)

    def test_uppercase_nouns_translated_for_bs_too(self):
        self.assertEqual(translate_domain_text("GRAVEL"), "ÇAKIL")


class TestLegacyProjectModes(unittest.TestCase):
    def _load(self, mode):
        from soilclass import project_file
        path = os.path.join(tempfile.mkdtemp(), "old.soilpro")
        project_file.save_project(path, make(S2, ll=45, pl=22), mode="ALL")
        import json
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        data["mode"] = mode
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        return project_file.load_project(path)

    def test_ts1500_project_opens_as_iso14688(self):
        self.assertEqual(self._load("TS1500")[1], "ISO14688")

    def test_aashto_project_opens_as_aashto(self):
        self.assertEqual(self._load("AASHTO")[1], "AASHTO")


if __name__ == "__main__":
    unittest.main()
