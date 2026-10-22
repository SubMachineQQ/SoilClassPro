from __future__ import annotations

import math
from typing import Optional

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from ..classifiers.rscs import (PLASTICITY_NAMES, SENSITIVITY_NAMES,
                                RSCSClassifier)
from ..i18n import capitalize, t, translate_domain_text
from ..models import SoilSample
from .style import COLORS, FONTS, apply_base_style

PLASTICITY_EDGES = [30.0, 50.0, 75.0]
SENSITIVITY_EDGES = [0.4, 1.0]


def _fines_values(sample: SoilSample) -> Optional[dict]:
    if (sample.liquid_limit is None or sample.ll_brine is None
            or sample.ll_kerosene is None):
        return None
    try:
        if float(sample.ll_brine) <= 0 or float(sample.ll_kerosene) <= 0:
            return None
        return RSCSClassifier.fines_classification(
            float(sample.liquid_limit), float(sample.ll_brine),
            float(sample.ll_kerosene))
    except (ValueError, ZeroDivisionError):
        return None


def _no_data_note(ax, sample: SoilSample) -> None:
    ax.text(0.5, 0.06,
            t("chart_rscsf_no_data").format(name=sample.name),
            transform=ax.transAxes, ha="center", va="bottom",
            fontsize=FONTS["annotation"], style="italic", color=COLORS["no_data_fg"],
            bbox=dict(boxstyle="round,pad=0.4", fc=COLORS["no_data_bg"],
                      ec=COLORS["spine"], lw=0.8))


def _mark(ax, x: float, y: float, lines) -> None:
    ax.plot([x], [y], marker="*", ms=17, color=COLORS["sample"],
            mec="white", mew=1.2, zorder=12)
    ax.annotate("\n".join(lines), (x, y), textcoords="offset points",
                xytext=(14, 52), fontsize=FONTS["annotation"], fontweight="bold",
                color=COLORS["sample"], zorder=13,
                arrowprops=dict(arrowstyle="-", color=COLORS["sample"], lw=1.0,
                                shrinkA=0, shrinkB=8),
                bbox=dict(boxstyle="round,pad=0.32", fc="white",
                          ec=COLORS["sample"], alpha=0.92, lw=0.9))


def rscs_fines_ratio_figure(sample: SoilSample,
                            figsize=(8.6, 5.4)) -> Figure:
    fig, ax = plt.subplots(figsize=figsize)
    apply_base_style(ax)

    x_max = 3.0
    y_max = 6.0

    ax.axvline(0.0, color=COLORS["rscs_se_divider"], lw=1.1, ls="--",
               zorder=3)
    ax.axhline(1.0, color=COLORS["rscs_se_divider"], lw=1.0, ls=":",
               zorder=3)

    theta = np.linspace(0, math.pi, 200)
    for level, key in ((0.4, "rscs_se_arc_low"), (1.0, "rscs_se_arc_high")):
        ax.plot(level * np.cos(theta), 1.0 + level * np.sin(theta),
                color=COLORS[key], lw=1.8, zorder=5)
        ax.annotate(f"S$_E$ = {level:g}",
                    (level * math.cos(2.3), 1.0 + level * math.sin(2.3)),
                    textcoords="offset points", xytext=(-6, 4),
                    ha="right", fontsize=FONTS["band_label"], fontweight="bold",
                    color=COLORS[key], zorder=6)

    ax.set_xlim(-x_max, x_max)
    ax.set_ylim(1.0, y_max)

    ticks = [-3, -2, -1, 0, 1, 2, 3]
    ax.set_xticks(ticks)
    ax.set_xticklabels(["3", "2", "1", "1", "1", "2", "3"])
    ax.set_xlabel("LL$_{ker}$ / LL$_{brine}$        \u2190  |  \u2192        "
                  "LL$_{brine}$ / LL$_{ker}$")
    ax.set_ylabel("LL$_{DW}$ / LL$_{brine}$")
    ax.set_title(t("chart_rscsf_ratio_title"), fontsize=FONTS["title"], fontweight="bold")
    ax.grid(True, ls="-", lw=0.4, color=COLORS["grid"], zorder=1)

    fc = _fines_values(sample)
    if fc is None:
        _no_data_note(ax, sample)
    else:
        r_ker = float(fc["ratio_ker"])
        r_dw = float(fc["ratio_dw"])
        b = r_ker if r_ker >= 1.0 else 1.0 / r_ker
        x = -(b - 1.0) if r_ker >= 1.0 else (b - 1.0)
        y = r_dw
        se = float(fc["SE"])
        _mark(ax, x, y, [sample.name,
                         f"S$_E$ = {se:.2f}",
                         f"{t('chart_rscsf_fines')}: {fc['symbol']}"])

    fig.tight_layout()
    return fig


def rscs_fines_sensitivity_figure(sample: SoilSample,
                                  figsize=(8.6, 5.4)) -> Figure:
    fig, ax = plt.subplots(figsize=figsize)
    apply_base_style(ax)

    ll_max, se_max = 200.0, 4.5

    for lo, hi, key in ((0.0, SENSITIVITY_EDGES[0], "rscs_se_sens_low"),
                        (SENSITIVITY_EDGES[0], SENSITIVITY_EDGES[1],
                         "rscs_se_sens_int"),
                        (SENSITIVITY_EDGES[1], se_max, "rscs_se_sens_high")):
        ax.axhspan(lo, hi, color=COLORS[key], alpha=0.55, zorder=0)
    for edge in SENSITIVITY_EDGES:
        ax.axhline(edge, color=COLORS["rscs_se_divider"], lw=1.1, ls="--",
                   zorder=3)

    for edge in PLASTICITY_EDGES:
        ax.axvline(edge, color=COLORS["rscs_se_divider"], lw=1.1, ls="--",
                   zorder=3)

    band_spans = [(0.0, PLASTICITY_EDGES[0], "N"),
                  (PLASTICITY_EDGES[0], PLASTICITY_EDGES[1], "L"),
                  (PLASTICITY_EDGES[1], PLASTICITY_EDGES[2], "I"),
                  (PLASTICITY_EDGES[2], ll_max, "H")]
    for lo, hi, letter in band_spans:
        ax.text((lo + hi) / 2.0, se_max - 0.12, letter,
                ha="center", va="top", fontsize=FONTS["zone_label"], fontweight="bold",
                color=COLORS["rscs_se_label"], zorder=6)
    ax.text(0.5, -0.16,
            t("chart_rscsf_band_legend"),
            transform=ax.transAxes, ha="center", va="top", fontsize=FONTS["band_label"],
            color=COLORS["rscs_se_label"])

    sens_spans = [(0.0, SENSITIVITY_EDGES[0], "L"),
                  (SENSITIVITY_EDGES[0], SENSITIVITY_EDGES[1], "I"),
                  (SENSITIVITY_EDGES[1], se_max, "H")]
    for lo, hi, letter in sens_spans:
        ax.text(ll_max - 2, (lo + hi) / 2.0, letter,
                ha="right", va="center", fontsize=FONTS["zone_label"], fontweight="bold",
                color=COLORS["rscs_se_label"], zorder=6)

    ax.set_xlim(0, ll_max)
    ax.set_ylim(0, se_max)
    ax.set_xlabel(t("chart_rscsf_sens_xlabel"))
    ax.set_ylabel(t("chart_rscsf_sens_ylabel"))
    ax.set_title(t("chart_rscsf_sens_title"), fontsize=FONTS["title"], fontweight="bold")
    ax.grid(True, ls="-", lw=0.4, color=COLORS["grid"], zorder=1)

    fc = _fines_values(sample)
    if fc is None:
        _no_data_note(ax, sample)
    else:
        ll_b = float(fc["LL_brine_corrected"])
        se = float(fc["SE"])
        symbol = str(fc["symbol"])
        plast, sens = symbol[0], symbol[1]
        _mark(ax, min(ll_b, ll_max), min(se, se_max),
              [sample.name,
               f"LL$_{{brine}}$ = {ll_b:.0f},  S$_E$ = {se:.2f}",
               f"{t('chart_rscsf_fines')}: {symbol}"])
        ax.text(0.985, 0.72,
                capitalize(translate_domain_text(
                    f"{PLASTICITY_NAMES[plast]}, {SENSITIVITY_NAMES[sens]}")),
                transform=ax.transAxes, fontsize=FONTS["band_label"], fontweight="bold",
                color=COLORS["sample"], va="bottom", ha="right",
                bbox=dict(boxstyle="round,pad=0.32", fc="white",
                          ec=COLORS["sample"], alpha=0.92, lw=0.9))

    fig.tight_layout()
    return fig
