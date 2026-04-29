from __future__ import annotations

import json
import pathlib

import numpy as np

from erdos97.search import (
    built_in_patterns,
    convexity_margin,
    convexity_margins,
    circulant_pattern,
    incidence_obstruction_stats,
    orient_margins,
    polygon_from_x,
    slsqp_search,
)


CATALOG_NAMES = ("C13_sidon_1_2_4_10", "C25_sidon_2_5_9_14", "C29_sidon_1_3_7_15")


def test_sidon_patterns_registered() -> None:
    pats = built_in_patterns()
    for name in CATALOG_NAMES:
        assert name in pats


def test_c13_sidon_singer_difference_set_property() -> None:
    pat = built_in_patterns()["C13_sidon_1_2_4_10"]
    n = pat.n
    assert n == 13
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            common = len(set(pat.S[i]).intersection(pat.S[j]))
            assert common == 1, f"|S_{i} cap S_{j}| = {common}, expected 1"


def test_c25_and_c29_sidon_pair_intersections_at_most_one() -> None:
    pats = built_in_patterns()
    for name in ("C25_sidon_2_5_9_14", "C29_sidon_1_3_7_15"):
        pat = pats[name]
        for i in range(pat.n):
            for j in range(i + 1, pat.n):
                common = len(set(pat.S[i]).intersection(pat.S[j]))
                assert common in (0, 1), f"{name}: |S_{i} cap S_{j}| = {common}"


def test_sidon_patterns_satisfy_two_circle_cap() -> None:
    pats = built_in_patterns()
    for name in CATALOG_NAMES:
        stats = incidence_obstruction_stats(pats[name].S)
        assert stats["max_common_selected_neighbors"] <= 2


def test_circulant_pattern_extension_supports_arbitrary_offsets() -> None:
    # Arbitrary 4-element D in Z_11 \ {0}: not in built_in catalog.
    pat = circulant_pattern(11, [1, 2, 5, 7], "C11_test_1_2_5_7")
    assert pat.n == 11
    assert len(pat.S) == 11
    for i, row in enumerate(pat.S):
        assert len(row) == 4
        assert i not in row
        assert sorted(row) == row


def test_catalog_json_contains_sidon_entries() -> None:
    root = pathlib.Path(__file__).resolve().parents[1]
    data = json.loads((root / "data" / "patterns" / "candidate_patterns.json").read_text())
    names = {entry["name"] for entry in data}
    for name in CATALOG_NAMES:
        assert name in names


def test_full_convexity_margin_rejects_local_turn_false_positive() -> None:
    """A locally left-turning cyclic chain need not be strictly convex."""
    P = np.array(
        [
            [-1.9442649759855442, -1.3077531969011476],
            [1.0868307847683634, -0.050604063111342405],
            [-0.2831250656795347, 1.643251614242697],
            [-1.2826492440738984, -0.5856577998413593],
            [-0.47258767675848407, 0.5863372815313004],
        ],
        dtype=float,
    )
    assert orient_margins(P).min() > 0.0
    assert convexity_margins(P).min() < 0.0
    assert convexity_margin(P) < 0.0


def test_slsqp_search_runs_and_returns_feasible_polygon() -> None:
    pat = built_in_patterns()["C13_sidon_1_2_4_10"]
    margin = 1e-3
    loss, x, _ = slsqp_search(pat, mode="polar", restarts=3, seed=1,
                              max_nfev=400, margin=margin, verbose=False)
    P = polygon_from_x(x, pat.n, "polar")
    # Hard-margin feasibility on the returned configuration.
    from erdos97.search import (
        min_edge_length,
        min_pair_distance,
    )
    assert np.isfinite(loss)
    assert convexity_margin(P) >= margin - 1e-9
    assert min_edge_length(P) >= margin - 1e-9
    assert min_pair_distance(P) >= margin - 1e-9
