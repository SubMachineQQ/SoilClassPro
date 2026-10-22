from __future__ import annotations

import datetime
import textwrap
from typing import List, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D

from .. import __app_name__
from ..assets_path import LOGO_PNG
from ..charts import ALL_FIGURES, classifiable_chart_defs, gsd_figure
from ..colors import PDF_REPORT as C
from ..classifiers import (AASHTOClassifier, ALL_CLASSIFIERS,
                           BS5930Classifier, ClassificationResult,
                           ISO14688Classifier, RSCSClassifier,
                           USCSClassifier, classify_selected)
from ..i18n import t
from ..models import SoilSample, conventions_for_systems

PAGE = (8.27, 11.69)
PAGE_LANDSCAPE = (PAGE[1], PAGE[0])

_SYSTEM_LABEL = {
    USCSClassifier: "USCS (ASTM D2487)",
    BS5930Classifier: "BS 5930",
    ISO14688Classifier: "TS EN ISO 14688",
    RSCSClassifier: "RSCS",
    AASHTOClassifier: "AASHTO (M 145)",
}
_SYSTEM_BOUNDARIES = {
    USCSClassifier: "USCS", BS5930Classifier: "BS",
    ISO14688Classifier: "ISO14688", RSCSClassifier: "RSCS",
    AASHTOClassifier: "USCS",
}


def _subtitle(classifiers) -> str:
    return "  \u00b7  ".join(_SYSTEM_LABEL.get(c, c.system_name)
                           for c in classifiers)


def _boundaries_for(classifiers) -> str:
    if len(classifiers) == 1:
        return _SYSTEM_BOUNDARIES.get(classifiers[0], "USCS")
    return "USCS"

MARGIN_LEFT = 0.08
MARGIN_RIGHT = 0.92
MARGIN_TOP = 0.955
MARGIN_BOTTOM = 0.08
CONTENT_TOP = 0.90

_LOGO_TOP_WIDTH = 0.034
_LOGO_TOP_RIGHT = MARGIN_RIGHT
_LOGO_TOP_TOP = 0.997
_LOGO_BOTTOM_WIDTH = 0.020
_LOGO_BOTTOM_LEFT = MARGIN_LEFT
_LOGO_BOTTOM_BOTTOM = 0.020


_LOGO_IMG = None


def _load_logo():
    global _LOGO_IMG
    if _LOGO_IMG is None:
        try:
            _LOGO_IMG = plt.imread(str(LOGO_PNG))
        except (OSError, ValueError):
            _LOGO_IMG = False
    return _LOGO_IMG if _LOGO_IMG is not False else None


def _logo_axes(fig, *, x: float, y: float, width_frac: float, anchor: str,
               page=PAGE):
    width_frac = width_frac * PAGE[0] / page[0]
    height_frac = width_frac * page[0] / page[1]
    if anchor == "top-right":
        left, bottom = x - width_frac, y - height_frac
    else:
        left, bottom = x, y
    ax = fig.add_axes((left, bottom, width_frac, height_frac))
    ax.axis("off")
    return ax, (left, bottom, left + width_frac, bottom + height_frac)


def _top_right_badge(fig, page=PAGE) -> None:
    logo = _load_logo()
    name_x = _LOGO_TOP_RIGHT
    if logo is not None:
        ax, (logo_left, _, _, _) = _logo_axes(
            fig, x=_LOGO_TOP_RIGHT, y=_LOGO_TOP_TOP,
            width_frac=_LOGO_TOP_WIDTH, anchor="top-right", page=page)
        ax.imshow(logo)
        name_x = logo_left - 0.008
    fig.text(name_x, _LOGO_TOP_TOP - _LOGO_TOP_WIDTH * PAGE[0] / page[1] / 2,
             __app_name__, fontsize=9.5, fontweight="bold",
             color=C["heading"], ha="right", va="center")


def _footer(fig, page=PAGE, number=None, total=None) -> None:
    logo = _load_logo()
    text_x = _LOGO_BOTTOM_LEFT
    if logo is not None:
        ax, (_, _, logo_right, _) = _logo_axes(
            fig, x=_LOGO_BOTTOM_LEFT, y=_LOGO_BOTTOM_BOTTOM,
            width_frac=_LOGO_BOTTOM_WIDTH, anchor="bottom-left", page=page)
        ax.imshow(logo)
        text_x = logo_right + 0.006
    fig.text(text_x, 0.03,
             f"{t('pdf_generated')} "
             f"{datetime.datetime.now():%Y-%m-%d %H:%M}",
             fontsize=7.5, color=C["footer_text"])
    label = t("pdf_page")
    if number is not None:
        label = f"{label} {number}" + (f" / {total}" if total else "")
    fig.text(MARGIN_RIGHT, 0.03, label, fontsize=7.5, color=C["footer_text"],
             ha="right")
    fig.text(text_x, 0.015, t("pdf_disclaimer"), fontsize=6.5,
             color=C["footer_text"], style="italic")


def _finalize_page(fig, page=PAGE, number=None, total=None) -> None:
    _top_right_badge(fig, page=page)
    _footer(fig, page=page, number=number, total=total)


def _chars_per_line(x0: float, x1: float, fontsize: float,
                    monospace: bool = False, page_width_in: float = PAGE[0]) -> int:
    width_in = max(0.5, (x1 - x0) * page_width_in)
    avg_char_in = fontsize * (0.62 if monospace else 0.52) / 72.0
    return max(15, int(width_in / avg_char_in))


def _wrap(text: str, max_chars: int) -> List[str]:
    if not text:
        return [""]
    return textwrap.wrap(text, width=max_chars,
                         break_long_words=True, break_on_hyphens=False) or [""]


def _line_height(fontsize: float, leading: float = 1.35,
                 page_height_in: float = PAGE[1]) -> float:
    return fontsize * leading / 72.0 / page_height_in


def _new_page(title: str) -> plt.Figure:
    fig = plt.figure(figsize=PAGE)
    fig.text(MARGIN_LEFT, MARGIN_TOP, title, fontsize=15, fontweight="bold",
             color=C["heading"])
    fig.lines.append(Line2D([MARGIN_LEFT, MARGIN_RIGHT], [MARGIN_TOP - 0.01] * 2,
                            transform=fig.transFigure, color=C["heading"], lw=1.4))
    return fig


def _flow_pages(title: str, paragraphs: Sequence[str], *, fontsize: float = 9.2,
                monospace: bool = True) -> List[plt.Figure]:
    chars = _chars_per_line(MARGIN_LEFT, MARGIN_RIGHT, fontsize, monospace)
    line_h = _line_height(fontsize)
    pages: List[plt.Figure] = []
    fig = _new_page(title)
    y = CONTENT_TOP
    first_page = True

    def _next_page():
        nonlocal fig, y, first_page
        pages.append(fig)
        fig = _new_page(f"{title} {t('pdf_continued_suffix')}")
        y = CONTENT_TOP
        first_page = False

    for para in paragraphs:
        for raw_line in str(para).split("\n"):
            for wline in _wrap(raw_line, chars):
                if y - line_h < MARGIN_BOTTOM:
                    _next_page()
                fig.text(MARGIN_LEFT, y, wline, fontsize=fontsize,
                        family="monospace" if monospace else None, va="top")
                y -= line_h
        y -= line_h * 0.5
    pages.append(fig)
    return pages


def _summary_page(sample: SoilSample,
                  results: List[ClassificationResult],
                  subtitle: str = None,
                  include_sieve: bool = False) -> plt.Figure:
    fig = plt.figure(figsize=PAGE)

    fig.text(0.5, MARGIN_TOP, t("pdf_title"), ha="center",
             fontsize=19, fontweight="bold", color=C["heading"])
    fig.text(0.5, 0.928,
             subtitle or _subtitle(ALL_CLASSIFIERS),
             ha="center", fontsize=9.5, color=C["subheading"])
    fig.lines.append(Line2D([MARGIN_LEFT, MARGIN_RIGHT], [0.915, 0.915],
                            transform=fig.transFigure, color=C["heading"], lw=1.6))

    meta = [(t("pdf_sample"), sample.name),
            (t("pdf_project"), sample.project.strip() if sample.project
                       and sample.project.strip() else t("pdf_untitled"))]
    for label, value in ((t("pdf_location"), sample.location),
                        (t("pdf_tested_by"), sample.operator),
                        (t("pdf_date"), sample.date)):
        if value and value.strip():
            meta.append((label, value.strip()))

    value_x = 0.24
    fontsize_meta = 9.5
    line_h = _line_height(fontsize_meta)
    chars = _chars_per_line(value_x, MARGIN_RIGHT, fontsize_meta)
    y = 0.885
    for k, v in meta:
        fig.text(MARGIN_LEFT, y, f"{k}:", fontsize=fontsize_meta, fontweight="bold")
        wrapped = _wrap(str(v), chars)
        for i, wline in enumerate(wrapped):
            fig.text(value_x, y, wline, fontsize=fontsize_meta)
            if i < len(wrapped) - 1:
                y -= line_h
        y -= line_h

    y -= 0.012
    fig.text(MARGIN_LEFT, y, t("pdf_classification_summary"), fontsize=12,
             fontweight="bold", color=C["body_text"])
    y -= 0.03
    fontsize_table = 9
    col_fracs = [0.30, 0.16, 0.54]
    total_chars = _chars_per_line(MARGIN_LEFT, MARGIN_RIGHT, fontsize_table) * 0.8
    sys_chars = max(10, int(total_chars * col_fracs[0]))
    name_chars = max(10, int(total_chars * col_fracs[2]))

    wrapped_rows, row_lines = [], []
    for r in results:
        sys_w = _wrap(r.system, sys_chars)
        name_w = _wrap(r.name, name_chars)
        wrapped_rows.append(["\n".join(sys_w), r.symbol, "\n".join(name_w)])
        row_lines.append(max(len(sys_w), len(name_w), 1))

    header_h_abs, line_h_abs = 0.045, 0.024
    row_h_abs = [line_h_abs * n for n in row_lines] or [line_h_abs]
    table_h = header_h_abs + sum(row_h_abs)
    table_top = y
    ax = fig.add_axes([MARGIN_LEFT, table_top - table_h, MARGIN_RIGHT - MARGIN_LEFT,
                       table_h])
    ax.axis("off")
    table = ax.table(cellText=wrapped_rows,
                     colLabels=[t("pdf_col_system"), t("pdf_col_group_symbol"),
                               t("pdf_col_group_name")],
                     colWidths=col_fracs,
                     cellLoc="left", loc="upper center")
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize_table)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor(C["table_border"])
        cell.set_height((header_h_abs if r == 0 else row_h_abs[r - 1]) / table_h)
        cell.PAD = 0.02
        if r == 0:
            cell.set_facecolor(C["table_header_bg"])
            cell.set_text_props(color=C["table_header_fg"], fontweight="bold")
        else:
            if r % 2 == 0:
                cell.set_facecolor(C["table_row_alt"])
            cell.set_text_props(va="center")
        if c == 1 and r > 0:
            cell.set_text_props(fontweight="bold", color=C["symbol_fg"])
    y = table_top - table_h - 0.025

    fig.text(MARGIN_LEFT, y, t("pdf_index_properties"), fontsize=12, fontweight="bold")
    y -= 0.032
    fontsize_idx = 8.8
    line_h_idx = _line_height(fontsize_idx)
    value_x2 = 0.55
    chars2 = _chars_per_line(value_x2, MARGIN_RIGHT, fontsize_idx)
    for k, v in sample.summary_rows(conventions_for_systems(
            [r.system for r in results])):
        fig.text(0.10, y, k, fontsize=fontsize_idx)
        wrapped = _wrap(str(v), chars2)
        for i, wline in enumerate(wrapped):
            fig.text(value_x2, y, wline, fontsize=fontsize_idx, fontweight="bold")
            if i < len(wrapped) - 1:
                y -= line_h_idx
        y -= line_h_idx
        if y < MARGIN_BOTTOM:
            fig.text(0.10, MARGIN_BOTTOM, "  ...", fontsize=fontsize_idx)
            break

    fig.sieve_included = False
    if include_sieve and sample.sieve_data:
        y -= 0.012
        rows_txt = _sieve_lines(sample)
        needed = 0.032 + line_h_idx * len(rows_txt)
        if y - needed > MARGIN_BOTTOM + 0.03:
            fig.text(MARGIN_LEFT, y, t("pdf_sieve_analysis"), fontsize=12,
                     fontweight="bold")
            y -= 0.032
            for line in rows_txt:
                fig.text(0.10, y, line, fontsize=fontsize_idx,
                         family="monospace")
                y -= line_h_idx
            fig.sieve_included = True

    return fig


def _sieve_lines(sample: SoilSample) -> List[str]:
    header = f"{t('pdf_size_mm'):>12} {t('pdf_passing_pct'):>14}"
    return [header] + [f"{d:12.3f} {p:14.1f}"
                       for d, p in reversed(sample.sieve_data)]


def _sieve_pages(sample: SoilSample) -> List[plt.Figure]:
    text = "\n".join(_sieve_lines(sample))
    return _flow_pages(t("pdf_sieve_analysis"), [text], fontsize=9.0, monospace=True)


def build_pdf(sample: SoilSample, path: str, classifiers=None,
             figures=None) -> str:
    classifiers = classifiers or ALL_CLASSIFIERS
    figures = figures if figures is not None else ALL_FIGURES
    results = [r for r in classify_selected(sample, classifiers) if r.ok]
    figures = classifiable_chart_defs(figures, sample)
    bset = _boundaries_for(classifiers)

    pages: List[Tuple[plt.Figure, Tuple[float, float]]] = []
    summary = _summary_page(sample, results, subtitle=_subtitle(classifiers),
                            include_sieve=True)
    pages.append((summary, PAGE))
    if sample.sieve_data and not summary.sieve_included:
        pages.extend((f, PAGE) for f in _sieve_pages(sample))

    for title, builder in figures:
        if builder is gsd_figure:
            fig = builder(sample, figsize=PAGE_LANDSCAPE, boundaries=bset)
        else:
            fig = builder(sample, figsize=PAGE_LANDSCAPE)
        fig.subplots_adjust(top=0.87, bottom=0.12)
        pages.append((fig, PAGE_LANDSCAPE))

    paragraphs = [r.as_text() for r in results]
    pages.extend((f, PAGE) for f in
                 _flow_pages(t("pdf_decision_trails_title"), paragraphs,
                             fontsize=9.2, monospace=True))

    with PdfPages(path) as pdf:
        for n, (fig, page) in enumerate(pages, start=1):
            _finalize_page(fig, page=page, number=n, total=len(pages))
            pdf.savefig(fig)
            plt.close(fig)

        meta = pdf.infodict()
        meta["Title"] = f"{t('pdf_title')} - {sample.name}"
        meta["Author"] = sample.operator or "SoilClass Pro"
        meta["Subject"] = _subtitle(classifiers).replace("  \u00b7  ", " / ")
        meta["Creator"] = "SoilClass Pro"
    return path
