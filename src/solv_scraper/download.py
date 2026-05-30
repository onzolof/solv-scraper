"""Download result CSV files from o-l.ch."""

from __future__ import annotations

import json
import re
import time
from dataclasses import asdict
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from solv_scraper.parse_index import EventListing, parse_index_html
from solv_scraper.utils import (
    BASE_URL,
    USER_AGENT,
    downloaded_data_dir,
    slugify_event_name,
)

INDEX_URL = BASE_URL + "results?type=rang&kind=all&csv=1&year={year}"
DOWNLOAD_DELAY_SEC = 0.3


def _session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    return session


def fetch_event_location(session: requests.Session, result_event_id: str) -> str:
    """Fetch map/area name from linked fixture page."""
    results_url = (
        f"{BASE_URL}results?type=rang&result_event_id={result_event_id}&kind=all"
    )
    try:
        response = session.get(results_url, timeout=30)
        response.encoding = "iso-8859-1"
        soup = BeautifulSoup(response.text, "html.parser")
        fixture_link = soup.find("a", href=re.compile(r"fixtures\?mode=show&unique_id=\d+"))
        if not fixture_link:
            return ""
        fixture_href = fixture_link["href"]
        fixture_url = fixture_href if fixture_href.startswith("http") else (
            "https://o-l.ch" + fixture_href if fixture_href.startswith("/") else BASE_URL + fixture_href
        )
        fixture_resp = session.get(fixture_url, timeout=30)
        fixture_resp.encoding = "iso-8859-1"
        fixture_soup = BeautifulSoup(fixture_resp.text, "html.parser")
        for row in fixture_soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2 and cells[0].get_text(strip=True).startswith("Karte"):
                return cells[1].get_text(strip=True)
    except requests.RequestException:
        return ""
    return ""


def event_filename(event: EventListing) -> str:
    slug = slugify_event_name(event.event_name)
    return f"{event.event_date}-{slug}.csv"


def download_year(
    session: requests.Session,
    year: int,
    data_dir: Path,
    *,
    fetch_locations: bool = True,
) -> tuple[int, int]:
    """Download missing events for a year. Returns (downloaded, skipped)."""
    url = INDEX_URL.format(year=year)
    response = session.get(url, timeout=60)
    response.encoding = "iso-8859-1"
    events = parse_index_html(response.text)

    downloaded = 0
    skipped = 0

    for event in events:
        filename = event_filename(event)
        csv_path = data_dir / filename
        meta_path = data_dir / f"{filename}.meta.json"

        if csv_path.exists():
            skipped += 1
            print(f"Skipped (exists): {filename} — {event.event_name}")
            continue

        csv_response = session.get(event.csv_url, timeout=60)
        csv_response.encoding = "iso-8859-1"
        csv_path.write_bytes(csv_response.content)

        location = ""
        if fetch_locations:
            location = fetch_event_location(session, event.result_event_id)
            time.sleep(DOWNLOAD_DELAY_SEC)

        meta = {
            **asdict(event),
            "filename": filename,
            "event_location": location,
        }
        meta_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        downloaded += 1
        print(f"Downloaded: {filename} — {event.event_name}")
        time.sleep(DOWNLOAD_DELAY_SEC)

    return downloaded, skipped


def run_download(year: int, root: Path | None = None, *, fetch_locations: bool = True) -> None:
    data_dir = downloaded_data_dir(root)
    session = _session()
    years = [year, year - 1]
    total_downloaded = 0
    total_skipped = 0

    for y in years:
        downloaded, skipped = download_year(
            session, y, data_dir, fetch_locations=fetch_locations
        )
        total_downloaded += downloaded
        total_skipped += skipped
        print(f"Year {y}: downloaded {downloaded}, skipped {skipped}")

    print(f"Total: downloaded {total_downloaded}, skipped {total_skipped}")
