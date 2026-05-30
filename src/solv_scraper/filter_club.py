"""Filter per-year master files to OLGSGA top-10 results."""

from __future__ import annotations

import csv
from pathlib import Path

from solv_scraper.club_match import is_olgsga
from solv_scraper.utils import (
    MASTER_COLUMNS,
    aggregated_data_dir,
    iter_master_year_files,
    project_root,
)


def run_filter(root: Path | None = None) -> Path:
    root = root or project_root()
    output_dir = aggregated_data_dir(root)
    output_path = output_dir / "master-top-ten.csv"

    filtered: list[dict[str, str]] = []
    for master_path in iter_master_year_files(root):
        with master_path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rank_str = (row.get("rank") or "").strip()
                if not rank_str.isdigit():
                    continue
                rank = int(rank_str)
                if rank < 1 or rank > 10:
                    continue
                if not is_olgsga(row.get("club", "")):
                    continue
                filtered.append(row)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MASTER_COLUMNS)
        writer.writeheader()
        writer.writerows(filtered)

    print(f"Wrote {len(filtered)} rows to {output_path}")
    return output_path
