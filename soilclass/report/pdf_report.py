from __future__ import annotations

import datetime
from functools import lru_cache
from typing import List, Optional, Sequence, Tuple

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.transforms import Affine2D

from ..fonts import UI_FONT
from .. import __app_name__, __version__
from ..assets_path import LOGO_PNG
from ..charts import ALL_FIGURES, classifiable_chart_defs, gsd_figure
from ..charts.declutter import declutter
from ..colors import PDF_REPORT as C
from ..classifiers import (AASHTOClassifier, ALL_CLASSIFIERS,
                           BS5930Classifier, ClassificationResult,
                           ISO14688Classifier, RSCSClassifier,
                           USCSClassifier, classify_selected)
from ..i18n import capitalize, t, upper
from ..models import (ASTM_SIZES, BS_SIZES, SoilSample,
                      conventions_for_systems)

PAGE = (8.27, 11.69)
PAGE_LANDSCAPE = (PAGE[1], PAGE[0])

MARGIN = 46.0
HEADER_H = 40.0
FOOTER_H = 44.0
GAP = 14.0

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

matplotlib.rcParams["pdf.fonttype"] = 42


def _family(preferred: str, fallback: str) -> str:
    try:
        font_manager.findfont(FontProperties(family=preferred),
                              fallback_to_default=False)
        return preferred
    except ValueError:
        return fallback


SANS = _family(UI_FONT, "DejaVu Sans")


def _subtitle(classifiers) -> str:
    return "  ·  ".join(_SYSTEM_LABEL.get(c, c.system_name)
                           for c in classifiers)


def _boundaries_for(classifiers) -> str:
    if len(classifiers) == 1:
        return _SYSTEM_BOUNDARIES.get(classifiers[0], "USCS")
    return "USCS"


_LOGO_IMG = None


def _load_logo():
    global _LOGO_IMG
    if _LOGO_IMG is None:
        try:
            _LOGO_IMG = plt.imread(str(LOGO_PNG))
        except (OSError, ValueError):
            _LOGO_IMG = False
    return _LOGO_IMG if _LOGO_IMG is not False else None


_RENDERER = RendererAgg(10, 10, 72)


@lru_cache(maxsize=4096)
def _measure(text: str, size: float, weight: str, family: str) -> float:
    if not text:
        return 0.0
    prop = FontProperties(family=family, size=size, weight=weight)
    width, _, _ = _RENDERER.get_text_width_height_descent(text, prop,
                                                          ismath=False)
    return width


def _split_long(word: str, width: float, size, weight, family) -> List[str]:
    parts, current = [], ""
    for ch in word:
        if current and _measure(current + ch, size, weight, family) > width:
            parts.append(current)
            current = ch
        else:
            current += ch
    if current:
        parts.append(current)
    return parts


def _wrap(text: str, width: float, size: float, weight: str = "normal",
          family: str = None) -> List[str]:
    family = family or SANS
    lines: List[str] = []
    for paragraph in str(text).split("\n"):
        words = paragraph.split(" ")
        current = ""
        for word in words:
            if not word:
                continue
            trial = f"{current} {word}" if current else word
            if _measure(trial, size, weight, family) <= width:
                current = trial
                continue
            if current:
                lines.append(current)
            if _measure(word, size, weight, family) > width:
                pieces = _split_long(word, width, size, weight, family)
                lines.extend(pieces[:-1])
                current = pieces[-1]
            else:
                current = word
        lines.append(current)
    return lines or [""]


def _ellipsize(text: str, width: float, size: float,
               weight: str = "normal") -> str:
    if _measure(text, size, weight, SANS) <= width:
        return text
    while text and _measure(text + "\u2026", size, weight, SANS) > width:
        text = text[:-1]
    return text.rstrip(" \u00b7/-,") + "\u2026"


def _line_h(size: float) -> float:
    return size * 1.38


class _Canvas:
    def __init__(self, fig: plt.Figure):
        self.fig = fig
        w_in, h_in = fig.get_size_inches()
        self.w, self.h = w_in * 72.0, h_in * 72.0
        self.tf = Affine2D().scale(1.0 / 72.0) + fig.dpi_scale_trans

    def text(self, x, y, s, size=9.0, weight="normal", color=None, ha="left",
             va="baseline", family=None, style="normal"):
        return self.fig.text(x, y, s, transform=self.tf, fontsize=size,
                             fontweight=weight, color=color or C["ink"],
                             ha=ha, va=va, family=family or SANS,
                             fontstyle=style)

    def rect(self, x, y, w, h, fill=None, edge=None, lw=0.8, radius=0.0):
        if radius:
            patch = FancyBboxPatch(
                (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                transform=self.tf, facecolor=fill or "none",
                edgecolor=edge or "none", linewidth=lw)
        else:
            patch = Rectangle((x, y), w, h, transform=self.tf,
                              facecolor=fill or "none",
                              edgecolor=edge or "none", linewidth=lw)
        self.fig.patches.append(patch)
        return patch

    def line(self, x1, y1, x2, y2, color=None, lw=0.8):
        self.fig.lines.append(Line2D([x1, x2], [y1, y2], transform=self.tf,
                                     color=color or C["border"], lw=lw))

    def image(self, img, x, y, size):
        ax = self.fig.add_axes((x / self.w, y / self.h, size / self.w,
                                size / self.h))
        ax.imshow(img)
        ax.axis("off")
        return ax


def _canvas_for(fig) -> _Canvas:
    return _Canvas(fig)


def _top_right_badge(fig, page=PAGE) -> None:
    cv = _canvas_for(fig)
    top = cv.h - 22.0
    x = MARGIN
    logo = _load_logo()
    if logo is not None:
        cv.image(logo, x, top - 9.0, 18.0)
        x += 24.0
    cv.text(x, top - 4.0, __app_name__, size=11, weight="bold",
            color=C["accent"])
    title = getattr(fig, "soil_header", None) or t("pdf_title")
    right_w = cv.w - 2 * MARGIN - 200.0
    cv.text(cv.w - MARGIN, top - 4.0, _ellipsize(title, right_w, 8.0),
            size=8.0, color=C["muted"], ha="right")
    cv.line(MARGIN, cv.h - HEADER_H, cv.w - MARGIN, cv.h - HEADER_H,
            color=C["border"], lw=0.8)


def _footer(fig, page=PAGE, number=None, total=None) -> None:
    cv = _canvas_for(fig)
    base = 26.0
    cv.line(MARGIN, FOOTER_H - 4.0, cv.w - MARGIN, FOOTER_H - 4.0,
            color=C["border"], lw=0.8)
    x = MARGIN
    logo = _load_logo()
    if logo is not None:
        cv.image(logo, x, base - 3.0, 10.0)
        x += 14.0
    stamp = datetime.datetime.now()
    cv.text(x, base, f"{t('pdf_generated')} {stamp:%Y-%m-%d %H:%M}  ·  "
                     f"v{__version__}", size=7.5, color=C["micro"])
    label = capitalize(t("pdf_page"))
    if number is not None:
        label = f"{label} {number}" + (f" / {total}" if total else "")
    cv.text(cv.w - MARGIN, base, label, size=7.5, color=C["micro"],
            ha="right")
    disclaimer = t("pdf_disclaimer")
    width = cv.w - 2 * MARGIN - (x - MARGIN)
    size = 6.6
    while size > 5.0 and _measure(disclaimer, size, "normal", SANS) > width:
        size -= 0.2
    cv.text(x, base - 11.0, _wrap(disclaimer, width, size)[0], size=size,
            color=C["micro"], style="italic")


def _finalize_page(fig, page=PAGE, number=None, total=None) -> None:
    _top_right_badge(fig, page=page)
    _footer(fig, page=page, number=number, total=total)


class _Flow:
    def __init__(self, header: str, title: str, continued: str = None):
        self.header = header
        self.title = title
        if continued is None and title:
            continued = f"{title} {t('pdf_continued_suffix')}"
        self.continued = continued
        self.pages: List[plt.Figure] = []
        self._new(self.title)

    def _new(self, title):
        fig = plt.figure(figsize=PAGE)
        fig.soil_header = self.header
        self.pages.append(fig)
        self.cv = _Canvas(fig)
        self.top = self.cv.h - HEADER_H - 22.0
        self.bottom = FOOTER_H + 10.0
        self.left = MARGIN
        self.right = self.cv.w - MARGIN
        self.width = self.right - self.left
        self.y = self.top
        if title:
            self.page_title(title)

    def page_title(self, title):
        self.y -= 15.0
        self.cv.text(self.left, self.y, title, size=15, weight="bold",
                     color=C["accent"])
        self.y -= 10.0
        self.cv.line(self.left, self.y, self.right, self.y, color=C["accent"],
                     lw=1.2)
        self.y -= GAP

    def ensure(self, height: float, title: Optional[str] = "continued"):
        if self.y - height < self.bottom:
            self._new(self.continued if title == "continued" else title)
            return True
        return False

    def section(self, title: str, keep: float = 0.0):
        self.ensure(24.0 + keep)
        self.cv.rect(self.left, self.y - 12.5, 3.0, 13.0, fill=C["accent"])
        self.cv.text(self.left + 9.0, self.y - 11.0, title, size=11.5,
                     weight="bold", color=C["ink"])
        self.y -= 22.0


def _meta_fields(sample: SoilSample) -> List[Tuple[str, str]]:
    project = (sample.project or "").strip() or t("pdf_untitled")
    fields = [(t("pdf_sample"), (sample.name or "").strip() or "-"),
              (t("pdf_project"), project)]
    for label, value in ((t("pdf_location"), sample.location),
                         (t("pdf_tested_by"), sample.operator),
                         (t("pdf_date"), sample.date)):
        if value and value.strip():
            fields.append((label, value.strip()))
    fields.append((t("pdf_report_date"),
                   datetime.date.today().isoformat()))
    return fields


def _info_card(flow: _Flow, sample: SoilSample) -> None:
    fields = _meta_fields(sample)
    cols = 3
    pad = 12.0
    col_w = (flow.width - 2 * pad - (cols - 1) * 16.0) / cols
    rows = [fields[i:i + cols] for i in range(0, len(fields), cols)]
    blocks = []
    height = pad
    for row in rows:
        cells = [(label, _wrap(value, col_w, 10.0, "bold")) for label, value
                 in row]
        row_h = 11.0 + max(len(lines) for _, lines in cells) * _line_h(10.0)
        blocks.append((cells, row_h))
        height += row_h + 8.0
    height += pad - 8.0
    flow.ensure(height)
    top = flow.y
    flow.cv.rect(flow.left, top - height, flow.width, height, fill=C["panel"],
            radius=4.0)
    y = top - pad
    for cells, row_h in blocks:
        for i, (label, lines) in enumerate(cells):
            x = flow.left + pad + i * (col_w + 16.0)
            flow.cv.text(x, y - 7.5, f"{label}:", size=7.8, color=C["muted"])
            ly = y - 11.0 - 10.0
            for line in lines:
                flow.cv.text(x, ly, line, size=10.0, weight="bold")
                ly -= _line_h(10.0)
        y -= row_h + 8.0
    flow.y = top - height - GAP


def _hero(flow: _Flow, results: List[ClassificationResult]) -> None:
    if not results:
        return
    primary = results[0]
    box_w = 92.0
    text_x = flow.left + box_w + 16.0
    text_w = flow.right - text_x
    caption = upper(f"{t('pdf_primary_result')}  ·  {primary.system}")
    caption_lines = _wrap(caption, text_w, 7.5)
    name_lines = _wrap(primary.name or primary.system, text_w, 13.0, "bold")
    others = "  ·  ".join(f"{r.system}: {r.symbol}".replace(" ", "\u00a0")
                              for r in results[1:] if r.symbol)
    other_lines = _wrap(others, text_w, 8.3) if others else []
    text_h = (len(caption_lines) * _line_h(7.5) + 4.0
              + len(name_lines) * _line_h(13.0) + 4.0
              + len(other_lines) * _line_h(8.3))
    sym_size = 22.0
    while sym_size > 10.0 and _measure(primary.symbol, sym_size, "bold",
                                       SANS) > box_w - 12.0:
        sym_size -= 1.0
    height = max(58.0, text_h + 8.0)
    flow.ensure(height)
    top = flow.y
    flow.cv.rect(flow.left, top - height, box_w, height, fill=C["paper"],
            edge=C["accent"], lw=1.4, radius=3.0)
    flow.cv.text(flow.left + box_w / 2.0, top - height / 2.0, primary.symbol,
            size=sym_size, weight="bold", color=C["accent"], ha="center",
            va="center_baseline")
    y = top - (height - text_h) / 2.0
    for line in caption_lines:
        y -= _line_h(7.5)
        flow.cv.text(text_x, y + 2.0, line, size=7.5, color=C["micro"])
    y -= 4.0
    for line in name_lines:
        y -= _line_h(13.0)
        flow.cv.text(text_x, y + 3.0, line, size=13.0, weight="bold")
    y -= 4.0
    for line in other_lines:
        y -= _line_h(8.3)
        flow.cv.text(text_x, y + 2.0, line, size=8.3, color=C["muted"],
                family=SANS)
    flow.y = top - height - GAP - 4.0


def _table(flow: _Flow, headers: Sequence[str], rows: Sequence[Sequence[str]],
           fracs: Sequence[float], *, size: float = 9.0,
           bold_cols: Sequence[int] = (), accent_cols: Sequence[int] = (),
           align: Sequence[str] = None, x: float = None,
           width: float = None, pad_y: float = 5.0) -> None:
    x0 = flow.left if x is None else x
    total_w = flow.width if width is None else width
    widths = [total_w * f for f in fracs]
    align = align or ["left"] * len(headers)
    pad_x = 7.0
    head_size = size - 0.5
    head_lines = [_wrap(h, w - 2 * pad_x, head_size, "bold")
                  for h, w in zip(headers, widths)]
    head_h = max(len(l) for l in head_lines) * _line_h(head_size) + 2 * pad_y

    def draw_header():
        top = flow.y
        flow.cv.rect(x0, top - head_h, total_w, head_h, fill=C["table_header_bg"])
        cx = x0
        for lines, w, al in zip(head_lines, widths, align):
            ty = top - pad_y
            for line in lines:
                ty -= _line_h(head_size)
                tx = {"left": cx + pad_x, "right": cx + w - pad_x,
                      "center": cx + w / 2.0}[al]
                flow.cv.text(tx, ty + 2.6, line, size=head_size, weight="bold",
                        color=C["table_header_fg"], ha=al)
            cx += w
        flow.y = top - head_h

    flow.ensure(head_h + _line_h(size) * 2 + 2 * pad_y)
    draw_header()
    for index, row in enumerate(rows):
        cells = []
        for col, (value, w) in enumerate(zip(row, widths)):
            weight = "bold" if col in bold_cols or col in accent_cols else "normal"
            cells.append((_wrap(str(value), w - 2 * pad_x, size, weight),
                          weight))
        row_h = max(len(lines) for lines, _ in cells) * _line_h(size) + 2 * pad_y
        if flow.ensure(row_h):
            draw_header()
        top = flow.y
        if index % 2 == 1:
            flow.cv.rect(x0, top - row_h, total_w, row_h, fill=C["zebra"])
        flow.cv.line(x0, top - row_h, x0 + total_w, top - row_h, color=C["border"],
                lw=0.6)
        cx = x0
        for col, ((lines, weight), w, al) in enumerate(zip(cells, widths,
                                                           align)):
            color = C["accent"] if col in accent_cols else C["ink"]
            ty = top - pad_y
            for line in lines:
                ty -= _line_h(size)
                tx = {"left": cx + pad_x, "right": cx + w - pad_x,
                      "center": cx + w / 2.0}[al]
                flow.cv.text(tx, ty + 2.6, line, size=size, weight=weight,
                        color=color, ha=al)
            cx += w
        flow.y = top - row_h
    flow.y -= GAP + 4.0


def _fmt(value, digits=1, unit=""):
    return "-" if value is None else f"{value:.{digits}f}{unit}"


def _property_cards(flow: _Flow, sample: SoilSample,
                    results: List[ClassificationResult]) -> None:
    pi = sample.plasticity_index
    limits = [(t("res_liquid_limit"), _fmt(sample.liquid_limit, 1, " %")),
              (t("res_plastic_limit"), _fmt(sample.plastic_limit, 1, " %")),
              (t("res_plasticity_index"), _fmt(pi, 1, " %")),
              (t("res_organic_soil"),
               t("res_yes") if sample.organic else t("res_no"))]
    grading = [("D10", _fmt(sample.d10, 4, " mm")),
               ("D30", _fmt(sample.d30, 4, " mm")),
               ("D60", _fmt(sample.d60, 4, " mm")),
               ("Cu", _fmt(sample.cu, 2)), ("Cc", _fmt(sample.cc, 2))]
    conventions = conventions_for_systems([r.system for r in results]) or \
        (ASTM_SIZES, BS_SIZES)
    frac_cols = []
    for conv in conventions:
        fr = sample.fractions(conv)
        if fr is not None:
            short = "ASTM" if conv is ASTM_SIZES else (
                "BS / ISO" if conv is BS_SIZES else "ISO")
            frac_cols.append((short, fr))
    fractions = [(t("pdf_gravel"), [f"{fr.gravel:.1f}" for _, fr in frac_cols]),
                 (t("pdf_sand"), [f"{fr.sand:.1f}" for _, fr in frac_cols]),
                 (t("pdf_fines"), [f"{fr.fines:.1f}" for _, fr in frac_cols])]

    gap = 12.0
    card_w = (flow.width - 2 * gap) / 3.0
    pad = 10.0
    row_h = 15.0
    cards = [
        (t("pdf_atterberg"), [(k, [v]) for k, v in limits], []),
        (t("pdf_gradation"), [(k, [v]) for k, v in grading], []),
        (t("pdf_fractions"), fractions, [name for name, _ in frac_cols]),
    ]
    max_rows = max(len(rows) + (1 if heads else 0) for _, rows, heads in cards)
    height = pad + 16.0 + max_rows * row_h + pad - 4.0
    flow.ensure(height)
    top = flow.y
    for i, (title, rows, heads) in enumerate(cards):
        x = flow.left + i * (card_w + gap)
        flow.cv.rect(x, top - height, card_w, height, fill=C["paper"],
                edge=C["border"], lw=0.8, radius=4.0)
        flow.cv.text(x + pad, top - pad - 7.0, upper(title), size=7.6,
                weight="bold", color=C["accent"])
        y = top - pad - 16.0
        value_cols = max(1, len(heads) or 1)
        col_w = 58.0 if value_cols > 1 else 0.0
        if heads:
            for j, head in enumerate(heads):
                hx = x + card_w - pad - (value_cols - 1 - j) * col_w
                flow.cv.text(hx, y - 10.0, head, size=7.2, weight="bold",
                        color=C["micro"], ha="right")
            y -= row_h
        for label, values in rows:
            label_w = card_w - 2 * pad - value_cols * max(col_w, 66.0)
            flow.cv.text(x + pad, y - 10.0, _wrap(label, max(label_w, 40.0),
                                             8.3)[0],
                    size=8.3, color=C["muted"])
            for j, value in enumerate(values):
                vx = x + card_w - pad - (value_cols - 1 - j) * col_w
                flow.cv.text(vx, y - 10.0, value, size=8.6, weight="bold",
                        ha="right")
            y -= row_h
    flow.y = top - height - GAP - 4.0


def _sieve_rows(sample: SoilSample) -> List[Tuple[str, str]]:
    return [(f"{d:g}", f"{p:.1f}") for d, p in reversed(sample.sieve_data)]


def _sieve_table(flow: _Flow, sample: SoilSample) -> None:
    rows = _sieve_rows(sample)
    headers = [t("pdf_size_mm"), t("pdf_passing_pct")]
    size, pad_y, gap = 8.6, 4.0, 16.0
    row_h = _line_h(size) + 2 * pad_y
    head_h = _line_h(size - 0.5) + 2 * pad_y

    def layout(available):
        for columns in (2, 3, 4):
            block = (flow.width - (columns - 1) * gap) / columns
            if any(len(_wrap(h, block / 2.0 - 14.0, size - 0.5, "bold")) > 1
                   for h in headers):
                break
            per = -(-len(rows) // columns)
            if 24.0 + head_h + per * row_h + 2.0 <= available:
                return columns, per
        return None

    choice = layout(flow.y - flow.bottom)
    if choice is None:
        fresh = layout(flow.top - 40.0 - flow.bottom)
        if fresh is not None:
            flow.ensure(flow.top)
            choice = layout(flow.y - flow.bottom) or fresh
    flow.section(t("pdf_sieve_analysis"), keep=head_h + 2 * row_h)
    if choice is None:
        _table(flow, headers, rows, [0.5, 0.5], size=size, pad_y=pad_y,
               align=["right", "right"], width=(flow.width - gap) / 2.0)
        return
    columns, per = choice
    block_w = (flow.width - (columns - 1) * gap) / columns
    top = flow.y
    lowest = top
    for index in range(columns):
        chunk = rows[index * per:(index + 1) * per]
        if not chunk:
            break
        flow.y = top
        _table(flow, headers, chunk, [0.5, 0.5], size=size, pad_y=pad_y,
               align=["right", "right"], width=block_w,
               x=flow.left + index * (block_w + gap))
        lowest = min(lowest, flow.y)
    flow.y = lowest


def _summary_page(sample: SoilSample,
                  results: List[ClassificationResult],
                  subtitle: str = None,
                  include_sieve: bool = False) -> plt.Figure:
    flow = _summary_flow(sample, [r for r in results if r.ok], subtitle,
                         include_sieve)
    fig = flow.pages[0]
    fig.sieve_included = include_sieve and bool(sample.sieve_data)
    fig.extra_pages = flow.pages[1:]
    return fig


def _report_header(sample: SoilSample) -> str:
    name = (sample.name or "").strip()
    title = t("pdf_header_title")
    return f"{title}  ·  {name}" if name else title


def _summary_flow(sample, results, subtitle, include_sieve) -> _Flow:
    flow = _Flow(_report_header(sample), None)
    flow.y -= 20.0
    flow.cv.text(flow.left, flow.y, t("pdf_title"), size=19, weight="bold",
            color=C["accent"])
    flow.y -= 16.0
    for line in _wrap(subtitle or _subtitle(ALL_CLASSIFIERS), flow.width, 9.5):
        flow.cv.text(flow.left, flow.y, line, size=9.5, color=C["muted"])
        flow.y -= _line_h(9.5)
    flow.y -= 6.0
    flow.cv.line(flow.left, flow.y, flow.right, flow.y, color=C["accent"], lw=1.4)
    flow.y -= GAP + 2.0

    _info_card(flow, sample)
    if results:
        _hero(flow, results)
        flow.section(t("pdf_classification_summary"), keep=60.0)
        _table(flow, [t("pdf_col_system"), t("pdf_col_group_symbol"),
                      t("pdf_col_group_name")],
               [(r.system, r.symbol, r.name) for r in results],
               [0.30, 0.17, 0.53], accent_cols=(1,))
    flow.section(t("pdf_index_properties"), keep=110.0)
    _property_cards(flow, sample, results)
    if include_sieve and sample.sieve_data:
        _sieve_table(flow, sample)
    return flow


def _trail_pages(sample: SoilSample,
                 results: List[ClassificationResult]) -> List[plt.Figure]:
    flow = _Flow(_report_header(sample), t("pdf_decision_trails_title"))
    trail_label = t("res_decision_trail_label").rstrip(" :")
    for result in results:
        name_lines = _wrap(f"{t('pdf_col_group_name')}: {result.name}",
                           flow.width - 16.0, 9.5)
        steps = [(f"{i}.", _wrap(note, flow.width - 34.0, 9.0))
                 for i, note in enumerate(result.notes, start=1)]
        first_step = len(steps[0][1]) * _line_h(9.0) if steps else 0.0
        band_h = 24.0
        flow.ensure(band_h + len(name_lines) * _line_h(9.5) + 30.0
                    + first_step)
        top = flow.y
        flow.cv.rect(flow.left, top - band_h, flow.width, band_h, fill=C["panel"],
                radius=3.0)
        flow.cv.rect(flow.left, top - band_h, 3.0, band_h, fill=C["accent"])
        symbol_w = _measure(result.symbol, 11.0, "bold", SANS)
        system_lines = _wrap(result.system, flow.width - symbol_w - 40.0, 11.0,
                             "bold")
        flow.cv.text(flow.left + 12.0, top - 15.5, system_lines[0], size=11.0,
                weight="bold")
        flow.cv.text(flow.right - 10.0, top - 15.5, result.symbol, size=11.0,
                weight="bold", color=C["accent"], ha="right")
        flow.y = top - band_h - 6.0
        for line in name_lines:
            flow.y -= _line_h(9.5)
            flow.cv.text(flow.left + 8.0, flow.y + 3.0, line, size=9.5,
                    weight="bold")
        extras = list(result.extras.items())
        if extras:
            flow.y -= 4.0
            col_w = (flow.width - 16.0) / 2.0
            for i in range(0, len(extras), 2):
                pair = extras[i:i + 2]
                wrapped = [_wrap(f"{k}: {v}", col_w - 10.0, 8.6)
                           for k, v in pair]
                row_h = max(len(w) for w in wrapped) * _line_h(8.6)
                flow.ensure(row_h)
                for j, lines in enumerate(wrapped):
                    ly = flow.y
                    for line in lines:
                        ly -= _line_h(8.6)
                        flow.cv.text(flow.left + 8.0 + j * col_w, ly + 2.5, line,
                                size=8.6, color=C["muted"])
                flow.y -= row_h
        if steps:
            flow.y -= 6.0
            flow.ensure(14.0 + first_step)
            flow.cv.text(flow.left + 8.0, flow.y - 9.0, upper(trail_label),
                    size=7.6, weight="bold", color=C["accent"])
            flow.y -= 14.0
            for number, lines in steps:
                block = len(lines) * _line_h(9.0) + 2.0
                flow.ensure(block)
                ly = flow.y
                flow.cv.text(flow.left + 26.0, ly - _line_h(9.0) + 2.5, number,
                        size=9.0, color=C["micro"], ha="right")
                for line in lines:
                    ly -= _line_h(9.0)
                    flow.cv.text(flow.left + 32.0, ly + 2.5, line, size=9.0)
                flow.y -= block
        flow.y -= GAP + 6.0
    return flow.pages


def fit_chart_to_page(fig) -> None:
    w_in, h_in = fig.get_size_inches()
    low = (FOOTER_H + 8.0) / 72.0
    high = h_in - (HEADER_H + 8.0) / 72.0
    left_limit = (MARGIN - 8.0) / 72.0
    right_limit = w_in - (MARGIN - 8.0) / 72.0
    fig.subplots_adjust(left=0.08, right=0.96, bottom=0.14, top=0.86)
    for _ in range(12):
        renderer = fig.canvas.get_renderer()
        declutter(fig, renderer)
        box = fig.get_tightbbox(renderer)
        sp = fig.subplotpars
        left, right, bottom, top = sp.left, sp.right, sp.bottom, sp.top
        step = 2.0 / 72.0
        if box.y0 < low:
            bottom += (low - box.y0 + step) / h_in
        if box.y1 > high:
            top -= (box.y1 - high + step) / h_in
        if box.x0 < left_limit:
            left += (left_limit - box.x0 + step) / w_in
        if box.x1 > right_limit:
            right -= (box.x1 - right_limit + step) / w_in
        if (left, right, bottom, top) == (sp.left, sp.right, sp.bottom,
                                          sp.top):
            return
        fig.subplots_adjust(left=left, right=right, bottom=bottom, top=top)
    declutter(fig, fig.canvas.get_renderer())


def build_pdf(sample: SoilSample, path: str, classifiers=None,
              figures=None) -> str:
    classifiers = classifiers or ALL_CLASSIFIERS
    figures = figures if figures is not None else ALL_FIGURES
    results = [r for r in classify_selected(sample, classifiers) if r.ok]
    figures = classifiable_chart_defs(figures, sample)
    bset = _boundaries_for(classifiers)

    pages: List[Tuple[plt.Figure, Tuple[float, float]]] = []
    flow = _summary_flow(sample, results, _subtitle(classifiers), True)
    pages.extend((fig, PAGE) for fig in flow.pages)

    header = _report_header(sample)
    for _title, builder in figures:
        if builder is gsd_figure:
            fig = builder(sample, figsize=PAGE_LANDSCAPE, boundaries=bset)
        else:
            fig = builder(sample, figsize=PAGE_LANDSCAPE)
        fig.soil_header = header
        fit_chart_to_page(fig)
        pages.append((fig, PAGE_LANDSCAPE))

    if results:
        pages.extend((fig, PAGE) for fig in _trail_pages(sample, results))

    with PdfPages(path) as pdf:
        for n, (fig, page) in enumerate(pages, start=1):
            _finalize_page(fig, page=page, number=n, total=len(pages))
            pdf.savefig(fig)
            plt.close(fig)

        meta = pdf.infodict()
        meta["Title"] = f"{t('pdf_title')} - {sample.name}"
        meta["Author"] = sample.operator or "SoilClass Pro"
        meta["Subject"] = _subtitle(classifiers).replace("  ·  ", " / ")
        meta["Creator"] = "SoilClass Pro"
    return path
