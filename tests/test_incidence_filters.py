from __future__ import annotations

from erdos97.incidence_filters import (
    adjacent_two_overlap_violations,
    chords_cross_in_order,
    crossing_bisector_violations,
    forced_equal_classes_from_matrix,
    mutual_midpoint_matrix,
    odd_forced_perpendicular_cycle,
    phi4_rectangle_trap_certificates,
    phi_directed_4_cycles,
    phi_map,
    row_ptolemy_product_cancellation_certificates,
)
from erdos97.search import built_in_patterns


N9_RECTANGLE_TRAP_PATTERN = [
    [1, 2, 3, 8],
    [0, 2, 4, 7],
    [1, 3, 5, 7],
    [1, 4, 6, 8],
    [0, 2, 5, 6],
    [3, 4, 6, 7],
    [2, 5, 7, 8],
    [0, 3, 6, 8],
    [0, 1, 4, 5],
]


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


def test_n9_rectangle_trap_survives_older_phi_filters() -> None:
    matrix = mutual_midpoint_matrix(N9_RECTANGLE_TRAP_PATTERN)

    assert odd_forced_perpendicular_cycle(N9_RECTANGLE_TRAP_PATTERN) is None
    assert matrix.rank() == 0
    assert forced_equal_classes_from_matrix(matrix, 9) == []
    assert adjacent_two_overlap_violations(N9_RECTANGLE_TRAP_PATTERN) == []
    assert crossing_bisector_violations(N9_RECTANGLE_TRAP_PATTERN, list(range(9))) == []


def test_n9_rectangle_trap_has_exact_phi4_certificate() -> None:
    cycles = phi_directed_4_cycles(N9_RECTANGLE_TRAP_PATTERN)
    certs = phi4_rectangle_trap_certificates(N9_RECTANGLE_TRAP_PATTERN)

    assert cycles == [((0, 6), (2, 8), (1, 5), (4, 7))]
    assert len(certs) == 1
    cert = certs[0]
    assert cert["status"] == "EXACT_OBSTRUCTION"
    assert cert["phi_cycle"] == [[0, 6], [2, 8], [1, 5], [4, 7]]
    assert cert["cyclic_subsequence"] == [0, 1, 2, 4, 5, 6, 7, 8]
    assert cert["determinant_identity"] == {
        "left": "D1 + D3 + D5 + D7",
        "right": "-4*a*b",
        "contradiction": (
            "Strict convexity requires D1,D3,D5,D7 > 0, "
            "but a,b > 0 makes their sum negative."
        ),
    }


def test_n9_rectangle_trap_accepts_reversed_cyclic_order() -> None:
    certs = phi4_rectangle_trap_certificates(
        N9_RECTANGLE_TRAP_PATTERN,
        list(reversed(range(9))),
    )

    assert len(certs) == 1
    assert certs[0]["cyclic_order_orientation"] == "reversed"


def test_row_ptolemy_product_cancellation_certificate_on_toy_pattern() -> None:
    rows = [
        [1, 2, 3, 4],
        [0, 2, 3, 4],
        [1, 3, 4, 5],
        [1, 2, 4, 5],
        [0, 1, 2, 3],
        [0, 1, 2, 3],
    ]

    certs = row_ptolemy_product_cancellation_certificates(rows, list(range(6)))

    row0_certs = [cert for cert in certs if cert["row"] == 0]
    assert row0_certs
    cert = row0_certs[0]
    assert cert["status"] == "EXACT_OBSTRUCTION_FOR_FIXED_PATTERN_AND_FIXED_ROW_ORDER"
    assert cert["witness_order"] == [1, 2, 3, 4]
    assert cert["ptolemy_identity"] == "d02*d13 = d01*d23 + d03*d12"
    assert cert["zero_product"]["expression"] == "d03*d12"
    assert any(
        cert["variant"] == "cancel_d01_d23_via_d02_eq_d01_and_d13_eq_d23"
        for cert in row0_certs
    )


def test_row_ptolemy_product_cancellation_depends_on_supplied_order() -> None:
    rows = [
        [1, 2, 3, 8],
        [0, 3, 4, 7],
        [1, 3, 5, 6],
        [2, 4, 5, 8],
        [0, 3, 6, 8],
        [2, 4, 6, 7],
        [1, 5, 7, 8],
        [0, 1, 4, 6],
        [0, 2, 5, 7],
    ]

    natural_certs = row_ptolemy_product_cancellation_certificates(rows, list(range(9)))
    scrambled_certs = row_ptolemy_product_cancellation_certificates(
        rows,
        [0, 1, 2, 6, 5, 7, 4, 8, 3],
    )

    assert len(natural_certs) == 6
    assert scrambled_certs == []


def test_phi4_rectangle_trap_determinant_identity_expands_exactly() -> None:
    import sympy as sp

    a, b, L0, L1, L2, L3 = sp.symbols("a b L0 L1 L2 L3")
    points = [
        (L0, 0),
        (a + L2, b),
        (a, L1),
        (0, b + L3),
        (a - L2, b),
        (-L0, 0),
        (0, b - L3),
        (a, -L1),
    ]

    def orient(i: int):
        p = sp.Matrix(points[i])
        q = sp.Matrix(points[(i + 1) % len(points)])
        r = sp.Matrix(points[(i + 2) % len(points)])
        v = q - p
        w = r - q
        return sp.expand(v[0] * w[1] - v[1] * w[0])

    determinants = [orient(i) for i in range(len(points))]

    odd_sum = determinants[1] + determinants[3] + determinants[5] + determinants[7]

    assert sp.factor(odd_sum) == -4 * a * b


def test_parity_patterns_have_natural_order_adjacent_two_overlap_violations() -> None:
    patterns = built_in_patterns()

    assert adjacent_two_overlap_violations(patterns["P18_parity_balanced"].S)
    assert adjacent_two_overlap_violations(patterns["P24_parity_balanced"].S)
