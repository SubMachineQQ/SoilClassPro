from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from ..i18n import t
from .table_parser import (INCH_MM, SIEVE_MM, ParsedData, _SIEVE_IN,
                           _SIEVE_NO, _to_float, validate)

Grid = List[List[Any]]

_SIZE = re.compile(r"açıklı|aciklik|opening|aperture|elek\s*(boyut|çap|cap)|"
                   r"sieve\s*size|particle\s*(size|diameter)|grain\s*size|"
                   r"dane\s*(boyut|çap|cap)|tane\s*(boyut|çap|cap)|diameter|"
                   r"\bçap\b|\bcap\b|\bsize\b|\(mm\)|\(µm\)|\(μm\)|\bmm\b",
                   re.IGNORECASE)
_SIEVE_NAME = re.compile(r"elek\s*(no|numara|ad)|sieve\s*(no|number|designation)|"
                         r"designation|^\s*elek\s*$|^\s*sieve\s*$|^\s*no\.?\s*$|"
                         r"^\s*#\s*$", re.IGNORECASE)
_PASSING = re.compile(r"geçen|gecen|passing|finer|ince\s*%|% *ince", re.IGNORECASE)
_RETAINED = re.compile(r"kalan|retained|tutulan|üzerinde\s*kal", re.IGNORECASE)
_CUMULATIVE = re.compile(r"kümülatif|kumulatif|cumulative|\bcum\b|birikimli|"
                         r"toplam\s*kalan|total\s*retained", re.IGNORECASE)
_MASS = re.compile(r"\(g\)|\bgr?\b|gram|kütle|kutle|mass|ağırlık|agirlik|"
                   r"weight|\bkg\b", re.IGNORECASE)
_PERCENT = re.compile(r"%|yüzde|yuzde|percent", re.IGNORECASE)
_MICRON = re.compile(r"µm|μm|micron|mikron", re.IGNORECASE)
_INCH_UNIT = re.compile(r"\(in\)|\binch\b|\binç\b", re.IGNORECASE)
_PAN = re.compile(r"tava|\bpan\b|\bkap\b|alt\s*kap|receiver|bottom",
                  re.IGNORECASE)
_TOTAL_MASS = re.compile(r"(toplam|total|başlangıç|baslangic|initial|ilk|kuru|"
                         r"dry|numune|sample|deney).*(kütle|kutle|mass|ağırlık|"
                         r"agirlik|weight)|^\s*(m|w)\s*[0-9]?\s*\(g\)",
                         re.IGNORECASE)
_SUM_ROW = re.compile(r"^\s*(toplam|total|sum|σ|Σ)\b", re.IGNORECASE)

_NUMBER_FIELDS = (
    ("ll_brine", r"tuzlu\s*su|brine"),
    ("ll_kerosene", r"gazya|kerosene"),
    ("e_max_gravel", r"(çakıl|cakil|gravel).*e\s*_?\s*(maks|max)"),
    ("e_min_gravel", r"(çakıl|cakil|gravel).*e\s*_?\s*min"),
    ("e_max_sand", r"(kum|sand).*e\s*_?\s*(maks|max)"),
    ("e_min_sand", r"(kum|sand).*e\s*_?\s*min"),
    ("liquid_limit", r"likit\s*limit|liquid\s*limit|sıvı\s*limit|^\s*ll\b|"
                     r"\(ll\)|^\s*w\s*_?\s*l\b|^\s*wl\b"),
    ("plastic_limit", r"plastik\s*limit|plastic\s*limit|^\s*pl\b|\(pl\)|"
                      r"^\s*w\s*_?\s*p\b|^\s*wp\b"),
)
_TEXT_FIELDS = (
    ("name", r"numune\s*(adı|adi|no|kodu)?|sample\s*(name|id|no)?|"
             r"specimen"),
    ("project", r"proje|project|iş\s*adı|job"),
    ("location", r"konum|location|sondaj|borehole|kuyu|lokasyon"),
    ("operator", r"deneyi\s*yapan|operator|tested\s*by|teknisyen|technician"),
    ("date", r"tarih|date"),
)
_ORGANIC = re.compile(r"organik|organic", re.IGNORECASE)
_YES = {"evet", "yes", "e", "y", "true", "1", "x", "var", "✓"}
_INLINE = re.compile(r"^\s*(ll|pl|w\s*l|w\s*p)\s*[:=]\s*(\d+(?:[.,]\d+)?)\s*$",
                     re.IGNORECASE)


def _norm(text: str) -> str:
    return text.casefold().replace("i̇", "i")


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, _dt.datetime):
        return value.date().isoformat()
    if isinstance(value, _dt.date):
        return value.isoformat()
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _number(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("%", "").replace(" ", "").strip()
    if not text:
        return None
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+,\d+", text):
        text = text.replace(".", "")
    try:
        return _to_float(text)
    except ValueError:
        return None


def _sieve_name_mm(value: Any) -> Optional[float]:
    text = _text(value)
    if not text:
        return None
    match = _SIEVE_NO.search(text)
    if match and match.group(1) in SIEVE_MM:
        return SIEVE_MM[match.group(1)]
    match = _SIEVE_IN.search(text)
    if match:
        key = match.group(1).replace(" ", "-").replace("--", "-")
        return INCH_MM.get(key, INCH_MM.get(match.group(1)))
    plain = text.replace(" ", "")
    if plain in SIEVE_MM and not re.search(r"[.,]", plain):
        return SIEVE_MM[plain]
    if plain in INCH_MM:
        return INCH_MM[plain]
    return None


@dataclass
class _Column:
    index: int
    kind: str
    header: str
    factor: float = 1.0


@dataclass
class _Table:
    columns: List[_Column]
    header_row: int
    rows: List[List[Any]] = field(default_factory=list)
    pan_mass: Optional[float] = None
    sum_mass: Optional[float] = None


def _classify(header: str) -> Optional[str]:
    h = _norm(header)
    if not h:
        return None
    if _PASSING.search(h):
        return "passing"
    if _RETAINED.search(h) or (_CUMULATIVE.search(h) and not _SIZE.search(h)):
        cumulative = bool(_CUMULATIVE.search(h))
        if _PERCENT.search(h):
            return "cum_ret_pct" if cumulative else "ret_pct"
        if _MASS.search(h) or not _PERCENT.search(h):
            return "cum_ret_mass" if cumulative else "ret_mass"
    if _SIEVE_NAME.search(h):
        return "sieve_name"
    if _SIZE.search(h):
        return "size"
    if re.search(r"\belek\b|\bsieve\b|\bno\b", h):
        return "sieve_name"
    return None


def _header_block(grid: Grid, r: int) -> List[str]:
    width = max((len(row) for row in grid[r:r + 3]), default=0)
    texts = []
    for c in range(width):
        parts = []
        for rr in range(r, min(r + 3, len(grid))):
            cell = grid[rr][c] if c < len(grid[rr]) else None
            if cell is None or _number(cell) is not None:
                if rr > r:
                    break
                continue
            parts.append(_text(cell))
        texts.append(" ".join(p for p in parts if p))
    return texts


def _header_rows_used(grid: Grid, r: int) -> int:
    used = 1
    for rr in range(r + 1, min(r + 3, len(grid))):
        row = grid[rr]
        if any(_number(c) is not None for c in row if c is not None):
            break
        if any(_text(c) for c in row):
            used += 1
        else:
            break
    return used


def _find_tables(grid: Grid) -> List[_Table]:
    tables = []
    for r in range(min(len(grid), 80)):
        row = grid[r]
        if not any(isinstance(c, str) and c.strip() for c in row):
            continue
        headers = _header_block(grid, r)
        columns = []
        for c, header in enumerate(headers):
            kind = _classify(header)
            if kind is None:
                continue
            factor = 1.0
            if kind == "size":
                if _MICRON.search(header):
                    factor = 0.001
                elif _INCH_UNIT.search(header):
                    factor = 25.4
            columns.append(_Column(c, kind, header, factor))
        kinds = {col.kind for col in columns}
        has_size = bool(kinds & {"size", "sieve_name"})
        has_value = bool(kinds & {"passing", "cum_ret_pct", "ret_pct",
                                  "cum_ret_mass", "ret_mass"})
        if not has_size:
            continue
        size_cols = {col.index for col in columns
                     if col.kind in ("size", "sieve_name")}
        start = r + _header_rows_used(grid, r)
        if not has_value:
            extra = []
            for c, header in enumerate(headers):
                if c in size_cols or not header:
                    continue
                values = [_number(grid[rr][c]) for rr in range(start, len(grid))
                          if c < len(grid[rr])]
                values = [v for v in values if v is not None]
                if len(values) >= 2 and all(0 <= v <= 100 for v in values):
                    extra.append(_Column(c, "passing", header))
            if not extra:
                continue
            columns.extend(extra)
        table = _Table(columns=columns, header_row=r)
        blank_run = 0
        for rr in range(start, len(grid)):
            data_row = grid[rr]
            if not any(_text(c) for c in data_row):
                blank_run += 1
                if blank_run >= 2 and table.rows:
                    break
                continue
            blank_run = 0
            label = " ".join(_text(c) for c in data_row
                             if isinstance(c, str))
            size = _row_size(data_row, columns)
            if size is None:
                masses = [_number(data_row[col.index]) for col in columns
                          if col.kind == "ret_mass" and col.index < len(data_row)]
                masses = [m for m in masses if m is not None]
                if masses and _PAN.search(label):
                    table.pan_mass = masses[0]
                elif masses and _SUM_ROW.search(label):
                    table.sum_mass = masses[0]
                if table.rows and re.search(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]{4,}",
                                            label) and not masses:
                    if _classify(label) or _SUM_ROW.search(label):
                        break
                continue
            table.rows.append(data_row)
        if len(table.rows) >= 2:
            tables.append(table)
    return tables


def _row_size(row: Sequence[Any], columns: List[_Column]) -> Optional[float]:
    for col in columns:
        if col.kind == "size" and col.index < len(row):
            value = _number(row[col.index])
            if value is None:
                value = _sieve_name_mm(row[col.index])
                if value is not None:
                    return value
                continue
            return value * col.factor
    for col in columns:
        if col.kind == "sieve_name" and col.index < len(row):
            value = _sieve_name_mm(row[col.index])
            if value is not None:
                return value
            value = _number(row[col.index])
            if value is not None and _text(row[col.index]) in SIEVE_MM:
                return SIEVE_MM[_text(row[col.index])]
    return None


def _as_percent(values: List[float]) -> List[float]:
    if values and max(values) <= 1.0 and min(values) >= 0.0 and any(
            v < 1.0 for v in values):
        return [v * 100.0 for v in values]
    return values


def _monotone(points: List[Tuple[float, float]]) -> bool:
    ordered = sorted(points, key=lambda p: -p[0])
    return all(b[1] <= a[1] + 0.51 for a, b in zip(ordered, ordered[1:]))


def _samples_from_table(table: _Table, total_mass: Optional[float]):
    sizes = [_row_size(row, table.columns) for row in table.rows]
    by_kind: Dict[str, List[_Column]] = {}
    for col in table.columns:
        by_kind.setdefault(col.kind, []).append(col)

    def values(col):
        out = []
        for row in table.rows:
            out.append(_number(row[col.index]) if col.index < len(row) else None)
        return out

    results = []
    method = None
    if "passing" in by_kind:
        method = "passing"
        for col in by_kind["passing"]:
            raw = values(col)
            known = _as_percent([v for v in raw if v is not None])
            it = iter(known)
            converted = [next(it) if v is not None else None for v in raw]
            results.append((col.header, converted))
    elif "cum_ret_pct" in by_kind:
        method = "cum_ret_pct"
        for col in by_kind["cum_ret_pct"]:
            raw = values(col)
            known = _as_percent([v for v in raw if v is not None])
            it = iter(known)
            results.append((col.header, [100.0 - next(it) if v is not None
                                         else None for v in raw]))
    elif "ret_pct" in by_kind:
        method = "ret_pct"
        for col in by_kind["ret_pct"]:
            raw = values(col)
            known = _as_percent([v for v in raw if v is not None])
            it = iter(known)
            pct = [next(it) if v is not None else None for v in raw]
            ordered = sorted(range(len(sizes)),
                             key=lambda i: -(sizes[i] or 0))
            passing = [None] * len(sizes)
            cumulative = 0.0
            for i in ordered:
                if pct[i] is None or sizes[i] is None:
                    continue
                cumulative += pct[i]
                passing[i] = 100.0 - cumulative
            results.append((col.header, passing))
    elif "cum_ret_mass" in by_kind or "ret_mass" in by_kind:
        cumulative_col = by_kind.get("cum_ret_mass", [None])[0]
        retained_col = by_kind.get("ret_mass", [None])[0]
        if cumulative_col is not None:
            method = "cum_ret_mass"
            cum = values(cumulative_col)
            total = total_mass or table.sum_mass
            if total is None:
                retained = values(retained_col) if retained_col else []
                known = [v for v in retained if v is not None]
                if known:
                    total = sum(known) + (table.pan_mass or 0.0)
            if total:
                results.append(("", [100.0 - c / total * 100.0 if c is not None
                                     else None for c in cum]))
        else:
            method = "ret_mass"
            retained = values(retained_col)
            known = [v for v in retained if v is not None]
            total = total_mass
            if total is None:
                total = table.sum_mass or (sum(known) + (table.pan_mass or 0.0))
            if total:
                ordered = sorted(range(len(sizes)),
                                 key=lambda i: -(sizes[i] or 0))
                passing = [None] * len(sizes)
                cumulative = 0.0
                for i in ordered:
                    if retained[i] is None or sizes[i] is None:
                        continue
                    cumulative += retained[i]
                    passing[i] = 100.0 - cumulative / total * 100.0
                results.append(("", passing))

    samples = []
    for (header, passing), column in zip(results, _result_columns(by_kind)):
        points = {}
        for size, value in zip(sizes, passing):
            if size is None or value is None:
                continue
            value = max(0.0, min(100.0, round(value, 4)))
            if 0 < size <= 1000:
                points[size] = value
        if len(points) >= 2:
            samples.append((header, sorted(points.items(), key=lambda p: -p[0]),
                            method, column))
    return samples


def _result_columns(by_kind):
    for kind in ("passing", "cum_ret_pct", "ret_pct"):
        if kind in by_kind:
            return [col.index for col in by_kind[kind]]
    return [None]


def _find_total_mass(grid: Grid) -> Optional[float]:
    for row in grid:
        cells = [c for c in row if _text(c)]
        for i, cell in enumerate(cells[:-1]):
            if isinstance(cell, str) and _TOTAL_MASS.search(_norm(cell)) \
                    and not _RETAINED.search(_norm(cell)):
                value = _number(cells[i + 1])
                if value is not None and value > 0:
                    return value
    return None


def _metadata(grid: Grid, skip_rows: set) -> Dict[str, Any]:
    meta: Dict[str, Any] = {}
    for r, row in enumerate(grid):
        if r in skip_rows:
            continue
        cells = [c for c in row if _text(c)]
        for i, cell in enumerate(cells):
            if not isinstance(cell, str):
                continue
            label = _norm(cell)
            inline = _INLINE.match(cell)
            if inline:
                key = ("liquid_limit" if inline.group(1).lower().replace(" ", "")
                       in ("ll", "wl") else "plastic_limit")
                meta.setdefault(key, _to_float(inline.group(2)))
                continue
            value = cells[i + 1] if i + 1 < len(cells) else None
            if value is None:
                continue
            for key, pattern in _NUMBER_FIELDS:
                if re.search(pattern, label, re.IGNORECASE):
                    number = _number(value)
                    if number is not None:
                        meta.setdefault(key, number)
                    break
            else:
                if _ORGANIC.search(label):
                    meta.setdefault("organic", _norm(_text(value)) in _YES)
                    continue
                if _MASS.search(label) or _PERCENT.search(label):
                    continue
                for key, pattern in _TEXT_FIELDS:
                    if re.search(pattern, label, re.IGNORECASE):
                        text = _text(value)
                        if text:
                            meta.setdefault(key, text)
                        break
    return meta


def _transpose(grid: Grid) -> Grid:
    width = max((len(row) for row in grid), default=0)
    return [[row[c] if c < len(row) else None for row in grid]
            for c in range(width)]


def _column_limits(grid: Grid, column: int) -> Dict[str, float]:
    limits = {}
    for row in grid:
        if column >= len(row):
            continue
        labels = [c for c in row[:column] if isinstance(c, str) and c.strip()]
        if not labels:
            continue
        label = _norm(labels[0])
        value = _number(row[column])
        if value is None:
            continue
        for key, pattern in _NUMBER_FIELDS:
            if re.search(pattern, label, re.IGNORECASE):
                limits.setdefault(key, value)
                break
    return limits


def read_grid(grid: Grid, sheet_name: str = "") -> List[Tuple[str, List, str, Dict]]:
    grid = [list(row) for row in grid]
    best, best_grid = [], grid
    for orientation in (grid, _transpose(grid)):
        found = []
        total = _find_total_mass(orientation)
        for table in _find_tables(orientation):
            for header, points, method, column in _samples_from_table(table,
                                                                     total):
                if _monotone(points) and all(points != f[1] for f in found):
                    found.append((header, points, method, column))
        if sum(len(f[1]) for f in found) > sum(len(b[1]) for b in best):
            best, best_grid = found, orientation
    if not best:
        return []
    meta = _metadata(grid, set())
    out, seen = [], set()
    for header, points, method, column in best:
        key = tuple(points)
        if key in seen:
            continue
        seen.add(key)
        sample_meta = dict(meta)
        if len(best) > 1 and column is not None:
            for k in ("liquid_limit", "plastic_limit", "ll_brine",
                      "ll_kerosene", "e_max_gravel", "e_min_gravel",
                      "e_max_sand", "e_min_sand"):
                sample_meta.pop(k, None)
            sample_meta.update(_column_limits(best_grid, column))
            sample_meta.pop("name", None)
        if sheet_name and "name" not in sample_meta and len(best) == 1:
            sample_meta["_sheet"] = sheet_name
        out.append((header, points, method, sample_meta))
    return out


def to_parsed(samples, source: str) -> List[ParsedData]:
    parsed = []
    for header, points, method, meta in samples:
        data = ParsedData(source=source)
        data.sieve = list(points)
        data.liquid_limit = meta.get("liquid_limit")
        data.plastic_limit = meta.get("plastic_limit")
        data.meta = {k: v for k, v in meta.items()
                     if k not in ("liquid_limit", "plastic_limit")}
        label = header.strip()
        if label and len(samples) > 1:
            data.meta["name"] = label
        data.meta["_method"] = method
        parsed.append(validate(data))
    return parsed


def method_label(method: Optional[str]) -> str:
    if not method:
        return ""
    return t(f"import_method_{method}")
