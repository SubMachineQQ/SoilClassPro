from __future__ import annotations

from datetime import date
from typing import Optional

from .i18n import get_language

AUTHORS = (
    "Batuhan Barış Döğer",
    "Erol Boz",
    "Furkan Kağan Ekici",
)
ACKNOWLEDGED = "Nejan Huvaj"
COPYRIGHT_YEAR = 2026
LICENSE_NAME = "MIT"

_MONTHS = {
    "en": ("January", "February", "March", "April", "May", "June", "July",
           "August", "September", "October", "November", "December"),
    "tr": ("Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
           "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"),
}


def format_date(day: Optional[date] = None, lang: Optional[str] = None) -> str:
    day = day or date.today()
    months = _MONTHS.get(lang or get_language(), _MONTHS["en"])
    return f"{day.day} {months[day.month - 1]} {day.year}"


def short_authors() -> str:
    return ", ".join(name.split()[-1] for name in AUTHORS)
