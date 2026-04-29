from __future__ import annotations

from pathlib import Path

from scripts.analyze_n8_fragile_covers import analyze_survivors


def test_n8_survivors_all_admit_incidence_fragile_cover() -> None:
    root = Path(__file__).resolve().parents[1]
    survivors = root / "data" / "incidence" / "n8_reconstructed_15_survivors.json"

    data = analyze_survivors(survivors)

    assert data["survivor_classes"] == 15
    assert data["all_survivors_admit_incidence_fragile_cover"] is True
    assert data["min_cover_size_distribution"] == {"2": 6, "3": 9}


def test_n8_class0_has_four_two_row_fragile_covers() -> None:
    root = Path(__file__).resolve().parents[1]
    survivors = root / "data" / "incidence" / "n8_reconstructed_15_survivors.json"

    data = analyze_survivors(survivors)
    class0 = data["classes"][0]

    assert class0["class_id"] == 0
    assert class0["min_cover_size"] == 2
    assert class0["cover_counts_by_size"]["2"] == 4
    assert [0, 4] in class0["example_covers_by_size"]["2"]
