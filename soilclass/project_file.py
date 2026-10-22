from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple, Union

from .models import SoilSample

FORMAT_NAME = "soilclasspro-project"
FORMAT_VERSION = 2

_LEGACY_MODES = {"TS1500": "ISO14688"}


def save_project(path: Union[str, Path], sample: SoilSample, mode: str) -> str:
    data = {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,
        "mode": mode,
        "sample": {
            "name": sample.name,
            "project": sample.project,
            "location": sample.location,
            "operator": sample.operator,
            "date": sample.date,
            "liquid_limit": sample.liquid_limit,
            "plastic_limit": sample.plastic_limit,
            "organic": sample.organic,
            "sieve_data": [[d, p] for d, p in sample.sieve_data],
            "e_max_gravel": sample.e_max_gravel,
            "e_min_gravel": sample.e_min_gravel,
            "e_max_sand": sample.e_max_sand,
            "e_min_sand": sample.e_min_sand,
            "roundness_gravel": sample.roundness_gravel,
            "cu_gravel": sample.cu_gravel,
            "roundness_sand": sample.roundness_sand,
            "cu_sand": sample.cu_sand,
            "ll_brine": sample.ll_brine,
            "ll_kerosene": sample.ll_kerosene,
            "rscs_enabled": sample.rscs_enabled,
        },
    }
    p = Path(path)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return str(p)


def load_project(path: Union[str, Path]) -> Tuple[SoilSample, str]:
    p = Path(path)
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"Could not read '{p.name}': {exc}") from exc

    if data.get("format") != FORMAT_NAME:
        raise ValueError(
            f"'{p.name}' is not a recognised SoilClass Pro project file.")

    s = data.get("sample", {})
    sample = SoilSample(
        name=s.get("name", "Sample 1"),
        sieve_data=[tuple(pair) for pair in s.get("sieve_data", [])],
        liquid_limit=s.get("liquid_limit"),
        plastic_limit=s.get("plastic_limit"),
        organic=bool(s.get("organic", False)),
        project=s.get("project", ""),
        location=s.get("location", ""),
        operator=s.get("operator", ""),
        date=s.get("date", ""),
        e_max_gravel=s.get("e_max_gravel"),
        e_min_gravel=s.get("e_min_gravel"),
        e_max_sand=s.get("e_max_sand"),
        e_min_sand=s.get("e_min_sand"),
        roundness_gravel=s.get("roundness_gravel"),
        cu_gravel=s.get("cu_gravel"),
        roundness_sand=s.get("roundness_sand"),
        cu_sand=s.get("cu_sand"),
        ll_brine=s.get("ll_brine"),
        ll_kerosene=s.get("ll_kerosene"),
    )
    mode = data.get("mode", "ALL")
    rscs_keys = ("e_max_gravel", "e_min_gravel", "e_max_sand", "e_min_sand",
                 "roundness_gravel", "cu_gravel", "roundness_sand", "cu_sand",
                 "ll_brine", "ll_kerosene")
    sample.rscs_enabled = bool(s.get(
        "rscs_enabled",
        mode == "RSCS" or any(s.get(k) is not None for k in rscs_keys)))
    mode = _LEGACY_MODES.get(mode, mode)
    return sample, mode
