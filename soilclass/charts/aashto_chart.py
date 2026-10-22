from __future__ import annotations

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from ..i18n import t
from .style import COLORS, FONTS, apply_base_style, mark_sample_or_note


def aashto_figure(sample=None, figsize=(8.6, 5.4),
                  extra_samples=None) -> Figure:
    fig, ax = plt.subplots(figsize=figsize)
    apply_base_style(ax)
    ll_max, pi_max = 100, 70


    ll = np.linspace(40, ll_max, 100)
    ax.plot(ll, ll - 30, color=COLORS["ink"], lw=1.6, ls="--", zorder=4)
    ax.text(88, 88 - 30 + 1.5, "PI = LL − 30", rotation=38,
            fontsize=FONTS["band_label"], color=COLORS["ink"])

    ax.axhline(10, color=COLORS["ink"], lw=1.8, zorder=4)
    ax.axvline(40, color=COLORS["ink"], lw=1.8, zorder=4)

    _and = t("chart_aashto_and")
    for x, y, zone_label in ((20, 5, f"A-4\n({_and} A-2-4)"),
                             (68, 5, f"A-5\n({_and} A-2-5)"),
                             (20, 38, f"A-6\n({_and} A-2-6)"),
                             (85, 40, "A-7-5\n(A-2-7)"),
                    (62, 55, "A-7-6")):
        ax.text(x, y, zone_label, ha="center", fontsize=FONTS["zone_label"],
                fontweight="bold", color=COLORS["ink"])

    if extra_samples:
        from .plasticity import _overlay_samples
        _overlay_samples(ax, extra_samples)
    elif sample is not None:
        mark_sample_or_note(ax, sample)

    ax.set_xlim(0, ll_max)
    ax.set_ylim(0, pi_max)
    ax.set_xlabel(t("chart_xlabel_ll"))
    ax.set_ylabel(t("chart_ylabel_pi"))
    ax.set_title(t("chart_aashto_title"),
                 fontsize=FONTS["title"], fontweight="bold")
    ax.grid(True, ls="-", lw=0.5, color=COLORS["grid"])
    fig.tight_layout()
    return fig
