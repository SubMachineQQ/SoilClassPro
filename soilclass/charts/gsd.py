from __future__ import annotations

from typing import Optional, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator

from ..models import SoilSample
from ..i18n import t
from .style import COLORS, FONTS, apply_base_style, series_colour

BOUNDARY_SETS = {
    "USCS": {
        "label_prefix": "USCS (ASTM D2487)",
        "bands": [("chart_gsd_fines", 1e-3, 0.075, "gsd_zone_fines"),
                  ("chart_gsd_sand", 0.075, 4.75, "gsd_zone_sand"),
                  ("chart_gsd_gravel", 4.75, 75.0, "gsd_zone_gravel"),
                  ("chart_gsd_cobbles", 75.0, 100.0, "gsd_zone_gravel")],
    },
    "BS": {
        "label_prefix": "BS 5930",
        "bands": [("chart_gsd_clay", 1e-3, 0.002, "gsd_zone_fines"),
                  ("chart_gsd_silt", 0.002, 0.063, "gsd_zone_fines"),
                  ("chart_gsd_sand", 0.063, 2.0, "gsd_zone_sand"),
                  ("chart_gsd_gravel", 2.0, 63.0, "gsd_zone_gravel"),
                  ("chart_gsd_cobbles", 63.0, 100.0, "gsd_zone_gravel")],
    },
    "RSCS": {
        "label_prefix": "RSCS (sieves #4 / #200)",
        "bands": [("chart_gsd_fines", 1e-3, 0.075, "gsd_zone_fines"),
                  ("chart_gsd_sand", 0.075, 4.75, "gsd_zone_sand"),
                  ("chart_gsd_gravel", 4.75, 100.0, "gsd_zone_gravel")],
    },
    "ISO14688": {
        "label_prefix": "TS EN ISO 14688",
        "bands": [("chart_gsd_clay", 1e-3, 0.002, "gsd_zone_fines"),
                  ("chart_gsd_silt", 0.002, 0.063, "gsd_zone_fines"),
                  ("chart_gsd_sand", 0.063, 2.0, "gsd_zone_sand"),
                  ("chart_gsd_gravel", 2.0, 63.0, "gsd_zone_gravel"),
                  ("chart_gsd_cobbles", 63.0, 100.0, "gsd_zone_gravel")],
    },
}

DEFAULT_BOUNDARIES = "USCS"

_XLIM = (1e-3, 100.0)


def _prepare_axes(ax, boundaries: str) -> None:
    bset = BOUNDARY_SETS.get(boundaries, BOUNDARY_SETS[DEFAULT_BOUNDARIES])

    for label_key, lo, hi, key in bset["bands"]:
        lo_c, hi_c = max(lo, _XLIM[0]), min(hi, _XLIM[1])
        if hi_c <= lo_c:
            continue
        ax.axvspan(lo_c, hi_c, color=COLORS[key], alpha=0.45, zorder=0)
        ax.text(np.sqrt(lo_c * hi_c), 101.5, t(label_key), ha="center", va="bottom",
                fontsize=FONTS["band_label"], color=COLORS["gsd_band_label"])
        if lo > _XLIM[0]:
            ax.axvline(lo, color=COLORS["spine"], lw=0.9, ls="-",
                       alpha=0.55, zorder=2)

    ax.set_xscale("log")
    ax.set_xlim(*_XLIM)
    ax.set_ylim(0, 100)
    ax.set_xlabel(t("chart_gsd_xlabel"))
    ax.set_ylabel(t("chart_gsd_ylabel"))
    ax.yaxis.set_major_locator(MultipleLocator(10))
    ax.yaxis.set_minor_locator(MultipleLocator(2))
    ax.tick_params(axis="y", which="minor", length=3,
                   colors=COLORS["tick"])
    ax.grid(True, which="major", ls="-", lw=0.5, color=COLORS["grid"],
            zorder=1)
    ax.grid(True, which="minor", axis="y", ls=":", lw=0.35,
            color=COLORS["grid"], zorder=1)
    ax.grid(True, which="minor", axis="x", ls=":", lw=0.35,
            color=COLORS["grid"], zorder=1)

    full_label = f"{bset['label_prefix']} {t('chart_gsd_boundaries_suffix')}"
    ax.text(0.985, 0.03, full_label, transform=ax.transAxes,
            ha="right", va="bottom", fontsize=FONTS["band_label"],
            color=COLORS["ink"],
            bbox=dict(boxstyle="round,pad=0.3", fc="white",
                      ec=COLORS["spine"], lw=0.8, alpha=0.92))


def _plot_measured_curve(ax, sample: SoilSample, colour: str,
                         linestyle: str = "-", label: Optional[str] = None):
    sizes = [d for d, _ in sample.sieve_data]
    passing = [p for _, p in sample.sieve_data]
    xs = np.logspace(np.log10(sizes[0]), np.log10(sizes[-1]), 300)
    ys = [sample.percent_passing(x) for x in xs]
    ax.plot(xs, ys, ls=linestyle, color=colour, lw=2.2, zorder=5,
            label=label)
    ax.plot(sizes, passing, "o", color=colour, ms=6, mfc="white", mew=1.8,
            zorder=6)


def gsd_figure(sample: SoilSample, figsize=(8.6, 5.4),
               boundaries: str = DEFAULT_BOUNDARIES,
               show_d_lines: bool = False) -> Figure:
    fig, ax = plt.subplots(figsize=figsize)
    apply_base_style(ax)
    _prepare_axes(ax, boundaries)

    if sample.has_sieve_data:
        _plot_measured_curve(ax, sample, COLORS["primary"],
                             label=sample.name or t("chart_sample"))

        if show_d_lines:
            for pct, dval in ((10, sample.d10), (30, sample.d30),
                              (60, sample.d60)):
                if dval:
                    ax.plot([dval, dval], [0, pct], ls=":",
                            color=COLORS["accent"], lw=1.1, zorder=3)
                    ax.plot([_XLIM[0], dval], [pct, pct], ls=":",
                            color=COLORS["accent"], lw=1.1, zorder=3)

        rows = []
        for pct, dval in ((60, sample.d60), (30, sample.d30),
                          (10, sample.d10)):
            if dval:
                rows.append(f"D{pct} = {dval:.3g} mm")
        if sample.cu is not None:
            rows.append(f"Cu = {sample.cu:.2f}")
        if sample.cc is not None:
            rows.append(f"Cc = {sample.cc:.2f}")
        if rows:
            ax.text(0.985, 0.44, "\n".join(rows), transform=ax.transAxes,
                    ha="right", va="top", fontsize=FONTS["annotation"],
                    fontweight="bold", color=COLORS["ink"], linespacing=1.4,
                    bbox=dict(boxstyle="round,pad=0.4", fc="white",
                              ec=COLORS["primary"], lw=1.1, alpha=0.95))
        ax.legend(loc="upper left", fontsize=FONTS["legend"],
                  framealpha=0.92, edgecolor=COLORS["spine"])

    ax.set_title(t("chart_gsd_title"), fontsize=FONTS["title"], fontweight="bold", pad=26)
    fig.tight_layout()
    return fig


def gsd_multi_figure(samples: Sequence[SoilSample], figsize=(9.4, 6.0),
                     boundaries: str = DEFAULT_BOUNDARIES,
                     title: Optional[str] = None) -> Figure:
    if title is None:
        title = f"{t('chart_gsd_title')} — {t('chart_comparison_suffix')}"
    fig, ax = plt.subplots(figsize=figsize)
    apply_base_style(ax)
    _prepare_axes(ax, boundaries)

    styles = ["-", "--", "-."]
    plotted = 0
    for i, sample in enumerate(samples):
        if not sample.has_sieve_data:
            continue
        _plot_measured_curve(ax, sample, series_colour(i),
                             linestyle=styles[(i // 10) % len(styles)],
                             label=sample.name or f"{t('chart_sample')} {i + 1}")
        plotted += 1

    if plotted:
        ncol = 2 if plotted > 6 else 1
        ax.legend(loc="upper left", fontsize=FONTS["legend"], ncol=ncol,
                  framealpha=0.92, edgecolor=COLORS["spine"])
    else:
        ax.text(0.5, 0.5, t("chart_no_sieve_data"), transform=ax.transAxes,
                ha="center", va="center", fontsize=FONTS["note"],
                style="italic", color=COLORS["no_data_fg"])

    ax.set_title(title, fontsize=FONTS["title"], fontweight="bold", pad=26)
    fig.tight_layout()
    return fig
