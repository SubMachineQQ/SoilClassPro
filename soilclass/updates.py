from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass
from typing import Optional, Tuple

from .version import __version__

GITHUB_REPO = "batuhanbarisdoger/SoilClassPro"
API_URL = "https://api.github.com/repos/{repo}/releases/latest"


@dataclass
class Release:
    version: str
    url: str


def parse_version(text: str) -> Tuple[int, ...]:
    numbers = re.findall(r"\d+", text or "")
    parts = [int(n) for n in numbers[:3]]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def is_newer(latest: str, current: str = __version__) -> bool:
    return parse_version(latest) > parse_version(current)


def fetch_latest(repo: str = GITHUB_REPO, timeout: float = 4.0) -> Optional[Release]:
    if not repo:
        return None
    request = urllib.request.Request(
        API_URL.format(repo=repo),
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "SoilClassPro-update-check"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError):
        return None
    tag = str(data.get("tag_name") or "")
    url = str(data.get("html_url") or "")
    if not tag or not url.startswith("https://github.com/"):
        return None
    return Release(tag.lstrip("vV"), url)


def check_for_update(repo: str = GITHUB_REPO) -> Optional[Release]:
    release = fetch_latest(repo)
    if release is not None and is_newer(release.version):
        return release
    return None
