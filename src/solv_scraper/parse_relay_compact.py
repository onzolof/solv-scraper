"""Parse compact relay CSV (single-line team header + runner line)."""

from __future__ import annotations

import json
import re
from typing import Any

from solv_scraper.utils import parse_rank

# e.g. HS;0.0;0;0;  1. CA Rosé ...
LINE1_META_RE = re.compile(
    r"^([A-Za-z0-9*]+);([^;]*);([^;]*);([^;]*);\s*(?:(\d+)\.\s+)?(.*)$",
)
# e.g. H12;;  1. OL Regio Olten ...  (Staffel OL Meisterschaften)
LINE1_SHORT_RE = re.compile(
    r"^([A-Za-z0-9*]+);;\s*(?:(\d+)\.\s+)?(.*)$",
)
FIRST_TIME_RE = re.compile(
    r"((?:\d+:)?\d{1,2}:\d{2}|n\.klas\.|dnf|dns)",
    re.IGNORECASE,
)
RUNNER_YEAR_RE = re.compile(
    r"([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\-\'\. ]+?)\s+(\d{2})(?=\s{2,}|\s*$)",
)


def _is_header_line(line: str) -> bool:
    return bool(LINE1_META_RE.match(line) or LINE1_SHORT_RE.match(line))


def _parse_team_header_line(line: str) -> tuple[str, int | None, str, str] | None:
    match = LINE1_META_RE.match(line) or LINE1_SHORT_RE.match(line)
    if not match:
        return None

    if LINE1_META_RE.match(line):
        category = match.group(1)
        rank = parse_rank(match.group(5) or "")
        remainder = match.group(6)
    else:
        category = match.group(1)
        rank = parse_rank(match.group(2) or "")
        remainder = match.group(3)

    time_match = FIRST_TIME_RE.search(remainder)
    if not time_match:
        return None
    club = remainder[: time_match.start()].strip()
    time_val = time_match.group(1)
    return category, rank, club, time_val


def _parse_runners_line(line: str) -> tuple[list[str], list[str]]:
    names: list[str] = []
    years: list[str] = []
    for match in RUNNER_YEAR_RE.finditer(line):
        name = match.group(1).strip()
        year = match.group(2)
        if name and name.lower() != "vakant":
            names.append(name)
            years.append(year)
    return names, years


def parse_relay_compact_csv(
    content: str,
    *,
    event_name: str,
    event_date: str,
    event_location: str,
    source_file: str,
) -> list[dict[str, Any]]:
    lines = [line for line in content.splitlines() if line.strip()]
    rows: list[dict[str, Any]] = []
    i = 0

    while i < len(lines):
        parsed = _parse_team_header_line(lines[i])
        if not parsed:
            i += 1
            continue

        category, rank, club, time_val = parsed
        names: list[str] = []
        years: list[str] = []
        if i + 1 < len(lines) and not _is_header_line(lines[i + 1]):
            names, years = _parse_runners_line(lines[i + 1])
            i += 2
        else:
            i += 1

        rows.append(
            {
                "event_name": event_name,
                "event_date": event_date,
                "event_location": event_location,
                "event_meta": json.dumps({"format": "relay_compact"}, ensure_ascii=False),
                "category": category,
                "rank": rank,
                "name": ", ".join(names),
                "year_of_birth": ", ".join(years),
                "runner_location": "",
                "club": club,
                "time": time_val,
                "source_file": source_file,
            }
        )

    return rows
