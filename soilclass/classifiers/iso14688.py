from __future__ import annotations

from typing import Optional, Tuple

from ..models import ISO14688_SIZES, SoilSample
from .base import ClassificationResult, Classifier

_PLASTICITY = [
    (35.0, "L", "low plasticity"),
    (50.0, "M", "medium plasticity"),
    (70.0, "H", "high plasticity"),
    (float("inf"), "V", "very high plasticity"),
]

_GRADING_WORD = {
    "W": "well graded", "M": "medium graded", "P": "poorly graded",
    "U": "uniformly graded", "G": "gap graded",
}


def plasticity_class(ll: float) -> Tuple[str, str]:
    for upper, letter, word in _PLASTICITY:
        if ll < upper:
            return letter, word
    return "V", "very high plasticity"


def fine_kind(ll: float, pi: float) -> str:
    a_line = 0.73 * (ll - 20.0)
    if pi < 4.0 or pi < a_line:
        return "silt"
    if pi <= 7.0:
        return "silty clay"
    return "clay"


def grading_letter(cu: Optional[float], cc: Optional[float]) -> Optional[str]:
    if cu is None or cc is None:
        return None
    if cu >= 15.0 and cc < 0.5:
        return "G"
    if cu >= 15.0 and 1.0 <= cc <= 3.0:
        return "W"
    if 6.0 <= cu < 15.0 and cc < 1.0:
        return "M"
    if 3.0 <= cu < 6.0 and cc < 1.0:
        return "P"
    if cu < 3.0 and cc < 1.0:
        return "U"
    return "P"


class ISO14688Classifier(Classifier):
    system_name = "TS EN ISO 14688"

    def classify(self, sample: SoilSample) -> ClassificationResult:
        fr = sample.fractions(ISO14688_SIZES)
        if fr is None:
            return self.insufficient(self.system_name,
                                     "Sieve data (incl. 0.063 mm) required.")
        notes = [f"Fines (< 0.063 mm) = {fr.fines:.1f} %, "
                 f"sand = {fr.sand:.1f} %, gravel = {fr.gravel:.1f} %"]
        if fr.fines >= 50.0:
            res = self._fine(sample, fr, notes)
        else:
            res = self._coarse(sample, fr, notes)
        if res.ok and sample.organic:
            res.symbol = "or" + res.symbol
            res.name = "organic " + res.name
            res.notes.append("Organic soil -> prefix 'or' and the word "
                             "'organic'.")
        return res

    def _fine(self, sample, fr, notes) -> ClassificationResult:
        ll, pi = sample.liquid_limit, sample.plasticity_index
        if ll is None or pi is None:
            return self.insufficient(self.system_name,
                                     "Atterberg limits required for fine soil.")
        letter, word = plasticity_class(ll)
        kind = fine_kind(ll, pi)
        a_line = 0.73 * (ll - 20.0)
        notes.append(f"Fines >= 50 % -> fine soil. LL = {ll:.1f}, PI = "
                     f"{pi:.1f}, A-line PI = {a_line:.1f} -> {kind}, "
                     f"{word} ({letter})")

        if kind == "clay":
            core, noun = f"Cl{letter}", f"{word} CLAY"
        elif kind == "silt":
            core, noun = f"Si{letter}", f"{word} SILT"
        else:
            core, noun = f"Cl{letter}-Si{letter}", f"{word} silty CLAY"
            notes.append("On/above the A-line with 4 <= PI <= 7 -> silty "
                         "clay (ClL-SiL).")

        coarse = max(fr.sand, fr.gravel)
        prefix, adj = "", ""
        if coarse > 15.0:
            sandy = fr.sand >= fr.gravel
            prefix = "sa" if sandy else "gr"
            adj = "sandy " if sandy else "gravelly "
            notes.append(f"{'Sand' if sandy else 'Gravel'} {coarse:.1f} % "
                         "> 15 % -> prefix '" + prefix + "'.")
        return ClassificationResult(self.system_name, prefix + core,
                                    adj + noun, notes)

    def _coarse(self, sample, fr, notes) -> ClassificationResult:
        gravel_soil = fr.gravel > fr.sand
        primary = "Gr" if gravel_soil else "Sa"
        noun = "GRAVEL" if gravel_soil else "SAND"
        other = fr.sand if gravel_soil else fr.gravel
        notes.append(f"Fines < 50 % -> coarse soil; "
                     f"{'gravel' if gravel_soil else 'sand'} is the primary "
                     "fraction.")

        if other > 15.0:
            notes.append(f"{'Sand' if gravel_soil else 'Gravel'} "
                         f"{other:.1f} % > 15 % of the sample, but the "
                         "tertiary coarse-fraction prefix (sa-/gr-) is not "
                         "applied by this app; only the primary fraction "
                         "and the fines prefix are reflected in the symbol.")

        cu, cc = sample.cu, sample.cc
        grade = grading_letter(cu, cc)
        if grade is not None:
            notes.append(f"Cu = {cu:.2f}, Cc = {cc:.2f} -> "
                         f"{_GRADING_WORD[grade]} ({grade})")

        if fr.fines < 5.0:
            if grade is None:
                grade = "P"
                notes.append("Cu/Cc not computable; assumed poorly graded.")
            notes.append("Fines < 5 % -> no fines prefix.")
            return ClassificationResult(
                self.system_name, f"{primary}{grade}",
                f"{_GRADING_WORD[grade]} {noun}", notes)

        fines_kind, provisional = self._fines_kind(sample, notes)
        if fines_kind == "silt":
            fpre, fadj = "si", "silty "
        elif fines_kind == "clay":
            fpre, fadj = "cl", "clayey "
        else:
            if fr.fines <= 15.0:
                fpre, fadj = "sicl", "silty clayey "
            else:
                fpre, fadj = "cl", "clayey "
        tag = " (provisional)" if provisional else ""

        if fr.fines <= 15.0:
            notes.append("Fines 5-15 % -> fines prefix and grading letter.")
            if fpre == "sicl":
                notes.append("Silty-clay fines (ClL-SiL) in a 5-15 % soil -> "
                             "'sicl', grading letter omitted.")
                grade = None
            elif grade is None:
                notes.append("Cu/Cc not computable (10 % size not reached); "
                             "grading letter omitted.")
            sym = f"{fpre}{primary}{grade or ''}"
            name = f"{fadj}{_GRADING_WORD[grade] + ' ' if grade else ''}{noun}"
            return ClassificationResult(self.system_name, sym, name + tag,
                                        notes)

        notes.append("Fines > 15 % -> fines prefix, no grading letter.")
        return ClassificationResult(
            self.system_name, f"{fpre}{primary}",
            f"{fadj}{noun}{tag}", notes)

    def _fines_kind(self, sample, notes):
        ll, pi = sample.liquid_limit, sample.plasticity_index
        if ll is None or pi is None:
            notes.insert(0, "WARNING: Atterberg limits missing; fines "
                            "assumed silty - result is provisional.")
            return "silt", True
        kind = fine_kind(ll, pi)
        notes.append(f"LL = {ll:.1f}, PI = {pi:.1f}, A-line PI = "
                     f"{0.73 * (ll - 20.0):.1f} -> fines are {kind}")
        return kind, False
