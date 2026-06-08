"""Shared helpers for parsing, slugs, and paths."""

from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path

BASE_URL = "https://o-l.ch/cgi-bin/"
USER_AGENT = "solv-scraper/0.1 (Swiss orienteering results; github.com/jonasvogel/solv-scraper)"

# Month keys are matched after lowercasing and UMLAUT_MAP translation (ä→ae, etc.).
# o-l.ch mixes abbreviated names (Jan., Apr., …) with full names (März, Juni, Juli, Mai).
GERMAN_MONTHS = {
    "jan": 1,
    "jan.": 1,
    "januar": 1,
    "feb": 2,
    "feb.": 2,
    "februar": 2,
    "maer": 3,
    "maer.": 3,
    "maerz": 3,
    "mar": 3,
    "mar.": 3,
    "apr": 4,
    "apr.": 4,
    "april": 4,
    "mai": 5,
    "jun": 6,
    "jun.": 6,
    "juni": 6,
    "jul": 7,
    "jul.": 7,
    "juli": 7,
    "aug": 8,
    "aug.": 8,
    "august": 8,
    "sep": 9,
    "sep.": 9,
    "sept": 9,
    "sept.": 9,
    "september": 9,
    "okt": 10,
    "okt.": 10,
    "oktober": 10,
    "nov": 11,
    "nov.": 11,
    "november": 11,
    "dez": 12,
    "dez.": 12,
    "dezember": 12,
}

UMLAUT_MAP = str.maketrans(
    {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "Ä": "ae",
        "Ö": "oe",
        "Ü": "ue",
        "ß": "ss",
    }
)

MASTER_COLUMNS = [
    "event_name",
    "event_date",
    "event_location",
    "event_meta",
    "category",
    "rank",
    "name",
    "year_of_birth",
    "runner_location",
    "club",
    "time",
    "source_file",
]


def project_root() -> Path:
    """Return repository root (parent of downloaded-data when run from repo)."""
    cwd = Path.cwd()
    if (cwd / "downloaded-data").is_dir():
        return cwd
    if (cwd.parent / "downloaded-data").is_dir():
        return cwd.parent
    return cwd


def downloaded_data_dir(root: Path | None = None) -> Path:
    path = (root or project_root()) / "downloaded-data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def aggregated_data_dir(root: Path | None = None) -> Path:
    path = (root or project_root()) / "aggregated-data"
    path.mkdir(parents=True, exist_ok=True)
    return path


MASTER_YEAR_FILE_RE = re.compile(r"^master-\d{4}\.csv$")


def iter_master_year_files(root: Path | None = None) -> list[Path]:
    """Return sorted master-YYYY.csv paths in aggregated-data."""
    data_dir = aggregated_data_dir(root)
    return sorted(
        p for p in data_dir.glob("master-*.csv") if MASTER_YEAR_FILE_RE.match(p.name)
    )


def unescape_html(text: str) -> str:
    return html.unescape(text).strip()


def parse_german_date(text: str) -> str | None:
    """Parse '17. Mai 2026' or '29. Apr. 2026' to YYYY-MM-DD."""
    text = unescape_html(text).strip()
    match = re.match(
        r"(\d{1,2})\.\s*([A-Za-zäöüÄÖÜß.]+)\s+(\d{4})",
        text,
    )
    if not match:
        return None
    day = int(match.group(1))
    month_key = match.group(2).lower().translate(UMLAUT_MAP)
    year = int(match.group(3))
    month = GERMAN_MONTHS.get(month_key)
    if not month:
        return None
    return f"{year:04d}-{month:02d}-{day:02d}"


def slugify_event_name(name: str, max_length: int = 80) -> str:
    """Build filesystem-safe slug from event title."""
    name = unescape_html(name)
    name = re.sub(r"^\d+\.\s*", "", name)
    name = name.translate(UMLAUT_MAP)
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = name.strip("-")
    if len(name) > max_length:
        name = name[:max_length].rstrip("-")
    return name or "event"


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.translate(UMLAUT_MAP)
    text = text.lower()
    text = text.replace(".", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_rank(value: str) -> int | None:
    value = (value or "").strip()
    if not value or not value.isdigit():
        return None
    return int(value)
