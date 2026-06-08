from pathlib import Path

from solv_scraper.parse_index import parse_index_html
from solv_scraper.utils import parse_german_date, slugify_event_name


FIXTURES = Path(__file__).parent / "fixtures"


# All month name variants observed on o-l.ch (2020–2026 index pages).
O_L_CH_MONTH_SAMPLES = [
    ("26. Jan. 2020", "2020-01-26"),
    ("28. Feb. 2020", "2020-02-28"),
    ("8. März 2020", "2020-03-08"),
    ("27. Apr. 2021", "2021-04-27"),
    ("30. Mai 2021", "2021-05-30"),
    ("30. Juni 2020", "2020-06-30"),
    ("31. Juli 2020", "2020-07-31"),
    ("30. Aug. 2020", "2020-08-30"),
    ("30. Sep. 2020", "2020-09-30"),
    ("25. Okt. 2020", "2020-10-25"),
    ("7. Nov. 2020", "2020-11-07"),
    ("5. Dez. 2020", "2020-12-05"),
]


def test_parse_german_date():
    assert parse_german_date("17. Mai 2026") == "2026-05-17"
    assert parse_german_date("29. Apr. 2026") == "2026-04-29"


def test_parse_german_date_all_o_l_ch_months():
    for date_str, expected in O_L_CH_MONTH_SAMPLES:
        assert parse_german_date(date_str) == expected, date_str


def test_parse_german_date_full_month_names():
    """Defensive coverage for full German month names not yet seen on o-l.ch."""
    for month, num in [
        ("Januar", 1),
        ("Februar", 2),
        ("April", 4),
        ("August", 8),
        ("September", 9),
        ("Oktober", 10),
        ("November", 11),
        ("Dezember", 12),
    ]:
        assert parse_german_date(f"1. {month} 2024") == f"2024-{num:02d}-01"


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


def test_parse_index_june_and_march():
    html = (FIXTURES / "index_june_snippet.html").read_text(encoding="utf-8")
    events = parse_index_html(html)
    assert len(events) == 2
    assert events[0].result_event_id == "3948"
    assert events[0].event_date == "2026-06-07"
    assert events[0].event_name == "48. Wisliger OL"
    assert events[1].result_event_id == "3864"
    assert events[1].event_date == "2026-03-01"
    assert events[1].event_name == "18. Stöff Memorial OL"


def test_parse_index_name_only_in_anchor():
    """Some events put the full title in the link text with only a date after it."""
    html = (FIXTURES / "index_name_in_anchor_snippet.html").read_text(encoding="utf-8")
    events = parse_index_html(html)
    assert len(events) == 1
    assert events[0].result_event_id == "2808"
    assert events[0].event_date == "2021-04-09"
    assert events[0].event_name == "1. Milchsuppe-Abend OL"
