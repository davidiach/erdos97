from __future__ import annotations

import json
from pathlib import Path

from erdos97.n7_fano import (
    all_pointed_fano_complements,
    analyze_n7_witness_pattern,
    cyclic_fano_witnesses,
    enumeration_data,
    enumeration_summary,
    pairwise_intersection_cap,
    pointed_fano_dihedral_classes,
    witnesses_from_complements,
)


def test_cyclic_fano_pattern_is_obstructed_by_odd_cycles() -> None:
    witnesses = cyclic_fano_witnesses()
    assert pairwise_intersection_cap(witnesses) == 2

    analysis = analyze_n7_witness_pattern(witnesses)

    assert analysis.indegrees == (4, 4, 4, 4, 4, 4, 4)
    assert set(analysis.intersection_sizes) == {2}
    assert len(analysis.chord_map) == 21
    assert sorted(analysis.cycle_lengths) == [7, 7, 7]
    assert analysis.has_odd_cycle
    assert not analysis.geometrically_realizable


def test_finite_n7_fano_enumeration_counts() -> None:
    summary = enumeration_summary()

    assert summary["labelled_fano_planes"] == 30
    assert summary["pointed_fano_patterns"] == 720
    assert summary["dihedral_classes"] == 54
    assert summary["dihedral_orbit_size_distribution"] == {"2": 3, "14": 51}
    assert summary["cycle_type_counts"] == {"7+7+7": 54}
    assert summary["all_pattern_cycle_type_counts"] == {"7+7+7": 720}
    assert summary["classes_with_odd_perpendicularity_cycle"] == 54
    assert summary["all_classes_obstructed"] is True


def test_every_labelled_pattern_has_odd_perpendicularity_cycles() -> None:
    for complements in all_pointed_fano_complements():
        analysis = analyze_n7_witness_pattern(witnesses_from_complements(complements))
        assert sorted(analysis.cycle_lengths) == [7, 7, 7]
        assert analysis.has_odd_cycle
        assert not analysis.geometrically_realizable


def test_every_dihedral_class_representative_has_recorded_constraints() -> None:
    data = enumeration_data()
    representatives = data["representatives"]
    assert isinstance(representatives, list)
    assert len(representatives) == len(pointed_fano_dihedral_classes()) == 54

    for record in representatives:
        assert record["cycle_lengths"] == [7, 7, 7]
        assert record["has_odd_perpendicularity_cycle"] is True
        assert record["geometrically_realizable_under_required_perpendicularities"] is False
        assert len(record["perpendicularity_map"]) == 21
        assert len(record["perpendicularity_cycles"]) == 3


def test_checked_in_n7_json_artifact_matches_generator() -> None:
    root = Path(__file__).resolve().parents[1]
    artifact = root / "data" / "incidence" / "n7_fano_dihedral_representatives.json"

    checked_in = json.loads(artifact.read_text(encoding="utf-8"))
    assert checked_in == enumeration_data()
