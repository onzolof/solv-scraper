"""Export recent OLGSGA top-10 results for Affinity copy-paste."""

from __future__ import annotations

import calendar
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

from solv_scraper.utils import aggregated_data_dir, project_root

AFFINITY_MONTHS = 4


def _months_ago(from_date: date, months: int) -> date:
    month = from_date.month - months
    year = from_date.year
    while month <= 0:
        month += 12
        year -= 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(from_date.day, last_day)
    return date(year, month, day)


def _parse_event_date(value: str) -> date | None:
    value = (value or "").strip()
    if len(value) < 10:
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _format_display_date(event_date: str) -> str:
    parsed = _parse_event_date(event_date)
    if not parsed:
        return event_date
    return f"{parsed.day:02d}.{parsed.month:02d}.{parsed.year}"


def _format_date_location_line(event_date: str, location: str) -> str:
    display_date = _format_display_date(event_date)
    loc = (location or "").strip()
    if loc:
        return f"{display_date} · {loc}"
    return display_date


def _result_sort_key(row: dict[str, str]) -> tuple[str, int]:
    category = (row.get("category") or "").strip()
    rank_str = (row.get("rank") or "").strip()
    rank = int(rank_str) if rank_str.isdigit() else 99
    return category, rank


def format_affinity_text(
    rows: list[dict[str, str]],
    *,
    reference_date: date | None = None,
    months: int = AFFINITY_MONTHS,
) -> str:
    """Build Affinity-friendly text from top-ten rows."""
    today = reference_date or date.today()
    cutoff = _months_ago(today, months)

    recent = [
        row
        for row in rows
        if (parsed := _parse_event_date(row.get("event_date", ""))) and parsed >= cutoff
    ]

    by_event: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in recent:
        key = (
            (row.get("event_date") or "").strip(),
            (row.get("event_name") or "").strip(),
            (row.get("event_location") or "").strip(),
        )
        by_event[key].append(row)

    event_keys = sorted(
        by_event,
        key=lambda k: (k[0], k[1]),
        reverse=True,
    )

    blocks: list[str] = []
    for event_date, event_name, event_location in event_keys:
        event_rows = sorted(by_event[(event_date, event_name, event_location)], key=_result_sort_key)
        lines = [
            event_name,
            _format_date_location_line(event_date, event_location),
            "",
        ]
        for row in event_rows:
            category = (row.get("category") or "").strip()
            rank = (row.get("rank") or "").strip()
            name = (row.get("name") or "").strip()
            lines.append(f"{category}\t{rank}.\t{name}")
        blocks.append("\n".join(lines))

    body = "\n\n".join(blocks) + ("\n" if blocks else "")
    return body, len(event_keys)


def run_affinity_export(
    root: Path | None = None,
    *,
    reference_date: date | None = None,
    months: int = AFFINITY_MONTHS,
) -> Path:
    root = root or project_root()
    output_dir = aggregated_data_dir(root)
    input_path = output_dir / "master-top-ten.csv"
    output_path = output_dir / "master-affinity.txt"

    with input_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    text, event_count = format_affinity_text(
        rows, reference_date=reference_date, months=months
    )
    output_path.write_text(text, encoding="utf-8")

    print(
        f"Wrote {event_count} events ({len(text.splitlines())} lines, "
        f"last {months} months) to {output_path}"
    )
    return output_path
