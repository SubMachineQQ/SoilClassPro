from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from ..i18n import t
from ..models import SoilSample
from .style import (COLORS, FONTS, apply_base_style, mark_sample_or_note,
                    sample_plot_point, series_colour)


def _a_line(ll):
    return 0.73 * (np.asarray(ll) - 20.0)


def _label_a_line(ax, ll: float) -> None:
    ax.text(ll, float(_a_line(ll)), t("chart_a_line"),
            rotation=float(np.degrees(np.arctan(0.73))),
            transform_rotates_text=True, rotation_mode="anchor",
            ha="center", va="bottom",
            fontsize=FONTS["band_label"], fontweight="bold",
            color=COLORS["ink"], zorder=6)


def _u_line(ll):
    return 0.9 * (np.asarray(ll) - 8.0)


_A_AT_PI4 = 20.0 + 4.0 / 0.73
_A_AT_PI7 = 20.0 + 7.0 / 0.73


def _overlay_samples(ax, samples: Sequence[SoilSample]) -> bool:
    drawn = 0
    for i, s in enumerate(samples):
        point = sample_plot_point(s)
        if point is None:
            continue
        x, y, _ = point
        ax.plot([x], [y], marker="o", ms=9, color=series_colour(i),
                mec="black", mew=0.8, zorder=10,
                label=s.name or f"{t('chart_sample')} {i + 1}")
        drawn += 1
    if drawn:
        ncol = 2 if drawn > 6 else 1
        ax.legend(loc="upper left", fontsize=FONTS["legend"], ncol=ncol,
                  framealpha=0.92, edgecolor=COLORS["spine"])
    return bool(drawn)


def astm_plasticity_figure(sample: Optional[SoilSample] = None,
                           figsize=(8.6, 5.4),
                           extra_samples: Optional[Sequence[SoilSample]] = None
                           ) -> Figure:
    fig, ax = plt.subplots(figsize=figsize)
    apply_base_style(ax)
    ll_max, pi_max = 110, 70

    ll_a = np.linspace(_A_AT_PI4, ll_max, 200)
    ax.plot(ll_a, _a_line(ll_a), color=COLORS["ink"], lw=2.0, zorder=4)
    ax.plot([4, _A_AT_PI4], [4, 4], color=COLORS["ink"], lw=1.6, zorder=4)
    ax.plot([4, _A_AT_PI7], [7, 7], color=COLORS["ink"], lw=1.2, ls=":",
            zorder=4)
    _label_a_line(ax, 94)

    ll_u = np.linspace(8.0, (pi_max / 0.9) + 8, 200)
    ax.plot(ll_u, _u_line(ll_u), ls="--", color=COLORS["u_line"], lw=1.6,
            zorder=4)
    ax.text(60, _u_line(60) + 2, t("chart_u_line"), rotation=37,
            fontsize=FONTS["band_label"], color=COLORS["ink"])

    ax.axvline(50, color=COLORS["ink"], lw=1.2, ls="-.", zorder=3)
    ax.text(50.8, pi_max - 3, "LL = 50 %", fontsize=FONTS["band_label"],
            color=COLORS["ink"], va="top")

    labels = [
        (37, 24, "CL"),
        (72, 47, "CH"),
        (80, 20, f"MH  {t('chart_or')}  OH"),
        (37, 2.0, f"ML  {t('chart_or')}  OL"),
        (15.0, 5.0, "CL-ML"),
    ]
    for x, y, zone_label in labels:
        ax.text(x, y, zone_label, fontsize=FONTS["zone_label"], fontweight="bold",
                ha="center", color=COLORS["ink"])

    if extra_samples:
        _overlay_samples(ax, extra_samples)
    elif sample is not None:
        mark_sample_or_note(ax, sample)

    ax.set_xlim(0, ll_max)
    ax.set_ylim(0, pi_max)
    ax.set_xlabel(t("chart_xlabel_ll"))
    ax.set_ylabel(t("chart_ylabel_pi"))
    ax.set_title(t("chart_astm_title"),
                 fontsize=FONTS["title"], fontweight="bold")
    ax.grid(True, ls="-", lw=0.5, color=COLORS["grid"], zorder=1)
    fig.tight_layout()
    return fig


def bs_plasticity_figure(sample: Optional[SoilSample] = None,
                         figsize=(8.6, 5.4),
                         extra_samples: Optional[Sequence[SoilSample]] = None
                         ) -> Figure:
    fig, ax = plt.subplots(figsize=figsize)
    apply_base_style(ax)
    ll_max, pi_max = 120, 80

    ll_a = np.linspace(20, ll_max, 200)
    ax.plot(ll_a, _a_line(ll_a), color=COLORS["ink"], lw=2.0, zorder=4)
    _label_a_line(ax, 101)

    for x in (35, 50, 70, 90):
        ax.axvline(x, color=COLORS["ink"], lw=1.0, ls="-.", zorder=3)

    for x0, x1, tag in ((0, 35, "L\n" + t("bs_band_low")),
                        (35, 50, "I\n" + t("bs_band_intermediate")),
                        (50, 70, "H\n" + t("bs_band_high")),
                        (70, 90, "V\n" + t("bs_band_very_high")),
                        (90, 120, "E\n" + t("bs_band_extremely_high"))):
        ax.text((x0 + x1) / 2, pi_max - 2, tag, ha="center", va="top",
                fontsize=FONTS["band_label"], color=COLORS["ink"],
                fontweight="bold")

    for x, tag in ((27, "CL"), (42, "CI"), (60, "CH"), (80, "CV"),
                   (104, "CE")):
        ax.text(x, max(_a_line(x), 0) + 9, tag, fontsize=FONTS["zone_label"],
                fontweight="bold", ha="center", color=COLORS["ink"])
    for x, tag in ((27, "ML"), (42, "MI"), (60, "MH"), (80, "MV"),
                   (104, "ME")):
        y = max(_a_line(x), 4) - 7.5 if x > 30 else 2.5
        ax.text(x, y, tag, fontsize=FONTS["zone_label"], fontweight="bold",
                ha="center", color=COLORS["ink"])

    if extra_samples:
        _overlay_samples(ax, extra_samples)
    elif sample is not None:
        mark_sample_or_note(ax, sample)

    ax.set_xlim(0, ll_max)
    ax.set_ylim(0, pi_max)
    ax.set_xlabel(t("chart_xlabel_ll"))
    ax.set_ylabel(t("chart_ylabel_pi"))
    ax.set_title(t("chart_bs_title"),
                 fontsize=FONTS["title"], fontweight="bold")
    ax.grid(True, ls="-", lw=0.5, color=COLORS["grid"], zorder=1)
    fig.tight_layout()
    return fig


def astm_plasticity_multi_figure(samples: Sequence[SoilSample],
                                 figsize=(9.4, 6.0)) -> Figure:
    fig = astm_plasticity_figure(None, figsize=figsize,
                                 extra_samples=samples)
    fig.axes[0].set_title(
        f"{t('chart_astm_title')} \u2014 {t('chart_comparison_suffix')}",
        fontsize=FONTS["title"], fontweight="bold")
    return fig


def bs_plasticity_multi_figure(samples: Sequence[SoilSample],
                               figsize=(9.4, 6.0)) -> Figure:
    fig = bs_plasticity_figure(None, figsize=figsize, extra_samples=samples)
    fig.axes[0].set_title(
        f"{t('chart_bs_title')} \u2014 {t('chart_comparison_suffix')}",
        fontsize=FONTS["title"], fontweight="bold")
    return fig
