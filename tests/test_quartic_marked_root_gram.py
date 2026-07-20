from __future__ import annotations

from fractions import Fraction

import pytest

from scripts.check_quartic_marked_root_gram import (
    DEFAULT_ARTIFACT,
    check_payload,
    load_json,
    normalize_payload,
)
from erdos97.quartic_marked_root_gram import (
    GRAM_PAIRS,
    equations_hold,
    finite_graph_chain_is_strict,
    gram_upper_from_coefficients,
    lifted_squared_distance,
    marked_root_divisibility_check,
    marked_row_equations,
    maximum_distance_multiplicity,
    polynomial_value,
    quartic_closure_pilot,
    rank_one_intersection_on_line,
    rank_one_psd_check,
    recover_rational_direction,
    reduced_row_echelon,
    rich_center_multiplicities,
    second_derivative_has_constant_sign,
    solve_affine,
    squared_distance,
    validate_parameters,
)


POSITIVE_COEFFICIENTS = (
    Fraction(-51017, 6552),
    Fraction(337469, 393120),
    Fraction(-2503, 65520),
    Fraction(253, 393120),
)
POSITIVE_WITNESSES = (7, 15, 20, 24)


def _upper_from_matrix(matrix: tuple[tuple[int, ...], ...]) -> tuple[Fraction, ...]:
    return tuple(Fraction(matrix[left - 1][right - 1]) for left, right in GRAM_PAIRS)


def test_direct_and_lifted_distances_agree() -> None:
    for coefficients in (
        (1, 0, 0, 0),
        (1, -2, 3, -4),
        (Fraction(2, 3), Fraction(-5, 7), Fraction(11, 13), Fraction(17, 19)),
    ):
        upper = gram_upper_from_coefficients(coefficients)
        for center, witness in ((-3, 2), (0, 4), (Fraction(1, 2), Fraction(-7, 3))):
            assert lifted_squared_distance(upper, center, witness) == squared_distance(
                coefficients,
                center,
                witness,
            )


def test_exact_one_rich_row_positive_control() -> None:
    upper = gram_upper_from_coefficients(POSITIVE_COEFFICIENTS)
    equations = marked_row_equations(0, POSITIVE_WITNESSES)

    assert [
        squared_distance(POSITIVE_COEFFICIENTS, 0, witness)
        for witness in POSITIVE_WITNESSES
    ] == [Fraction(625)] * 4
    assert equations_hold(equations, upper)
    assert marked_root_divisibility_check(0, POSITIVE_WITNESSES, upper)
    assert rank_one_psd_check(upper).quartic_gram
    assert second_derivative_has_constant_sign(POSITIVE_COEFFICIENTS, 0, 24)
    assert finite_graph_chain_is_strict(
        POSITIVE_COEFFICIENTS,
        (0, *POSITIVE_WITNESSES),
    )
    assert maximum_distance_multiplicity(
        upper,
        0,
        (0, *POSITIVE_WITNESSES),
    ) == 4
    assert rich_center_multiplicities(upper, (0, *POSITIVE_WITNESSES)) == (4, 1, 1, 1, 1)


def test_marked_divisibility_rejects_perturbed_row() -> None:
    upper = gram_upper_from_coefficients(POSITIVE_COEFFICIENTS)
    perturbed = (7, 15, 20, 23)
    assert not equations_hold(marked_row_equations(0, perturbed), upper)
    assert not marked_root_divisibility_check(0, perturbed, upper)


def test_payload_normalization_matches_json_round_trip() -> None:
    assert normalize_payload({"sample": ((1, 2),)}) == {"sample": [[1, 2]]}


def test_rref_is_canonical_and_exposes_nullspace() -> None:
    first = (1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 3)
    second = (0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 4)
    scaled_first = tuple(5 * value for value in first)

    expected = reduced_row_echelon((first, second))
    assert expected == reduced_row_echelon((second, scaled_first, first))

    solution = solve_affine((first, second))
    assert solution is not None
    assert solution.rank == 2
    assert solution.dimension == 8
    assert solution.pivots == (0, 1)
    for row in (first, second):
        assert equations_hold((tuple(Fraction(value) for value in row),), solution.particular)
        for vector in solution.nullspace:
            homogeneous = tuple(Fraction(value) for value in row[:-1]) + (Fraction(0),)
            assert equations_hold((homogeneous,), vector)


def test_rref_detects_inconsistent_and_ignores_zero_rows() -> None:
    zero = (0,) * 11
    inconsistent = (0,) * 10 + (1,)

    assert reduced_row_echelon((zero,)) == ()
    assert reduced_row_echelon((zero, inconsistent)) is None
    assert solve_affine((inconsistent,)) is None


def test_rank_one_psd_gate_separates_relaxation_failures() -> None:
    quartic = gram_upper_from_coefficients((1, 2, 3, 4))
    cubic = gram_upper_from_coefficients((1, 2, 3, 0))
    negative_quartic = tuple(-value for value in quartic)
    high_rank_psd = _upper_from_matrix(
        (
            (1, 0, 0, 0),
            (0, 1, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        )
    )
    zero = (0,) * 10

    assert rank_one_psd_check(quartic).quartic_gram
    assert rank_one_psd_check(high_rank_psd).positive_semidefinite
    assert not rank_one_psd_check(high_rank_psd).rank_one
    assert rank_one_psd_check(negative_quartic).rank_one
    assert not rank_one_psd_check(negative_quartic).positive_semidefinite
    assert rank_one_psd_check(cubic).rank_one
    assert rank_one_psd_check(cubic).positive_semidefinite
    assert not rank_one_psd_check(cubic).degree_four
    assert not rank_one_psd_check(zero).rank_one


def test_recovery_accepts_nonsquare_rational_scale() -> None:
    base = gram_upper_from_coefficients((1, 2, 3, 4))
    scaled = tuple(Fraction(2) * value for value in base)
    direction = recover_rational_direction(scaled)

    assert direction == (Fraction(1), Fraction(2), Fraction(3), Fraction(4))


@pytest.mark.parametrize(
    ("particular", "direction", "kind", "parameters"),
    (
        (
            ((0, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
            ((1, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
            "RATIONAL_PARAMETERS",
            (Fraction(0),),
        ),
        (
            ((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
            ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
            "RATIONAL_PARAMETERS",
            (Fraction(-1), Fraction(1)),
        ),
        (
            ((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
            ((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
            "NO_REAL_RANK_ONE",
            (),
        ),
        (
            ((0, 1, 0, 0), (1, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
            ((1, 0, 0, 0), (0, 2, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
            "IRRATIONAL_REAL_QUADRATIC",
            (),
        ),
        (
            ((0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
            ((1, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
            "ALL_PARAMETERS_RANK_AT_MOST_ONE",
            (),
        ),
    ),
)
def test_rank_one_line_classifications(
    particular: tuple[tuple[int, ...], ...],
    direction: tuple[tuple[int, ...], ...],
    kind: str,
    parameters: tuple[Fraction, ...],
) -> None:
    result = rank_one_intersection_on_line(
        _upper_from_matrix(particular),
        _upper_from_matrix(direction),
    )

    assert result.kind == kind
    assert result.rational_parameters == parameters


def test_rank_one_line_can_have_no_common_minor_root() -> None:
    particular = _upper_from_matrix(
        ((0, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 0))
    )
    direction = _upper_from_matrix(
        ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0))
    )

    assert rank_one_intersection_on_line(particular, direction).kind == "NO_RANK_ONE"


def test_convexity_gate_accepts_isolated_zeros_and_rejects_sign_changes() -> None:
    assert second_derivative_has_constant_sign((0, 0, 0, 1), -1, 1)
    assert second_derivative_has_constant_sign((0, 0, 1, 0), 0, 1)
    changing = (0, Fraction(-1, 2), 0, Fraction(1, 12))
    assert not second_derivative_has_constant_sign(changing, -2, 2)
    assert second_derivative_has_constant_sign(changing, Fraction(-1, 2), Fraction(1, 2))
    assert not second_derivative_has_constant_sign((1, 0, 0, 0), -1, 1)


def test_tiny_pilot_is_deterministic_and_overlap_cap_closes_it() -> None:
    first = quartic_closure_pilot(parameters=(0, 1, 2, 3, 4), anchor_centers=(0, 1, 2))
    second = quartic_closure_pilot(parameters=(0, 1, 2, 3, 4), anchor_centers=(0, 1, 2))

    assert first == second
    assert first.anchor.raw_triple_count == 1
    assert first.anchor.overlap_admissible_count == 0
    assert first.anchor.exceptional_affine_state_count == 0
    assert first.unresolved_affine_state_count == 0
    assert first.strict_finite_full_closure_candidate_count == 0


def test_malformed_inputs_are_rejected() -> None:
    with pytest.raises(ValueError, match="at least five"):
        validate_parameters((0, 1, 2, 3))
    with pytest.raises(ValueError, match="distinct"):
        validate_parameters((0, 1, 2, 3, 3))
    with pytest.raises(ValueError, match="increasing"):
        validate_parameters((0, 2, 1, 3, 4))
    with pytest.raises(ValueError, match="four distinct"):
        marked_row_equations(0, (1, 1, 2, 3))
    with pytest.raises(ValueError, match="center"):
        marked_row_equations(0, (0, 1, 2, 3))
    with pytest.raises(ValueError, match="increasing"):
        marked_row_equations(0, (2, 1, 3, 4))
    with pytest.raises(ValueError, match="direction"):
        rank_one_intersection_on_line((0,) * 10, (0,) * 10)


def test_polynomial_value_rejects_wrong_coefficient_count() -> None:
    with pytest.raises(ValueError, match="length four"):
        polynomial_value((1, 2, 3), 4)


@pytest.mark.artifact
def test_stored_fixed_grid_artifact_contract() -> None:
    payload = load_json(DEFAULT_ARTIFACT)

    check_payload(payload, assert_expected=True)
    assert payload["provenance"]["generator"] == (
        "scripts/check_quartic_marked_root_gram.py"
    )
    assert payload["controls"]["positive_one_rich_row"]["squared_radius"] == "625"
    assert payload["controls"]["higher_rank_psd_relaxation_trap"]["rank_one"] is False
