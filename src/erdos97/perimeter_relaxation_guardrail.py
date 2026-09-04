"""Exact guardrail accompanying an alternate-vertex perimeter obstruction.

The geometric theorem documented in
``docs/alternate-vertex-perimeter-obstruction.md`` excludes a restricted
infinite family of selected-witness systems.  The finite object generated here
is an abstract metric relaxation that passes the explicitly replayed triangle,
Kalmanson, incidence/crossing, chord-order, and weak-turn conditions while its
even rows have exactly that forbidden form.

This object is not a planar configuration and not a counterexample to Erdos
Problem #97.  A uniform off-diagonal shift does give an exact Euclidean metric
in dimension 19; that lift still has no claimed planar convex realization.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, permutations
from math import gcd
from typing import Any, Iterable, Sequence

N = 20
CYCLIC_PROFILE = (0, 14, 26, 37, 47, 56, 64, 70, 74, 76, 77)
PARITY_WEIGHT = 50
EVEN_OFFSETS = (1, -1, 6, -6)
ODD_OFFSETS = (2, -2, 9, -9)
EVEN_RADIUS = 64
ODD_RADIUS = 126
UNIFORM_SHIFT = 10_000

SCHEMA = "erdos97.perimeter_relaxation_guardrail.v1"
STATUS = "REVIEW_PENDING_RESTRICTED_THEOREM_AND_EXACT_RELAXATION_CONTROL"
TRUST = "PAPER_PROOF_CANDIDATE_PLUS_EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "A paper-proof candidate excludes one infinite alternate-vertex reciprocal-"
    "cycle family. The exact n=20 metric object is a negative control for the "
    "explicitly replayed relaxations. It is not a planar point configuration, "
    "not a counterexample, not a proof or disproof of Erdos Problem #97, and "
    "not a source-of-truth or official/global status update."
)
CONCLUSION = (
    "Strict triangle and Kalmanson inequalities, selected-row overlap/crossing, "
    "strong connectivity, within-row chord ordering, and the current weak-turn "
    "inequalities do not jointly recover the alternate-vertex perimeter "
    "obstruction. A successful general bridge needs additional planar convex "
    "metric information."
)
REVIEW_REQUIREMENTS = [
    "Review the alternate-vertex perimeter lower bound and the tour-perimeter comparison.",
    "Review the propagation of one common radius along reciprocal step-k edges.",
    "Review each replayed relaxation independently; no unlisted repository filter is claimed.",
    "Review the conditional-negative-type violation for the unshifted metric.",
    "Review the Gershgorin bound certifying the shifted dimension-19 Euclidean lift.",
    "Preserve the distinction between a restricted theorem, an abstract metric, and a planar realization.",
]
PROVENANCE = {
    "generator": "scripts/check_perimeter_relaxation_guardrail.py",
    "command": (
        "python scripts/check_perimeter_relaxation_guardrail.py "
        "--assert-expected --write"
    ),
}

EXPECTED_TRIANGLE_CHECKS = 6_840
EXPECTED_KALMANSON_CHECKS = 9_690
EXPECTED_WEAK_TURN_CHECKS = 240
EXPECTED_CHORD_ORDER_CHECKS = 160
EXPECTED_NEGATIVE_TYPE_VIOLATION = 387_780
EXPECTED_SHIFT_GAP = 32_144_749
EXPECTED_ROW_INTERSECTION_HISTOGRAM = {"0": 90, "1": 80, "2": 20}
EXPECTED_PAIR_MULTIPLICITY_HISTOGRAM = {"1": 80, "2": 20}
EXPECTED_TURN_SUPPORT_SIZE_HISTOGRAM = {
    "5": 20,
    "8": 20,
    "10": 40,
    "13": 40,
    "17": 60,
    "18": 60,
}


def _histogram(values: Iterable[int]) -> dict[str, int]:
    return {
        str(value): count
        for value, count in sorted(Counter(int(value) for value in values).items())
    }


def cyclic_gap(left: int, right: int, *, n: int = N) -> int:
    """Return the unoriented cyclic separation of two labels."""

    forward = (right - left) % n
    return min(forward, n - forward)


def vertex_weights() -> tuple[int, ...]:
    """Return the alternating additive vertex weights."""

    return tuple(PARITY_WEIGHT * (vertex % 2) for vertex in range(N))


def distance_matrix() -> tuple[tuple[int, ...], ...]:
    """Return the exact unshifted abstract metric."""

    weights = vertex_weights()
    return tuple(
        tuple(
            0
            if left == right
            else CYCLIC_PROFILE[cyclic_gap(left, right)]
            + weights[left]
            + weights[right]
            for right in range(N)
        )
        for left in range(N)
    )


def selected_rows() -> list[list[int]]:
    """Return the fixed exact-four witness rows."""

    rows: list[list[int]] = []
    for center in range(N):
        offsets = EVEN_OFFSETS if center % 2 == 0 else ODD_OFFSETS
        rows.append(sorted({(center + offset) % N for offset in offsets}))
    return rows


def formal_turns() -> tuple[Fraction, ...]:
    """Return the strict rational witness for the weak-turn relaxation."""

    return tuple(
        Fraction(1, 10) if vertex % 2 == 0 else Fraction(3, 10)
        for vertex in range(N)
    )


def rich_class_summary(
    distances: Sequence[Sequence[int]], rows: Sequence[Sequence[int]]
) -> dict[str, Any]:
    """Check positivity, symmetry, and the unique exact-four class at each row."""

    records: list[dict[str, Any]] = []
    for center in range(N):
        groups: defaultdict[int, list[int]] = defaultdict(list)
        for witness in range(N):
            if center == witness:
                if distances[center][witness] != 0:
                    raise AssertionError("distance diagonal is nonzero")
                continue
            if distances[center][witness] <= 0:
                raise AssertionError("off-diagonal distance is not positive")
            if distances[center][witness] != distances[witness][center]:
                raise AssertionError("distance matrix is not symmetric")
            groups[int(distances[center][witness])].append(witness)

        rich = {
            radius: sorted(witnesses)
            for radius, witnesses in groups.items()
            if len(witnesses) >= 4
        }
        expected_radius = EVEN_RADIUS if center % 2 == 0 else ODD_RADIUS
        if rich != {expected_radius: sorted(int(value) for value in rows[center])}:
            raise AssertionError(f"unexpected rich classes at center {center}: {rich}")
        records.append(
            {
                "center": center,
                "radius": expected_radius,
                "witnesses": sorted(int(value) for value in rows[center]),
            }
        )

    return {
        "all_rows_self_excluding_exact_four_sets": all(
            len(set(row)) == 4 and center not in row
            for center, row in enumerate(rows)
        ),
        "unique_rich_class_per_center": True,
        "rich_class_size": 4,
        "even_radius": EVEN_RADIUS,
        "odd_radius": ODD_RADIUS,
        "records": records,
    }


def triangle_summary(distances: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Replay every ordered strict triangle inequality."""

    count = 0
    minimum_slack: int | None = None
    for left, middle, right in permutations(range(N), 3):
        slack = (
            int(distances[left][middle])
            + int(distances[middle][right])
            - int(distances[left][right])
        )
        count += 1
        minimum_slack = slack if minimum_slack is None else min(minimum_slack, slack)
    if minimum_slack is None or minimum_slack <= 0:
        raise AssertionError("strict triangle replay failed")
    return {"check_count": count, "minimum_slack": minimum_slack, "strict": True}


def kalmanson_summary(distances: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Replay both strict Kalmanson inequalities for every cyclic quadruple."""

    count = 0
    minimum_slack: int | None = None
    for first, second, third, fourth in combinations(range(N), 4):
        crossing = (
            int(distances[first][third]) + int(distances[second][fourth])
        )
        for uncrossed in (
            int(distances[first][second]) + int(distances[third][fourth]),
            int(distances[first][fourth]) + int(distances[second][third]),
        ):
            slack = crossing - uncrossed
            count += 1
            minimum_slack = (
                slack if minimum_slack is None else min(minimum_slack, slack)
            )
    if minimum_slack is None or minimum_slack <= 0:
        raise AssertionError("strict Kalmanson replay failed")

    extended_profile = [
        CYCLIC_PROFILE[min(index, N - index)] for index in range(N + 1)
    ]
    increments = [
        extended_profile[index + 1] - extended_profile[index]
        for index in range(N)
    ]
    if not all(left > right for left, right in zip(increments, increments[1:])):
        raise AssertionError("cyclic profile increments are not strictly decreasing")
    return {
        "check_count": count,
        "minimum_slack": minimum_slack,
        "strict": True,
        "cyclic_profile_increments": increments,
        "increments_strictly_decreasing": True,
        "additive_vertex_weights_cancel": True,
    }


def _strongly_connected(rows: Sequence[Sequence[int]]) -> bool:
    for root in range(N):
        reached = {root}
        stack = [root]
        while stack:
            center = stack.pop()
            for witness in rows[center]:
                witness = int(witness)
                if witness not in reached:
                    reached.add(witness)
                    stack.append(witness)
        if len(reached) != N:
            return False
    return True


def incidence_summary(rows: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Check degree, overlap, crossing, connectivity, and the forbidden subpattern."""

    indegrees = Counter(int(witness) for row in rows for witness in row)
    if any(indegrees[vertex] != 4 for vertex in range(N)):
        raise AssertionError("witness indegrees are not uniformly four")

    row_intersections: list[int] = []
    crossing_pair_count = 0
    for left, right in combinations(range(N), 2):
        common = set(rows[left]).intersection(rows[right])
        row_intersections.append(len(common))
        if len(common) > 2:
            raise AssertionError("two selected rows overlap in more than two labels")
        if len(common) == 2:
            crossing_pair_count += 1
            first, second = sorted(common)
            if (first < left < second) == (first < right < second):
                raise AssertionError("a two-overlap center chord does not cross")

    pair_multiplicities: Counter[tuple[int, int]] = Counter()
    for row in rows:
        for left, right in combinations(sorted(int(value) for value in row), 2):
            pair_multiplicities[(left, right)] += 1
    if max(pair_multiplicities.values()) > 2:
        raise AssertionError("a witness pair appears in more than two rows")

    connected = _strongly_connected(rows)
    if not connected:
        raise AssertionError("selected digraph is not strongly connected")

    even_cycle = [0]
    for _ in range(N // 2):
        even_cycle.append((even_cycle[-1] + 6) % N)
    if even_cycle[-1] != 0 or len(set(even_cycle[:-1])) != N // 2:
        raise AssertionError("the even reciprocal step does not form a Hamiltonian cycle")
    if not all(
        next_vertex in rows[center]
        for center, next_vertex in zip(even_cycle, even_cycle[1:])
    ):
        raise AssertionError("the even cycle uses a nonselected edge")

    return {
        "every_witness_indegree": 4,
        "row_intersection_size_histogram": _histogram(row_intersections),
        "maximum_row_overlap": max(row_intersections),
        "two_overlap_pair_count": crossing_pair_count,
        "all_two_overlap_center_witness_chords_cross": True,
        "pair_multiplicity_histogram": _histogram(pair_multiplicities.values()),
        "selected_digraph_strongly_connected": connected,
        "proper_closed_all_rich_subset_excluded": True,
        "alternate_vertex_forbidden_subsystem": {
            "m": N // 2,
            "k": 3,
            "gcd_m_k": gcd(N // 2, 3),
            "centers": list(range(0, N, 2)),
            "step_on_full_labels": 6,
            "reciprocal_hamiltonian_cycle": even_cycle,
            "boundary_neighbors_selected_at_every_even_center": True,
        },
    }


def weak_turn_summary(rows: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Replay the repository weak-turn interval convention exactly."""

    turns = formal_turns()
    if sum(turns) != 4 or min(turns) <= 0:
        raise AssertionError("formal turn vector is not positive with sum four")

    support_sizes: list[int] = []
    slacks: list[Fraction] = []
    for center, row in enumerate(rows):
        offsets = sorted((int(witness) - center) % N for witness in row)
        for left, right in combinations(offsets, 2):
            supports = (
                [(center + offset) % N for offset in range(1, right)],
                [(center + offset) % N for offset in range(left + 1, N)],
            )
            for support in supports:
                support_sizes.append(len(support))
                slacks.append(sum((turns[vertex] for vertex in support), Fraction()) - 1)
    minimum_slack = min(slacks)
    if minimum_slack <= 0:
        raise AssertionError("weak-turn replay is not strictly feasible")
    return {
        "formal_turn_vector": [str(value) for value in turns],
        "sum_constraint": str(sum(turns)),
        "check_count": len(slacks),
        "support_size_histogram": _histogram(support_sizes),
        "minimum_slack": str(minimum_slack),
        "all_terms_strictly_satisfied": True,
        "interpretation": "Formal relaxation witness only; these are not planar polygon angles.",
    }


def chord_order_summary(
    distances: Sequence[Sequence[int]], rows: Sequence[Sequence[int]]
) -> dict[str, Any]:
    """Check the within-row three-witness Kalmanson consequences."""

    slacks: list[int] = []
    for center, row in enumerate(rows):
        ordered = sorted(row, key=lambda witness: (int(witness) - center) % N)
        for first, second, third in combinations(ordered, 3):
            slacks.extend(
                [
                    int(distances[first][third]) - int(distances[first][second]),
                    int(distances[first][third]) - int(distances[second][third]),
                ]
            )
    if min(slacks) <= 0:
        raise AssertionError("within-row chord-order replay failed")
    return {
        "check_count": len(slacks),
        "minimum_slack": min(slacks),
        "strict": True,
        "slack_histogram": _histogram(slacks),
    }


def negative_type_summary(distances: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Give an exact obstruction to Euclidean realization of the unshifted metric."""

    coefficients = tuple(1 if vertex % 2 == 0 else -1 for vertex in range(N))
    if sum(coefficients) != 0:
        raise AssertionError("negative-type test coefficients do not sum to zero")
    energy = sum(
        coefficients[left]
        * coefficients[right]
        * int(distances[left][right]) ** 2
        for left in range(N)
        for right in range(N)
    )
    if energy <= 0:
        raise AssertionError("expected a positive squared-distance energy")
    return {
        "coefficients": list(coefficients),
        "coefficient_sum": 0,
        "squared_distance_energy": energy,
        "violates_euclidean_conditional_negative_type": True,
        "identity": (
            "For Euclidean points and sum(c_i)=0, sum_ij c_i*c_j*d_ij^2 "
            "= -2*||sum_i c_i*p_i||^2 <= 0."
        ),
    }


def shifted_euclidean_summary(distances: Sequence[Sequence[int]]) -> dict[str, Any]:
    """Certify a dimension-19 Euclidean lift after one uniform distance shift."""

    maximum_distance = max(max(int(value) for value in row) for row in distances)
    maximum_error_entry = (
        2 * UNIFORM_SHIFT * maximum_distance + maximum_distance**2
    )
    error_row_sum_bound = (N - 1) * maximum_error_entry
    strict_gap = UNIFORM_SHIFT**2 - error_row_sum_bound
    if strict_gap <= 0:
        raise AssertionError("uniform-shift conditional-negative-type bound failed")
    return {
        "uniform_off_diagonal_shift": UNIFORM_SHIFT,
        "maximum_unshifted_distance": maximum_distance,
        "maximum_error_entry": maximum_error_entry,
        "gershgorin_error_row_sum_bound": error_row_sum_bound,
        "strict_conditional_negative_type_gap": strict_gap,
        "strict_conditional_negative_type_certified": True,
        "certified_affine_embedding_dimension": N - 1,
        "selected_equalities_preserved": True,
        "strict_kalmanson_slacks_preserved": True,
        "interpretation": (
            "The shifted metric has an exact Euclidean realization in R^19, "
            "but no planar or convex realization is claimed."
        ),
    }


def control_payload() -> dict[str, Any]:
    """Return the stable exact relaxation-control payload."""

    distances = distance_matrix()
    rows = selected_rows()
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "cyclic_order": list(range(N)),
        "construction": {
            "cyclic_profile": list(CYCLIC_PROFILE),
            "parity_weight": PARITY_WEIGHT,
            "even_offsets": list(EVEN_OFFSETS),
            "odd_offsets": list(ODD_OFFSETS),
            "distance_formula": (
                "d(i,j)=f[min((i-j) mod 20,(j-i) mod 20)]+w_i+w_j "
                "for i!=j; d(i,i)=0; w_i=50*(i mod 2)."
            ),
        },
        "selected_rows": rows,
        "rich_classes": rich_class_summary(distances, rows),
        "strict_triangle_replay": triangle_summary(distances),
        "strict_kalmanson_replay": kalmanson_summary(distances),
        "incidence_replay": incidence_summary(rows),
        "within_row_chord_order_replay": chord_order_summary(distances, rows),
        "weak_turn_replay": weak_turn_summary(rows),
        "unshifted_euclidean_obstruction": negative_type_summary(distances),
        "shifted_high_dimensional_euclidean_lift": shifted_euclidean_summary(
            distances
        ),
        "limitations": [
            "The restricted perimeter theorem is not a general extraction theorem.",
            "The unshifted metric is abstract and is not Euclidean in any dimension.",
            "The shifted Euclidean lift has dimension 19, not dimension 2.",
            "No planar strictly convex realization is supplied or claimed.",
            "Only the explicitly named relaxations are replayed.",
            "No proof, disproof, or counterexample for Erdos Problem #97 is claimed.",
        ],
        "conclusion": CONCLUSION,
        "review_requirements": list(REVIEW_REQUIREMENTS),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_payload(payload: dict[str, Any]) -> None:
    """Assert stable exact fields for the guardrail."""

    expected = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "cyclic_order": list(range(N)),
        "conclusion": CONCLUSION,
        "review_requirements": REVIEW_REQUIREMENTS,
        "provenance": PROVENANCE,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise AssertionError(
                f"{key}: expected {value!r}, got {payload.get(key)!r}"
            )

    rich = payload["rich_classes"]
    if rich.get("unique_rich_class_per_center") is not True:
        raise AssertionError("rich classes are not unique")
    if rich.get("rich_class_size") != 4:
        raise AssertionError("unexpected rich-class size")
    if rich.get("even_radius") != EVEN_RADIUS or rich.get("odd_radius") != ODD_RADIUS:
        raise AssertionError("unexpected selected radius")

    triangle = payload["strict_triangle_replay"]
    if triangle.get("check_count") != EXPECTED_TRIANGLE_CHECKS:
        raise AssertionError("unexpected strict triangle check count")
    if triangle.get("minimum_slack") != 2:
        raise AssertionError("unexpected strict triangle minimum slack")

    kalmanson = payload["strict_kalmanson_replay"]
    if kalmanson.get("check_count") != EXPECTED_KALMANSON_CHECKS:
        raise AssertionError("unexpected strict Kalmanson check count")
    if kalmanson.get("minimum_slack") != 1:
        raise AssertionError("unexpected strict Kalmanson minimum slack")

    incidence = payload["incidence_replay"]
    if (
        incidence.get("row_intersection_size_histogram")
        != EXPECTED_ROW_INTERSECTION_HISTOGRAM
    ):
        raise AssertionError("unexpected row-intersection histogram")
    if (
        incidence.get("pair_multiplicity_histogram")
        != EXPECTED_PAIR_MULTIPLICITY_HISTOGRAM
    ):
        raise AssertionError("unexpected witness-pair multiplicity histogram")
    if incidence.get("two_overlap_pair_count") != 20:
        raise AssertionError("unexpected two-overlap pair count")
    if incidence.get("selected_digraph_strongly_connected") is not True:
        raise AssertionError("selected digraph is not strongly connected")
    forbidden = incidence["alternate_vertex_forbidden_subsystem"]
    if forbidden.get("m") != 10 or forbidden.get("k") != 3:
        raise AssertionError("unexpected alternate-vertex subsystem")
    if forbidden.get("gcd_m_k") != 1:
        raise AssertionError("alternate-vertex step is not coprime")

    turns = payload["weak_turn_replay"]
    if turns.get("check_count") != EXPECTED_WEAK_TURN_CHECKS:
        raise AssertionError("unexpected weak-turn check count")
    if turns.get("minimum_slack") != "1/10":
        raise AssertionError("unexpected weak-turn minimum slack")
    if turns.get("support_size_histogram") != EXPECTED_TURN_SUPPORT_SIZE_HISTOGRAM:
        raise AssertionError("unexpected weak-turn support histogram")

    chord_order = payload["within_row_chord_order_replay"]
    if chord_order.get("check_count") != EXPECTED_CHORD_ORDER_CHECKS:
        raise AssertionError("unexpected chord-order check count")
    if chord_order.get("minimum_slack") != 6:
        raise AssertionError("unexpected chord-order minimum slack")

    obstruction = payload["unshifted_euclidean_obstruction"]
    if (
        obstruction.get("squared_distance_energy")
        != EXPECTED_NEGATIVE_TYPE_VIOLATION
    ):
        raise AssertionError("unexpected negative-type violation")

    lift = payload["shifted_high_dimensional_euclidean_lift"]
    if lift.get("strict_conditional_negative_type_gap") != EXPECTED_SHIFT_GAP:
        raise AssertionError("unexpected shifted Euclidean gap")
    if lift.get("certified_affine_embedding_dimension") != N - 1:
        raise AssertionError("unexpected shifted embedding dimension")


def validate_payload(payload: dict[str, Any]) -> list[str]:
    """Compare a stored artifact with complete deterministic regeneration."""

    errors: list[str] = []
    try:
        assert_expected_payload(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))
        return errors
    if payload != control_payload():
        errors.append("stored payload differs from complete regenerated guardrail")
    return errors
