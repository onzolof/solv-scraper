"""Command-line interface for the SOLV results scraper."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from solv_scraper.affinity_export import run_affinity_export
from solv_scraper.download import run_download
from solv_scraper.filter_club import run_filter
from solv_scraper.merge import run_merge
from solv_scraper.utils import project_root


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Download and aggregate Swiss orienteering results from o-l.ch",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=date.today().year,
        help="Target year (also downloads previous year). Default: current year.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: auto-detect)",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Skip download step; only merge and filter existing data",
    )
    parser.add_argument(
        "--skip-location-fetch",
        action="store_true",
        help="Do not fetch fixture pages for event location during download",
    )
    args = parser.parse_args(argv)
    root = args.root or project_root()

    if not args.skip_download:
        run_download(
            args.year,
            root,
            fetch_locations=not args.skip_location_fetch,
        )
    run_merge(root)
    run_filter(root)
    run_affinity_export(root)


if __name__ == "__main__":
    main()
