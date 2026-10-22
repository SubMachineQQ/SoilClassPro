import unittest

from soilclass.gui.modes import (MODE_CHARTS, MODE_CLASSIFIERS, MODE_TITLE,
                                 VALID_MODES)
from soilclass.i18n import t
from soilclass.standard_info import STANDARD_INFO

SINGLE_MODES = ("ASTM", "BS", "ISO14688", "AASHTO", "RSCS")


class TestModes(unittest.TestCase):
    def test_all_modes_have_title_classifiers_and_charts(self):
        for mode in VALID_MODES:
            self.assertIn(mode, MODE_TITLE)
            self.assertIn(mode, MODE_CLASSIFIERS)
            self.assertIn(mode, MODE_CHARTS)

    def test_single_standard_modes_have_exactly_one_classifier(self):
        for mode in SINGLE_MODES:
            self.assertEqual(len(MODE_CLASSIFIERS[mode]), 1)

    def test_all_mode_has_all_five_classifiers(self):
        self.assertEqual(len(MODE_CLASSIFIERS["ALL"]), 5)

    def test_every_single_standard_mode_starts_with_grain_size(self):
        for mode in SINGLE_MODES:
            labels = [label for label, _ in MODE_CHARTS[mode]]
            self.assertIn(t("chart_tab_grain_size"), labels)
            self.assertGreaterEqual(len(labels), 2)

    def test_astm_bs_iso14688_aashto_have_exactly_two_charts(self):
        for mode in ("ASTM", "BS", "ISO14688", "AASHTO"):
            self.assertEqual(len(MODE_CHARTS[mode]), 2)

    def test_rscs_mode_has_ternary_plus_both_fines_charts(self):
        labels = [label for label, _ in MODE_CHARTS["RSCS"]]
        self.assertEqual(len(labels), 4)
        self.assertIn(t("chart_tab_rscs_ternary"), labels)
        self.assertIn(t("chart_tab_rscs_fines_a"), labels)
        self.assertIn(t("chart_tab_rscs_fines_b"), labels)

    def test_all_mode_has_eight_charts(self):
        self.assertEqual(len(MODE_CHARTS["ALL"]), 8)
        labels = [label for label, _ in MODE_CHARTS["ALL"]]
        self.assertIn(t("chart_tab_aashto"), labels)
        self.assertIn(t("chart_tab_rscs_fines_a"), labels)
        self.assertIn(t("chart_tab_rscs_fines_b"), labels)


class TestStandardInfo(unittest.TestCase):
    def test_every_single_standard_has_a_card(self):
        for mode in SINGLE_MODES:
            self.assertIn(mode, STANDARD_INFO)

    def test_cards_have_required_fields(self):
        for key, info in STANDARD_INFO.items():
            for field in ("label", "standard", "tests", "inputs"):
                self.assertIn(field, info, f"{key} missing '{field}'")
            self.assertGreater(len(info["tests"]), 0)
            self.assertGreater(len(info["inputs"]), 0)

    def test_removed_standards_have_no_card(self):
        self.assertNotIn("TS1500", STANDARD_INFO)

    def test_iso14688_card_cites_kovacevic_and_rscs_card_cites_cho(self):
        self.assertIn("Kova", STANDARD_INFO["ISO14688"]["standard"])
        self.assertIn("2018", STANDARD_INFO["ISO14688"]["standard"])
        self.assertIn("Cho, Dodds", STANDARD_INFO["RSCS"]["standard"])
        self.assertIn("2006", STANDARD_INFO["RSCS"]["standard"])


if __name__ == "__main__":
    unittest.main()
