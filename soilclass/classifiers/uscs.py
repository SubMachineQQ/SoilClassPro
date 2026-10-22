from __future__ import annotations

from ..models import ASTM_SIZES, SoilSample
from .base import ClassificationResult, Classifier


class USCSClassifier(Classifier):
    system_name = "USCS (ASTM D2487)"

    def classify(self, sample: SoilSample) -> ClassificationResult:
        fr = sample.fractions(ASTM_SIZES)
        if fr is None:
            return self.insufficient(self.system_name,
                                     "Sieve data (incl. 0.075 mm) required.")
        notes = [f"Fines (< 0.075 mm) = {fr.fines:.1f} %, "
                 f"sand = {fr.sand:.1f} %, gravel = {fr.gravel:.1f} %"]

        if fr.fines >= 50.0:
            return self._fine_grained(sample, notes)
        return self._coarse_grained(sample, fr, notes)

    def _fines_symbol(self, sample: SoilSample, notes) -> str:
        ll, pi = sample.liquid_limit, sample.plasticity_index
        if ll is None or pi is None:
            notes.append("Atterberg limits missing; fines assumed silty (M).")
            return "ML"
        a = self.a_line(ll)
        if sample.organic:
            sym = "OL" if ll < 50 else "OH"
            notes.append(f"Organic soil, LL = {ll:.0f} -> {sym}")
            return sym
        if ll < 50:
            if pi > 7 and pi >= a:
                notes.append(f"LL < 50, PI = {pi:.1f} > 7 and above A-line "
                             f"(PI_A = {a:.1f}) -> CL")
                return "CL"
            if pi < 4 or pi < a:
                notes.append(f"LL < 50, PI = {pi:.1f} < 4 or below A-line -> ML")
                return "ML"
            notes.append(f"LL < 50, 4 <= PI = {pi:.1f} <= 7 and on/above "
                         "A-line -> CL-ML")
            return "CL-ML"
        if pi >= a:
            notes.append("LL >= 50, PI on/above A-line -> CH")
            return "CH"
        notes.append("LL >= 50, PI below A-line -> MH")
        return "MH"

    _FINE_NAMES = {
        "CL": "Lean clay", "ML": "Silt", "CH": "Fat clay",
        "MH": "Elastic silt", "CL-ML": "Silty clay",
        "OL": "Organic silt/clay (low plasticity)",
        "OH": "Organic silt/clay (high plasticity)",
    }

    def _fine_grained(self, sample: SoilSample, notes) -> ClassificationResult:
        sym = self._fines_symbol(sample, notes)
        name = self._FINE_NAMES.get(sym, "Fine-grained soil")
        fr = sample.fractions(ASTM_SIZES)
        coarse = fr.sand + fr.gravel
        if 15 <= coarse < 30:
            name += " with sand" if fr.sand >= fr.gravel else " with gravel"
        elif coarse >= 30:
            name = ("Sandy " if fr.sand >= fr.gravel else "Gravelly ") + name.lower()
        return ClassificationResult(self.system_name, sym, name, notes)

    def _coarse_grained(self, sample, fr, notes) -> ClassificationResult:
        gravel_soil = fr.gravel > fr.sand
        prefix = "G" if gravel_soil else "S"
        soil_word = "gravel" if gravel_soil else "sand"
        notes.append(f"{'Gravel' if gravel_soil else 'Sand'} fraction dominates "
                     f"the coarse portion -> '{prefix}' group")

        cu, cc = sample.cu, sample.cc
        cu_lim = 4.0 if gravel_soil else 6.0
        well = (cu is not None and cc is not None
                and cu >= cu_lim and 1.0 <= cc <= 3.0)
        grading_sym = prefix + ("W" if well else "P")
        if cu is not None and cc is not None:
            notes.append(f"Cu = {cu:.2f} (limit {cu_lim:g}), Cc = {cc:.2f} "
                         f"-> {'well' if well else 'poorly'} graded")
        else:
            notes.append("Cu/Cc not computable; assumed poorly graded.")

        if fr.fines < 5.0:
            name = f"{'Well' if well else 'Poorly'}-graded {soil_word}"
            name = self._with_second_coarse(name, fr, gravel_soil)
            return ClassificationResult(self.system_name, grading_sym, name, notes)

        fines_sym = self._fines_symbol(sample, notes)
        plast = {"CL": "C", "CH": "C", "ML": "M", "MH": "M",
                 "CL-ML": "C-M", "OL": "M", "OH": "M"}[fines_sym]

        if fr.fines > 12.0:
            if plast == "C-M":
                sym = f"{prefix}C-{prefix}M"
                name = f"Silty, clayey {soil_word}"
            else:
                sym = prefix + plast
                name = (f"{'Clayey' if plast == 'C' else 'Silty'} {soil_word}")
            name = self._with_second_coarse(name, fr, gravel_soil)
            notes.append(f"Fines > 12 % -> {sym}")
            return ClassificationResult(self.system_name, sym, name, notes)

        second = prefix + ("M" if plast in ("M", "C-M") else "C")
        sym = f"{grading_sym}-{second}"
        name = (f"{'Well' if well else 'Poorly'}-graded {soil_word} with "
                f"{'silt' if second.endswith('M') else 'clay'}")
        name = self._with_second_coarse(name, fr, gravel_soil)
        notes.append(f"Fines between 5 % and 12 % -> dual symbol {sym}")
        return ClassificationResult(self.system_name, sym, name, notes)

    @staticmethod
    def _with_second_coarse(name, fr, gravel_soil) -> str:
        other = fr.sand if gravel_soil else fr.gravel
        if other >= 15:
            name += " with sand" if gravel_soil else " with gravel"
        return name
