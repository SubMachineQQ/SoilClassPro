import os
import tempfile
import unittest

import matplotlib
matplotlib.use("Agg")

from soilclass.example_data import example_sample
from soilclass.models import SoilSample
from soilclass.report import build_pdf
from soilclass.report.pdf_report import PAGE


def _page_count_and_sizes(path):
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(path)
    try:
        return len(pdf), [pdf[i].get_size() for i in range(len(pdf))]
    finally:
        pdf.close()


@unittest.skipUnless(
    __import__("importlib").util.find_spec("pypdfium2") is not None,
    "pypdfium2 not installed")
class TestPdfPageFiltering(unittest.TestCase):
    def _build(self, sample):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "report.pdf")
            build_pdf(sample, path)
            return _page_count_and_sizes(path)

    def test_every_chart_page_is_landscape(self):
        from soilclass.charts import classifiable_chart_defs
        from soilclass.report.pdf_report import ALL_FIGURES
        sample = example_sample()
        n, sizes = self._build(sample)
        portrait = (PAGE[0] * 72.0, PAGE[1] * 72.0)
        landscape = (PAGE[1] * 72.0, PAGE[0] * 72.0)

        def matches(size, want):
            return all(abs(g - w) <= 1.0 for g, w in zip(size, want))

        self.assertTrue(all(matches(sz, portrait) or matches(sz, landscape)
                            for sz in sizes))
        wide = [i for i, sz in enumerate(sizes) if matches(sz, landscape)]
        charts = len(classifiable_chart_defs(ALL_FIGURES, sample))
        self.assertEqual(len(wide), charts)
        self.assertEqual(wide, list(range(wide[0], wide[0] + charts)))
        self.assertTrue(matches(sizes[0], portrait))
        self.assertTrue(matches(sizes[-1], portrait))

    def test_non_plastic_sample_produces_fewer_pages(self):
        full_n, _ = self._build(example_sample())
        sparse_sample = SoilSample("Clean sand", [(4.75, 100), (0.075, 2)])
        sparse_n, _ = self._build(sparse_sample)
        self.assertLess(sparse_n, full_n)


if __name__ == "__main__":
    unittest.main()
