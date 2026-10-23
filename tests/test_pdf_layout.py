import importlib.util
import itertools
import os
import tempfile
import unittest

import matplotlib
matplotlib.use("Agg")

from soilclass import i18n
from soilclass.example_data import example_sample
from soilclass.models import SoilSample
from soilclass.report import build_pdf
from soilclass.report.pdf_report import FOOTER_H, HEADER_H


def _long_sample():
    sample = example_sample()
    sample.name = "BH-12 / 14,50-15,00 m / UD-3 (tekrar deneyi, ikinci numune)"
    sample.project = ("Çok Uzun Proje Adı - Ankara Çevre Yolu Viyadük "
                      "Temelleri ve Yaklaşım Dolguları (Revizyon 3)")
    sample.location = "Km 12+450 - 12+780 arası, SK-14 sondaj kuyusu"
    sample.operator = "ODTÜ İnşaat Mühendisliği Geoteknik Laboratuvarı"
    sample.ll_brine, sample.ll_kerosene = 35, 45
    return sample


def _cases():
    yield example_sample()
    yield _long_sample()
    yield SoilSample(name="Temiz kum", sieve_data=[(9.5, 100), (4.75, 97),
                     (2, 85), (0.425, 40), (0.075, 3)])
    yield SoilSample(name="CH kil", sieve_data=[(2, 100), (0.425, 99),
                     (0.075, 92), (0.005, 50), (0.001, 30)],
                     liquid_limit=78, plastic_limit=30)


def _spans(page, pymupdf):
    out = []
    for number, block in enumerate(page.get_text("rawdict")["blocks"]):
        for line in block.get("lines", []):
            rotated = abs(line["dir"][1]) > 0.05
            for span in line["spans"]:
                text = "".join(c["c"] for c in span["chars"])
                if not text.strip():
                    continue
                chars = [pymupdf.Rect(c["bbox"]) for c in span["chars"]
                         if c["c"].strip()]
                out.append((pymupdf.Rect(span["bbox"]), text, rotated, chars,
                            number, span["size"]))
    return out


def _overlap(a, b):
    r = a & b
    if r.is_empty:
        return 0.0
    return r.get_area() / max(1e-6, min(a.get_area(), b.get_area()))


@unittest.skipUnless(importlib.util.find_spec("pymupdf"), "pymupdf not installed")
class TestPdfLayout(unittest.TestCase):
    def setUp(self):
        self._lang = i18n._current_language

    def tearDown(self):
        i18n._current_language = self._lang

    def _problems(self, path):
        import pymupdf
        problems = []
        for number, page in enumerate(pymupdf.open(path), start=1):
            w, h = page.rect.width, page.rect.height
            items = _spans(page, pymupdf)
            for rect, text, *_ in items:
                if rect.x0 < 2 or rect.y0 < 2 or rect.x1 > w - 2 or rect.y1 > h - 2:
                    problems.append((number, "outside", text))
                header = rect.y1 <= HEADER_H + 1
                footer = rect.y0 >= h - FOOTER_H - 1
                if not header and not footer and (
                        rect.y0 < HEADER_H - 1 or rect.y1 > h - FOOTER_H + 5):
                    problems.append((number, "band", text))
            for a, b in itertools.combinations(items, 2):
                ra, ta, rota, ca, ba, sa = a
                rb, tb, rotb, cb, bb, sb = b
                if ba == bb:
                    continue
                if abs(sa - sb) > 0.5 and ta.strip("−-").isdigit() \
                        and tb.strip("−-").isdigit():
                    continue
                if rota or rotb:
                    hit = any(_overlap(x, y) > 0.15 for x in ca for y in cb)
                else:
                    hit = _overlap(ra, rb) > 0.08
                if hit:
                    problems.append((number, "overlap", f"{ta!r} / {tb!r}"))
        return problems

    def test_no_text_overlaps_or_leaves_the_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            for lang in ("tr", "en"):
                i18n._current_language = lang
                for index, sample in enumerate(_cases()):
                    path = os.path.join(tmp, f"{lang}_{index}.pdf")
                    build_pdf(sample, path)
                    self.assertEqual(self._problems(path), [],
                                     f"{lang} case {index}")


if __name__ == "__main__":
    unittest.main()
