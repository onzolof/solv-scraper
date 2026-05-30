from pathlib import Path

from solv_scraper.parse_index import parse_index_html
from solv_scraper.utils import parse_german_date, slugify_event_name


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_german_date():
    assert parse_german_date("17. Mai 2026") == "2026-05-17"
    assert parse_german_date("29. Apr. 2026") == "2026-04-29"


def test_slugify():
    assert slugify_event_name("52. Galgener OL") == "galgener-ol"


def test_parse_index_snippet():
    html = (FIXTURES / "index_snippet.html").read_text(encoding="utf-8")
    events = parse_index_html(html)
    assert len(events) == 2
    assert events[0].result_event_id == "3933"
    assert events[0].event_date == "2026-05-17"
    assert events[0].event_name == "52. Galgener OL"
    assert "result_event_id=3933" in events[0].csv_url
