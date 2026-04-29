from __future__ import annotations

from pathlib import Path

from scripts.analyze_n8_metric_fragility import analyze_survivors


def test_n8_metric_fragility_probe_fingerprints() -> None:
    root = Path(__file__).resolve().parents[1]
    survivors = root / "data" / "incidence" / "n8_reconstructed_15_survivors.json"

    data = analyze_survivors(survivors)

    assert data["survivor_classes"] == 15
    assert data["selected_ed_inconsistent_classes"] == list(range(14))
    assert data["selected_ed_consistent_classes"] == [14]
    assert data["consistent_classes_with_eligible_fragile_cover"] == [14]


def test_class14_has_no_forced_alternate_fourcohort() -> None:
    root = Path(__file__).resolve().parents[1]
    survivors = root / "data" / "incidence" / "n8_reconstructed_15_survivors.json"

    data = analyze_survivors(survivors)
    class14 = data["classes"][14]

    assert class14["class_id"] == 14
    assert class14["selected_ed_ideal_inconsistent"] is False
    assert class14["algebraically_forced_nonfragile_rows"] == []
    assert class14["eligible_rows_cover_all_vertices"] is True
    assert class14["eligible_min_cover_size"] == 3
