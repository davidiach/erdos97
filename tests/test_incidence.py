from __future__ import annotations

import pathlib

from erdos97.search import built_in_patterns, incidence_obstruction_stats, verify_json


def test_built_in_patterns_have_outdegree_four_and_no_loops() -> None:
    for pattern in built_in_patterns().values():
        assert len(pattern.S) == pattern.n
        for i, selected in enumerate(pattern.S):
            assert len(selected) == 4
            assert len(set(selected)) == 4
            assert i not in selected


def test_built_in_patterns_satisfy_pairwise_common_neighbor_cap() -> None:
    for pattern in built_in_patterns().values():
        stats = incidence_obstruction_stats(pattern.S)
        assert stats["max_common_selected_neighbors"] <= 2


def test_saved_b12_near_miss_is_not_certified_at_strict_tolerance() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    path = root / "data" / "runs" / "best_B12_slsqp_m1e-6.json"
    diag = verify_json(str(path), tol=1e-8)
    assert not diag["ok_at_tol"]
    assert diag["convexity_margin"] > 0


def test_archive_c12_imports_are_not_certified_at_synthesis_tolerance() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    runs = root / "data" / "runs"
    paths = [
        runs / "archive_C12_offsets_4_5_8_11_near_convex.json",
        runs / "archive_C12_offsets_2_3_4_10_degenerate.json",
    ]
    for path in paths:
        diag = verify_json(str(path), tol=1e-6)
        assert not diag["ok_at_tol"]
