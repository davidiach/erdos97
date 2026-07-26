"""Exact abstract guardrail for the fragile/turn/pivot bridge.

The circulant selected-row system

``S_i = i + {2, 9, 10, 13} (mod 16)``

passes the currently isolated fragile-cover, pair/crossing, good-deletion,
hinge-free, weak-turn, and vertex-circle conditions.  It also admits an
essential row-to-witness matching with a genuine three-cycle and a
three-witness halo at every matched row.

An exact two-row Kalmanson inverse certificate rejects the same fixed cyclic
order, so this is an abstract negative control rather than a Euclidean
configuration or a counterexample to Erdos Problem #97.  Its purpose is to
show that a general three-pivot contradiction needs stronger convex metric
information than the current bridge axioms.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Any, Sequence

from erdos97.fragile_hypergraph import check_fragile_hypergraph, check_to_json
from erdos97.n9_turn_inequality_frontier import turn_inequality_terms_for_pattern
from erdos97.quotient_cone import (
    kalmanson_row,
    rows_from_circulant_offsets,
    selected_distance_quotient,
)
from erdos97.vertex_circle_quotient_replay import (
    parse_selected_rows,
    replay_vertex_circle_quotient,
)

N = 16
OFFSETS = (2, 9, 10, 13)
ORDER = tuple(range(N))

SCHEMA = "erdos97.fragile_turn_pivot_guardrail.v1"
STATUS = "MACHINE_CHECKED_ABSTRACT_BRIDGE_NEGATIVE_CONTROL"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact abstract n=16 negative control for a proposed general "
    "fragile-matching/three-pivot bridge: it passes the currently isolated "
    "fragile-cover, pair/crossing, good-deletion, hinge-free, weak-turn, and "
    "vertex-circle conditions but is rejected by an exact Kalmanson inverse "
    "pair; not a Euclidean realization, not a counterexample, not a proof or "
    "disproof of Erdos Problem #97, and not a source-of-truth or "
    "official/global status update."
)
CONCLUSION = (
    "The current abstract fragile-cover, incidence/crossing, good-deletion, "
    "hinge-free, weak-turn, and vertex-circle conditions do not by themselves "
    "force a contradiction from a surjective fragile matching with a marked "
    "three-cycle and three-witness halos. The exact Kalmanson inverse pair "
    "shows that stronger convex metric information rejects this fixed-order "
    "negative control."
)
REVIEW_REQUIREMENTS = [
    "Review the distinction between abstract selected-row data and Euclidean realization.",
    "Review the good-deletion condition when the displayed rows are the only rich classes.",
    "Review the canonical weak-turn interval indexing and strict uniform witness.",
    "Review the vertex-circle quotient replay and the exact Kalmanson inverse pair.",
    "Do not call the restricted-search discovery globally minimal.",
]
PROVENANCE = {
    "generator": "scripts/check_fragile_turn_pivot_guardrail.py",
    "command": (
        "python scripts/check_fragile_turn_pivot_guardrail.py "
        "--assert-expected --write"
    ),
}

EXPECTED_PAIR_MULTIPLICITY_HISTOGRAM = {"1": 80, "2": 8}
EXPECTED_ROW_INTERSECTION_SIZE_HISTOGRAM = {"0": 32, "1": 80, "2": 8}
EXPECTED_GOOD_DELETION_SEED_COUNT = (1 << N) - 2
EXPECTED_MATCHING_CYCLE_TYPE = [3, 13]
EXPECTED_TURN_SUPPORT_SIZE_HISTOGRAM = {
    "5": 16,
    "6": 32,
    "8": 16,
    "9": 32,
    "12": 48,
    "13": 48,
}
EXPECTED_VERTEX_CIRCLE_STRICT_EDGES = 144

# Written in cycle order for reviewer readability.
MATCHING_CYCLES = (
    (0, 9, 3),
    (1, 10, 12, 5, 14, 7, 4, 6, 8, 2, 11, 13, 15),
)


def selected_rows() -> list[list[int]]:
    """Return the fixed circulant selected-row system."""

    return rows_from_circulant_offsets(N, OFFSETS)


def matching_permutation() -> tuple[int, ...]:
    """Return the row-to-generating-witness permutation from its cycles."""

    permutation = list(range(N))
    for cycle in MATCHING_CYCLES:
        for index, center in enumerate(cycle):
            permutation[center] = cycle[(index + 1) % len(cycle)]
    return tuple(permutation)


def inverse_permutation(permutation: Sequence[int]) -> tuple[int, ...]:
    """Return the inverse of a permutation."""

    if sorted(int(value) for value in permutation) != list(range(len(permutation))):
        raise ValueError("input is not a permutation")
    inverse = [0] * len(permutation)
    for center, witness in enumerate(permutation):
        inverse[int(witness)] = center
    return tuple(inverse)


def cycle_type(permutation: Sequence[int]) -> tuple[int, ...]:
    """Return sorted cycle lengths."""

    if sorted(int(value) for value in permutation) != list(range(len(permutation))):
        raise ValueError("input is not a permutation")
    seen: set[int] = set()
    lengths: list[int] = []
    for start in range(len(permutation)):
        if start in seen:
            continue
        cursor = start
        length = 0
        while cursor not in seen:
            seen.add(cursor)
            length += 1
            cursor = int(permutation[cursor])
        lengths.append(length)
    return tuple(sorted(lengths))


def pair_multiplicity_histogram(
    rows: Sequence[Sequence[int]],
) -> dict[str, int]:
    """Count unordered witness-pair multiplicities over selected rows."""

    pair_counts: Counter[tuple[int, int]] = Counter()
    for row in rows:
        for left, right in combinations(sorted(int(value) for value in row), 2):
            pair_counts[(left, right)] += 1
    return {
        str(multiplicity): count
        for multiplicity, count in sorted(Counter(pair_counts.values()).items())
    }


def row_intersection_size_histogram(
    rows: Sequence[Sequence[int]],
) -> dict[str, int]:
    """Count row-pair intersection sizes."""

    sizes = [
        len(set(rows[left]).intersection(rows[right]))
        for left, right in combinations(range(len(rows)), 2)
    ]
    return {
        str(size): count for size, count in sorted(Counter(sizes).items())
    }


def reciprocal_selected_pairs(rows: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return center pairs that select one another."""

    return [
        [left, right]
        for left, right in combinations(range(len(rows)), 2)
        if right in rows[left] and left in rows[right]
    ]


def good_deletion_summary(rows: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Exhaust all nonempty proper deletion seeds.

    With the displayed exact-four rows treated as the only rich classes, a
    surviving center is good after deleting seed ``A`` exactly when its row
    meets ``A``.  The closure condition asks for at least one such center for
    every nonempty proper seed.
    """

    eligible_count_histogram: Counter[int] = Counter()
    violating_seeds: list[list[int]] = []
    full_mask = (1 << N) - 1
    for deleted_mask in range(1, full_mask):
        eligible = []
        for center, row in enumerate(rows):
            if (deleted_mask >> center) & 1:
                continue
            if any((deleted_mask >> int(witness)) & 1 for witness in row):
                eligible.append(center)
        eligible_count_histogram[len(eligible)] += 1
        if not eligible:
            violating_seeds.append(
                [
                    vertex
                    for vertex in range(N)
                    if (deleted_mask >> vertex) & 1
                ]
            )
    return {
        "nonempty_proper_seed_count": full_mask - 1,
        "all_seeds_have_good_survivor": not violating_seeds,
        "violating_seeds": violating_seeds,
        "eligible_center_count_histogram": {
            str(count): multiplicity
            for count, multiplicity in sorted(eligible_count_histogram.items())
        },
        "generator_proof": (
            "If a surviving set Q contains S_i for every i in Q, then Q is "
            "invariant under +2 and +9. Since 9 - 4*2 = 1 modulo 16, Q is "
            "empty or all of Z/16."
        ),
    }


def _minimal_supports(supports: Sequence[frozenset[int]]) -> list[frozenset[int]]:
    unique = sorted(set(supports), key=lambda support: (len(support), sorted(support)))
    return [
        support
        for support in unique
        if not any(other < support for other in unique)
    ]


def turn_summary(rows: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Check every canonical weak-turn term with the uniform strict witness."""

    terms = turn_inequality_terms_for_pattern(rows, n=N)
    support_sizes = [len(term["support"]) for term in terms]
    support_sums_quarters = [size for size in support_sizes]
    row0_supports = [
        frozenset(int(value) for value in term["support"])
        for term in terms
        if int(term["center"]) == 0
    ]
    minimal = _minimal_supports(row0_supports)
    return {
        "term_count": len(terms),
        "support_size_histogram": {
            str(size): count
            for size, count in sorted(Counter(support_sizes).items())
        },
        "uniform_turn_vector": ["1/4"] * N,
        "sum_constraint": "16*(1/4)=4",
        "minimum_support_sum": f"{min(support_sums_quarters)}/4",
        "all_weak_terms_strictly_satisfied": all(
            numerator > 4 for numerator in support_sums_quarters
        ),
        "row0_inclusion_minimal_supports": [
            sorted(support) for support in minimal
        ],
        "row0_inclusion_minimal_support_sizes": sorted(
            len(support) for support in minimal
        ),
        "essential_support_sums": [
            f"{len(support)}/4" for support in minimal
        ],
    }


def vertex_circle_summary(rows: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Replay the full selected system through the exact quotient checker."""

    replay = replay_vertex_circle_quotient(
        N,
        ORDER,
        parse_selected_rows(rows),
    )
    return {
        "status": replay.status,
        "selected_row_count": replay.selected_row_count,
        "strict_edge_count": replay.strict_edge_count,
        "self_edge_conflict_count": len(replay.self_edge_conflicts),
        "strict_cycle_edge_count": len(replay.cycle_edges),
        "hand_potential": {
            "level_0": ["cyclic gap 5"],
            "level_1": ["cyclic gap 4", "cyclic gap 8"],
            "level_2": ["cyclic gap 1", "each selected radius class R_i"],
            "claim": "Every strict quotient edge increases the displayed level.",
        },
    }


def kalmanson_inverse_summary(rows: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Check the exact two-row Kalmanson zero-sum certificate."""

    quotient = selected_distance_quotient(rows)
    first = kalmanson_row(
        quotient,
        "K1_diag_gt_sides",
        [0, 3, 7, 9],
    )
    second = kalmanson_row(
        quotient,
        "K2_diag_gt_other",
        [0, 3, 9, 13],
    )
    combined = tuple(
        left + right for left, right in zip(first.vector, second.vector)
    )
    return {
        "strict_row_count": 2,
        "distance_class_count": quotient.class_count,
        "rows": [
            {
                "kind": str(first.metadata["kind"]),
                "quad": list(first.metadata["quad"]),
                "terms": [
                    [[pair[0], pair[1]], coefficient]
                    for pair, coefficient in first.terms
                ],
            },
            {
                "kind": str(second.metadata["kind"]),
                "quad": list(second.metadata["quad"]),
                "terms": [
                    [[pair[0], pair[1]], coefficient]
                    for pair, coefficient in second.terms
                ],
            },
        ],
        "combined_nonzero_coefficient_count": sum(
            coefficient != 0 for coefficient in combined
        ),
        "zero_sum_verified": not any(combined),
        "selected_equality_cancellation": [
            "d(0,7)=d(7,9) from row 7",
            "d(0,9)=d(0,13) from row 0",
            "d(3,13)=d(0,3) from row 3",
        ],
        "interpretation": (
            "The two strict Kalmanson left-minus-right expressions sum to "
            "zero in the selected-distance quotient, so this fixed cyclic "
            "order is not realizable by a strictly convex polygon."
        ),
    }


def guardrail_payload() -> dict[str, Any]:
    """Return the stable exact abstract negative-control payload."""

    rows = selected_rows()
    matching = matching_permutation()
    witness_map = inverse_permutation(matching)
    fragile = check_fragile_hypergraph(
        N,
        {center: row for center, row in enumerate(rows)},
        order=ORDER,
        witness_map={
            vertex: center for vertex, center in enumerate(witness_map)
        },
    )
    if not fragile.ok:
        raise AssertionError("fixed guardrail fails the fragile-hypergraph check")
    if any(matching[center] not in rows[center] for center in range(N)):
        raise AssertionError("fixed matching uses a witness outside its row")

    halos = [
        {
            "deleted_vertex": witness,
            "fragile_center": center,
            "halo": sorted(set(rows[center]) - {witness}),
        }
        for center, witness in enumerate(matching)
    ]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "cyclic_order": list(ORDER),
        "circulant_offsets": list(OFFSETS),
        "selected_rows": rows,
        "fragile_hypergraph": check_to_json(fragile),
        "pair_multiplicity_histogram": pair_multiplicity_histogram(rows),
        "row_intersection_size_histogram": row_intersection_size_histogram(rows),
        "good_deletion": good_deletion_summary(rows),
        "hinge_guardrail": {
            "reciprocal_selected_pair_count": len(
                reciprocal_selected_pairs(rows)
            ),
            "reciprocal_selected_pairs": reciprocal_selected_pairs(rows),
            "offsets": list(OFFSETS),
            "negative_offsets": sorted((-offset) % N for offset in OFFSETS),
        },
        "essential_matching": {
            "center_to_witness": list(matching),
            "witness_to_center": list(witness_map),
            "cycle_type": list(cycle_type(matching)),
            "cycles": [list(cycle) for cycle in MATCHING_CYCLES],
            "marked_three_cycle": list(MATCHING_CYCLES[0]),
            "all_matching_edges_in_rows": True,
            "all_halo_sizes": sorted({len(record["halo"]) for record in halos}),
            "halos": halos,
        },
        "weak_turn_replay": turn_summary(rows),
        "vertex_circle_replay": vertex_circle_summary(rows),
        "kalmanson_inverse": kalmanson_inverse_summary(rows),
        "limitations": [
            "This is abstract selected-row data, not point coordinates.",
            "Passing necessary incidence, turn, and vertex-circle checks is not a realization certificate.",
            "The exact Kalmanson inverse pair rejects the fixed natural cyclic order.",
            "The restricted circulant scan that found this model does not establish global minimality.",
            "No proof, disproof, or counterexample for Erdos Problem #97 is claimed.",
        ],
        "conclusion": CONCLUSION,
        "review_requirements": list(REVIEW_REQUIREMENTS),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_payload(payload: dict[str, Any]) -> None:
    """Assert stable exact fields for the abstract negative control."""

    expected = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "cyclic_order": list(ORDER),
        "circulant_offsets": list(OFFSETS),
        "pair_multiplicity_histogram": EXPECTED_PAIR_MULTIPLICITY_HISTOGRAM,
        "row_intersection_size_histogram": (
            EXPECTED_ROW_INTERSECTION_SIZE_HISTOGRAM
        ),
        "conclusion": CONCLUSION,
        "review_requirements": REVIEW_REQUIREMENTS,
        "provenance": PROVENANCE,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise AssertionError(
                f"{key}: expected {value!r}, got {payload.get(key)!r}"
            )

    fragile = payload["fragile_hypergraph"]
    for key in (
        "ok",
        "cover_ok",
        "self_exclusion_ok",
        "uniformity_ok",
        "pairwise_intersection_ok",
        "crossing_ok",
        "essential_cover_ok",
        "witness_map_ok",
    ):
        if fragile.get(key) is not True:
            raise AssertionError(f"fragile_hypergraph.{key} is not true")

    good_deletion = payload["good_deletion"]
    if (
        good_deletion.get("nonempty_proper_seed_count")
        != EXPECTED_GOOD_DELETION_SEED_COUNT
    ):
        raise AssertionError("unexpected good-deletion seed count")
    if good_deletion.get("all_seeds_have_good_survivor") is not True:
        raise AssertionError("good-deletion closure failed")

    hinge = payload["hinge_guardrail"]
    if hinge.get("reciprocal_selected_pair_count") != 0:
        raise AssertionError("unexpected reciprocal selected pair")

    matching = payload["essential_matching"]
    if matching.get("cycle_type") != EXPECTED_MATCHING_CYCLE_TYPE:
        raise AssertionError("unexpected matching cycle type")
    if matching.get("all_halo_sizes") != [3]:
        raise AssertionError("unexpected matching halo size")

    turn = payload["weak_turn_replay"]
    if (
        turn.get("support_size_histogram")
        != EXPECTED_TURN_SUPPORT_SIZE_HISTOGRAM
    ):
        raise AssertionError("unexpected turn support-size histogram")
    if turn.get("all_weak_terms_strictly_satisfied") is not True:
        raise AssertionError("uniform turn witness is not strict")
    if turn.get("row0_inclusion_minimal_support_sizes") != [5, 8]:
        raise AssertionError("unexpected inclusion-minimal turn supports")

    vertex_circle = payload["vertex_circle_replay"]
    if vertex_circle.get("status") != "ok":
        raise AssertionError("unexpected vertex-circle obstruction")
    if (
        vertex_circle.get("strict_edge_count")
        != EXPECTED_VERTEX_CIRCLE_STRICT_EDGES
    ):
        raise AssertionError("unexpected vertex-circle strict-edge count")
    if vertex_circle.get("self_edge_conflict_count") != 0:
        raise AssertionError("unexpected vertex-circle self-edge")
    if vertex_circle.get("strict_cycle_edge_count") != 0:
        raise AssertionError("unexpected vertex-circle strict cycle")

    kalmanson = payload["kalmanson_inverse"]
    if kalmanson.get("zero_sum_verified") is not True:
        raise AssertionError("Kalmanson inverse pair did not sum to zero")
    if kalmanson.get("combined_nonzero_coefficient_count") != 0:
        raise AssertionError("Kalmanson inverse pair has nonzero coefficients")


def validate_payload(payload: dict[str, Any]) -> list[str]:
    """Compare a stored artifact with a complete deterministic regeneration."""

    errors: list[str] = []
    try:
        assert_expected_payload(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))
        return errors
    if payload != guardrail_payload():
        errors.append("stored payload differs from complete regenerated guardrail")
    return errors
