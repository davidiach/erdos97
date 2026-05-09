from __future__ import annotations

from erdos97.reciprocal_radial_budget import (
    affine_circle_example,
    jump_formula_check,
    middle_budget_inequalities,
    order_witnesses_on_visible_chain,
    pentagon_tight_example,
    smoke_report,
    visible_chain_offset,
)


def test_visible_chain_ordering_sorts_across_modulus() -> None:
    assert order_witnesses_on_visible_chain(9, 7, [2, 8, 0, 5]) == (8, 0, 2, 5)
    assert visible_chain_offset(9, 7, 8) == 1
    assert visible_chain_offset(9, 7, 5) == 7


def test_pentagon_tight_example_hits_middle_budget_equalities() -> None:
    points = pentagon_tight_example()
    entries = middle_budget_inequalities(points, 0, (1, 2, 3, 4))

    assert [entry.middle for entry in entries] == [2, 3]
    assert max(abs(entry.margin) for entry in entries) < 1e-12
    for entry in entries:
        assert all(value > 0 for value in entry.positive_denominators.values())


def test_jump_formula_on_affine_circle_control() -> None:
    points = affine_circle_example()
    errors = []
    denominators = []
    turns = []

    for center in range(len(points)):
        for vertex in range(len(points)):
            if vertex == center:
                continue
            offset = visible_chain_offset(len(points), center, vertex)
            if offset in (1, len(points) - 1):
                continue
            check = jump_formula_check(points, center, vertex)
            errors.append(abs(check.error))
            denominators.extend(
                [check.incoming_denominator, check.outgoing_denominator]
            )
            turns.append(check.exterior_turn_cross)

    assert max(errors) < 1e-12
    assert min(denominators) > 0
    assert min(turns) > 0


def test_smoke_report_keeps_non_proof_scope() -> None:
    report = smoke_report()

    assert report["schema"] == "reciprocal_radial_budget_smoke_v1"
    assert "not a proof" in str(report["claim_scope"])
    assert report["trust"] == "RESEARCH_PACKET_LOCAL_NECESSARY_CONDITION"
