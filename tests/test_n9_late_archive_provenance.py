from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n9_late_archive_provenance.json"


def test_n9_late_archive_provenance_is_review_pending() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert payload["type"] == "n9_late_archive_provenance_v1"
    assert payload["trust"] == "REVIEW_PENDING_PROVENANCE"
    assert any("No general proof" in note for note in payload["notes"])
    assert any("No counterexample" in note for note in payload["notes"])


def test_sequential_vertex_circle_counts_are_stable() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    summary = payload["summaries"]["sequential_vertex_circle_exclusion"]

    assert summary["verified_by_local_run"] is True
    assert summary["row0_case_count"] == 70
    assert summary["all_row0_closed"] is True
    assert summary["total_nodes_visited"] == 37614
    assert summary["total_row_options_considered"] == 2628150
    assert summary["total_full_patterns_reached"] == 0
    assert summary["total_rejection_counts"] == {
        "adjacent_two_overlap": 255354,
        "crossing_bisector": 1163137,
        "row_pair_intersection_cap": 1102641,
        "vertex_circle_self_edge": 34445,
        "vertex_circle_strict_cycle": 35029,
    }


def test_row0_quotient_bundle_is_static_provenance_only() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    summary = payload["summaries"]["row0_quotient_certificate_bundle"]

    assert summary["embedded_verifier_executed_during_integration"] is False
    assert summary["zip_member_count"] == 25
    assert summary["row_certificate_files"] == 17
    assert summary["canonical_row0_count"] == 38
    assert summary["row_count_with_full_patterns"] == 17
    assert summary["full_patterns"] == 102
    assert summary["classification_counts"] == {
        "accepted_frontier": 0,
        "kalmanson_certificate": 70,
        "mutual_midpoint_collapse": 0,
        "odd_forced_perpendicular_cycle": 11,
        "phi4_rectangle_trap": 21,
    }
