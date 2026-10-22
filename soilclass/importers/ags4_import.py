from __future__ import annotations

import csv
import io
from typing import Dict, List, Tuple

from .table_parser import ParsedData, _to_float, validate

_GRADING_GROUPS = (("GRAT", "GRAT_SIZE", "GRAT_PERP"),
                   ("GRAD", "GRAD_SIZE", "GRAD_PERP"),
                   ("GRAN", "GRAN_SIZE", "GRAN_PERP"))
_KEY_FIELDS = ("LOCA_ID", "SAMP_TOP", "SAMP_REF", "SAMP_TYPE", "SAMP_ID",
               "SPEC_REF", "SPEC_DPTH", "HOLE_ID", "SAMP_REFERENCE")


def looks_like_ags(text: str) -> bool:
    head = text.lstrip("﻿ \r\n")[:200].upper()
    return head.startswith('"GROUP"') or head.startswith("**")


def _groups(text: str) -> Dict[str, List[Dict[str, str]]]:
    groups: Dict[str, List[Dict[str, str]]] = {}
    current = None
    headings: List[str] = []
    for row in csv.reader(io.StringIO(text.lstrip("﻿"))):
        if not row:
            continue
        tag = row[0].strip().upper()
        if tag == "GROUP" and len(row) > 1:
            current = row[1].strip().upper()
            groups.setdefault(current, [])
            headings = []
        elif tag == "HEADING":
            headings = [h.strip().upper() for h in row[1:]]
        elif tag == "DATA" and current and headings:
            groups[current].append(dict(zip(headings, row[1:])))
        elif tag.startswith("**") and len(tag) > 2:
            current = tag[2:].strip('"')
            groups.setdefault(current, [])
            headings = []
        elif tag.startswith("*") and current:
            headings = [h.strip().strip("*").upper() for h in row]
        elif current and headings and len(row) == len(headings) and \
                not tag.startswith("<"):
            groups[current].append(dict(zip(headings, row)))
    return groups


def _key(record: Dict[str, str]) -> Tuple[str, ...]:
    return tuple(record.get(f, "").strip() for f in _KEY_FIELDS)


def _number(text: str):
    text = (text or "").strip()
    if not text:
        return None
    try:
        return _to_float(text)
    except ValueError:
        return None


def read_ags(text: str, source: str = "") -> List[ParsedData]:
    groups = _groups(text)
    samples: Dict[Tuple[str, ...], ParsedData] = {}
    for group, size_field, pass_field in _GRADING_GROUPS:
        for record in groups.get(group, []):
            size = _number(record.get(size_field))
            passing = _number(record.get(pass_field))
            if size is None or passing is None:
                continue
            if not (0 < size <= 1000 and 0 <= passing <= 100):
                continue
            key = _key(record)
            data = samples.setdefault(key, ParsedData(source=source))
            data.sieve.append((size, passing))
        if samples:
            break
    for record in groups.get("LLPL", []):
        key = _key(record)
        if key not in samples:
            continue
        ll = _number(record.get("LLPL_LL"))
        pl_text = (record.get("LLPL_PL") or "").strip().upper()
        samples[key].liquid_limit = ll
        samples[key].plastic_limit = None if pl_text == "NP" else _number(pl_text)
        if pl_text == "NP":
            samples[key].meta["non_plastic"] = True
    project = (groups.get("PROJ") or [{}])[0]
    out = []
    for key, data in samples.items():
        loca, top = key[0] or key[7], key[1]
        name = loca
        if top and (_number(top) or 0) != 0:
            name = f"{loca} / {top} m" if loca else f"{top} m"
        elif not loca and top:
            name = f"{top} m"
        if name:
            data.meta["name"] = name
        if project.get("PROJ_NAME"):
            data.meta["project"] = project["PROJ_NAME"].strip()
        if project.get("PROJ_LOC"):
            data.meta["location"] = project["PROJ_LOC"].strip()
        data.meta["_method"] = "ags"
        data.sieve = sorted(dict(data.sieve).items(), key=lambda p: -p[0])
        out.append(validate(data))
    return out
