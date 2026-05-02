from __future__ import annotations

from scripts.find_minimal_stuck_sets import fragile_cover_label


def test_fragile_cover_label_marks_truncated_empty_window() -> None:
    assert (
        fragile_cover_label(
            {
                "status": "SEARCHED",
                "cover_exists": False,
                "search_complete": False,
                "searched_up_to_size": 7,
                "min_cover_size": None,
            }
        )
        == "NONE<=7"
    )


def test_fragile_cover_label_marks_complete_empty_search() -> None:
    assert (
        fragile_cover_label(
            {
                "status": "SEARCHED",
                "cover_exists": False,
                "search_complete": True,
                "searched_up_to_size": 8,
                "min_cover_size": None,
            }
        )
        == "NO"
    )
