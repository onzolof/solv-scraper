"""Parse standard semicolon-separated result CSV files."""

from __future__ import annotations

import csv
import json
from io import StringIO
from typing import Any

from solv_scraper.utils import MASTER_COLUMNS, parse_rank


def parse_standard_csv(
    content: str,
    *,
    event_name: str,
    event_date: str,
    event_location: str,
    source_file: str,
) -> list[dict[str, Any]]:
    reader = csv.DictReader(StringIO(content), delimiter=";")
    if not reader.fieldnames or "Kategorie" not in reader.fieldnames:
        return []

    rows: list[dict[str, Any]] = []
    for row in reader:
        meta = {
            "laenge": row.get("Laenge", ""),
            "steigung": row.get("Steigung", ""),
            "poanz": row.get("PoAnz", ""),
        }
        rows.append(
            {
                "event_name": event_name,
                "event_date": event_date,
                "event_location": event_location,
                "event_meta": json.dumps(meta, ensure_ascii=False),
                "category": (row.get("Kategorie") or "").strip(),
                "rank": parse_rank(row.get("Rang", "")),
                "name": (row.get("Name") or "").strip(),
                "year_of_birth": (row.get("Jahrgang") or "").strip(),
                "runner_location": (row.get("Ort") or "").strip(),
                "club": (row.get("Club") or "").strip(),
                "time": (row.get("Zeit") or "").strip(),
                "source_file": source_file,
            }
        )
    return rows
