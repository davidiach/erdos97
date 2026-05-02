from __future__ import annotations

import json
import math
import pathlib

import numpy as np

from erdos97.search import (
    built_in_patterns,
    convexity_margin,
    incidence_obstruction_stats,
    min_pair_distance,
    verify_json,
)


def regular_ngon(n: int, scale: float = 1.0) -> list[list[float]]:
    return [
        [scale * math.cos(2.0 * math.pi * i / n), scale * math.sin(2.0 * math.pi * i / n)]
        for i in range(n)
    ]


def write_candidate(path: pathlib.Path, coordinates: list[list[float]], S: list[list[int]]) -> None:
    path.write_text(json.dumps({"coordinates": coordinates, "S": S}), encoding="utf-8")


def circulant_witnesses(n: int, offsets: list[int]) -> list[list[int]]:
    return [[(i + offset) % n for offset in offsets] for i in range(n)]


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


def test_verify_json_rejects_duplicate_self_witness_rows(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "bad_self_witness.json"
    write_candidate(path, regular_ngon(5), [[i, i, i, i] for i in range(5)])

    diag = verify_json(str(path), tol=1e-8)

    assert not diag["ok_at_tol"]
    assert any("duplicate targets" in err for err in diag["validation_errors"])
    assert any("own center" in err for err in diag["validation_errors"])


def test_verify_json_normalizes_before_acceptance(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "tiny_regular_pentagon.json"
    witnesses = circulant_witnesses(7, [1, 2, 3, 5])
    write_candidate(path, regular_ngon(7, scale=1e-12), witnesses)

    diag = verify_json(str(path), tol=1e-8)

    assert not diag["ok_at_tol"]
    assert diag["validation_errors"] == []
    assert diag["max_spread"] > 1.0


def test_verify_json_accepts_certificate_template_coordinate_key(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "certificate_template.json"
    witnesses = circulant_witnesses(7, [1, 2, 3, 5])
    path.write_text(
        json.dumps({"coordinates_float": regular_ngon(7), "S": witnesses}),
        encoding="utf-8",
    )

    diag = verify_json(str(path), tol=1e-8)

    assert not diag["ok_at_tol"]
    assert diag["validation_errors"] == []


def test_verify_json_rejects_pairwise_common_neighbor_cap_violation(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "bad_pairwise_cap.json"
    witnesses = [[j for j in range(5) if j != i] for i in range(5)]
    write_candidate(path, regular_ngon(5), witnesses)

    diag = verify_json(str(path), tol=1e-8)

    assert not diag["ok_at_tol"]
    assert any("pairwise cap of 2" in err for err in diag["validation_errors"])


def test_min_pair_distance_detects_duplicate_points() -> None:
    P = np.array([[0.0, 0.0], [0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])

    assert min_pair_distance(P) == 0.0


def test_convexity_margin_checks_edges_against_all_vertices() -> None:
    pentagon = np.array(regular_ngon(5), dtype=float)
    star_order = pentagon[[0, 2, 4, 1, 3]]

    assert convexity_margin(star_order) < 0.0
