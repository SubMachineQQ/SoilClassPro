from __future__ import annotations

from ..models import SoilSample
from .base import ClassificationResult, Classifier


class AASHTOClassifier(Classifier):
    system_name = "AASHTO (M 145)"

    _RATINGS = {
        "A-1": "Excellent to good subgrade (stone fragments, gravel, sand)",
        "A-3": "Excellent to good subgrade (fine sand)",
        "A-2": "Excellent to good subgrade (silty or clayey gravel and sand)",
        "A-4": "Fair to poor subgrade (silty soil)",
        "A-5": "Fair to poor subgrade (silty soil)",
        "A-6": "Fair to poor subgrade (clayey soil)",
        "A-7": "Fair to poor subgrade (clayey soil)",
    }

    def classify(self, sample: SoilSample) -> ClassificationResult:
        p10 = sample.percent_passing(2.0)
        p40 = sample.percent_passing(0.425)
        p200 = sample.percent_passing(0.075)
        if p200 is None:
            return self.insufficient(self.system_name,
                                     "Sieve data (incl. 0.075 mm) required.")
        ll = sample.liquid_limit
        pi = sample.plasticity_index
        np_soil = pi is None or pi <= 0
        notes = [f"P(No.10) = {self._f(p10)} %, P(No.40) = {self._f(p40)} %, "
                 f"P(No.200) = {p200:.1f} %",
                 f"LL = {self._f(ll)}, PI = "
                 f"{'NP' if np_soil else f'{pi:.1f}'}"]

        if p200 <= 35.0:
            sym = self._granular(p10, p40, p200, ll, pi, np_soil, notes)
        else:
            sym = self._silt_clay(ll, pi, notes)

        gi = self._group_index(sym, p200, ll, pi)
        full = f"{sym} ({gi})"
        family = sym.split("-")[0] + "-" + sym.split("-")[1][0]
        name = self._RATINGS.get(family, "")
        notes.append(f"Group Index GI = {gi}")
        return ClassificationResult(self.system_name, full, name, notes,
                                    extras={"Group Index": str(gi)})

    def _granular(self, p10, p40, p200, ll, pi, np_soil, notes) -> str:
        pi_v = 0.0 if np_soil else pi
        if (p10 is not None and p40 is not None and
                p10 <= 50 and p40 <= 30 and p200 <= 15 and pi_v <= 6):
            notes.append("Meets A-1-a limits.")
            return "A-1-a"
        if p40 is not None and p40 <= 50 and p200 <= 25 and pi_v <= 6:
            notes.append("Meets A-1-b limits.")
            return "A-1-b"
        if p40 is not None and p40 > 50 and p200 <= 10 and np_soil:
            notes.append("Non-plastic fine sand -> A-3.")
            return "A-3"
        ll_v = ll if ll is not None else 0.0
        if pi_v <= 10:
            sub = "A-2-4" if ll_v <= 40 else "A-2-5"
        else:
            sub = "A-2-6" if ll_v <= 40 else "A-2-7"
        notes.append(f"Granular with plastic fines -> {sub}.")
        return sub

    def _silt_clay(self, ll, pi, notes) -> str:
        if ll is None or pi is None:
            notes.append("Atterberg limits missing; assumed A-4.")
            return "A-4"
        if pi <= 10:
            sym = "A-4" if ll <= 40 else "A-5"
        else:
            if ll <= 40:
                sym = "A-6"
            else:
                sym = "A-7-5" if pi <= ll - 30 else "A-7-6"
                notes.append(f"PI {'<=' if sym == 'A-7-5' else '>'} LL - 30 "
                             f"-> {sym}")
        notes.append(f"Silt-clay material -> {sym}.")
        return sym

    @staticmethod
    def _group_index(sym: str, f200: float, ll, pi) -> int:
        if sym.startswith(("A-1", "A-3")) or sym in ("A-2-4", "A-2-5"):
            return 0
        ll_v = ll if ll is not None else 0.0
        pi_v = pi if pi is not None else 0.0
        a = min(max(f200 - 35.0, 0.0), 40.0)
        b = min(max(f200 - 15.0, 0.0), 40.0)
        c = min(max(ll_v - 40.0, 0.0), 20.0)
        d = min(max(pi_v - 10.0, 0.0), 20.0)
        if sym in ("A-2-6", "A-2-7"):
            gi = 0.01 * b * d
        else:
            gi = a * (0.2 + 0.005 * c) + 0.01 * b * d
        return max(0, round(gi))

    @staticmethod
    def _f(v):
        return f"{v:.1f}" if v is not None else "-"
