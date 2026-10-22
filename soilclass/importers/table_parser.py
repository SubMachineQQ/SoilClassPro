from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ..i18n import t

SIEVE_MM = {
    "4": 4.75, "8": 2.36, "10": 2.00, "16": 1.18, "20": 0.850,
    "30": 0.600, "40": 0.425, "50": 0.300, "60": 0.250, "100": 0.150,
    "140": 0.106, "200": 0.075,
}
INCH_MM = {
    "3": 75.0, "2": 50.0, "1.5": 37.5, "1-1/2": 37.5, "1 1/2": 37.5,
    "1": 25.0, "3/4": 19.0, "1/2": 12.5, "3/8": 9.5, "1/4": 6.3,
}

_NUM = re.compile(r"\d+(?:[.,]\d+)?")
_SIEVE_NO = re.compile(r"(?:no\.?\s*|#)\s*(\d+)", re.IGNORECASE)
_SIEVE_IN = re.compile(r'(\d(?:[-\s]?1/2)?|3/4|1/2|3/8|1/4)\s*(?:"|in\b|inch)',
                       re.IGNORECASE)
_LL = re.compile(r"(?:liquid\s*limit|\bLL\b)\s*[:=]?\s*(\d+(?:[.,]\d+)?)",
                 re.IGNORECASE)
_PL = re.compile(r"(?:plastic\s*limit|\bPL\b)\s*[:=]?\s*(\d+(?:[.,]\d+)?)",
                 re.IGNORECASE)


def _to_float(s: str) -> float:
    return float(s.replace(",", "."))


@dataclass
class ParsedData:
    sieve: List[Tuple[float, float]] = field(default_factory=list)
    liquid_limit: Optional[float] = None
    plastic_limit: Optional[float] = None
    warnings: List[str] = field(default_factory=list)
    source: str = ""
    meta: Dict[str, object] = field(default_factory=dict)
    others: List["ParsedData"] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.sieve) >= 2


def _line_to_pair(line: str) -> Optional[Tuple[float, float]]:
    nums = _NUM.findall(line)
    if not nums:
        return None

    size: Optional[float] = None
    m = _SIEVE_NO.search(line)
    if m and m.group(1) in SIEVE_MM:
        size = SIEVE_MM[m.group(1)]
        nums = [n for n in nums if n != m.group(1)] or nums[1:]
    else:
        m = _SIEVE_IN.search(line)
        if m:
            key = m.group(1).replace(" ", "-").replace("--", "-")
            size = INCH_MM.get(key, INCH_MM.get(m.group(1)))

    if size is None:
        if len(nums) < 2:
            return None
        size = _to_float(nums[0])
        passing = _to_float(nums[-1])
    else:
        if not nums:
            return None
        passing = _to_float(nums[-1])

    if size <= 0 or size > 1000 or not (0.0 <= passing <= 100.0):
        return None
    return (size, passing)


def parse_text(text: str, source: str = "") -> ParsedData:
    out = ParsedData(source=source)

    m = _LL.search(text)
    if m:
        out.liquid_limit = _to_float(m.group(1))
    m = _PL.search(text)
    if m:
        out.plastic_limit = _to_float(m.group(1))

    seen = {}
    for line in text.splitlines():
        low = line.lower()
        if any(k in low for k in ("liquid", "plastic", "date", "project",
                                  "sample", "operator", "borehole")):
            continue
        pair = _line_to_pair(line)
        if pair:
            seen[pair[0]] = pair[1]

    out.sieve = sorted(seen.items(), key=lambda x: -x[0])
    return validate(out)


def validate(out: ParsedData) -> ParsedData:
    for (d1, p1), (d2, p2) in zip(out.sieve, out.sieve[1:]):
        if p2 > p1 + 0.51:
            out.warnings.append(t("import_warn_increasing").format(
                p1=f"{p1:g}", d1=f"{d1:g}", p2=f"{p2:g}", d2=f"{d2:g}"))
    if (out.liquid_limit is not None and out.plastic_limit is not None
            and out.plastic_limit > out.liquid_limit):
        out.warnings.append(t("import_warn_pl_gt_ll"))
    if not out.ok:
        out.warnings.append(t("import_warn_too_few"))
    return out
