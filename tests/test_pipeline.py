import csv
from pathlib import Path

from solv_scraper.affinity_export import run_affinity_export
from solv_scraper.filter_club import run_filter
from solv_scraper.merge import run_merge


def test_merge_filter_affinity(tmp_path):
    data_dir = tmp_path / "downloaded-data"
    data_dir.mkdir()
    csv_content = (
        "Kategorie;Laenge;Steigung;PoAnz;Rang;Name;Jahrgang;Ort;Club;Zeit\n"
        "H40;5.3;0;22;3;Test Runner;40;Appenzell;OLG St. Gallen/App.;1:00:00\n"
    ).encode("iso-8859-1")
    csv_path = data_dir / "2026-01-01-test-ol.csv"
    csv_path.write_bytes(csv_content)
    meta = {
        "event_name": "Test OL",
        "event_date": "2026-01-01",
        "event_location": "Test Area",
        "filename": csv_path.name,
    }
    (data_dir / f"{csv_path.name}.meta.json").write_text(
        __import__("json").dumps(meta),
        encoding="utf-8",
    )

    run_merge(tmp_path)
    run_filter(tmp_path)
    run_affinity_export(tmp_path)

    agg_dir = tmp_path / "aggregated-data"
    master = agg_dir / "master-2026.csv"
    top_ten = agg_dir / "master-top-ten.csv"
    affinity = agg_dir / "master-affinity.txt"
    assert master.exists()
    with master.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    with top_ten.open(encoding="utf-8") as handle:
        top_rows = list(csv.DictReader(handle))
    assert len(top_rows) == 1
    assert top_rows[0]["rank"] == "3"
    assert "\t" in affinity.read_text(encoding="utf-8")
