from __future__ import annotations

import math

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon as MplPolygon

from ..classifiers.rscs import (APEX_FINES, CORNER_GRAVEL, CORNER_SAND,
                                GROUP_POLYGONS, RSCSClassifier, to_xy)
from ..i18n import t
from ..models import ASTM_SIZES, SoilSample
from .declutter import (FAR_AROUND, NUDGE, keep_clear, movable, ring,
                        wrap_label)
from .style import COLORS, FONTS, apply_base_style

ZONE_KEYS = {
    "G(G)": "rscs_zone_gg",
    "GS(S)": "rscs_zone_gss",
    "S(S)": "rscs_zone_ss",
    "G(F)": "rscs_zone_gf",
    "GS(F)": "rscs_zone_gsf",
    "S(F)": "rscs_zone_sf",
    "GF(F)": "rscs_zone_gff",
    "GSF(F)": "rscs_zone_gsff",
    "SF(F)": "rscs_zone_sff",
    "F(F)": "rscs_zone_ff",
}

MECH_SEGMENTS = [(1, 3), (3, 2), (4, 6), (6, 5),
                 (1, 7), (7, 9), (9, 3),
                 (4, 8), (8, 9), (9, 6),
                 (3, 6)]

FLOW_SEGMENTS = [("Gc", 10), (10, 11), (11, 12), (12, 13), (13, "Sc")]

_SQ3_2 = math.sqrt(3.0) / 2.0
_TICK_LEN = 1.8
_LABEL_OFF = 5.0
_TICK_FONT = 10
_POINT_FONT = 9.5
_SMALL_ZONE = 120.0
_ZONE_FAR = [
    (dx, dy, "center", "center")
    for dy in (-34, 34, -48, 48)
    for dx in (0, -40, 40, -80, 80)
]


def _corner(key, mixtures):
    if key == "Gc":
        return CORNER_GRAVEL
    if key == "Sc":
        return CORNER_SAND
    if key == "Ap":
        return APEX_FINES
    return to_xy(*mixtures[key])


def _area(poly) -> float:
    n = len(poly)
    return 0.5 * abs(sum(poly[i][0] * poly[(i + 1) % n][1]
                         - poly[(i + 1) % n][0] * poly[i][1]
                         for i in range(n)))


def rscs_figure(sample: SoilSample, figsize=(8.4, 7.4)) -> Figure:
    fig, ax = plt.subplots(figsize=figsize)
    apply_base_style(ax)
    ax.set_aspect("equal")
    ax.axis("off")

    clf = RSCSClassifier()
    ll = sample.liquid_limit if sample.liquid_limit else 25.0
    pk = clf.packing(sample)
    fv = clf.fines_void_ratios(ll)
    mixtures = clf.notable_mixtures(pk, fv)

    for name, poly_keys in GROUP_POLYGONS.items():
        poly = [_corner(k, mixtures) for k in poly_keys]
        if _area(poly) < 1e-6:
            continue
        ax.add_patch(MplPolygon(poly, closed=True,
                                facecolor=COLORS[ZONE_KEYS[name]],
                                edgecolor="none", zorder=1))
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        small = _area(poly) < _SMALL_ZONE
        label = ax.annotate(
            name, (cx, cy), textcoords="offset points", xytext=(0, 0),
            ha="center", va="center",
            fontsize=FONTS["zone_label"] - (2 if small else 0),
            fontweight="bold", color=COLORS["rscs_zone_label"], zorder=6,
            arrowprops=dict(arrowstyle="-", color=COLORS["rscs_zone_label"],
                            lw=0.7, shrinkA=2, shrinkB=0))
        movable(label, NUDGE + _ZONE_FAR, priority=0)

    for i in range(1, 10):
        f = i * 10.0
        for a, b in ((to_xy(100 - f, 0, f), to_xy(0, 100 - f, f)),
                     (to_xy(100 - f, f, 0), to_xy(0, f, 100 - f)),
                     (to_xy(f, 100 - f, 0), to_xy(f, 0, 100 - f))):
            ax.plot([a[0], b[0]], [a[1], b[1]], color=COLORS["rscs_gridline"],
                    lw=0.9, alpha=0.75, zorder=2)

    def seg(a, b, **kw):
        pa, pb = _corner(a, mixtures), _corner(b, mixtures)
        ax.plot([pa[0], pb[0]], [pa[1], pb[1]], **kw)

    for a, b in MECH_SEGMENTS:
        seg(a, b, color=COLORS["rscs_mech_line"], lw=1.7, zorder=4)
    for a, b in FLOW_SEGMENTS:
        seg(a, b, color=COLORS["rscs_flow_line"], lw=1.7, ls="--", zorder=5)

    tri = [CORNER_GRAVEL, CORNER_SAND, APEX_FINES, CORNER_GRAVEL]
    ax.plot([p[0] for p in tri], [p[1] for p in tri], color=COLORS["ink"],
            lw=1.8, zorder=7)

    for i in range(1, 14):
        x, y = to_xy(*mixtures[i])
        ax.plot([x], [y], "o", ms=4.5, mfc="white",
                mec=COLORS["rscs_mixture_pt"], mew=1.0, zorder=8)
        keep_clear(ax, x, y, 3.5)
        movable(ax.annotate(str(i), (x, y), textcoords="offset points",
                            xytext=(4, 4), fontsize=_POINT_FONT,
                            color=COLORS["rscs_mixture_pt"], zorder=9),
                ring((4, 7, 10, 14, 18)), priority=2)

    n_left, n_bottom, n_right = (-0.866, 0.5), (0.0, -1.0), (0.866, 0.5)
    for i in range(1, 20):
        v = i * 5.0
        major = i % 2 == 0
        tick_len = _TICK_LEN if major else _TICK_LEN * 0.55
        frac = (100.0 - v) / 100.0
        px, py = frac * 50.0, frac * 100.0 * _SQ3_2
        ax.plot([px, px + tick_len * n_left[0]],
                [py, py + tick_len * n_left[1]],
                color=COLORS["spine"], lw=0.8, zorder=7)
        if major:
            ax.text(px + _LABEL_OFF * n_left[0], py + _LABEL_OFF * n_left[1],
                    f"{v:.0f}", fontsize=_TICK_FONT, ha="center",
                    va="center", color=COLORS["tick"], rotation=60)

        ax.plot([v, v], [0.0, tick_len * n_bottom[1]],
                color=COLORS["spine"], lw=0.8, zorder=7)
        if major:
            ax.text(v, _LABEL_OFF * n_bottom[1], f"{v:.0f}",
                    fontsize=_TICK_FONT, ha="center", va="center",
                    color=COLORS["tick"])

        px, py = 100.0 - 0.5 * v, 100.0 * _SQ3_2 * v / 100.0
        ax.plot([px, px + tick_len * n_right[0]],
                [py, py + tick_len * n_right[1]],
                color=COLORS["spine"], lw=0.8, zorder=7)
        if major:
            ax.text(px + _LABEL_OFF * n_right[0], py + _LABEL_OFF * n_right[1],
                    f"{v:.0f}", fontsize=_TICK_FONT, ha="center",
                    va="center", color=COLORS["tick"], rotation=-60)

    ax.text(9.0, 45.5, t("chart_rscs_gravel_axis"), fontsize=FONTS["axis_label"], fontweight="bold",
            color=COLORS["label_muted"], rotation=60, ha="center", va="center")
    ax.text(50.0, -11.0, t("chart_rscs_sand_axis"), fontsize=FONTS["axis_label"], fontweight="bold",
            color=COLORS["label_muted"], ha="center", va="center")
    ax.text(91.0, 45.5, t("chart_rscs_fines_axis"), fontsize=FONTS["axis_label"], fontweight="bold",
            color=COLORS["label_muted"], rotation=-60, ha="center", va="center")

    fr = sample.fractions(ASTM_SIZES)
    symbol = ""
    if fr is not None:
        sx, sy = to_xy(fr.gravel, fr.sand, fr.fines)
        result = clf.classify(sample)
        symbol = result.symbol if result.ok else ""
        ax.plot([sx], [sy], marker="*", ms=19, color=COLORS["sample"],
                mec="white", mew=1.2, zorder=12)
        keep_clear(ax, sx, sy, 9.0)
        label = ax.annotate(
            f"{wrap_label(sample.name)}\n"
            f"{t('chart_rscs_letter_gravel')} {fr.gravel:.0f} / "
            f"{t('chart_rscs_letter_sand')} {fr.sand:.0f} / "
            f"{t('chart_rscs_letter_fines')} {fr.fines:.0f} %"
            + (f"\n\u2192 {symbol}" if symbol else ""),
            (sx, sy), xycoords="data", xytext=(-110, 90),
            textcoords="offset points", ha="right", va="bottom",
            fontsize=FONTS["annotation"],
            fontweight="bold", color=COLORS["sample"], zorder=12,
            linespacing=1.35, multialignment="left",
            arrowprops=dict(arrowstyle="-", color=COLORS["sample"], lw=1.0,
                            shrinkA=0, shrinkB=6),
            bbox=dict(boxstyle="round,pad=0.32", fc="white",
                      ec=COLORS["sample"], alpha=0.92, lw=0.9))
        movable(label, FAR_AROUND, priority=1, region="figure")

    ax.legend(handles=[
        Line2D([0], [0], color=COLORS["rscs_mech_line"], lw=1.7,
               label=t("chart_rscs_mech_boundary")),
        Line2D([0], [0], color=COLORS["rscs_flow_line"], lw=1.7, ls="--",
               label=t("chart_rscs_flow_boundary")),
        Line2D([0], [0], marker="o", color="none", mfc="white",
               mec=COLORS["rscs_mixture_pt"], ms=5.5,
               label=t("chart_rscs_notable_mixtures")),
    ], loc="upper right", fontsize=FONTS["legend"], framealpha=0.95)

    title = t("chart_rscs_title")
    if symbol:
        title += f"  \u2014  {symbol}"
    ax.set_title(
        f"{title}\n"
        f"{t('chart_rscs_gravel_e')} = {pk.e_min_gravel:.3f}\u2013{pk.e_max_gravel:.3f}   "
        f"{t('chart_rscs_sand_e')} = {pk.e_min_sand:.3f}\u2013{pk.e_max_sand:.3f}   "
        f"LL = {ll:.0f} %   \u03bb = {fv.lam:.2f}",
        fontsize=FONTS["title"], fontweight="bold")

    ax.set_xlim(-16, 116)
    ax.set_ylim(-16, 100)
    fig.tight_layout()
    return fig
