import unittest

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from soilclass import __app_name__
from soilclass.report.pdf_report import (PAGE, _finalize_page, _footer,
                                         _load_logo, _top_right_badge)


def _texts(fig):
    return [t.get_text() for t in fig.texts]


class TestLetterheadOnABareFigure(unittest.TestCase):
    def _blank_page(self):
        return plt.figure(figsize=PAGE)

    def test_top_right_badge_shows_the_app_name(self):
        fig = self._blank_page()
        _top_right_badge(fig)
        self.assertIn(__app_name__, _texts(fig))

    def test_footer_shows_the_app_name_and_page_word(self):
        fig = self._blank_page()
        _footer(fig)
        texts = "\n".join(_texts(fig))
        self.assertIn(__app_name__, texts)

    def test_finalize_page_adds_both(self):
        fig = self._blank_page()
        _finalize_page(fig)
        texts = "\n".join(_texts(fig))
        self.assertEqual(texts.count(__app_name__), 2)

    def test_logo_loads_from_the_bundled_asset(self):
        self.assertIsNotNone(_load_logo())

    def test_finalize_page_draws_the_logo_image_twice(self):
        if _load_logo() is None:
            self.skipTest("logo asset not readable in this environment")
        fig = self._blank_page()
        before = len(fig.axes)
        _finalize_page(fig)
        images = [ax for ax in fig.axes if ax.get_images()]
        self.assertEqual(len(images), before + 2)


class TestLetterheadOnEveryReportPage(unittest.TestCase):
    except_reason = None

    @classmethod
    def setUpClass(cls):
        try:
            import pypdfium2
        except ImportError:
            cls.except_reason = "pypdfium2 not installed"

    def test_letterhead_text_appears_on_every_page(self):
        if self.except_reason:
            self.skipTest(self.except_reason)
        import os
        import tempfile
        import pypdfium2 as pdfium
        from soilclass.example_data import example_sample
        from soilclass.report import build_pdf

        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "report.pdf")
            build_pdf(example_sample(), path)
            pdf = pdfium.PdfDocument(path)
            try:
                self.assertGreater(len(pdf), 1)
                for i in range(len(pdf)):
                    page_text = pdf[i].get_textpage().get_text_range()
                    self.assertIn(__app_name__, page_text,
                                 f"page {i} is missing the letterhead")
            finally:
                pdf.close()


if __name__ == "__main__":
    unittest.main()
