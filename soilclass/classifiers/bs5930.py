from __future__ import annotations

from ..models import BS_SIZES, SoilSample
from .base import ClassificationResult, Classifier


class BS5930Classifier(Classifier):
    system_name = "British Standard (BS 5930)"

    _RANGES = [
        (35.0, "L", "low plasticity"),
        (50.0, "I", "intermediate plasticity"),
        (70.0, "H", "high plasticity"),
        (90.0, "V", "very high plasticity"),
        (float("inf"), "E", "extremely high plasticity"),
    ]

    def classify(self, sample: SoilSample) -> ClassificationResult:
        fr = sample.fractions(BS_SIZES)
        if fr is None:
            return self.insufficient(self.system_name,
                                     "Sieve data (incl. 0.063 mm) required.")
        notes = [f"Fines (< 0.063 mm) = {fr.fines:.1f} %, "
                 f"sand = {fr.sand:.1f} %, gravel = {fr.gravel:.1f} %"]

        if fr.fines >= 35.0:
            return self._fine(sample, fr, notes)
        return self._coarse(sample, fr, notes)

    def _plasticity_suffix(self, ll: float):
        for upper, suffix, word in self._RANGES:
            if ll < upper:
                return suffix, word
        return "E", "extremely high plasticity"

    def _fine(self, sample, fr, notes) -> ClassificationResult:
        ll, pi = sample.liquid_limit, sample.plasticity_index
        if ll is None or pi is None:
            return self.insufficient(self.system_name,
                                     "Atterberg limits required for fine soil.")
        suffix, word = self._plasticity_suffix(ll)
        a = self.a_line(ll)
        clay = pi >= a and pi > 0
        letter = "C" if clay else "M"
        if sample.organic:
            sym = f"{letter}{suffix}O"
            base = f"Organic {'clay' if clay else 'silt'} of {word}"
            notes.append("Organic soil -> suffix 'O'.")
        else:
            sym = f"{letter}{suffix}"
            base = f"{'Clay' if clay else 'Silt'} of {word}"
        notes.append(f"LL = {ll:.1f}, PI = {pi:.1f}, A-line PI = {a:.1f} "
                     f"-> {'clay (C)' if clay else 'silt (M)'}, range '{suffix}'")

        coarse = fr.sand + fr.gravel
        name = base
        if coarse >= 35.0:
            lead = "Sandy" if fr.sand >= fr.gravel else "Gravelly"
            sym = ("S" if fr.sand >= fr.gravel else "G") + sym
            name = f"{lead} {base.lower()}"
            notes.append(f"Coarse fraction {coarse:.1f} % >= 35 % -> "
                         f"'{lead.lower()}' qualifier")
        return ClassificationResult(self.system_name, sym, name, notes)

    def _coarse(self, sample, fr, notes) -> ClassificationResult:
        gravel_soil = fr.gravel > fr.sand
        prefix = "G" if gravel_soil else "S"
        soil_word = "GRAVEL" if gravel_soil else "SAND"
        notes.append(f"{soil_word.capitalize()} dominates the coarse fraction.")

        cu, cc = sample.cu, sample.cc
        cu_lim = 4.0 if gravel_soil else 6.0
        well = (cu is not None and cc is not None
                and cu >= cu_lim and 1.0 <= cc <= 3.0)
        uniform = cu is not None and cu <= 3.0

        fines_letter, fines_word = self._fines_nature(sample, notes)

        if fr.fines < 5.0:
            if well:
                sym, grading = prefix + "W", "Well graded"
            elif uniform:
                sym, grading = prefix + "Pu", "Uniformly graded"
            else:
                sym, grading = prefix + "P", "Poorly graded"
            if cu is not None:
                notes.append(f"Cu = {cu:.2f} (limit {cu_lim:g}), Cc = "
                             f"{cc:.2f} -> {grading.lower()}")
            name = f"{grading} {soil_word.lower()}"
            return ClassificationResult(self.system_name, sym, name, notes)

        if fr.fines <= 15.0:
            sym = f"{prefix}-{fines_letter}"
            name = f"Slightly {fines_word} {soil_word.lower()}"
            notes.append("Fines 5-15 % -> 'slightly silty/clayey'.")
        else:
            sym = f"{prefix}{fines_letter}"
            name = f"Very {fines_word} {soil_word.lower()}"
            notes.append("Fines 15-35 % -> 'very silty/clayey'.")

        if sample.liquid_limit is not None and sample.plasticity_index:
            suffix, _ = self._plasticity_suffix(sample.liquid_limit)
            sym += suffix
        return ClassificationResult(self.system_name, sym, name, notes)

    def _fines_nature(self, sample, notes):
        ll, pi = sample.liquid_limit, sample.plasticity_index
        if ll is None or pi is None or pi <= 0:
            notes.append("Fines assumed silty (no/low plasticity data).")
            return "M", "silty"
        if pi >= self.a_line(ll):
            return "C", "clayey"
        return "M", "silty"
