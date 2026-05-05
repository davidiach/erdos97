from __future__ import annotations

from erdos97.fragile_hypergraph import (
    block6_family,
    canonical_witness_map,
    check_fragile_hypergraph,
    essential_row_matching,
    full_selected_extension,
)


def test_block6_family_satisfies_fragile_hypergraph_axioms() -> None:
    n, rows = block6_family(2)
    witness_map = canonical_witness_map(n, rows)

    result = check_fragile_hypergraph(n, rows, witness_map=witness_map)

    assert result.ok
    assert result.essential_cover_ok
    assert result.fragile_centers == [0, 3, 6, 9]
    assert witness_map[0] == 3
    assert witness_map[5] == 3
    assert witness_map[6] == 9
    assert witness_map[11] == 9


def test_crossing_violation_is_reported() -> None:
    rows = {
        0: [1, 2, 3, 4],
        6: [0, 2, 3, 5],
    }

    result = check_fragile_hypergraph(7, rows)

    assert not result.ok
    assert result.pairwise_intersection_ok
    assert not result.crossing_ok
    assert result.crossing_violations == [
        {
            "source": [0, 6],
            "target": [2, 3],
            "order": [0, 1, 2, 3, 4, 5, 6],
        }
    ]


def test_witness_map_must_choose_a_covering_fragile_center() -> None:
    n, rows = block6_family(1)
    bad_witness_map = {vertex: 0 for vertex in range(n)}

    result = check_fragile_hypergraph(n, rows, witness_map=bad_witness_map)

    assert not result.ok
    assert result.witness_map_ok is False
    assert {
        "vertex": 0,
        "center": 0,
        "reason": "witness center does not cover vertex",
    } in result.witness_map_violations


def test_witness_map_must_use_every_fragile_center() -> None:
    rows = {
        0: [1, 2, 3, 4],
        1: [0, 5, 6, 7],
        2: [0, 1, 3, 5],
    }
    witness_map = {
        0: 1,
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 1,
        6: 1,
        7: 1,
    }

    result = check_fragile_hypergraph(8, rows, witness_map=witness_map)

    assert not result.ok
    assert result.witness_map_ok is False
    assert {
        "center": 2,
        "reason": "fragile center is not assigned any vertex",
    } in result.witness_map_violations


def test_essential_row_matching_detects_hall_defect() -> None:
    rows = {
        0: [1, 2, 3, 4],
        1: [2, 3, 4, 5],
        2: [3, 4, 5, 6],
        3: [4, 5, 6, 7],
        4: [0, 5, 6, 7],
        5: [0, 1, 6, 7],
        6: [0, 1, 2, 7],
        7: [0, 1, 2, 3],
        8: [0, 1, 2, 3],
    }

    matching, unmatched = essential_row_matching(9, rows)
    result = check_fragile_hypergraph(9, rows)

    assert len(matching) == 8
    assert unmatched
    assert not result.essential_cover_ok
    assert result.essential_matching_unmatched_centers == unmatched


def test_single_block6_has_no_full_selected_extension() -> None:
    n, rows = block6_family(1)

    extension = full_selected_extension(n, rows)

    assert not extension.ok
    assert extension.search_exhausted
    assert extension.failure_reason == "no extension exists"


def test_two_block6_still_has_full_selected_extension() -> None:
    n, rows = block6_family(2)

    extension = full_selected_extension(n, rows)

    assert extension.ok
    assert extension.full_rows is not None
    assert extension.full_rows[0] == rows[0]
    assert extension.full_rows[3] == rows[3]
    assert extension.full_rows[6] == rows[6]
    assert extension.full_rows[9] == rows[9]
