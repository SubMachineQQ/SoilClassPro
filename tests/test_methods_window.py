import os
import unittest

from soilclass import i18n
from soilclass.methods_text import method_sections

KINDS = {"h1", "h2", "p", "b", "f", "t"}


class TestMethodsText(unittest.TestCase):
    def test_both_languages_cover_the_same_systems(self):
        tr = method_sections("tr")
        en = method_sections("en")
        self.assertEqual(len(tr), len(en))
        self.assertEqual(len(tr), 7)
        for (tr_title, tr_blocks), (en_title, en_blocks) in zip(tr, en):
            self.assertEqual([k for k, _ in tr_blocks],
                             [k for k, _ in en_blocks], (tr_title, en_title))

    def test_every_section_is_well_formed(self):
        for lang in ("tr", "en"):
            for title, blocks in method_sections(lang):
                self.assertEqual(blocks[0][0], "h1", title)
                for kind, content in blocks:
                    self.assertIn(kind, KINDS)
                    if kind == "t":
                        self.assertTrue(all(isinstance(r, tuple) for r in content))
                    else:
                        self.assertTrue(str(content).strip())

    def test_key_values_match_the_classifiers(self):
        from soilclass.classifiers import rscs
        text = "\n".join(str(c) for _, blocks in method_sections("en")
                         for _, c in blocks)
        self.assertIn(f"R = {rscs.DEFAULT_R}", text)
        self.assertIn(f"Cu = {rscs.DEFAULT_CU}", text)
        self.assertIn(f"LL = {rscs.DEFAULT_LL:g}", text)
        self.assertIn(f"{rscs.C_BRINE}", text)
        self.assertIn(f"{rscs.G_KER}", text)
        self.assertIn(f"Gs = {rscs.GS}", text)
        self.assertIn(f"α(gravel–sand) = {rscs.ALPHA_GRAVEL_SAND}", text)
        self.assertIn(f"α(coarse–fines) = {rscs.ALPHA_COARSE_FINES}", text)
        e_max = rscs.emax_from_R_Cu(rscs.DEFAULT_R, rscs.DEFAULT_CU)
        e_min = rscs.emin_from_R_Cu(rscs.DEFAULT_R, rscs.DEFAULT_CU)
        self.assertIn(f"e_max = {e_max:.3f}", text)
        self.assertIn(f"e_min = {e_min:.3f}", text)

    def test_menu_label_is_translated(self):
        self.assertIn("methods_menu", i18n._EN)
        self.assertIn("methods_menu", i18n._TR)


@unittest.skipUnless(os.environ.get("DISPLAY"), "no DISPLAY available for a GUI test")
class TestMethodsWindow(unittest.TestCase):
    def test_window_has_one_tab_per_section_and_reuses_itself(self):
        from soilclass.gui.app import SoilClassApp
        app = SoilClassApp("ALL")
        self.addCleanup(app.destroy)
        app.update()
        app.show_methods()
        first = app._methods_window
        app.update()
        self.assertEqual(len(first.nb.tabs()), len(method_sections()))
        self.assertTrue(all(str(t.cget("state")) == "disabled"
                            for t in first.texts))
        app.show_methods()
        self.assertIs(app._methods_window, first)


if __name__ == "__main__":
    unittest.main()
