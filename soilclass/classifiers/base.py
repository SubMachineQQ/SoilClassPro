from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List

from ..i18n import t
from ..models import SoilSample


@dataclass
class ClassificationResult:
    system: str
    symbol: str
    name: str
    notes: List[str] = field(default_factory=list)
    extras: Dict[str, str] = field(default_factory=dict)
    ok: bool = True

    def as_text(self) -> str:
        lines = [f"{self.system}",
                 f"  {t('res_group_symbol_label')} {self.symbol}",
                 f"  {t('res_group_name_label')} {self.name}"]
        for k, v in self.extras.items():
            lines.append(f"  {k}: {v}")
        if self.notes:
            lines.append(f"  {t('res_decision_trail_label')}")
            lines.extend(f"    - {n}" for n in self.notes)
        return "\n".join(lines)


class Classifier(ABC):
    system_name: str = "Unnamed system"

    @abstractmethod
    def classify(self, sample: SoilSample) -> ClassificationResult:
        pass

    @staticmethod
    def a_line(ll: float) -> float:
        return 0.73 * (ll - 20.0)

    @staticmethod
    def u_line(ll: float) -> float:
        return 0.9 * (ll - 8.0)

    @staticmethod
    def insufficient(system: str, why: str) -> ClassificationResult:
        return ClassificationResult(
            system=system, symbol="-", name="Insufficient data",
            notes=[why], ok=False,
        )
