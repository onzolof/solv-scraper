"""Parse team-event semicolon CSV (Name / Name2 / Name3 columns)."""

from __future__ import annotations

import csv
import json
from io import StringIO
from typing import Any

from solv_scraper.utils import parse_rank

NAME_COLUMNS = ("Name", "Name2", "Name3", "Name4", "Name5")


def _birth_year_column(name_col: str) -> str:
    if name_col == "Name":
        return "Jg"
    return name_col.replace("Name", "Jg")


def _collect_members(row: dict[str, str]) -> tuple[list[str], list[str]]:
    names: list[str] = []
    years: list[str] = []
    for name_col in NAME_COLUMNS:
        if name_col != "Name" and name_col not in row:
            break
        name = (row.get(name_col) or "").strip()
        if not name or name == "-":
            continue
        year = (row.get(_birth_year_column(name_col)) or "").strip()
        names.append(name)
        if year:
            years.append(year)
    return names, years


def parse_team_csv(
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
        names, years = _collect_members(row)
        meta = {
            "format": "team",
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
                "name": ", ".join(names),
                "year_of_birth": ", ".join(years),
                "runner_location": (row.get("Ort") or "").strip(),
                "club": (row.get("Club") or "").strip(),
                "time": (row.get("Zeit") or "").strip(),
                "source_file": source_file,
            }
        )
    return rows
