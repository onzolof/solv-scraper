"""Parse o-l.ch year index pages for event listings."""

from __future__ import annotations

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup

from solv_scraper.utils import BASE_URL, parse_german_date, unescape_html


@dataclass(frozen=True)
class EventListing:
    result_event_id: str
    short_name: str
    event_date: str
    event_name: str
    csv_url: str


EVENT_LINK_RE = re.compile(
    r'results\?type=rang&result_event_id=(\d+)&kind=all&csv=1',
)


def parse_index_html(html: str) -> list[EventListing]:
    """Extract events from a year index page."""
    soup = BeautifulSoup(html, "html.parser")
    events: list[EventListing] = []
    seen_ids: set[str] = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        match = EVENT_LINK_RE.search(href)
        if not match:
            continue
        event_id = match.group(1)
        if event_id in seen_ids:
            continue

        short_name = unescape_html(anchor.get_text())
        tail = anchor.next_sibling
        if tail is None:
            continue
        tail_text = str(tail)
        parts = re.split(r"\s{2,}", tail_text.strip(), maxsplit=1)
        if not parts:
            continue
        date_str = parts[0].strip()
        event_date = parse_german_date(date_str)
        if not event_date:
            continue

        if len(parts) >= 2 and parts[1].strip():
            full_name = unescape_html(parts[1].strip())
        else:
            full_name = short_name
        csv_url = href if href.startswith("http") else BASE_URL + href.lstrip("/")
        events.append(
            EventListing(
                result_event_id=event_id,
                short_name=short_name,
                event_date=event_date,
                event_name=full_name,
                csv_url=csv_url,
            )
        )
        seen_ids.add(event_id)

    return events
