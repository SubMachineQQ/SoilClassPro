import matplotlib

from ..colors import CHART as COLORS
from .declutter import AROUND_POINT, keep_clear, movable, wrap_label
from ..i18n import t

__all__ = ["COLORS", "FONTS", "apply_base_style", "mark_sample",
          "sample_plot_point", "mark_sample_or_note", "series_colour"]

FONTS = {
    "title": 15,
    "axis_label": 13,
    "tick": 12,
    "legend": 11,
    "annotation": 11,
    "zone_label": 12,
    "band_label": 11,
    "note": 10,
}

matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans"]
matplotlib.rcParams["mathtext.fontset"] = "dejavusans"

_SERIES_KEYS = [f"series_{i}" for i in range(1, 11)]


def series_colour(index: int) -> str:
    return COLORS[_SERIES_KEYS[index % len(_SERIES_KEYS)]]


def apply_base_style(ax) -> None:
    ax.set_facecolor(COLORS["axes_face"])
    for spine in ax.spines.values():
        spine.set_color(COLORS["spine"])
        spine.set_linewidth(1.1)
    ax.tick_params(colors=COLORS["tick"], labelsize=FONTS["tick"], pad=6,
                   which="both")
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_color(COLORS["tick"])
    ax.xaxis.label.set_color(COLORS["ink"])
    ax.yaxis.label.set_color(COLORS["ink"])
    ax.xaxis.label.set_fontsize(FONTS["axis_label"])
    ax.yaxis.label.set_fontsize(FONTS["axis_label"])
    ax.title.set_color(COLORS["ink"])
    ax.title.set_fontsize(FONTS["title"])


def sample_plot_point(sample):
    if sample.liquid_limit is None:
        return None
    ll = sample.liquid_limit
    if sample.plasticity_index is not None:
        pi = sample.plasticity_index
        lines = [sample.name, f"LL={ll:.0f}, PI={pi:.0f}"]
    else:
        pi = 0.0
        lines = [sample.name, f"LL={ll:.0f}, non-plastic (NP)"]
    return ll, pi, lines


def mark_sample_or_note(ax, sample) -> None:
    point = sample_plot_point(sample)
    if point is not None:
        mark_sample(ax, *point)
        return
    ax.text(0.02, 0.02,
            f"{sample.name}: {t('chart_non_plastic_note')}",
            transform=ax.transAxes, fontsize=FONTS["note"], style="italic",
            color=COLORS["no_data_fg"], ha="left", va="bottom",
            bbox=dict(boxstyle="round,pad=0.35", fc=COLORS["no_data_bg"],
                      ec=COLORS["spine"], lw=0.8))


def mark_sample(ax, x, y, lines) -> None:
    if isinstance(lines, str):
        lines = [lines]
    ax.plot([x], [y], marker="*", ms=19, color=COLORS["sample"],
            mec="white", mew=1.2, zorder=10)
    keep_clear(ax, x, y, 9.0)
    label = ax.annotate("\n".join([wrap_label(lines[0])] + list(lines[1:])),
                        (x, y), textcoords="offset points",
                        xytext=(11, 9), fontsize=FONTS["annotation"],
                        fontweight="bold", color=COLORS["sample"], zorder=11,
                        linespacing=1.35, multialignment="left",
                        arrowprops=dict(arrowstyle="-", color=COLORS["sample"],
                                        lw=0.9, shrinkA=0, shrinkB=8),
                        bbox=dict(boxstyle="round,pad=0.32", fc="white",
                                  ec=COLORS["sample"], alpha=0.92, lw=0.9))
    movable(label, AROUND_POINT, priority=0)
