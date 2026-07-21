from __future__ import annotations

from fractions import Fraction
from itertools import combinations

import pytest

from scripts.check_quartic_marked_root_gram import (
    DEFAULT_ARTIFACT,
    check_payload,
    load_json,
    normalize_payload,
)
from erdos97.quartic_marked_root_gram import (
    E11_UPPER,
    GRAM_PAIRS,
    UNIVERSAL_PHANTOM_UPPER,
    canonical_primitive_upper,
    classify_full_gram_kernel_direction,
    equations_hold,
    finite_graph_chain_is_strict,
    full_gram_from_graph_gram,
    full_gram_squared_distance,
    full_gram_upper_from_coordinate_coefficients,
    graph_gram_from_full_gram,
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
    symmetric_matrix_rank,
    symmetric_matrix_inertia,
    translate_affine_equations_to_full_gram,
    validate_parameters,
)


POSITIVE_COEFFICIENTS = (
    Fraction(-51017, 6552),
    Fraction(337469, 393120),
    Fraction(-2503, 65520),
    Fraction(253, 393120),
)
POSITIVE_WITNESSES = (7, 15, 20, 24)
FULL_GRAM_ANCHOR_RAYS = (
    (2308, 108, -232, 24, 183, 18, -21, 28, -6, 3),
    (292, -248, -88, 44, 211, 74, -37, 28, -14, 7),
)


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


def test_universal_phantom_annihilates_distances_and_marked_rows() -> None:
    center = Fraction(1, 3)
    witnesses = (Fraction(-5, 2), Fraction(-1), Fraction(2), Fraction(7, 3))

    assert all(
        lifted_squared_distance(UNIVERSAL_PHANTOM_UPPER, center, witness) == 0
        for witness in witnesses
    )
    assert equations_hold(
        marked_row_equations(center, witnesses),
        UNIVERSAL_PHANTOM_UPPER,
    )
    phantom_check = rank_one_psd_check(UNIVERSAL_PHANTOM_UPPER)
    assert phantom_check.rank_one
    assert not phantom_check.positive_semidefinite
    assert full_gram_from_graph_gram(UNIVERSAL_PHANTOM_UPPER) == (Fraction(0),) * 10


def test_full_gram_translation_makes_marked_rows_homogeneous() -> None:
    graph_equations = marked_row_equations(0, POSITIVE_WITNESSES)
    full_equations = translate_affine_equations_to_full_gram(graph_equations)
    graph_gram = gram_upper_from_coefficients(POSITIVE_COEFFICIENTS)
    full_gram = full_gram_from_graph_gram(graph_gram)

    assert all(row[-1] == 0 for row in full_equations)
    assert equations_hold(graph_equations, graph_gram)
    assert equations_hold(full_equations, full_gram)
    assert graph_gram_from_full_gram(full_gram) == graph_gram
    assert full_gram_from_graph_gram((0,) * 10) == E11_UPPER


def test_coordinate_full_gram_identity_and_constant_term_cancellation() -> None:
    x_nonconstant = (Fraction(2), Fraction(-1), Fraction(0), Fraction(3))
    y_nonconstant = (
        Fraction(1, 2),
        Fraction(0),
        Fraction(4),
        Fraction(-2),
    )
    full_gram = full_gram_upper_from_coordinate_coefficients(
        (x_nonconstant, y_nonconstant)
    )
    center = Fraction(-3, 2)
    witness = Fraction(5, 3)

    def coordinate_value(
        constant: Fraction,
        coefficients: tuple[Fraction, ...],
        parameter: Fraction,
    ) -> Fraction:
        return constant + sum(
            (
                coefficient * parameter**degree
                for degree, coefficient in enumerate(coefficients, 1)
            ),
            Fraction(0),
        )

    x_difference = coordinate_value(
        Fraction(101), x_nonconstant, witness
    ) - coordinate_value(Fraction(101), x_nonconstant, center)
    y_difference = coordinate_value(
        Fraction(-37), y_nonconstant, witness
    ) - coordinate_value(Fraction(-37), y_nonconstant, center)
    assert full_gram_squared_distance(full_gram, center, witness) == (
        x_difference**2 + y_difference**2
    )

    graph_coefficients = (1, -2, 3, -4)
    assert full_gram_upper_from_coordinate_coefficients(
        ((1, 0, 0, 0), graph_coefficients)
    ) == full_gram_from_graph_gram(
        gram_upper_from_coefficients(graph_coefficients)
    )


def test_full_gram_kernel_gate_rejects_rank_three_determinant_zero() -> None:
    direction = _upper_from_matrix(
        (
            (1, 0, 0, 0),
            (0, 1, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 0),
        )
    )
    check = classify_full_gram_kernel_direction(direction)

    assert symmetric_matrix_rank(direction) == 3
    assert check.positive_semidefinite
    assert not check.admits_nonzero_planar_full_gram


def test_full_gram_kernel_gate_rejects_indefinite_rank_two_and_zero() -> None:
    indefinite = _upper_from_matrix(
        (
            (1, 0, 0, 0),
            (0, -1, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        )
    )
    negative_semidefinite = _upper_from_matrix(
        (
            (-1, 0, 0, 0),
            (0, -2, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
        )
    )
    indefinite_check = classify_full_gram_kernel_direction(indefinite)
    negative_check = classify_full_gram_kernel_direction(negative_semidefinite)
    zero_check = classify_full_gram_kernel_direction((0,) * 10)

    assert indefinite_check.rank == 2
    assert not indefinite_check.positive_semidefinite
    assert not indefinite_check.negative_semidefinite
    assert not indefinite_check.admits_nonzero_planar_full_gram
    assert negative_check.negative_semidefinite
    assert negative_check.admits_nonzero_planar_full_gram
    assert zero_check.rank == 0
    assert not zero_check.nonzero
    assert not zero_check.admits_nonzero_planar_full_gram


def test_two_planar_anchor_rays_are_exact_degenerate_controls() -> None:
    parameters = tuple(range(-4, 5))
    expected_collisions = (
        ((-3, 4), (-2, -1), (2, 3)),
        ((-3, 4), (-2, 3), (-1, 2), (0, 1)),
    )

    for upper, collisions in zip(
        FULL_GRAM_ANCHOR_RAYS,
        expected_collisions,
        strict=True,
    ):
        check = classify_full_gram_kernel_direction(upper)
        assert check.rank == 2
        assert check.positive_semidefinite
        assert check.admits_nonzero_planar_full_gram
        assert symmetric_matrix_inertia(upper) == (2, 0, 2)
        assert canonical_primitive_upper(
            tuple(Fraction(-3, 5) * value for value in upper)
        ) == upper

        actual_collisions = tuple(
            (left, right)
            for left, right in combinations(parameters, 2)
            if full_gram_squared_distance(upper, left, right) == 0
        )
        assert actual_collisions == collisions

        multiplicities = []
        for center in parameters:
            distance_counts: dict[Fraction, int] = {}
            for witness in parameters:
                if witness == center:
                    continue
                distance = full_gram_squared_distance(upper, center, witness)
                if distance > 0:
                    distance_counts[distance] = distance_counts.get(distance, 0) + 1
            multiplicities.append(max(distance_counts.values(), default=0))
        assert tuple(multiplicities) == (2, 4, 4, 4, 4, 4, 4, 4, 4)


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
    assert first.full_gram_four_center_unresolved_state_count == 0
    assert first.strict_finite_full_closure_candidate_count == 0


@pytest.mark.slow
def test_seven_parameter_pilot_exercises_anchor_and_extension_paths() -> None:
    summary = quartic_closure_pilot(
        parameters=tuple(range(-3, 4)),
        anchor_centers=(0, 2, 3),
        sample_limit=0,
    )

    assert summary.anchor.raw_triple_count == 3375
    assert summary.anchor.overlap_admissible_count == 870
    assert summary.anchor.rank_counts == ((8, 120), (9, 750))
    assert summary.anchor.exceptional_affine_state_count == 120
    anchor_full_gram = dict(summary.anchor.full_gram_kernel_census)
    assert anchor_full_gram["phantom_roots"] == 750
    assert anchor_full_gram["other_rank_one_roots"] == 0
    assert anchor_full_gram["planar_kernel_lines"] == 1

    assert len(summary.extension_steps) == 1
    step = summary.extension_steps[0]
    assert step["center"] == "-3"
    assert step["raw_state_row_branches"] == 1800
    assert step["deduplicated_consistent_affine_states"] == 24
    assert step["negative_semidefinite_rank_one_roots"] == 24
    assert step["deduplicated_affine_states_out"] == 0

    extension_full_gram = dict(summary.full_gram_extension_census)
    assert extension_full_gram["affine_rank_9_states"] == 23
    assert extension_full_gram["affine_rank_10_states"] == 1
    assert extension_full_gram["planar_kernel_lines"] == 1
    assert extension_full_gram["phantom_line_roots"] == 23
    assert extension_full_gram["phantom_singletons"] == 1
    assert summary.full_gram_four_center_unresolved_state_count == 0
    assert summary.full_gram_pairwise_distinct_candidate_count == 0
    assert summary.unresolved_affine_state_count == 0


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
    assert payload["schema"] == "erdos97.quartic_marked_root_gram.v2"
    assert payload["provenance"]["generator"] == (
        "scripts/check_quartic_marked_root_gram.py"
    )
    assert payload["controls"]["positive_one_rich_row"]["squared_radius"] == "625"
    assert payload["controls"]["higher_rank_psd_relaxation_trap"]["rank_one"] is False
    full_gram = payload["post_hoc_full_gram_upgrade"]
    assert full_gram["homogeneous_identity"]["formula"] == "B=A+E11"
    assert full_gram["anchor_kernel_census"]["planar_kernel_lines"] == 2
    assert full_gram["extension_kernel_census"]["affine_rank_9_states"] == 314
    assert full_gram["extension_kernel_census"]["affine_rank_10_states"] == 1
    assert full_gram["extension_kernel_census"]["planar_kernel_lines"] == 0
    assert full_gram["outcome"][
        "unresolved_affine_states_after_four_test_centers"
    ] == 0
    assert [
        candidate["center_multiplicities"]
        for candidate in full_gram["anchor_planar_rank_two_psd_candidates"]
    ] == [[2, 4, 4, 4, 4, 4, 4, 4, 4]] * 2
