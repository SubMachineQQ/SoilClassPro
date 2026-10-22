from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from ..i18n import t
from ..models import SoilSample
from .plasticity import (_A_AT_PI4, _A_AT_PI7, _a_line, _label_a_line,
                         _overlay_samples)
from .style import COLORS, FONTS, apply_base_style, mark_sample_or_note


def iso14688_plasticity_figure(sample: Optional[SoilSample] = None,
                               figsize=(8.6, 5.4),
                               extra_samples: Optional[Sequence[SoilSample]] = None
                               ) -> Figure:
    fig, ax = plt.subplots(figsize=figsize)
    apply_base_style(ax)
    ll_max, pi_max = 110, 80

    ll_a = np.linspace(_A_AT_PI4, ll_max, 200)
    ax.plot(ll_a, _a_line(ll_a), color=COLORS["ink"], lw=2.0, zorder=4)
    ax.plot([4, _A_AT_PI4], [4, 4], color=COLORS["ink"], lw=1.6, zorder=4)
    ax.plot([4, _A_AT_PI7], [7, 7], color=COLORS["ink"], lw=1.2, ls=":",
            zorder=4)
    _label_a_line(ax, 94)

    for x in (35, 50, 70):
        ax.axvline(x, color=COLORS["ink"], lw=1.0, ls="-.", zorder=3)
    for x0, x1, tag in ((0, 35, "L\n" + t("iso_band_low")),
                        (35, 50, "M\n" + t("iso_band_medium")),
                        (50, 70, "H\n" + t("iso_band_high")),
                        (70, ll_max, "V\n" + t("iso_band_very_high"))):
        ax.text((x0 + x1) / 2, pi_max - 2, tag, ha="center", va="top",
                fontsize=FONTS["band_label"], color=COLORS["ink"],
                fontweight="bold")

    zones = [
        (21, 17, "ClL"), (42.5, 27, "ClM"), (58, 41, "ClH"), (88, 62, "ClV"),
        (27, 1.6, "SiL"), (42.5, 5.5, "SiM"), (60, 14, "SiH"), (90, 27, "SiV"),
    ]
    for x, y, label in zones:
        ax.text(x, y, label, fontsize=FONTS["zone_label"], fontweight="bold",
                ha="center", color=COLORS["ink"])
    ax.text(15.0, 5.5, "ClL-SiL", fontsize=FONTS["note"] - 1,
            fontweight="bold", ha="center", va="center",
            color=COLORS["ink"], zorder=5,
            bbox=dict(boxstyle="square,pad=0.05", fc="white", ec="none"))

    if extra_samples:
        _overlay_samples(ax, extra_samples)
    elif sample is not None:
        mark_sample_or_note(ax, sample)

    ax.set_xlim(0, ll_max)
    ax.set_ylim(0, pi_max)
    ax.set_xlabel(t("chart_xlabel_ll"))
    ax.set_ylabel(t("chart_ylabel_pi"))
    ax.set_title(t("chart_iso14688_title"),
                 fontsize=FONTS["title"], fontweight="bold")
    ax.grid(True, ls="-", lw=0.5, color=COLORS["grid"], zorder=1)
    fig.tight_layout()
    return fig


def iso14688_plasticity_multi_figure(samples: Sequence[SoilSample],
                                     figsize=(9.4, 6.0)) -> Figure:
    fig = iso14688_plasticity_figure(None, figsize=figsize,
                                     extra_samples=samples)
    fig.axes[0].set_title(
        f"{t('chart_iso14688_title')} — {t('chart_comparison_suffix')}",
        fontsize=FONTS["title"], fontweight="bold")
    return fig
