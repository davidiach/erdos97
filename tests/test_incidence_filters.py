from __future__ import annotations

from erdos97.incidence_filters import (
    adjacent_two_overlap_violations,
    chords_cross_in_order,
    forced_equal_classes_from_matrix,
    mutual_midpoint_matrix,
    odd_forced_perpendicular_cycle,
    phi_map,
)
from erdos97.search import built_in_patterns


def test_chords_cross_in_order() -> None:
    order = [0, 1, 2, 3]

    assert chords_cross_in_order((0, 2), (1, 3), order)
    assert not chords_cross_in_order((0, 1), (2, 3), order)
    assert not chords_cross_in_order((0, 2), (2, 3), order)


def test_phi_map_on_toy_pattern() -> None:
    S = [
        [2, 3, 4, 5],
        [2, 3, 6, 7],
        [],
        [],
        [],
        [],
        [],
        [],
    ]

    assert phi_map(S)[(0, 1)] == (2, 3)


def test_mutual_midpoint_matrix_on_toy_reciprocal_pair() -> None:
    S = [
        [2, 3, 4, 5],
        [2, 3, 6, 7],
        [0, 1, 4, 6],
        [0, 1, 5, 7],
        [],
        [],
        [],
        [],
    ]

    matrix = mutual_midpoint_matrix(S)

    assert matrix.shape == (1, 8)
    assert list(matrix.row(0)) == [1, 1, -1, -1, 0, 0, 0, 0]
    assert forced_equal_classes_from_matrix(matrix, 8) == []


def test_expected_mutual_midpoint_fixed_pattern_kills() -> None:
    patterns = built_in_patterns()
    expected = {
        "B12_3x4_danzer_lift": {
            "rank": 8,
            "classes": [[0, 4, 8], [1, 5, 9], [2, 6, 10], [3, 7, 11]],
        },
        "B20_4x5_FR_lift": {
            "rank": 15,
            "classes": [
                [0, 5, 10, 15],
                [1, 6, 11, 16],
                [2, 7, 12, 17],
                [3, 8, 13, 18],
                [4, 9, 14, 19],
            ],
        },
        "C9_pm_2_4": {
            "rank": 8,
            "classes": [[0, 1, 2, 3, 4, 5, 6, 7, 8]],
        },
        "C13_pm_3_5": {
            "rank": 12,
            "classes": [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]],
        },
        "C16_pm_1_6": {
            "rank": 14,
            "classes": [[0, 2, 4, 6, 8, 10, 12, 14], [1, 3, 5, 7, 9, 11, 13, 15]],
        },
        "C20_pm_4_9": {
            "rank": 16,
            "classes": [
                [0, 4, 8, 12, 16],
                [1, 5, 9, 13, 17],
                [2, 6, 10, 14, 18],
                [3, 7, 11, 15, 19],
            ],
        },
    }

    for name, values in expected.items():
        matrix = mutual_midpoint_matrix(patterns[name].S)
        assert matrix.rank() == values["rank"]
        assert forced_equal_classes_from_matrix(matrix, patterns[name].n) == values["classes"]


def test_c17_skew_has_odd_forced_perpendicularity_cycle() -> None:
    cycle = odd_forced_perpendicular_cycle(built_in_patterns()["C17_skew"].S)

    assert cycle is not None
    assert len(cycle) % 2 == 1


def test_parity_patterns_have_natural_order_adjacent_two_overlap_violations() -> None:
    patterns = built_in_patterns()

    assert adjacent_two_overlap_violations(patterns["P18_parity_balanced"].S)
    assert adjacent_two_overlap_violations(patterns["P24_parity_balanced"].S)
