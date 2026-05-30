from pathlib import Path

from solv_scraper.parse_relay import parse_relay_csv
from solv_scraper.parse_standard import parse_standard_csv

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_standard_sample():
    content = (FIXTURES / "standard_sample.csv").read_bytes().decode("iso-8859-1")
    rows = parse_standard_csv(
        content,
        event_name="52. Galgener OL",
        event_date="2026-05-17",
        event_location="Hoch Ybrig Nord",
        source_file="2026-05-17-galgener-ol.csv",
    )
    assert len(rows) == 3
    olgsga = [r for r in rows if "Gallen" in r["club"]]
    assert len(olgsga) == 2
    assert olgsga[0]["rank"] == 1
    assert olgsga[0]["year_of_birth"] == "60"


def test_parse_relay_sample():
    content = (FIXTURES / "relay_sample.csv").read_bytes().decode("iso-8859-1")
    rows = parse_relay_csv(
        content,
        event_name="Schweizer Sprint-Staffel-Meisterschaft",
        event_date="2026-05-09",
        event_location="",
        source_file="2026-05-09-schweizer-sprint-staffel-meisterschaft.csv",
    )
    assert len(rows) == 2
    team1 = rows[0]
    assert team1["category"] == "SS12"
    assert team1["rank"] == 1
    assert "Gfeller" in team1["name"]
    assert "Wegm" in team1["name"]
    olgsga = rows[1]
    assert olgsga["rank"] == 13
    assert "Gallen" in olgsga["club"]
