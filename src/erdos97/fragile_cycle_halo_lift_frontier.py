"""Exact bounded halo-lift frontier for the scalable seven-role quotient.

The proper quotient that identifies scalable-template roles 23 and 27 has
seven core roles.  This module asks how many additional cyclic halo roles are
needed to lift its four retained strict rows to an abstract fragile cover and
then to a full selected-row incidence system.

The computation is deliberately combinatorial.  It checks the row-intersection
cap, the crossing rule for two-overlaps, witness-pair capacity, selected
indegree capacity, cover essentiality, and (for complete systems) good
deletion.  At the first complete boundary, n=9, it joins the witnesses to the
stored review-pending vertex-circle classification and exact positive-circuit
duals.  Nothing here constructs or certifies a Euclidean realization.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations, combinations_with_replacement
import json
from typing import Any, Iterable, Mapping, Sequence

from erdos97.fragile_hypergraph import (
    _selected_pair_ok,
    check_fragile_hypergraph,
    check_to_json,
    essential_row_matching,
)


SCHEMA = "erdos97.fragile_cycle_halo_lift_frontier.v1"
STATUS = "EXACT_BOUNDED_HALO_LIFT_DIAGNOSTIC"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact bounded abstract halo-lift diagnostic for the two proper seven-role "
    "quotients of the stored scalable four-row Kalmanson circuit: it checks "
    "zero, one, and two added cyclic halo roles under stated incidence, "
    "crossing, capacity, cover, and full-selected-extension rules, then joins "
    "the six n=9 extension witnesses to stored review-pending vertex-circle "
    "positive circuits; not a Euclidean realization, not a fragile-cycle "
    "forcing lemma, not a proof of n=9, not a general proof, not a "
    "counterexample, and not an official/global status update."
)
CONCLUSION = (
    "Center injectivity rejects the 18=23 quotient as a lift of four distinct "
    "retained fragile rows.  For the 23=27 quotient, one added halo role is "
    "necessary and sufficient for a four-row fragile cover, while two are "
    "necessary and sufficient within this bounded search for a full selected "
    "incidence extension.  Exactly six of the 7,708 two-halo cover lifts admit "
    "a deterministic full-extension witness; all six are among the stored "
    "n=9 frontier assignments and inherit exact positive-circuit "
    "contradictions.  This sharpens a proof-mining target but does not force "
    "the quotient from minimal-counterexample geometry."
)
PROVENANCE = {
    "generator": "scripts/check_fragile_cycle_halo_lift_frontier.py",
    "command": (
        "python scripts/check_fragile_cycle_halo_lift_frontier.py "
        "--write --assert-expected"
    ),
}

FRONTIER_SCHEMA = "erdos97.n9_vertex_circle_frontier_motif_classification.v1"
DUAL_SCHEMA = "erdos97.n9_vertex_circle_template_duals.v1"

CORE_ORDER = tuple(range(7))
FRAGILE_CENTERS = (1, 3, 4, 6)
REQUIRED_WITNESSES = {
    1: frozenset((0, 4)),
    3: frozenset((4, 5)),
    4: frozenset((0, 2)),
    6: frozenset((2, 5)),
}
CORE_ROLE_BLOCKS = [[1], [8], [16], [18], [23, 27], [37], [44]]
ROW_SIZE = 4
PAIR_CAP = 2

EXPECTED_ONE_HALO_COUNTS = [4, 9, 9, 6, 3, 3, 4]
EXPECTED_TWO_HALO_PARTIAL_COUNTS = [
    252,
    339,
    339,
    237,
    223,
    223,
    252,
    426,
    426,
    308,
    305,
    305,
    339,
    426,
    308,
    305,
    305,
    339,
    200,
    194,
    194,
    237,
    176,
    176,
    223,
    176,
    223,
    252,
]
EXPECTED_TWO_HALO_EXTENDABLE_COUNTS = [
    0,
    0,
    0,
    0,
    0,
    0,
    1,
    0,
    0,
    0,
    0,
    1,
    0,
    0,
    0,
    0,
    0,
    1,
    0,
    1,
    1,
    0,
    0,
    0,
    0,
    0,
    1,
    0,
]
EXPECTED_ASSIGNMENT_IDS = ["A138", "A008", "A079", "A121", "A179", "A069"]
EXPECTED_FAMILY_IDS = ["F04", "F07", "F05", "F01", "F11", "F11"]
EXPECTED_TEMPLATE_IDS = ["T02", "T11", "T03", "T02", "T06", "T06"]

Rows = dict[int, tuple[int, ...]]
Pair = tuple[int, int]


def _pair(left: int, right: int) -> Pair:
    return (left, right) if left < right else (right, left)


def _rows_json(rows: Mapping[int, Sequence[int]]) -> list[list[int]]:
    return [
        [center, *sorted(int(value) for value in rows[center])]
        for center in sorted(rows)
    ]


def _rows_from_compact(raw_rows: Sequence[Sequence[int]]) -> Rows:
    return {
        int(raw[0]): tuple(sorted(int(value) for value in raw[1:])) for raw in raw_rows
    }


def _pair_counts(rows: Mapping[int, Sequence[int]]) -> Counter[Pair]:
    counts: Counter[Pair] = Counter()
    for row in rows.values():
        for left, right in combinations(sorted(set(row)), 2):
            counts[_pair(left, right)] += 1
    return counts


def _selected_indegrees(rows: Mapping[int, Sequence[int]]) -> Counter[int]:
    return Counter(int(value) for row in rows.values() for value in row)


def cyclic_order_for_gaps(gaps: Sequence[int]) -> tuple[int, ...]:
    """Insert canonically labelled, otherwise interchangeable halos after gaps."""

    normalized = tuple(sorted(int(gap) for gap in gaps))
    if normalized != tuple(int(gap) for gap in gaps):
        raise ValueError("halo gaps must be nondecreasing")
    if any(gap not in CORE_ORDER for gap in normalized):
        raise ValueError("halo gap must be one of the seven core labels")
    multiplicity = Counter(normalized)
    order: list[int] = []
    halo = len(CORE_ORDER)
    for core in CORE_ORDER:
        order.append(core)
        for _ in range(multiplicity[core]):
            order.append(halo)
            halo += 1
    return tuple(order)


def _fragile_row_options(order: Sequence[int], center: int) -> list[tuple[int, ...]]:
    labels = set(int(label) for label in order)
    required = REQUIRED_WITNESSES[center]
    pool = sorted(labels - {center} - required)
    return [
        tuple(sorted(required | set(extra)))
        for extra in combinations(pool, ROW_SIZE - len(required))
    ]


def enumerate_fragile_covers(order: Sequence[int]) -> dict[str, Any]:
    """Exhaust four-row lifts and retain essential capacity-respecting covers."""

    options = {
        center: _fragile_row_options(order, center) for center in FRAGILE_CENTERS
    }
    raw_count = 1
    for center in FRAGILE_CENTERS:
        raw_count *= len(options[center])

    pair_crossing_count = 0
    pair_capacity_count = 0
    cover_count = 0
    covers: list[Rows] = []
    labels = set(int(label) for label in order)

    def search(index: int, assigned: Rows) -> None:
        nonlocal cover_count, pair_capacity_count, pair_crossing_count
        if index == len(FRAGILE_CENTERS):
            pair_crossing_count += 1
            pair_counts = _pair_counts(assigned)
            if max(pair_counts.values(), default=0) > PAIR_CAP:
                return
            pair_capacity_count += 1
            covered = set().union(*(set(row) for row in assigned.values()))
            if covered != labels:
                return
            cover_count += 1
            _, unmatched = essential_row_matching(len(order), assigned)
            if not unmatched:
                covers.append(dict(assigned))
            return

        center = FRAGILE_CENTERS[index]
        for row in options[center]:
            if all(
                _selected_pair_ok(center, row, other, other_row, order)
                for other, other_row in assigned.items()
            ):
                assigned[center] = row
                search(index + 1, assigned)
                del assigned[center]

    search(0, {})
    return {
        "row_option_count_by_center": {
            str(center): len(options[center]) for center in FRAGILE_CENTERS
        },
        "raw_row_combination_count": raw_count,
        "pair_and_crossing_compatible_count": pair_crossing_count,
        "pair_capacity_compatible_count": pair_capacity_count,
        "cover_count": cover_count,
        "essential_cover_count": len(covers),
        "covers": covers,
    }


def _full_extension(
    order: Sequence[int], fixed_rows: Mapping[int, Sequence[int]]
) -> dict[str, Any]:
    """Find the first full selected extension under the n-dependent capacities."""

    n = len(order)
    labels = set(int(label) for label in order)
    indegree_cap = (PAIR_CAP * (n - 1)) // (ROW_SIZE - 1)
    candidates = {
        center: list(combinations(sorted(labels - {center}), ROW_SIZE))
        for center in labels
        if center not in fixed_rows
    }
    assigned: Rows = {
        int(center): tuple(sorted(int(value) for value in row))
        for center, row in fixed_rows.items()
    }
    pair_counts = _pair_counts(assigned)
    indegrees = _selected_indegrees(assigned)
    nodes = 0
    initial_option_counts: dict[str, int] = {}

    def viable(center: int, row: Sequence[int]) -> bool:
        if any(indegrees[value] >= indegree_cap for value in row):
            return False
        if any(
            pair_counts[_pair(left, right)] >= PAIR_CAP
            for left, right in combinations(row, 2)
        ):
            return False
        return all(
            _selected_pair_ok(center, row, other, other_row, order)
            for other, other_row in assigned.items()
        )

    for center in sorted(candidates):
        initial_option_counts[str(center)] = sum(
            viable(center, row) for row in candidates[center]
        )

    def search() -> Rows | None:
        nonlocal nodes
        if len(assigned) == n:
            return dict(assigned)
        best_center: int | None = None
        best_options: list[tuple[int, ...]] | None = None
        for center in sorted(labels - set(assigned)):
            options = [row for row in candidates[center] if viable(center, row)]
            if not options:
                return None
            if best_options is None or len(options) < len(best_options):
                best_center = center
                best_options = options
        assert best_center is not None and best_options is not None
        for row in best_options:
            nodes += 1
            assigned[best_center] = row
            row_pairs = [_pair(left, right) for left, right in combinations(row, 2)]
            for value in row:
                indegrees[value] += 1
            for pair in row_pairs:
                pair_counts[pair] += 1
            result = search()
            if result is not None:
                return result
            for pair in row_pairs:
                pair_counts[pair] -= 1
            for value in row:
                indegrees[value] -= 1
            del assigned[best_center]
        return None

    full_rows = search()
    return {
        "ok": full_rows is not None,
        "search_exhausted": full_rows is None,
        "nodes_visited": nodes,
        "indegree_cap": indegree_cap,
        "initial_option_counts": initial_option_counts,
        "initial_dead_centers": [
            int(center) for center, count in initial_option_counts.items() if count == 0
        ],
        "full_rows": full_rows,
    }


def _good_deletion_summary(rows: Mapping[int, Sequence[int]]) -> dict[str, Any]:
    n = len(rows)
    histogram: Counter[int] = Counter()
    violations: list[list[int]] = []
    for deleted_mask in range(1, (1 << n) - 1):
        eligible = [
            center
            for center, row in rows.items()
            if not ((deleted_mask >> center) & 1)
            and any((deleted_mask >> witness) & 1 for witness in row)
        ]
        histogram[len(eligible)] += 1
        if not eligible:
            violations.append(
                [vertex for vertex in range(n) if (deleted_mask >> vertex) & 1]
            )
    return {
        "nonempty_proper_seed_count": (1 << n) - 2,
        "all_seeds_have_good_survivor": not violations,
        "violating_seeds": violations,
        "eligible_center_count_histogram": {
            str(count): multiplicity
            for count, multiplicity in sorted(histogram.items())
        },
    }


def _natural_rows(order: Sequence[int], rows: Mapping[int, Sequence[int]]) -> Rows:
    position = {int(label): index for index, label in enumerate(order)}
    return {
        position[center]: tuple(sorted(position[int(value)] for value in row))
        for center, row in rows.items()
    }


def _canonical_dihedral_rows(
    rows: Mapping[int, Sequence[int]],
) -> tuple[tuple[int, ...], ...]:
    n = len(rows)
    representatives = []
    for direction in (1, -1):
        for shift in range(n):
            label_map = tuple((direction * label + shift) % n for label in range(n))
            transformed: list[tuple[int, ...] | None] = [None] * n
            for center, row in rows.items():
                transformed[label_map[center]] = tuple(
                    sorted(label_map[value] for value in row)
                )
            assert all(row is not None for row in transformed)
            representatives.append(tuple(row for row in transformed if row is not None))
    return min(representatives)


def _vector_add(
    vector: Counter[Pair], left: Pair, right: Pair, coefficient: int
) -> None:
    vector[left] += coefficient
    vector[right] -= coefficient
    if vector[left] == 0:
        del vector[left]
    if vector[right] == 0:
        del vector[right]


def _inverse_label_map(to_canonical: Sequence[int]) -> tuple[int, ...]:
    inverse = [0] * len(to_canonical)
    for source, target in enumerate(to_canonical):
        inverse[int(target)] = source
    return tuple(inverse)


def _mapped_positive_circuit(
    assignment: Mapping[str, Any],
    certificate: Mapping[str, Any],
) -> dict[str, Any]:
    inverse = _inverse_label_map(assignment["to_canonical_label_map"])
    core_rows = _rows_from_compact(assignment["core_selected_rows"])
    strict_terms = []
    equality_terms = []
    balance: Counter[Pair] = Counter()
    for raw in certificate["strict_terms"]:
        outer = _pair(
            inverse[int(raw["outer_pair"][0])], inverse[int(raw["outer_pair"][1])]
        )
        inner = _pair(
            inverse[int(raw["inner_pair"][0])], inverse[int(raw["inner_pair"][1])]
        )
        coefficient = int(raw["coefficient"])
        mapped_row = inverse[int(raw["row"])]
        witness_order = [inverse[int(value)] for value in raw["witness_order"]]
        if tuple(sorted(witness_order)) != core_rows.get(mapped_row):
            raise AssertionError(
                "mapped strict term is absent from the assignment core"
            )
        _vector_add(balance, outer, inner, coefficient)
        strict_terms.append(
            {
                "coefficient": coefficient,
                "outer_pair": list(outer),
                "inner_pair": list(inner),
                "row": mapped_row,
                "witness_order": witness_order,
            }
        )
    for raw in certificate["equality_terms"]:
        left = _pair(
            inverse[int(raw["left_pair"][0])], inverse[int(raw["left_pair"][1])]
        )
        right = _pair(
            inverse[int(raw["right_pair"][0])], inverse[int(raw["right_pair"][1])]
        )
        coefficient = int(raw["coefficient"])
        supporting_rows = sorted(
            inverse[int(value)] for value in raw["supporting_rows"]
        )
        for center in supporting_rows:
            row_distances = {_pair(center, witness) for witness in core_rows[center]}
            if left not in row_distances or right not in row_distances:
                raise AssertionError(
                    "mapped equality term is absent from the assignment core"
                )
        _vector_add(balance, left, right, coefficient)
        equality_terms.append(
            {
                "coefficient": coefficient,
                "left_pair": list(left),
                "right_pair": list(right),
                "supporting_rows": supporting_rows,
            }
        )
    if balance:
        raise AssertionError(f"mapped dual identity does not cancel: {balance!r}")
    return {
        "skeleton_id": certificate["skeleton_id"],
        "contradiction_type": certificate["contradiction_type"],
        "strict_terms": strict_terms,
        "equality_terms": equality_terms,
        "identity_balance": [],
        "identity_verified_zero": True,
    }


def _assignment_lookup(
    payload: Mapping[str, Any],
) -> dict[tuple[tuple[int, ...], ...], Mapping[str, Any]]:
    if payload.get("schema") != FRONTIER_SCHEMA:
        raise ValueError("unexpected n=9 frontier-classification schema")
    lookup = {}
    for raw in payload["assignments"]:
        rows = _rows_from_compact(raw["selected_rows"])
        key = tuple(rows[center] for center in range(9))
        lookup[key] = raw
    return lookup


def _dual_lookup(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    if payload.get("schema") != DUAL_SCHEMA:
        raise ValueError("unexpected n=9 template-dual schema")
    return {str(raw["family_id"]): raw for raw in payload["certificates"]}


def _source_record(path: str, payload: Mapping[str, Any], role: str) -> dict[str, Any]:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "path": path,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "canonical_json_sha256": sha256(encoded).hexdigest(),
        "role": role,
    }


def _placement_payload(
    gaps: tuple[int, ...],
    assignment_lookup: Mapping[tuple[tuple[int, ...], ...], Mapping[str, Any]],
    dual_lookup: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    order = cyclic_order_for_gaps(gaps)
    enumeration = enumerate_fragile_covers(order)
    covers = enumeration.pop("covers")
    extension_nodes = 0
    extendable = 0
    initial_dead = 0
    witnesses = []
    for cover_index, cover in enumerate(covers):
        extension = _full_extension(order, cover)
        extension_nodes += int(extension["nodes_visited"])
        if extension["initial_dead_centers"]:
            initial_dead += 1
        if not extension["ok"]:
            continue
        extendable += 1
        full_rows = extension["full_rows"]
        assert isinstance(full_rows, dict)
        natural_rows = _natural_rows(order, full_rows)
        key = tuple(natural_rows[center] for center in range(9))
        assignment = assignment_lookup.get(key)
        if assignment is None:
            raise AssertionError(
                "n=9 extension absent from stored frontier assignments"
            )
        family_id = str(assignment["family_id"])
        certificate = dual_lookup.get(family_id)
        if certificate is None:
            raise AssertionError(f"missing dual certificate for {family_id}")
        fragile_check = check_to_json(
            check_fragile_hypergraph(len(order), cover, order=order)
        )
        pair_counts = _pair_counts(full_rows)
        intersections = Counter(
            len(set(full_rows[left]) & set(full_rows[right]))
            for left, right in combinations(sorted(full_rows), 2)
        )
        indegrees = _selected_indegrees(full_rows)
        witnesses.append(
            {
                "gaps_after_core_roles": list(gaps),
                "cover_index": cover_index,
                "cyclic_order": list(order),
                "fragile_rows": _rows_json(cover),
                "fragile_hypergraph_check": fragile_check,
                "selected_rows": _rows_json(full_rows),
                "natural_order_selected_rows": _rows_json(natural_rows),
                "selected_indegrees": {
                    str(label): indegrees[label] for label in range(len(order))
                },
                "witness_pair_multiplicity_histogram": {
                    str(count): multiplicity
                    for count, multiplicity in sorted(
                        Counter(pair_counts.values()).items()
                    )
                },
                "row_intersection_size_histogram": {
                    str(count): multiplicity
                    for count, multiplicity in sorted(intersections.items())
                },
                "maximum_witness_pair_multiplicity": max(pair_counts.values()),
                "good_deletion": _good_deletion_summary(full_rows),
                "n9_frontier_assignment": {
                    key: assignment[key]
                    for key in (
                        "assignment_id",
                        "family_id",
                        "template_id",
                        "status",
                        "core_selected_rows",
                        "to_canonical_label_map",
                    )
                },
                "positive_circuit": _mapped_positive_circuit(assignment, certificate),
            }
        )
    placement = {
        "gaps_after_core_roles": list(gaps),
        "cyclic_order": list(order),
        **enumeration,
        "full_extension": {
            "partial_cover_count": len(covers),
            "extendable_partial_cover_count": extendable,
            "unextendable_partial_cover_count": len(covers) - extendable,
            "initially_dead_partial_cover_count": initial_dead,
            "nodes_visited": extension_nodes,
        },
    }
    return placement, witnesses


def _counter_json(values: Iterable[str]) -> dict[str, int]:
    counts = Counter(values)
    return {key: counts[key] for key in sorted(counts)}


def halo_lift_payload(
    frontier_classification_payload: Mapping[str, Any],
    template_dual_payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Regenerate the complete bounded halo-lift artifact."""

    assignment_lookup = _assignment_lookup(frontier_classification_payload)
    dual_lookup = _dual_lookup(template_dual_payload)

    zero_order = cyclic_order_for_gaps(())
    zero_enumeration = enumerate_fragile_covers(zero_order)
    zero_enumeration.pop("covers")

    one_placements = []
    one_cover_rows: list[Rows] = []
    one_extension_nodes = 0
    one_initially_dead = 0
    for gap in CORE_ORDER:
        order = cyclic_order_for_gaps((gap,))
        enumeration = enumerate_fragile_covers(order)
        covers = enumeration.pop("covers")
        extension_results = [_full_extension(order, cover) for cover in covers]
        one_extension_nodes += sum(
            int(result["nodes_visited"]) for result in extension_results
        )
        one_initially_dead += sum(
            bool(result["initial_dead_centers"]) for result in extension_results
        )
        if any(result["ok"] for result in extension_results):
            raise AssertionError("one-halo cover unexpectedly has a full extension")
        one_cover_rows.extend(covers)
        one_placements.append(
            {
                "gaps_after_core_roles": [gap],
                "cyclic_order": list(order),
                **enumeration,
                "full_extension": {
                    "partial_cover_count": len(covers),
                    "extendable_partial_cover_count": 0,
                    "unextendable_partial_cover_count": len(covers),
                    "initially_dead_partial_cover_count": sum(
                        bool(result["initial_dead_centers"])
                        for result in extension_results
                    ),
                    "nodes_visited": sum(
                        int(result["nodes_visited"]) for result in extension_results
                    ),
                },
            }
        )

    two_placements = []
    witnesses: list[dict[str, Any]] = []
    for gaps in combinations_with_replacement(CORE_ORDER, 2):
        placement, placement_witnesses = _placement_payload(
            gaps,
            assignment_lookup,
            dual_lookup,
        )
        two_placements.append(placement)
        witnesses.extend(placement_witnesses)

    canonical_systems = {
        _canonical_dihedral_rows(
            _rows_from_compact(witness["natural_order_selected_rows"])
        )
        for witness in witnesses
    }
    assignment_ids = [
        str(witness["n9_frontier_assignment"]["assignment_id"]) for witness in witnesses
    ]
    family_ids = [
        str(witness["n9_frontier_assignment"]["family_id"]) for witness in witnesses
    ]
    template_ids = [
        str(witness["n9_frontier_assignment"]["template_id"]) for witness in witnesses
    ]
    statuses = [
        str(witness["n9_frontier_assignment"]["status"]) for witness in witnesses
    ]

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_template": {
            "name": "scalable_k8_four_circuit",
            "formal_roles": [1, 8, 16, 18, 23, 27, 37, 44],
            "retained_strict_row_centers": [8, 18, 23, 44],
            "proper_quotients": [
                {
                    "identified_roles": [18, 23],
                    "four_center_injective": False,
                    "disposition": "rejected_as_four_distinct_fragile_row_lift",
                    "reason": "two retained strict-row centers are identified",
                },
                {
                    "identified_roles": [23, 27],
                    "four_center_injective": True,
                    "disposition": "bounded_halo_lift_scan",
                    "core_role_blocks": CORE_ROLE_BLOCKS,
                    "core_cyclic_order": list(CORE_ORDER),
                    "fragile_centers": list(FRAGILE_CENTERS),
                    "required_witness_pairs": {
                        str(center): sorted(REQUIRED_WITNESSES[center])
                        for center in FRAGILE_CENTERS
                    },
                },
            ],
        },
        "search_contract": {
            "halo_placement_model": (
                "Added halos are otherwise interchangeable and inserted into the seven "
                "cyclic gaps; nondecreasing gap multisets give one canonical placement "
                "per halo-label permutation."
            ),
            "fragile_row_completion": (
                "Each retained center keeps its two certificate witnesses and chooses "
                "two additional witnesses to form a self-excluding four-set."
            ),
            "fragile_cover_filters": [
                "row intersections have size at most two",
                "every two-overlap crosses the center chord in the supplied cyclic order",
                "every witness pair occurs in at most two retained rows",
                "the four retained rows cover every displayed role",
                "the four retained rows admit a matching to distinct covered roles",
            ],
            "full_extension_filters": [
                "one self-excluding four-witness selected row at every center",
                "the same row-intersection and crossing rules",
                "witness-pair multiplicity at most two",
                "selected indegree at most floor(2(n-1)/3)",
            ],
            "search_order": (
                "lexicographic row options with minimum-remaining-options center choice; "
                "one deterministic full-extension witness is retained per extendable cover"
            ),
        },
        "zero_halos": {
            "halo_count": 0,
            "placement_count": 1,
            "cyclic_order": list(zero_order),
            **zero_enumeration,
            "full_extension": {
                "partial_cover_count": 0,
                "extendable_partial_cover_count": 0,
            },
        },
        "one_halo": {
            "halo_count": 1,
            "placement_count": len(one_placements),
            "raw_row_combination_count": sum(
                int(record["raw_row_combination_count"]) for record in one_placements
            ),
            "essential_cover_count": len(one_cover_rows),
            "extendable_partial_cover_count": 0,
            "unextendable_partial_cover_count": len(one_cover_rows),
            "initially_dead_partial_cover_count": one_initially_dead,
            "extension_nodes_visited": one_extension_nodes,
            "placements": one_placements,
        },
        "two_halos": {
            "halo_count": 2,
            "placement_count": len(two_placements),
            "raw_row_combination_count": sum(
                int(record["raw_row_combination_count"]) for record in two_placements
            ),
            "essential_cover_count": sum(
                int(record["essential_cover_count"]) for record in two_placements
            ),
            "extendable_partial_cover_count": len(witnesses),
            "unextendable_partial_cover_count": sum(
                int(record["full_extension"]["unextendable_partial_cover_count"])
                for record in two_placements
            ),
            "extension_nodes_visited": sum(
                int(record["full_extension"]["nodes_visited"])
                for record in two_placements
            ),
            "placements_with_extension_count": sum(
                bool(record["full_extension"]["extendable_partial_cover_count"])
                for record in two_placements
            ),
            "canonical_full_system_count": len(canonical_systems),
            "assignment_ids": assignment_ids,
            "family_id_counts": _counter_json(family_ids),
            "template_id_counts": _counter_json(template_ids),
            "frontier_status_counts": _counter_json(statuses),
            "all_fragile_hypergraph_checks_ok": all(
                witness["fragile_hypergraph_check"]["ok"] for witness in witnesses
            ),
            "all_good_deletion_checks_ok": all(
                witness["good_deletion"]["all_seeds_have_good_survivor"]
                for witness in witnesses
            ),
            "all_positive_circuit_identities_zero": all(
                witness["positive_circuit"]["identity_verified_zero"]
                for witness in witnesses
            ),
            "placements": two_placements,
            "extension_witnesses": witnesses,
        },
        "summary": {
            "center_collision_quotient_count": 1,
            "scanned_seven_role_quotient_count": 1,
            "minimum_added_halos_for_fragile_cover": 1,
            "minimum_added_halos_for_full_selected_extension": 2,
            "one_halo_essential_cover_count": len(one_cover_rows),
            "two_halo_essential_cover_count": sum(
                int(record["essential_cover_count"]) for record in two_placements
            ),
            "two_halo_extendable_partial_cover_count": len(witnesses),
            "two_halo_canonical_full_system_count": len(canonical_systems),
            "n9_frontier_assignment_ids": assignment_ids,
            "all_n9_witnesses_have_exact_positive_circuit": all(
                witness["positive_circuit"]["identity_verified_zero"]
                for witness in witnesses
            ),
        },
        "limitations": [
            "The scan starts from one stored seven-role certificate quotient; it does not prove that a minimal counterexample contains that quotient.",
            "The halo count measures additional formal cyclic roles in this bounded completion model, not all possible geometric halo structures.",
            "The full-extension search imposes only the stated incidence, crossing, pair-capacity, and indegree conditions before the stored n=9 certificate join.",
            "The joined n=9 frontier and template-dual artifacts remain review-pending diagnostics and are not independently rederived here.",
            "No Euclidean realization, n=9 theorem, general proof, or counterexample is claimed.",
        ],
        "conclusion": CONCLUSION,
        "source_artifacts": [
            _source_record(
                "data/certificates/n9_vertex_circle_frontier_motif_classification.json",
                frontier_classification_payload,
                "exact lookup of each full n=9 selected-row witness",
            ),
            _source_record(
                "data/certificates/n9_vertex_circle_template_duals.json",
                template_dual_payload,
                "exact transformed positive circuit for each matched n=9 family",
            ),
        ],
        "provenance": PROVENANCE,
    }
    return payload


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts and certificate invariants."""

    for key, expected in (
        ("schema", SCHEMA),
        ("status", STATUS),
        ("trust", TRUST),
        ("claim_scope", CLAIM_SCOPE),
        ("conclusion", CONCLUSION),
    ):
        if payload.get(key) != expected:
            raise AssertionError(f"unexpected {key}")
    zero = payload["zero_halos"]
    if zero["raw_row_combination_count"] != 1296 or zero["essential_cover_count"] != 0:
        raise AssertionError("unexpected zero-halo frontier")
    one = payload["one_halo"]
    if [
        record["essential_cover_count"] for record in one["placements"]
    ] != EXPECTED_ONE_HALO_COUNTS:
        raise AssertionError("unexpected one-halo placement counts")
    for key, expected in (
        ("raw_row_combination_count", 70_000),
        ("essential_cover_count", 38),
        ("extendable_partial_cover_count", 0),
        ("unextendable_partial_cover_count", 38),
        ("initially_dead_partial_cover_count", 38),
        ("extension_nodes_visited", 0),
    ):
        if one.get(key) != expected:
            raise AssertionError(f"unexpected one_halo.{key}")
    two = payload["two_halos"]
    if [
        record["essential_cover_count"] for record in two["placements"]
    ] != EXPECTED_TWO_HALO_PARTIAL_COUNTS:
        raise AssertionError("unexpected two-halo placement counts")
    if [
        record["full_extension"]["extendable_partial_cover_count"]
        for record in two["placements"]
    ] != EXPECTED_TWO_HALO_EXTENDABLE_COUNTS:
        raise AssertionError("unexpected two-halo extension placement counts")
    for key, expected in (
        ("raw_row_combination_count", 1_417_500),
        ("essential_cover_count", 7_708),
        ("extendable_partial_cover_count", 6),
        ("unextendable_partial_cover_count", 7_702),
        ("extension_nodes_visited", 2_414),
        ("placements_with_extension_count", 6),
        ("canonical_full_system_count", 5),
        ("assignment_ids", EXPECTED_ASSIGNMENT_IDS),
        ("family_id_counts", {"F01": 1, "F04": 1, "F05": 1, "F07": 1, "F11": 2}),
        ("template_id_counts", {"T02": 2, "T03": 1, "T06": 2, "T11": 1}),
        ("frontier_status_counts", {"self_edge": 5, "strict_cycle": 1}),
        ("all_fragile_hypergraph_checks_ok", True),
        ("all_good_deletion_checks_ok", True),
        ("all_positive_circuit_identities_zero", True),
    ):
        if two.get(key) != expected:
            raise AssertionError(f"unexpected two_halos.{key}: {two.get(key)!r}")
    witnesses = two["extension_witnesses"]
    if [
        item["n9_frontier_assignment"]["family_id"] for item in witnesses
    ] != EXPECTED_FAMILY_IDS:
        raise AssertionError("unexpected matched family ids")
    if [
        item["n9_frontier_assignment"]["template_id"] for item in witnesses
    ] != EXPECTED_TEMPLATE_IDS:
        raise AssertionError("unexpected matched template ids")
    if not all(
        item["positive_circuit"]["identity_balance"] == [] for item in witnesses
    ):
        raise AssertionError("nonzero mapped positive-circuit balance")
    summary = payload["summary"]
    for key, expected in (
        ("minimum_added_halos_for_fragile_cover", 1),
        ("minimum_added_halos_for_full_selected_extension", 2),
        ("one_halo_essential_cover_count", 38),
        ("two_halo_essential_cover_count", 7_708),
        ("two_halo_extendable_partial_cover_count", 6),
        ("two_halo_canonical_full_system_count", 5),
        ("n9_frontier_assignment_ids", EXPECTED_ASSIGNMENT_IDS),
        ("all_n9_witnesses_have_exact_positive_circuit", True),
    ):
        if summary.get(key) != expected:
            raise AssertionError(f"unexpected summary.{key}")


def validate_payload(
    payload: Mapping[str, Any],
    frontier_classification_payload: Mapping[str, Any],
    template_dual_payload: Mapping[str, Any],
) -> list[str]:
    """Compare a stored packet with complete deterministic regeneration."""

    errors: list[str] = []
    try:
        assert_expected_payload(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))
        return errors
    generated = halo_lift_payload(
        frontier_classification_payload, template_dual_payload
    )
    if payload != generated:
        errors.append(
            "stored payload differs from complete regenerated halo-lift frontier"
        )
    return errors


__all__ = [
    "CLAIM_SCOPE",
    "CONCLUSION",
    "PROVENANCE",
    "SCHEMA",
    "STATUS",
    "TRUST",
    "assert_expected_payload",
    "cyclic_order_for_gaps",
    "enumerate_fragile_covers",
    "halo_lift_payload",
    "validate_payload",
]
