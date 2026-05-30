"""Export master-top-ten.csv as tab-separated text for Affinity."""

from __future__ import annotations

import csv
from pathlib import Path

from solv_scraper.utils import MASTER_COLUMNS, aggregated_data_dir, project_root


def run_affinity_export(root: Path | None = None) -> Path:
    root = root or project_root()
    output_dir = aggregated_data_dir(root)
    input_path = output_dir / "master-top-ten.csv"
    output_path = output_dir / "master-affinity.txt"

    with input_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=MASTER_COLUMNS,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {output_path}")
    return output_path
