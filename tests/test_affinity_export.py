from datetime import date

from solv_scraper.affinity_export import format_affinity_text


def test_format_affinity_text_event_and_runner_sort_order():
    rows = [
        {
            "event_date": "2026-05-29",
            "event_name": "Newest Event",
            "event_location": "A",
            "category": "H40",
            "rank": "2",
            "name": "Runner B",
        },
        {
            "event_date": "2026-05-29",
            "event_name": "Newest Event",
            "event_location": "A",
            "category": "H40",
            "rank": "1",
            "name": "Runner A",
        },
        {
            "event_date": "2026-05-29",
            "event_name": "Newest Event",
            "event_location": "A",
            "category": "D60",
            "rank": "5",
            "name": "Runner C",
        },
        {
            "event_date": "2026-04-01",
            "event_name": "Oldest Event",
            "event_location": "B",
            "category": "H40",
            "rank": "1",
            "name": "Runner D",
        },
    ]

    text, event_count = format_affinity_text(
        rows, reference_date=date(2026, 5, 30), months=3
    )

    assert event_count == 2
    blocks = text.strip().split("\n\n")
    assert blocks[0].startswith("Oldest Event")
    assert blocks[-1].startswith("Newest Event")

    newest_lines = blocks[-1].splitlines()
    assert newest_lines[0] == "Newest Event"
    assert newest_lines[1] == "29.05.2026 · A"
    assert newest_lines[2:] == [
        "D60\t5.\tRunner C",
        "H40\t1.\tRunner A",
        "H40\t2.\tRunner B",
    ]
