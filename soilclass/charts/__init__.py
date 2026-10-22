from .gsd import gsd_figure
from .plasticity import astm_plasticity_figure, bs_plasticity_figure
from .iso14688_chart import iso14688_plasticity_figure
from .aashto_chart import aashto_figure
from .rscs_chart import rscs_figure
from .rscs_fines import (rscs_fines_ratio_figure,
                         rscs_fines_sensitivity_figure)

ALL_FIGURES = [
    ("Grain Size Distribution", gsd_figure),
    ("Plasticity Chart (ASTM)", astm_plasticity_figure),
    ("Plasticity Chart (BS 5930)", bs_plasticity_figure),
    ("Plasticity Chart (TS EN ISO 14688)", iso14688_plasticity_figure),
    ("AASHTO LL-PI Chart", aashto_figure),
    ("RSCS Ternary Chart", rscs_figure),
    ("RSCS Fines - LL Ratio Plane", rscs_fines_ratio_figure),
    ("RSCS Fines - Plasticity vs Sensitivity", rscs_fines_sensitivity_figure),
]

_PLASTICITY_BUILDERS = {astm_plasticity_figure, bs_plasticity_figure,
                        iso14688_plasticity_figure, aashto_figure}

_RSCS_FINES_BUILDERS = {rscs_fines_ratio_figure, rscs_fines_sensitivity_figure}

_RSCS_BUILDERS = _RSCS_FINES_BUILDERS | {rscs_figure}


def classifiable_chart_defs(chart_defs, sample):
    out = []
    for label, builder in chart_defs:
        if builder in _PLASTICITY_BUILDERS and sample.liquid_limit is None:
            continue
        if builder in _RSCS_BUILDERS and not getattr(sample, "rscs_enabled", True):
            continue
        if builder in _RSCS_FINES_BUILDERS and not sample.has_three_liquid_limits:
            continue
        out.append((label, builder))
    return out


__all__ = ["gsd_figure", "astm_plasticity_figure", "bs_plasticity_figure",
           "iso14688_plasticity_figure", "aashto_figure",
           "rscs_figure", "rscs_fines_ratio_figure",
           "rscs_fines_sensitivity_figure", "ALL_FIGURES",
           "classifiable_chart_defs"]
