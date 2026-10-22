from __future__ import annotations

from ..charts import (aashto_figure, astm_plasticity_figure,
                      bs_plasticity_figure, gsd_figure,
                      iso14688_plasticity_figure, rscs_figure,
                      rscs_fines_ratio_figure,
                      rscs_fines_sensitivity_figure)
from ..classifiers import (AASHTOClassifier, BS5930Classifier,
                           ISO14688Classifier, RSCSClassifier,
                           USCSClassifier)
from collections.abc import Mapping

from ..i18n import t


class _Key(str):
    pass


def _resolve(value):
    return t(value) if isinstance(value, _Key) else value


class _TitleMap(Mapping):
    def __init__(self, spec):
        self._spec = spec

    def __getitem__(self, mode):
        return _resolve(self._spec[mode])

    def __iter__(self):
        return iter(self._spec)

    def __len__(self):
        return len(self._spec)


class _ChartMap(Mapping):
    def __init__(self, spec):
        self._spec = spec

    def __getitem__(self, mode):
        return [(_resolve(label), builder) for label, builder in self._spec[mode]]

    def __iter__(self):
        return iter(self._spec)

    def __len__(self):
        return len(self._spec)

MODE_TITLE = _TitleMap({
    "ALL": _Key("launcher_all_standards"),
    "ASTM": "USCS (ASTM D2487)",
    "BS": _Key("mode_bs"),
    "ISO14688": "TS EN ISO 14688",
    "AASHTO": "AASHTO (M 145)",
    "RSCS": "RSCS (Park & Santamarina 2017)",
})

MODE_CLASSIFIERS = {
    "ALL": [USCSClassifier, BS5930Classifier, ISO14688Classifier,
            RSCSClassifier, AASHTOClassifier],
    "ASTM": [USCSClassifier],
    "BS": [BS5930Classifier],
    "ISO14688": [ISO14688Classifier],
    "AASHTO": [AASHTOClassifier],
    "RSCS": [RSCSClassifier],
}

MODE_CHARTS = _ChartMap({
    "ALL": [
        (_Key("chart_tab_grain_size"), gsd_figure),
        (_Key("chart_tab_plasticity_astm"), astm_plasticity_figure),
        (_Key("chart_tab_plasticity_bs"), bs_plasticity_figure),
        (_Key("chart_tab_plasticity_iso14688"), iso14688_plasticity_figure),
        (_Key("chart_tab_aashto"), aashto_figure),
        (_Key("chart_tab_rscs_ternary"), rscs_figure),
        (_Key("chart_tab_rscs_fines_a"), rscs_fines_ratio_figure),
        (_Key("chart_tab_rscs_fines_b"), rscs_fines_sensitivity_figure),
    ],
    "ASTM": [
        (_Key("chart_tab_grain_size"), gsd_figure),
        (_Key("chart_tab_plasticity_astm"), astm_plasticity_figure),
    ],
    "BS": [
        (_Key("chart_tab_grain_size"), gsd_figure),
        (_Key("chart_tab_plasticity_bs"), bs_plasticity_figure),
    ],
    "RSCS": [
        (_Key("chart_tab_grain_size"), gsd_figure),
        (_Key("chart_tab_rscs_ternary"), rscs_figure),
        (_Key("chart_tab_rscs_fines_a"), rscs_fines_ratio_figure),
        (_Key("chart_tab_rscs_fines_b"), rscs_fines_sensitivity_figure),
    ],
    "ISO14688": [
        (_Key("chart_tab_grain_size"), gsd_figure),
        (_Key("chart_tab_plasticity_iso14688"), iso14688_plasticity_figure),
    ],
    "AASHTO": [
        (_Key("chart_tab_grain_size"), gsd_figure),
        (_Key("chart_tab_aashto"), aashto_figure),
    ],
})

VALID_MODES = tuple(MODE_TITLE.keys())
