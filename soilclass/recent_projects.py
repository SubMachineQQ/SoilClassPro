from __future__ import annotations

import json
from pathlib import Path
from typing import List

STORE_DIR = Path.home() / ".soilclasspro"
STORE_FILE = STORE_DIR / "recent_projects.json"
MAX_ITEMS = 8


def get_recent() -> List[str]:
    try:
        data = json.loads(STORE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    paths = [p for p in data.get("recent", []) if Path(p).is_file()]
    return paths[:MAX_ITEMS]


def add_recent(path: str) -> None:
    resolved = str(Path(path).resolve())
    items = [p for p in get_recent() if p != resolved]
    items.insert(0, resolved)
    items = items[:MAX_ITEMS]
    try:
        STORE_DIR.mkdir(parents=True, exist_ok=True)
        STORE_FILE.write_text(json.dumps({"recent": items}, indent=2),
                              encoding="utf-8")
    except OSError:
        pass
