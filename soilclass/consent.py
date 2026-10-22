from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

from .version import __version__

DISCLAIMER_VERSION = 1
CONSENT_FILE = Path.home() / ".soilclasspro" / "consent.json"


def is_accepted(path: Path | None = None) -> bool:
    path = path or CONSENT_FILE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeDecodeError):
        return False
    if not isinstance(data, dict):
        return False
    version = data.get("disclaimer_version")
    accepted_at = data.get("accepted_at")
    return (type(version) is int and version == DISCLAIMER_VERSION
            and isinstance(accepted_at, str) and bool(accepted_at))


def record_acceptance(path: Path | None = None) -> bool:
    path = path or CONSENT_FILE
    record = {
        "disclaimer_version": DISCLAIMER_VERSION,
        "app_version": __version__,
        "accepted_at": datetime.now().isoformat(timespec="seconds"),
    }
    tmp_name = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=".consent-", suffix=".tmp",
                                        dir=str(path.parent))
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(record, handle, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
        tmp_name = None
    except OSError:
        return False
    finally:
        if tmp_name is not None:
            try:
                os.remove(tmp_name)
            except OSError:
                pass
    return is_accepted(path)
