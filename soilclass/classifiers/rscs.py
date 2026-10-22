from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ..models import ASTM_SIZES, SoilSample
from .base import ClassificationResult, Classifier

EF10_MODE = "paper"
LAMBDA_MODE = "paper"

GS = 2.65
C_BRINE = 0.11688
G_KER = 0.78

ALPHA_GRAVEL_SAND = 2.5
ALPHA_COARSE_FINES = 1.3

DEFAULT_R = 0.35
DEFAULT_CU = 2.0
DEFAULT_LL = 25.0

SQ3_2 = math.sqrt(3.0) / 2.0


def emax_from_R_Cu(R: float, Cu: float) -> float:
    return 0.032 + 0.154 / R + 0.522 / Cu


def emin_from_R_Cu(R: float, Cu: float) -> float:
    return -0.012 + 0.082 / R + 0.371 / Cu


@dataclass
class Packing:
    e_max_gravel: float
    e_min_gravel: float
    e_max_sand: float
    e_min_sand: float
    source: str = ""


@dataclass
class FinesVoidRatios:
    e_ll: float
    e_10kpa: float
    e_1mpa: float
    lam: float
    e_flow: float


@dataclass
class RSCSThresholds:
    ff_low: float
    ff_high: float
    ff_flow: float


def to_xy(gravel: float, sand: float, fines: float) -> Tuple[float, float]:
    return sand + fines / 2.0, SQ3_2 * fines


CORNER_GRAVEL = to_xy(100.0, 0.0, 0.0)
CORNER_SAND = to_xy(0.0, 100.0, 0.0)
APEX_FINES = to_xy(0.0, 0.0, 100.0)

GROUP_POLYGONS: Dict[str, List] = {
    "G(G)":   ["Gc", 2, 11, 10],
    "GS(S)":  [2, 5, 12, 11],
    "S(S)":   [5, "Sc", 13, 12],
    "G(F)":   [10, 11, 3, 1],
    "GS(F)":  [11, 12, 6, 3],
    "S(F)":   [12, 13, 4, 6],
    "GF(F)":  [1, 3, 9, 7],
    "GSF(F)": [3, 6, 9],
    "SF(F)":  [6, 4, 8, 9],
    "F(F)":   [7, 9, 8, "Ap"],
}

GROUP_NAMES = {
    "G(G)":   "Gravel-controlled; gravel controls fluid flow",
    "GS(S)":  "Gravel and sand carry the load; sand controls fluid flow",
    "S(S)":   "Sand-controlled; sand controls fluid flow",
    "G(F)":   "Gravel carries the load; fines control fluid flow",
    "GS(F)":  "Gravel and sand carry the load; fines control fluid flow",
    "S(F)":   "Sand carries the load; fines control fluid flow",
    "GF(F)":  "Transitional: gravel and fines carry the load; fines control flow",
    "GSF(F)": "Transitional: all three fractions carry the load; fines control flow",
    "SF(F)":  "Transitional: sand and fines carry the load; fines control flow",
    "F(F)":   "Fines-controlled; fines control both load and fluid flow",
}

PLASTICITY_NAMES = {"N": "non-plastic", "L": "low plasticity",
                    "I": "intermediate plasticity", "H": "high plasticity"}
SENSITIVITY_NAMES = {"L": "low electrical sensitivity",
                     "I": "intermediate electrical sensitivity",
                     "H": "high electrical sensitivity"}


def _polygon_area(poly: List[Tuple[float, float]]) -> float:
    n = len(poly)
    return 0.5 * abs(sum(poly[i][0] * poly[(i + 1) % n][1]
                         - poly[(i + 1) % n][0] * poly[i][1]
                         for i in range(n)))


def _point_in_polygon(p: Tuple[float, float],
                      poly: List[Tuple[float, float]]) -> bool:
    x, y = p
    n = len(poly)
    inside = False
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        cross = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)
        if (abs(cross) < 1e-9
                and min(x1, x2) - 1e-9 <= x <= max(x1, x2) + 1e-9
                and min(y1, y2) - 1e-9 <= y <= max(y1, y2) + 1e-9):
            return True
        if (y1 > y) != (y2 > y):
            x_int = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < x_int:
                inside = not inside
    return inside


def _two_phase(e_host: float, e_guest: float) -> Tuple[float, float]:
    guest = 100.0 * e_host / (1.0 + e_host + e_guest)
    return 100.0 - guest, guest


def _three_phase(e_g: float, e_s: float, e_f: float) -> Tuple[float, float, float]:
    denom = (1.0 + e_g / (1.0 + e_s)
             + (e_g / (1.0 + e_f)) * (1.0 - 1.0 / (1.0 + e_s)))
    gravel = 100.0 / denom
    sand = 100.0 * (e_g / (1.0 + e_s)) / denom
    return gravel, sand, 100.0 - gravel - sand


class RSCSClassifier(Classifier):
    system_name = "RSCS (Park & Santamarina 2017)"

    @staticmethod
    def packing(sample: Optional[SoilSample] = None) -> Packing:
        notes = []

        def one(e_max, e_min, R, cu, label):
            if e_max is not None and e_min is not None:
                notes.append(f"{label}: measured e_max/e_min")
                return float(e_max), float(e_min)
            if R and cu:
                notes.append(f"{label}: e_max/e_min from R={R:g}, Cu={cu:g} "
                             "(Youd 1973; Cho et al. 2006)")
                return emax_from_R_Cu(R, cu), emin_from_R_Cu(R, cu)
            notes.append(f"{label}: no data - assumed R={DEFAULT_R}, "
                         f"Cu={DEFAULT_CU}")
            return (emax_from_R_Cu(DEFAULT_R, DEFAULT_CU),
                    emin_from_R_Cu(DEFAULT_R, DEFAULT_CU))

        s = sample
        e_max_g, e_min_g = one(
            getattr(s, "e_max_gravel", None), getattr(s, "e_min_gravel", None),
            getattr(s, "roundness_gravel", None), getattr(s, "cu_gravel", None),
            "Gravel")
        e_max_s, e_min_s = one(
            getattr(s, "e_max_sand", None), getattr(s, "e_min_sand", None),
            getattr(s, "roundness_sand", None), getattr(s, "cu_sand", None),
            "Sand")
        return Packing(e_max_g, e_min_g, e_max_s, e_min_s, "; ".join(notes))

    @staticmethod
    def fines_void_ratios(ll: float) -> FinesVoidRatios:
        e_ll = GS / 100.0 * ll
        if EF10_MODE == "excel":
            e_10 = 0.0265 * ll
        else:
            e_10 = 0.026 * ll + 0.07
        e_1m = 0.011 * ll + 0.21

        if LAMBDA_MODE == "excel":
            lam = 2.0 * math.log10(ll - 25.0) if ll > 27.0 else 1.0
        elif ll <= 25.0:
            lam = 1.0
        else:
            lam = max(2.0 * math.log10(ll - 25.0), 1.0)

        e_flow = lam * e_ll
        e_flow = max(e_flow, e_10)
        return FinesVoidRatios(e_ll, e_10, e_1m, lam, e_flow)

    def notable_mixtures(self, pk: Packing, fv: FinesVoidRatios
                         ) -> Dict[int, Tuple[float, float, float]]:
        a_gs = ALPHA_GRAVEL_SAND
        a_cf = ALPHA_COARSE_FINES
        m: Dict[int, Tuple[float, float, float]] = {}

        g, f = _two_phase(pk.e_min_gravel, fv.e_10kpa)
        m[1] = (g, 0.0, f)
        g, s = _two_phase(pk.e_min_gravel, pk.e_max_sand)
        m[2] = (g, s, 0.0)
        m[3] = _three_phase(pk.e_min_gravel, pk.e_max_sand, fv.e_10kpa)

        s, f = _two_phase(pk.e_min_sand, fv.e_10kpa)
        m[4] = (0.0, s, f)
        g, s = _two_phase(a_gs * pk.e_max_gravel, pk.e_min_sand)
        m[5] = (g, s, 0.0)
        m[6] = _three_phase(a_gs * pk.e_max_gravel, pk.e_min_sand, fv.e_10kpa)

        g, f = _two_phase(a_cf * pk.e_max_gravel, fv.e_1mpa)
        m[7] = (g, 0.0, f)
        s, f = _two_phase(a_cf * pk.e_max_sand, fv.e_1mpa)
        m[8] = (0.0, s, f)
        m[9] = _three_phase(a_gs * pk.e_max_gravel, a_cf * pk.e_max_sand,
                            fv.e_1mpa)

        g, f = _two_phase(pk.e_min_gravel, fv.e_flow)
        m[10] = (g, 0.0, f)
        m[11] = _three_phase(pk.e_min_gravel, pk.e_max_sand, fv.e_flow)
        m[12] = _three_phase(a_gs * pk.e_max_gravel, pk.e_min_sand, fv.e_flow)
        s, f = _two_phase(pk.e_min_sand, fv.e_flow)
        m[13] = (0.0, s, f)
        return m

    def polygon(self, name: str, mixtures) -> List[Tuple[float, float]]:
        out = []
        for key in GROUP_POLYGONS[name]:
            if key == "Gc":
                out.append(CORNER_GRAVEL)
            elif key == "Sc":
                out.append(CORNER_SAND)
            elif key == "Ap":
                out.append(APEX_FINES)
            else:
                out.append(to_xy(*mixtures[key]))
        return out

    def thresholds(self, ll: float, e_max: Optional[float] = None,
                   e_min: Optional[float] = None) -> RSCSThresholds:
        if e_max is None:
            e_max = emax_from_R_Cu(DEFAULT_R, DEFAULT_CU)
        if e_min is None:
            e_min = emin_from_R_Cu(DEFAULT_R, DEFAULT_CU)
        fv = self.fines_void_ratios(ll)
        _, ff_low = _two_phase(e_min, fv.e_10kpa)
        _, ff_high = _two_phase(ALPHA_COARSE_FINES * e_max, fv.e_1mpa)
        _, ff_flow = _two_phase(e_min, fv.e_flow)
        return RSCSThresholds(ff_low / 100.0, ff_high / 100.0,
                              ff_flow / 100.0)

    @staticmethod
    def fines_classification(ll_dw: float, ll_brine: float,
                             ll_ker: float) -> Dict[str, object]:
        salt = 1.0 - C_BRINE * ll_brine / 100.0
        r_ker = (ll_ker / ll_brine) * (salt / G_KER)
        r_dw = (ll_dw / ll_brine) * salt
        b = r_ker if r_ker >= 1.0 else 1.0 / r_ker
        c = r_dw if r_dw >= 1.0 else 1.0 / r_dw
        se = math.hypot(b - 1.0, c - 1.0)
        ll_b = ll_brine / salt

        plasticity = ("H" if ll_b > 75 else "I" if ll_b > 50
                      else "L" if ll_b > 30 else "N")
        sensitivity = "H" if se > 1.0 else "I" if se > 0.4 else "L"
        return {"SE": se, "LL_brine_corrected": ll_b,
                "ratio_ker": r_ker, "ratio_dw": r_dw,
                "plasticity": plasticity, "sensitivity": sensitivity,
                "symbol": plasticity + sensitivity}

    def classify(self, sample: SoilSample) -> ClassificationResult:
        if not getattr(sample, "rscs_enabled", True):
            return self.insufficient(self.system_name,
                                     "RSCS classification was not selected.")
        fr = sample.fractions(ASTM_SIZES)
        if fr is None:
            return self.insufficient(self.system_name,
                                     "Sieve analysis is required.")

        notes: List[str] = []

        if sample.liquid_limit is None:
            ll = DEFAULT_LL
            notes.append(f"Liquid limit not measured; LL = {DEFAULT_LL:g} "
                         "assumed (non-plastic fines).")
        else:
            ll = float(sample.liquid_limit)
            notes.append(f"Liquid limit of the fines, LL = {ll:.1f} %.")

        pk = self.packing(sample)
        notes.append(pk.source)
        notes.append(f"Packing: gravel e_max = {pk.e_max_gravel:.3f}, "
                     f"e_min = {pk.e_min_gravel:.3f}; sand "
                     f"e_max = {pk.e_max_sand:.3f}, e_min = {pk.e_min_sand:.3f}.")

        fv = self.fines_void_ratios(ll)
        notes.append(f"Fines void ratios: e_F|LL = {fv.e_ll:.3f}, "
                     f"e_F|10kPa = {fv.e_10kpa:.3f}, "
                     f"e_F|1MPa = {fv.e_1mpa:.3f}.")
        notes.append(f"Flow parameter lambda = 2 log(LL - 25) = {fv.lam:.2f}; "
                     f"e_F|flow = {fv.e_flow:.3f}.")
        if fv.lam <= 1.0 + 1e-9:
            notes.append("lambda = 1: the flow boundary coincides with the "
                         "mechanical boundary, so the G(F), GS(F) and S(F) "
                         "groups do not exist for these fines.")

        mixtures = self.notable_mixtures(pk, fv)
        gravel, sand, fines = fr.gravel, fr.sand, fr.fines
        notes.append(f"Fractions (sieves #4 / #200): gravel = {gravel:.1f} %, "
                     f"sand = {sand:.1f} %, fines = {fines:.1f} %.")

        point = to_xy(gravel, sand, fines)
        hits = []
        for name in GROUP_POLYGONS:
            poly = self.polygon(name, mixtures)
            if _polygon_area(poly) < 1e-6:
                continue
            if _point_in_polygon(point, poly):
                hits.append(name)

        if not hits:
            return self.insufficient(
                self.system_name,
                "The sample does not fall inside any RSCS group - check that "
                "the gravel, sand and fines fractions sum to 100 %.")

        symbol = hits[0]
        if len(hits) > 1:
            notes.append("The sample lies on a boundary between "
                         + " and ".join(hits) + f"; reported as {symbol}.")

        mech, flow = symbol.split("(")
        flow = flow.rstrip(")")
        extras = {
            "Mechanical control": mech,
            "Fluid flow control": flow,
            "lambda": f"{fv.lam:.2f}",
        }

        name = GROUP_NAMES[symbol]
        if "F" in symbol and sample.has_three_liquid_limits:
            fc = self.fines_classification(float(sample.liquid_limit),
                                           float(sample.ll_brine),
                                           float(sample.ll_kerosene))
            symbol = f"{symbol}-{fc['symbol']}"
            extras["Electrical sensitivity, SE"] = f"{fc['SE']:.3f}"
            extras["LL_brine (corrected)"] = f"{fc['LL_brine_corrected']:.1f} %"
            extras["Fines group"] = str(fc["symbol"])
            notes.append(
                f"Fines: LL_dw = {sample.liquid_limit:.1f}, "
                f"LL_brine = {sample.ll_brine:.1f}, "
                f"LL_ker = {sample.ll_kerosene:.1f} -> SE = {fc['SE']:.3f}, "
                f"corrected LL_brine = {fc['LL_brine_corrected']:.1f} "
                f"-> {fc['symbol']} "
                f"({PLASTICITY_NAMES[str(fc['plasticity'])]}, "
                f"{SENSITIVITY_NAMES[str(fc['sensitivity'])]}).")
            name += (f"; fines are of "
                     f"{PLASTICITY_NAMES[str(fc['plasticity'])]} with "
                     f"{SENSITIVITY_NAMES[str(fc['sensitivity'])]}")
        elif "F" in symbol:
            notes.append("Supply LL with 2-M brine and with kerosene to also "
                         "classify the fines by plasticity and electrical "
                         "sensitivity (Jang & Santamarina 2016).")

        return ClassificationResult(self.system_name, symbol, name, notes,
                                    extras)
