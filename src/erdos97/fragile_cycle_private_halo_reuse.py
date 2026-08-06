"""Pair-budget forcing for retained-private halos in full selected systems.

The fixed 23=27 quotient core has four retained four-witness rows.  The
large-halo slot budget forces several halo roles to occur in exactly one of
those rows.  This module asks how many of those roles may remain private after
the retained cover is extended to one selected row at every center.

The main bound is a direct witness-pair count.  Stored full-row systems are
guardrails showing that selected-private halos can still survive the abstract
incidence, crossing, capacity, and good-deletion checks.  They are not
Euclidean realizations and both contain known hinge/splice motifs.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations, product
from math import comb
from typing import Any, Mapping, Sequence

from erdos97.fragile_cycle_halo_lift_frontier import (
    CORE_ORDER,
    FRAGILE_CENTERS,
    PAIR_CAP,
    REQUIRED_WITNESSES,
    ROW_SIZE,
    _good_deletion_summary,
    _pair_counts,
    _selected_indegrees,
    _selected_pair_ok,
)
from erdos97.fragile_cycle_halo_slot_budget import (
    has_equilateral_hinge,
    has_kalmanson_splice,
)
from erdos97.fragile_hypergraph import essential_row_matching


SCHEMA = "erdos97.fragile_cycle_private_halo_reuse.v1"
STATUS = "EXACT_FIXED_CORE_PRIVATE_HALO_REUSE_BOUND"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact witness-pair budget for full selected-row extensions of the fixed "
    "23=27 four/five-halo retained covers. In a four-halo extension at most "
    "two retained-private halos remain selected-private, so at least one of "
    "three or two of four must be reused. In a five-halo extension at most "
    "three remain selected-private, so at least two are reused. Stored "
    "abstract full-row guardrails show that selected-private halos can still "
    "survive. This does not force the quotient core, close the four/five-halo "
    "regimes, prove full-rich-class privacy, Euclidean realizability, n=11, "
    "n=12, the general problem, or a counterexample."
)
CONCLUSION = (
    "The retained-private alternative cannot stay completely private in any "
    "full selected system: witness-pair capacity forces non-retained selected "
    "rows, hence additional rich classes, to reuse at least one/two of the "
    "four-halo private roles and at least two of the five-halo roles. The "
    "stored guardrails leave one and two selected-private halos respectively, "
    "so incidence and crossing alone do not upgrade every halo to reuse or "
    "give a geometric contradiction."
)
PROVENANCE = {
    "generator": "scripts/check_fragile_cycle_private_halo_reuse.py",
    "command": (
        "python scripts/check_fragile_cycle_private_halo_reuse.py "
        "--write --assert-expected --summary-json"
    ),
}

Rows = dict[int, tuple[int, ...]]


FOUR_HALO_GUARDRAIL = {
    "name": "four_halo_one_selected_private",
    "halo_gaps": [0, 0, 0, 0],
    "cyclic_order": [0, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6],
    "retained_rows": [
        [1, 0, 3, 4, 10],
        [3, 1, 4, 5, 9],
        [4, 0, 1, 2, 6],
        [6, 2, 5, 7, 8],
    ],
    "full_rows": [
        [0, 1, 4, 6, 7],
        [1, 0, 3, 4, 10],
        [2, 5, 6, 7, 10],
        [3, 1, 4, 5, 9],
        [4, 0, 1, 2, 6],
        [5, 0, 3, 7, 9],
        [6, 2, 5, 7, 8],
        [7, 0, 5, 9, 10],
        [8, 2, 4, 7, 9],
        [9, 1, 3, 7, 10],
        [10, 2, 3, 6, 9],
    ],
    "expected_retained_private_halos": [7, 8, 9, 10],
    "expected_selected_private_halos": [8],
}

FIVE_HALO_GUARDRAIL = {
    "name": "five_halo_two_selected_private",
    "halo_gaps": [0, 0, 0, 0, 0],
    "cyclic_order": [0, 7, 8, 9, 10, 11, 1, 2, 3, 4, 5, 6],
    "retained_rows": [
        [1, 0, 4, 10, 11],
        [3, 1, 4, 5, 9],
        [4, 0, 2, 3, 6],
        [6, 2, 5, 7, 8],
    ],
    "full_rows": [
        [0, 3, 4, 6, 7],
        [1, 0, 4, 10, 11],
        [2, 1, 3, 7, 11],
        [3, 1, 4, 5, 9],
        [4, 0, 2, 3, 6],
        [5, 4, 6, 8, 11],
        [6, 2, 5, 7, 8],
        [7, 0, 1, 3, 8],
        [8, 1, 5, 6, 7],
        [9, 3, 5, 8, 11],
        [10, 0, 2, 7, 11],
        [11, 1, 2, 4, 8],
    ],
    "expected_retained_private_halos": [7, 8, 9, 10, 11],
    "expected_selected_private_halos": [9, 10],
}


def _rows_from_compact(raw_rows: Sequence[Sequence[int]]) -> Rows:
    return {
        int(raw[0]): tuple(sorted(int(value) for value in raw[1:]))
        for raw in raw_rows
    }


def minimum_retained_pair_load(selected_private_count: int) -> int:
    """Minimize retained pairs avoiding the selected-private roles.

    A retained row has four witnesses and at most two halo slots.  If ``p_i``
    selected-private halos occur in row ``i``, that row contributes
    ``C(4-p_i, 2)`` witness-pair occurrences wholly outside the private set.
    """

    if selected_private_count < 0 or selected_private_count > 8:
        raise ValueError("selected-private count must lie between zero and eight")
    loads = (
        sum(comb(ROW_SIZE - value, 2) for value in distribution)
        for distribution in product(range(3), repeat=len(FRAGILE_CENTERS))
        if sum(distribution) == selected_private_count
    )
    try:
        return min(loads)
    except ValueError as error:
        raise ValueError("selected-private count exceeds retained halo slots") from error


def pair_budget_obstruction(
    *, n: int, selected_private_count: int
) -> dict[str, int | bool]:
    """Return the exact pair-capacity ledger for a proposed private set."""

    if n < len(FRAGILE_CENTERS):
        raise ValueError("full system cannot have fewer than four centers")
    private_count = int(selected_private_count)
    retained_load = minimum_retained_pair_load(private_count)
    nonretained_row_count = n - len(FRAGILE_CENTERS)
    nonretained_load = nonretained_row_count * comb(ROW_SIZE, 2)
    available_pair_capacity = PAIR_CAP * comb(n - private_count, 2)
    required_pair_load = retained_load + nonretained_load
    return {
        "n": n,
        "selected_private_count": private_count,
        "nonretained_row_count": nonretained_row_count,
        "nonretained_pair_load": nonretained_load,
        "minimum_retained_pair_load": retained_load,
        "required_pair_load": required_pair_load,
        "available_pair_capacity": available_pair_capacity,
        "capacity_deficit": required_pair_load - available_pair_capacity,
        "obstructed": required_pair_load > available_pair_capacity,
    }


def _guardrail_summary(raw: Mapping[str, Any]) -> dict[str, Any]:
    order = tuple(int(value) for value in raw["cyclic_order"])
    n = len(order)
    labels = set(order)
    retained = _rows_from_compact(raw["retained_rows"])
    full = _rows_from_compact(raw["full_rows"])
    if set(full) != labels:
        raise AssertionError("guardrail does not contain one row at every center")
    if set(retained) != set(FRAGILE_CENTERS):
        raise AssertionError("guardrail retained-center set changed")
    for center in FRAGILE_CENTERS:
        if retained[center] != full[center]:
            raise AssertionError("full guardrail does not extend retained rows")
        if not REQUIRED_WITNESSES[center].issubset(retained[center]):
            raise AssertionError("retained row lost a required core pair")

    for center, row in full.items():
        if len(row) != ROW_SIZE or len(set(row)) != ROW_SIZE or center in row:
            raise AssertionError("guardrail row violates size or self-exclusion")
    for left, right in combinations(sorted(full), 2):
        if not _selected_pair_ok(left, full[left], right, full[right], order):
            raise AssertionError("guardrail violates intersection/crossing rules")

    pair_counts = _pair_counts(full)
    maximum_pair_multiplicity = max(pair_counts.values(), default=0)
    if maximum_pair_multiplicity > PAIR_CAP:
        raise AssertionError("guardrail violates witness-pair capacity")
    indegrees = _selected_indegrees(full)
    indegree_cap = (PAIR_CAP * (n - 1)) // (ROW_SIZE - 1)
    if max(indegrees.values(), default=0) > indegree_cap:
        raise AssertionError("guardrail violates selected-indegree capacity")

    covered = set().union(*(set(row) for row in retained.values()))
    if covered != labels:
        raise AssertionError("retained guardrail rows do not actively cover labels")
    _, unmatched = essential_row_matching(n, retained)
    if unmatched:
        raise AssertionError("retained guardrail cover is not essential")

    halos = labels - set(CORE_ORDER)
    retained_indegrees = Counter(
        witness for row in retained.values() for witness in row
    )
    retained_private = sorted(
        halo for halo in halos if retained_indegrees[halo] == 1
    )
    selected_private = sorted(halo for halo in retained_private if indegrees[halo] == 1)
    if retained_private != list(raw["expected_retained_private_halos"]):
        raise AssertionError("guardrail retained-private roles changed")
    if selected_private != list(raw["expected_selected_private_halos"]):
        raise AssertionError("guardrail selected-private roles changed")
    reused = sorted(set(retained_private) - set(selected_private))

    deletion = _good_deletion_summary(full)
    if not deletion["all_seeds_have_good_survivor"]:
        raise AssertionError("guardrail failed selected-row good deletion")

    return {
        "name": raw["name"],
        "halo_gaps": list(raw["halo_gaps"]),
        "cyclic_order": list(order),
        "retained_rows": [list(row) for row in raw["retained_rows"]],
        "full_rows": [list(row) for row in raw["full_rows"]],
        "retained_private_halos": retained_private,
        "selected_private_halos": selected_private,
        "reused_retained_private_halos": reused,
        "maximum_pair_multiplicity": maximum_pair_multiplicity,
        "selected_indegree_cap": indegree_cap,
        "maximum_selected_indegree": max(indegrees.values(), default=0),
        "essential_cover_ok": True,
        "pair_crossing_ok": True,
        "all_nonempty_proper_seeds_have_good_survivor": True,
        "nonempty_proper_seed_count": deletion["nonempty_proper_seed_count"],
        "contains_equilateral_hinge": has_equilateral_hinge(full, order),
        "contains_kalmanson_splice": has_kalmanson_splice(full, order),
    }


def private_halo_reuse_payload() -> dict[str, Any]:
    """Build the deterministic proof ledger and guardrail packet."""

    four = pair_budget_obstruction(n=11, selected_private_count=3)
    five = pair_budget_obstruction(n=12, selected_private_count=4)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "pair_budget_lemma": {
            "pair_multiplicity_cap": PAIR_CAP,
            "retained_row_count": len(FRAGILE_CENTERS),
            "row_size": ROW_SIZE,
            "formula": (
                "6*(n-4) + sum_i C(4-p_i,2) <= 2*C(n-q,2)"
            ),
            "four_halos_three_selected_private": four,
            "four_halos_maximum_selected_private": 2,
            "four_halos_minimum_reused_if_three_retained_private": 1,
            "four_halos_minimum_reused_if_four_retained_private": 2,
            "five_halos_four_selected_private": five,
            "five_halos_maximum_selected_private": 3,
            "five_halos_minimum_reused": 2,
        },
        "guardrails": [
            _guardrail_summary(FOUR_HALO_GUARDRAIL),
            _guardrail_summary(FIVE_HALO_GUARDRAIL),
        ],
        "limitations": [
            "The fixed 23=27 quotient core and its four retained rows are assumed.",
            "Selected-private is relative to one chosen full selected-row system.",
            "Selected-private does not imply privacy in every full rich class.",
            "The pair-budget lower bounds are not claimed sharp.",
            "Both stored guardrails contain hinge and splice obstructions.",
            "No Euclidean, n=11, n=12, general, or counterexample claim is made.",
        ],
        "conclusion": CONCLUSION,
        "provenance": PROVENANCE,
    }


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert the proof arithmetic, guardrails, and claim boundary."""

    expected = private_halo_reuse_payload()
    if payload != expected:
        raise AssertionError("private-halo reuse packet changed")


__all__ = [
    "CLAIM_SCOPE",
    "CONCLUSION",
    "FIVE_HALO_GUARDRAIL",
    "FOUR_HALO_GUARDRAIL",
    "PROVENANCE",
    "SCHEMA",
    "STATUS",
    "TRUST",
    "assert_expected_payload",
    "minimum_retained_pair_load",
    "pair_budget_obstruction",
    "private_halo_reuse_payload",
]
