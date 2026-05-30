"""Merge downloaded CSV files into per-year master files."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from solv_scraper.csv_format import detect_csv_format
from solv_scraper.parse_relay import parse_relay_csv
from solv_scraper.parse_relay_compact import parse_relay_compact_csv
from solv_scraper.parse_standard import parse_standard_csv
from solv_scraper.parse_team import parse_team_csv
from solv_scraper.utils import (
    MASTER_COLUMNS,
    aggregated_data_dir,
    project_root,
)


def _load_meta(meta_path: Path, csv_path: Path) -> dict[str, Any]:
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))

    stem = csv_path.stem
    event_date = stem[:10] if len(stem) >= 10 else ""
    slug = stem[11:] if len(stem) > 11 else stem
    return {
        "event_name": slug.replace("-", " "),
        "event_date": event_date,
        "event_location": "",
        "filename": csv_path.name,
    }


def merge_file(csv_path: Path) -> list[dict[str, Any]]:
    meta_path = csv_path.with_suffix(csv_path.suffix + ".meta.json")
    meta = _load_meta(meta_path, csv_path)
    content = csv_path.read_bytes().decode("iso-8859-1", errors="replace")

    event_name = meta.get("event_name", "")
    event_date = meta.get("event_date", "")
    event_location = meta.get("event_location", "")
    source_file = meta.get("filename", csv_path.name)

    kwargs = {
        "event_name": event_name,
        "event_date": event_date,
        "event_location": event_location,
        "source_file": source_file,
    }

    fmt = detect_csv_format(content)
    if fmt == "standard":
        return parse_standard_csv(content, **kwargs)
    if fmt == "team":
        return parse_team_csv(content, **kwargs)
    if fmt == "relay_block":
        return parse_relay_csv(content, **kwargs)
    if fmt == "relay_compact":
        return parse_relay_compact_csv(content, **kwargs)

    print(f"Warning: unknown CSV format in {csv_path.name}, skipping")
    return []


def run_merge(root: Path | None = None) -> list[Path]:
    root = root or project_root()
    data_dir = root / "downloaded-data"
    output_dir = aggregated_data_dir(root)

    all_rows: list[dict[str, Any]] = []
    for csv_path in sorted(data_dir.glob("*.csv")):
        if csv_path.name.startswith("."):
            continue
        rows = merge_file(csv_path)
        all_rows.extend(rows)

    by_year: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in all_rows:
        event_date = (row.get("event_date") or "").strip()
        year = event_date[:4] if len(event_date) >= 4 and event_date[:4].isdigit() else "unknown"
        by_year[year].append(row)

    written_paths: list[Path] = []
    for year in sorted(by_year):
        output_path = output_dir / f"master-{year}.csv"
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=MASTER_COLUMNS, extrasaction="ignore")
            writer.writeheader()
            for row in by_year[year]:
                rank = row.get("rank")
                row["rank"] = "" if rank is None else str(rank)
                writer.writerow(row)
        written_paths.append(output_path)
        print(f"Wrote {len(by_year[year])} rows to {output_path}")

    return written_paths
