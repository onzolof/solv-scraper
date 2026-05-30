from datetime import date

from solv_scraper.affinity_export import format_affinity_text


def test_format_affinity_text_last_four_months():
    rows = [
        {
            "event_name": "25. Zuger Frühlings-OL",
            "event_date": "2026-05-25",
            "event_location": "Zug",
            "category": "H16",
            "rank": "1",
            "name": "Tim Meier",
        },
        {
            "event_name": "25. Zuger Frühlings-OL",
            "event_date": "2026-05-25",
            "event_location": "Zug",
            "category": "D14",
            "rank": "2",
            "name": "Mia Keller",
        },
        {
            "event_name": "Old Event",
            "event_date": "2025-01-01",
            "event_location": "Somewhere",
            "category": "H10",
            "rank": "1",
            "name": "Old Runner",
        },
    ]
    text, event_count = format_affinity_text(rows, reference_date=date(2026, 5, 30), months=4)
    assert event_count == 1
    assert "25. Zuger Frühlings-OL" in text
    assert "25.05.2026 · Zug" in text
    assert "D14\t2.\tMia Keller" in text
    assert "H16\t1.\tTim Meier" in text
    assert "Old Event" not in text
    assert "Old Runner" not in text


def test_format_affinity_multiple_events():
    rows = [
        {
            "event_name": "7. TMO GOLD Middle Astano",
            "event_date": "2026-05-24",
            "event_location": "Astano",
            "category": "D35",
            "rank": "4",
            "name": "Sabine Frei",
        },
        {
            "event_name": "25. Zuger Frühlings-OL",
            "event_date": "2026-05-25",
            "event_location": "Zug",
            "category": "H16",
            "rank": "1",
            "name": "Tim Meier",
        },
    ]
    text, _ = format_affinity_text(rows, reference_date=date(2026, 5, 30), months=4)
    zuger_pos = text.index("Zuger")
    tmo_pos = text.index("TMO")
    assert zuger_pos < tmo_pos
