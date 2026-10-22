import unittest

from soilclass.charts import ALL_FIGURES, classifiable_chart_defs
from soilclass.example_data import example_sample
from soilclass.models import SoilSample


def _labels(chart_defs):
    return [label for label, _ in chart_defs]


class TestClassifiableChartDefs(unittest.TestCase):
    def test_plastic_sample_keeps_plasticity_and_aashto_charts(self):
        labels = _labels(classifiable_chart_defs(ALL_FIGURES, example_sample()))
        for expected in ("Plasticity Chart (ASTM)", "Plasticity Chart (BS 5930)",
                         "Plasticity Chart (TS EN ISO 14688)", "AASHTO LL-PI Chart"):
            self.assertIn(expected, labels)

    def test_non_plastic_sample_drops_plasticity_and_aashto_charts(self):
        sample = SoilSample("Clean sand", [(4.75, 100), (0.075, 2)])
        labels = _labels(classifiable_chart_defs(ALL_FIGURES, sample))
        for dropped in ("Plasticity Chart (ASTM)", "Plasticity Chart (BS 5930)",
                        "Plasticity Chart (TS EN ISO 14688)", "AASHTO LL-PI Chart"):
            self.assertNotIn(dropped, labels)
        self.assertIn("Grain Size Distribution", labels)
        self.assertIn("RSCS Ternary Chart", labels)

    def test_sample_without_extra_lls_drops_rscs_fines_charts(self):
        labels = _labels(classifiable_chart_defs(ALL_FIGURES, example_sample()))
        self.assertNotIn("RSCS Fines - LL Ratio Plane", labels)
        self.assertNotIn("RSCS Fines - Plasticity vs Sensitivity", labels)

    def test_sample_with_extra_lls_keeps_rscs_fines_charts(self):
        sample = example_sample()
        sample.ll_brine = 68.0
        sample.ll_kerosene = 30.0
        labels = _labels(classifiable_chart_defs(ALL_FIGURES, sample))
        self.assertIn("RSCS Fines - LL Ratio Plane", labels)
        self.assertIn("RSCS Fines - Plasticity vs Sensitivity", labels)


if __name__ == "__main__":
    unittest.main()
