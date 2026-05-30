"""Match orienteering club names for OLG St.Gallen/Appenzell (OLGSGA)."""

from __future__ import annotations

from solv_scraper.utils import normalize_text

OLGSGA_PATTERNS = [
    "olg st gallen",
    "olg st.gallen",
    "olgsga",
    "olg sga",
    "st gallen/appenzell",
    "st.gallen/appenzell",
    "st gallen-appenzell",
    "st.gallen-appenzell",
    "st gallen/app",
    "st.gallen/app",
]


def is_olgsga(club: str) -> bool:
    if not club:
        return False
    normalized = normalize_text(club)
    return any(pattern in normalized for pattern in OLGSGA_PATTERNS)
