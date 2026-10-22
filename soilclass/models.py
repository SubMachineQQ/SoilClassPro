from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .curve import GsdCurve
from .i18n import t


@dataclass(frozen=True)
class SizeConvention:
    name: str
    gravel_sand: float
    sand_fines: float


ASTM_SIZES = SizeConvention("ASTM D2487", gravel_sand=4.75, sand_fines=0.075)
BS_SIZES = SizeConvention("BS 5930 / TS EN ISO 14688",
                          gravel_sand=2.0, sand_fines=0.063)
ISO14688_SIZES = SizeConvention("TS EN ISO 14688",
                                gravel_sand=2.0, sand_fines=0.063)


@dataclass
class FractionSummary:
    convention: SizeConvention
    gravel: float
    sand: float
    fines: float


@dataclass
class SoilSample:
    name: str = "Sample 1"
    sieve_data: List[Tuple[float, float]] = field(default_factory=list)
    liquid_limit: Optional[float] = None
    plastic_limit: Optional[float] = None
    organic: bool = False

    project: str = ""
    location: str = ""
    operator: str = ""
    date: str = ""

    e_max_gravel: Optional[float] = None
    e_min_gravel: Optional[float] = None
    e_max_sand: Optional[float] = None
    e_min_sand: Optional[float] = None

    roundness_gravel: Optional[float] = None
    cu_gravel: Optional[float] = None
    roundness_sand: Optional[float] = None
    cu_sand: Optional[float] = None

    ll_brine: Optional[float] = None
    ll_kerosene: Optional[float] = None

    _curve_cache: Optional[GsdCurve] = field(
        default=None, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        self.sieve_data = sorted(
            [(float(d), float(p)) for d, p in self.sieve_data if d > 0],
            key=lambda x: x[0],
        )

    @property
    def plasticity_index(self) -> Optional[float]:
        if self.liquid_limit is None or self.plastic_limit is None:
            return None
        pi = self.liquid_limit - self.plastic_limit
        return max(pi, 0.0)

    @property
    def has_sieve_data(self) -> bool:
        return len(self.sieve_data) >= 2

    def _curve(self) -> Optional[GsdCurve]:
        if not self.has_sieve_data:
            return None
        if self._curve_cache is None:
            self._curve_cache = GsdCurve(self.sieve_data)
        return self._curve_cache

    def percent_passing(self, size_mm: float) -> Optional[float]:
        curve = self._curve()
        return None if curve is None else curve.value_at(size_mm)

    def extended_curve(self, sizes) -> List[Optional[float]]:
        curve = self._curve()
        if curve is None:
            return [None] * len(sizes)
        d_min, d_max = 10 ** curve.x_min, 10 ** curve.x_max
        y_at_min, y_at_max = curve.value_at(d_min), curve.value_at(d_max)
        slope_lo = curve.slope_at_log_size(curve.x_min)
        slope_hi = curve.slope_at_log_size(curve.x_max)

        out = []
        for x in sizes:
            if x > d_max:
                y = y_at_max + slope_hi * (math.log10(x) - curve.x_max)
            elif x < d_min:
                y = y_at_min + slope_lo * (math.log10(x) - curve.x_min)
            else:
                y = curve.value_at(x)
            out.append(None if y is None else max(0.0, min(100.0, y)))
        return out

    def diameter_at_passing(self, percent: float) -> Optional[float]:
        curve = self._curve()
        return None if curve is None else curve.size_at(percent)

    @property
    def d10(self) -> Optional[float]:
        return self.diameter_at_passing(10)

    @property
    def d30(self) -> Optional[float]:
        return self.diameter_at_passing(30)

    @property
    def d60(self) -> Optional[float]:
        return self.diameter_at_passing(60)

    @property
    def cu(self) -> Optional[float]:
        if self.d10 and self.d60 and self.d10 > 0:
            return self.d60 / self.d10
        return None

    @property
    def cc(self) -> Optional[float]:
        if self.d10 and self.d30 and self.d60 and self.d10 * self.d60 > 0:
            return self.d30 ** 2 / (self.d10 * self.d60)
        return None

    def fractions(self, convention: SizeConvention) -> Optional[FractionSummary]:
        p_gs = self.percent_passing(convention.gravel_sand)
        p_sf = self.percent_passing(convention.sand_fines)
        if p_gs is None or p_sf is None:
            return None
        fines = max(0.0, min(100.0, p_sf))
        sand = max(0.0, p_gs - p_sf)
        gravel = max(0.0, 100.0 - p_gs)
        return FractionSummary(convention, gravel=gravel, sand=sand, fines=fines)

    @property
    def has_three_liquid_limits(self) -> bool:
        return (self.liquid_limit is not None
                and self.ll_brine is not None
                and self.ll_kerosene is not None)

    def summary_rows(self, conventions=None) -> List[Tuple[str, str]]:
        def fmt(v, nd=2, unit=""):
            return f"{v:.{nd}f}{unit}" if v is not None else "-"

        rows = [
            (t("res_liquid_limit"), fmt(self.liquid_limit, 1, " %")),
            (t("res_plastic_limit"), fmt(self.plastic_limit, 1, " %")),
            (t("res_plasticity_index"), fmt(self.plasticity_index, 1, " %")),
            (t("res_organic_soil"), t("res_yes") if self.organic else t("res_no")),
            ("D10", fmt(self.d10, 4, " mm")),
            ("D30", fmt(self.d30, 4, " mm")),
            ("D60", fmt(self.d60, 4, " mm")),
            ("Cu = D60/D10", fmt(self.cu)),
            ("Cc = D30\u00b2/(D10\u00b7D60)", fmt(self.cc)),
        ]
        for conv in (conventions or (ASTM_SIZES, BS_SIZES)):
            fr = self.fractions(conv)
            if fr:
                rows.append(
                    (
                        f"{t('res_gravel_sand_fines')} ({conv.name})",
                        f"{fr.gravel:.1f} / {fr.sand:.1f} / {fr.fines:.1f} %",
                    )
                )
        return rows


def conventions_for_systems(system_names) -> Tuple[SizeConvention, ...]:
    conv: List[SizeConvention] = []
    for name in system_names:
        if "BS" in name or "British" in name:
            c = BS_SIZES
        elif "ISO" in name:
            c = ISO14688_SIZES
        else:
            c = ASTM_SIZES
        if c not in conv:
            conv.append(c)
    if BS_SIZES in conv and ISO14688_SIZES in conv:
        conv.remove(ISO14688_SIZES)
    return tuple(conv) or (ASTM_SIZES, BS_SIZES)
