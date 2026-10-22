import itertools
import math
import re
import unittest

from soilclass import i18n
from soilclass.classifiers import ALL_CLASSIFIERS, classify_selected
from soilclass.models import SoilSample

ENGLISH = re.compile(
    r"\b(the|of|and|is|are|by|only|not|with|than|void|ratios?|flow|parameter|"
    r"packing|fractions?|sieves?|applied|sample|data|assumed|fines|sand|"
    r"gravel|coarse|graded|organic|plastic|plasticity|above|below|between|"
    r"prefix|symbol|reflected|but|measured|lambda|controls?|mechanical|fluid|"
    r"boundary|transitional|carry|carries|load|range|qualifier|corrected|"
    r"elastic|sensitivity|electrical|clay|clayey|silty|sandy|gravelly|"
    r"British|Standard)\b", re.IGNORECASE)

SIZES = [75, 37.5, 19, 9.5, 4.75, 2, 0.85, 0.425, 0.25, 0.106, 0.075, 0.02,
         0.005, 0.001]


def _curve(gravel, fines):
    sand = 100 - gravel - fines
    log = math.log10
    points = []
    for d in SIZES:
        if d >= 75:
            p = 100.0
        elif d > 4.75:
            p = max(100 - gravel, 100 - gravel * ((75 - d) / 70.25) ** 0.5)
        elif d >= 0.075:
            p = fines + sand * (log(d) - log(0.075)) / (log(4.75) - log(0.075))
        else:
            p = fines * (d / 0.075) ** 0.35
        points.append([d, round(min(100.0, max(0.0, p)), 2)])
    for i in range(1, len(points)):
        points[i][1] = min(points[i][1], points[i - 1][1])
    return [tuple(p) for p in points]


class TestTurkishDecisionTrail(unittest.TestCase):
    def setUp(self):
        self._saved = i18n._current_language
        i18n._current_language = "tr"

    def tearDown(self):
        i18n._current_language = self._saved

    def _texts(self):
        limits = ((None, None), (25, 20), (38, 19), (45, 40), (60, 25),
                  (80, 45))
        for g, f, (ll, pl), organic, rscs in itertools.product(
                (0, 30, 60), (5, 15, 30, 55, 90), limits, (False, True),
                (False, True)):
            sample = SoilSample(name="X", sieve_data=_curve(g, f),
                                liquid_limit=ll, plastic_limit=pl,
                                organic=organic)
            if rscs:
                sample.e_max_gravel, sample.e_min_gravel = 0.7, 0.4
                sample.e_max_sand, sample.e_min_sand = 0.9, 0.5
                sample.ll_brine, sample.ll_kerosene = 35, 45
            for result in classify_selected(sample, ALL_CLASSIFIERS):
                yield result.system
                yield result.name
                yield from result.notes
                for key, value in result.extras.items():
                    yield f"{key}: {value}"

    def test_no_english_words_in_turkish_results(self):
        leftovers = sorted({text for text in self._texts()
                            if ENGLISH.search(text)})
        self.assertEqual(leftovers, [])

    def test_known_sentences(self):
        tr = i18n.translate_domain_text
        self.assertEqual(
            tr("Sand carries the load; fines control fluid flow; fines are of "
               "low plasticity with intermediate electrical sensitivity"),
            "Kum yükü taşır; akışkan akışını ince dane kontrol eder; ince "
            "daneler düşük plastisiteli ve orta elektriksel duyarlılıklı")
        self.assertEqual(tr("Sandy clay of low plasticity"),
                         "Kumlu, düşük plastisiteli kil")
        self.assertEqual(tr("British Standard (BS 5930)"),
                         "İngiliz Standardı (BS 5930)")

    def test_turkish_upper_case(self):
        self.assertEqual(i18n.upper("Fraksiyonlar"), "FRAKSİYONLAR")
        self.assertEqual(i18n.upper("kayıtlı nokta"), "KAYITLI NOKTA")


if __name__ == "__main__":
    unittest.main()
