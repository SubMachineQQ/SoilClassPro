import unittest

import matplotlib
matplotlib.use("Agg")

from soilclass.models import SoilSample
from soilclass.report.pdf_report import _summary_page
from soilclass.classifiers import classify_selected, ALL_CLASSIFIERS


def _texts(fig):
    return [t.get_text() for t in fig.texts]


class TestPdfMetadata(unittest.TestCase):
    def _sample(self, **overrides):
        defaults = dict(
            name="BH-1", sieve_data=[(4.75, 100), (0.075, 28)],
            liquid_limit=38, plastic_limit=19,
            project="", location="", operator="", date="",
        )
        defaults.update(overrides)
        return SoilSample(**defaults)

    def test_empty_project_becomes_untitled(self):
        sample = self._sample(project="")
        results = classify_selected(sample, ALL_CLASSIFIERS)
        fig = _summary_page(sample, results)
        texts = _texts(fig)
        self.assertIn("Untitled", texts)
        self.assertIn("Project:", texts)

    def test_named_project_is_shown_verbatim(self):
        sample = self._sample(project="Riverside Embankment")
        results = classify_selected(sample, ALL_CLASSIFIERS)
        fig = _summary_page(sample, results)
        texts = _texts(fig)
        self.assertIn("Riverside Embankment", texts)
        self.assertNotIn("Untitled", texts)

    def test_empty_optional_fields_are_omitted(self):
        sample = self._sample(location="", operator="", date="")
        results = classify_selected(sample, ALL_CLASSIFIERS)
        fig = _summary_page(sample, results)
        texts = _texts(fig)
        self.assertNotIn("Location:", texts)
        self.assertNotIn("Tested by:", texts)
        self.assertNotIn("Date:", texts)

    def test_filled_optional_fields_are_shown(self):
        sample = self._sample(location="Site A", operator="J. Doe",
                              date="2026-07-11")
        results = classify_selected(sample, ALL_CLASSIFIERS)
        fig = _summary_page(sample, results)
        texts = _texts(fig)
        self.assertIn("Location:", texts)
        self.assertIn("Site A", texts)
        self.assertIn("Tested by:", texts)
        self.assertIn("J. Doe", texts)
        self.assertIn("Date:", texts)
        self.assertIn("2026-07-11", texts)

    def test_sample_name_always_shown(self):
        sample = self._sample(name="BH-99")
        results = classify_selected(sample, ALL_CLASSIFIERS)
        fig = _summary_page(sample, results)
        texts = _texts(fig)
        self.assertIn("Sample:", texts)
        self.assertIn("BH-99", texts)


if __name__ == "__main__":
    unittest.main()
