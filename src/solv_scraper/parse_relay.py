"""Parse relay/staffel multi-line result CSV files."""

from __future__ import annotations

import json
import re
from typing import Any

from solv_scraper.utils import parse_rank

BLOCK_START_RE = re.compile(r"^([A-Z0-9]+);;")
HEADER_RE = re.compile(
    r"^\s*(\d+)\.\s+(.+?)\s+((?:\d+:)?\d{1,2}:\d{2}|n\.klas\.|dns|dnf)\s*$",
    re.IGNORECASE,
)
RUNNER_RE = re.compile(
    r"([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\-\+' ]+?)\s+\d+:\d+",
)


def _strip_html(text: str) -> str:
    return text.replace("<b>", "").replace("</b>", "").strip()


def _extract_runners(line: str) -> list[str]:
    names: list[str] = []
    for match in RUNNER_RE.finditer(line):
        name = match.group(1).strip()
        if name and name not in names:
            names.append(name)
    return names


def _parse_header_line(line: str) -> tuple[int | None, str, str] | None:
    line = _strip_html(line)
    match = HEADER_RE.search(line)
    if not match:
        return None
    rank = parse_rank(match.group(1))
    club = match.group(2).strip()
    time_val = match.group(3).strip()
    return rank, club, time_val


def parse_relay_csv(
    content: str,
    *,
    event_name: str,
    event_date: str,
    event_location: str,
    source_file: str,
) -> list[dict[str, Any]]:
    lines = content.splitlines()
    rows: list[dict[str, Any]] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        start = BLOCK_START_RE.match(line)
        if not start:
            i += 1
            continue

        category = start.group(1)
        header_part = line[start.end() :]
        parsed = _parse_header_line(header_part)
        if not parsed:
            i += 1
            continue

        rank, club, time_val = parsed
        runners: list[str] = []
        i += 1
        while i < len(lines) and not BLOCK_START_RE.match(lines[i]):
            continuation = lines[i]
            if continuation.strip() and not continuation.strip().startswith("("):
                runners.extend(_extract_runners(continuation))
            i += 1

        deduped: list[str] = []
        for runner in runners:
            if runner not in deduped:
                deduped.append(runner)

        rows.append(
            {
                "event_name": event_name,
                "event_date": event_date,
                "event_location": event_location,
                "event_meta": json.dumps({"format": "relay"}, ensure_ascii=False),
                "category": category,
                "rank": rank,
                "name": ", ".join(deduped),
                "year_of_birth": "",
                "runner_location": "",
                "club": club,
                "time": time_val,
                "source_file": source_file,
            }
        )

    return rows
