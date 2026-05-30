from pathlib import Path

from solv_scraper.csv_format import detect_csv_format
from solv_scraper.merge import merge_file
from solv_scraper.parse_relay_compact import parse_relay_compact_csv
from solv_scraper.parse_team import parse_team_csv

FIXTURES = Path(__file__).parent / "fixtures"


def test_detect_formats():
    assert detect_csv_format((FIXTURES / "standard_sample.csv").read_text()) == "standard"
    assert detect_csv_format((FIXTURES / "team_sample.csv").read_text()) == "team"
    assert detect_csv_format((FIXTURES / "relay_sample.csv").read_text()) == "relay_block"
    assert (
        detect_csv_format((FIXTURES / "relay_compact_sample.csv").read_text())
        == "relay_compact"
    )
    assert (
        detect_csv_format((FIXTURES / "relay_compact_staffel_sample.csv").read_text())
        == "relay_compact"
    )


def test_parse_team_sample():
    content = (FIXTURES / "team_sample.csv").read_text(encoding="utf-8")
    rows = parse_team_csv(
        content,
        event_name="Schweizermeisterschaft Team-OL",
        event_date="2024-11-03",
        event_location="",
        source_file="2024-11-03-schweizermeisterschaft-team-ol.csv",
    )
    assert len(rows) == 1
    assert rows[0]["name"] == "Matti Baechi, Theo Manser, Tobias Maier"
    assert rows[0]["year_of_birth"] == "14, 15, 14"
    assert "SGA" in rows[0]["club"]


def test_parse_relay_compact_sample():
    content = (FIXTURES / "relay_compact_sample.csv").read_text(encoding="utf-8")
    rows = parse_relay_compact_csv(
        content,
        event_name="Harzer-Staffel",
        event_date="2025-09-20",
        event_location="",
        source_file="2025-09-20-harzer-staffel.csv",
    )
    assert len(rows) == 1
    assert rows[0]["rank"] == 4
    assert "Jonas Vogel" in rows[0]["name"]
    assert rows[0]["year_of_birth"] == "06, 62, 04"


def test_parse_staffel_compact_sample():
    content = (FIXTURES / "relay_compact_staffel_sample.csv").read_text(encoding="utf-8")
    rows = parse_relay_compact_csv(
        content,
        event_name="Staffel OL Meisterschaften",
        event_date="2025-09-14",
        event_location="Batzberg",
        source_file="2025-09-14-staffel-ol-meisterschaften.csv",
    )
    assert len(rows) == 2
    assert rows[0]["rank"] == 1
    assert "Dario Strugalla" in rows[0]["name"]
    assert rows[0]["club"] == "OL Regio Olten/OL Regio Burgdorf"
    assert rows[0]["time"] == "1:04:26"
    assert rows[1]["name"] == "Matti Baechi, Jari Baechi, Theo Manser"
    assert "Gallen" in rows[1]["club"]


def test_merge_staffel_ol_real():
    staffel = (
        Path(__file__).parent.parent
        / "downloaded-data"
        / "2025-09-14-staffel-ol-meisterschaften.csv"
    )
    if not staffel.exists():
        return
    from solv_scraper.csv_format import detect_csv_format

    assert detect_csv_format(staffel.read_bytes().decode("iso-8859-1")) == "relay_compact"
    rows = merge_file(staffel)
    assert len(rows) >= 350
    assert all(r.get("name") for r in rows)
    assert "22:53" not in rows[0]["club"]


def test_merge_team_file_real():
    team_file = (
        Path(__file__).parent.parent
        / "downloaded-data"
        / "2024-11-03-schweizermeisterschaft-team-ol.csv"
    )
    if not team_file.exists():
        return
    rows = merge_file(team_file)
    olgsga = [r for r in rows if "SGA" in r.get("club", "") or "Gallen" in r.get("club", "")]
    assert olgsga
    assert ", " in olgsga[0]["name"]
    assert olgsga[0]["year_of_birth"]
