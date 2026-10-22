from __future__ import annotations

import csv
import datetime as _dt
import io
import math
from typing import List, Sequence

from ..classifiers import short_system_name
from ..models import BS_SIZES, SoilSample
from ..version import __version__

AGS_VERSION = "4.1.1"

_SAMPLE_KEYS = [
    ("LOCA_ID", "", "ID"),
    ("SAMP_TOP", "m", "2DP"),
    ("SAMP_REF", "", "X"),
    ("SAMP_TYPE", "", "PA"),
    ("SAMP_ID", "", "ID"),
]
_SPECIMEN_KEYS = _SAMPLE_KEYS + [
    ("SPEC_REF", "", "X"),
    ("SPEC_DPTH", "m", "2DP"),
]

_GROUPS = {
    "PROJ": [
        ("PROJ_ID", "", "ID"),
        ("PROJ_NAME", "", "X"),
        ("PROJ_LOC", "", "X"),
        ("PROJ_MEMO", "", "X"),
    ],
    "TRAN": [
        ("TRAN_ISNO", "", "X"),
        ("TRAN_DATE", "yyyy-mm-dd", "DT"),
        ("TRAN_PROD", "", "X"),
        ("TRAN_STAT", "", "X"),
        ("TRAN_AGS", "", "X"),
        ("TRAN_RECV", "", "X"),
        ("TRAN_DLIM", "", "X"),
        ("TRAN_RCON", "", "X"),
    ],
    "ABBR": [
        ("ABBR_HDNG", "", "X"),
        ("ABBR_CODE", "", "X"),
        ("ABBR_DESC", "", "X"),
    ],
    "TYPE": [
        ("TYPE_TYPE", "", "X"),
        ("TYPE_DESC", "", "X"),
    ],
    "UNIT": [
        ("UNIT_UNIT", "", "X"),
        ("UNIT_DESC", "", "X"),
    ],
    "LOCA": [
        ("LOCA_ID", "", "ID"),
        ("LOCA_TYPE", "", "PA"),
        ("LOCA_REM", "", "X"),
    ],
    "SAMP": _SAMPLE_KEYS + [
        ("SAMP_DTIM", "yyyy-mm-dd", "DT"),
    ],
    "GRAG": _SPECIMEN_KEYS + [
        ("GRAG_GRAV", "%", "1DP"),
        ("GRAG_SAND", "%", "1DP"),
        ("GRAG_FINE", "%", "1DP"),
        ("GRAG_REM", "", "X"),
    ],
    "GRAT": _SPECIMEN_KEYS + [
        ("GRAT_SIZE", "mm", "3SF"),
        ("GRAT_PERP", "%", "1DP"),
    ],
    "LLPL": _SPECIMEN_KEYS + [
        ("LLPL_LL", "%", "XN"),
        ("LLPL_PL", "%", "XN"),
        ("LLPL_PI", "%", "XN"),
    ],
}

_TYPE_DESC = {
    "ID": "Unique identifier",
    "X": "Text",
    "PA": "Text listed in ABBR group",
    "DT": "Date time in international format",
    "2DP": "Value; 2 decimal places",
    "1DP": "Value; 1 decimal place",
    "3SF": "Value; 3 significant figures",
    "XN": "Text or numeric",
}
_UNIT_DESC = {
    "m": "metre",
    "mm": "millimetre",
    "%": "percentage",
    "yyyy-mm-dd": "year month day",
}
_ABBR = [
    ("LOCA_TYPE", "BH", "Borehole"),
    ("SAMP_TYPE", "B", "Bulk disturbed sample"),
]


def _group_lines(group: str, rows: Sequence[Sequence[str]]) -> List[List[str]]:
    headings, units, types = zip(*_GROUPS[group])
    lines = [
        ["GROUP", group],
        ["HEADING", *headings],
        ["UNIT", *units],
        ["TYPE", *types],
    ]
    lines.extend(["DATA", *row] for row in rows)
    return lines


def _fmt(value, nd=None) -> str:
    if value is None:
        return ""
    if nd is not None:
        return f"{value:.{nd}f}"
    return str(value)


def _sig(value: float, figures: int = 3) -> str:
    if value == 0:
        return "0"
    decimals = max(0, figures - 1 - int(math.floor(math.log10(abs(value)))))
    return f"{value:.{decimals}f}"


def _classification_memo(results) -> str:
    parts = [f"{short_system_name(r.system)}: {r.symbol}" for r in results if r.ok]
    if not parts:
        return "Classified with SoilClass Pro."
    return "Classified with SoilClass Pro - " + "; ".join(parts) + "."


def _date(text: str) -> str:
    text = (text or "").strip()
    try:
        return _dt.date.fromisoformat(text[:10]).isoformat()
    except ValueError:
        return ""


def build_ags4_text(sample: SoilSample, results=()) -> str:
    loca_id = (sample.name or "Sample 1").strip() or "Sample 1"
    samp_top = _fmt(0.0, 2)
    sample_key = [loca_id, samp_top, "1", "B", loca_id]
    specimen_key = sample_key + ["1", samp_top]
    used_groups = ["PROJ", "TRAN", "ABBR", "TYPE", "UNIT", "LOCA", "SAMP",
                   "GRAG", "GRAT"]
    has_limits = sample.liquid_limit is not None or sample.plastic_limit is not None
    if has_limits:
        used_groups.append("LLPL")

    lines: List[List[str]] = []
    lines += _group_lines("PROJ", [[
        sample.project or "SoilClassPro-project",
        sample.project or "", sample.location or "",
        f"Tested by: {sample.operator}" if sample.operator else "",
    ]])
    lines += _group_lines("TRAN", [[
        "1", _dt.date.today().isoformat(), f"SoilClass Pro {__version__}",
        "Final", AGS_VERSION, "Not specified", "|", "+",
    ]])
    lines += _group_lines("ABBR", [list(row) for row in _ABBR])
    used_types = sorted({kind for g in used_groups for _, _, kind in _GROUPS[g]})
    lines += _group_lines("TYPE", [[k, _TYPE_DESC[k]] for k in used_types])
    used_units = sorted({unit for g in used_groups for _, unit, _ in _GROUPS[g]
                         if unit})
    lines += _group_lines("UNIT", [[u, _UNIT_DESC[u]] for u in used_units])
    lines += _group_lines("LOCA", [[loca_id, "BH", _classification_memo(results)]])
    lines += _group_lines("SAMP", [sample_key + [_date(sample.date)]])

    fractions = sample.fractions(BS_SIZES)
    lines += _group_lines("GRAG", [specimen_key + [
        _fmt(fractions.gravel, 1) if fractions else "",
        _fmt(fractions.sand, 1) if fractions else "",
        _fmt(fractions.fines, 1) if fractions else "",
        "Fractions by BS 5930 / EN ISO 14688 boundaries (2 mm, 0.063 mm)",
    ]])
    lines += _group_lines("GRAT", [
        specimen_key + [_sig(size), _fmt(passing, 1)]
        for size, passing in sorted(sample.sieve_data, key=lambda p: -p[0])
    ])
    if has_limits:
        pl = _fmt(sample.plastic_limit, 1) if sample.plastic_limit is not None else "NP"
        pi = sample.plasticity_index
        lines += _group_lines("LLPL", [specimen_key + [
            _fmt(sample.liquid_limit, 1), pl,
            _fmt(pi, 1) if pi is not None else "NP",
        ]])

    buf = io.StringIO()
    writer = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    for index, line in enumerate(lines):
        if line[0] == "GROUP" and index:
            buf.write("\r\n")
        writer.writerow(line)
    return buf.getvalue()


def export_ags4(path: str, sample: SoilSample, results=()) -> None:
    text = build_ags4_text(sample, results)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)
