"""Exact slot-budget closure for large lifts of the fragile-cycle core.

The fixed 23=27 quotient core retains four selected rows.  Each row already
contains a required witness pair, leaving exactly two free witnesses.  This
module turns that eight-slot budget into a finite halo cap and exhausts the
only two previously unchecked active-cover sizes, four and five halos.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations, combinations_with_replacement
import json
from typing import Any, Mapping, Sequence

from erdos97.fragile_cycle_halo_lift_frontier import (
    CORE_ORDER,
    FRAGILE_CENTERS,
    PAIR_CAP,
    REQUIRED_WITNESSES,
    ROW_SIZE,
    _pair,
    _selected_pair_ok,
    cyclic_order_for_gaps,
)
from erdos97.fragile_hypergraph import essential_row_matching


SCHEMA = "erdos97.fragile_cycle_halo_slot_budget.v1"
STATUS = "EXACT_BOUNDED_HALO_SLOT_BUDGET"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact incidence-level slot-budget lemma and coverage-first census for "
    "four- and five-halo lifts of the fixed 23=27 seven-role quotient core. "
    "It proves that the four retained rows cannot actively cover more than "
    "five halos and that every four/five-halo cover has at least three "
    "retained-private halo roles. It does not force the quotient core, make "
    "retained-private roles private in full rich classes, prove Euclidean "
    "realizability, n=11, n=12, the general problem, or a counterexample."
)
CONCLUSION = (
    "The eight free witness slots cap every active 23=27 retained-row lift at "
    "five halos. Four-halo covers force at least three retained-private halos; "
    "five-halo covers force all five halos to be retained-private. The exact "
    "census records a large motif-free escape population, so the honest next "
    "bridge target is to convert this private-halo alternative into genuine "
    "rich-class or deletion geometry, not to claim fixed-core closure."
)
PROVENANCE = {
    "generator": "scripts/check_fragile_cycle_halo_slot_budget.py",
    "command": (
        "python scripts/check_fragile_cycle_halo_slot_budget.py "
        "--write --assert-expected --summary-json"
    ),
}

REQUIRED_COVERED_ROLES = frozenset().union(*REQUIRED_WITNESSES.values())
MISSING_CORE_ROLES = frozenset(CORE_ORDER) - REQUIRED_COVERED_ROLES
FREE_SLOTS_PER_ROW = ROW_SIZE - 2
FREE_SLOT_COUNT = len(FRAGILE_CENTERS) * FREE_SLOTS_PER_ROW
MAX_ACTIVE_HALO_COUNT = FREE_SLOT_COUNT - len(MISSING_CORE_ROLES)

EXPECTED_CENSUS = {
    4: {
        "placement_count": 210,
        "aggregate_counts": {
            "crossing_rejects": 353_010,
            "essential_covers": 529_200,
            "motif_free_covers": 518_760,
            "search_states": 2_087_580,
            "splice_only_covers": 10_440,
        },
        "retained_private_halo_histogram": {"3": 239_400, "4": 289_800},
        "spare_kind_histogram": {
            "duplicated_halo": 239_400,
            "duplicated_missing_core": 117_180,
            "required_anchor_reuse": 172_620,
        },
        "placement_trace_sha256": (
            "5ee7c02529164134b32ec5a26c91c791f2d9dcf6bc6f2e3ff2b4b7766fe37b11"
        ),
    },
    5: {
        "placement_count": 462,
        "aggregate_counts": {
            "essential_covers": 512_820,
            "motif_free_covers": 512_820,
            "search_states": 1_299_144,
        },
        "retained_private_halo_histogram": {"5": 512_820},
        "spare_kind_histogram": {"none": 512_820},
        "placement_trace_sha256": (
            "cfb7fab0f26323081d77810065eadf0ed364dcee9589dfe73b2083063623c7f2"
        ),
    },
}

Rows = dict[int, tuple[int, ...]]
Pair = tuple[int, int]


def _rows_json(rows: Mapping[int, Sequence[int]]) -> list[list[int]]:
    return [
        [center, *sorted(int(value) for value in rows[center])]
        for center in sorted(rows)
    ]


def _is_dihedral_role_order(
    roles: Sequence[int],
    position: Mapping[int, int],
    size: int,
) -> bool:
    start = position[int(roles[0])]
    forward = tuple(
        (position[int(value)] - start) % size for value in roles[1:]
    )
    backward = tuple(
        (start - position[int(value)]) % size for value in roles[1:]
    )
    return all(left < right for left, right in zip(forward, forward[1:])) or all(
        left < right for left, right in zip(backward, backward[1:])
    )


def has_equilateral_hinge(
    rows: Mapping[int, Sequence[int]],
    cyclic_order: Sequence[int],
) -> bool:
    """Return whether the generic equilateral-hinge footprint occurs."""

    order = tuple(int(label) for label in cyclic_order)
    position = {label: index for index, label in enumerate(order)}
    row_sets = {
        int(center): frozenset(int(value) for value in row)
        for center, row in rows.items()
    }
    for a, row_a in row_sets.items():
        for b, row_b in row_sets.items():
            if a == b or b not in row_a or a not in row_b:
                continue
            for c in row_a & (row_b - {a, b}):
                for d, row_d in row_sets.items():
                    roles = (a, b, c, d)
                    if len(set(roles)) != 4 or a not in row_d or b not in row_d:
                        continue
                    if _is_dihedral_role_order(roles, position, len(order)):
                        return True
    return False


def has_kalmanson_splice(
    rows: Mapping[int, Sequence[int]],
    cyclic_order: Sequence[int],
) -> bool:
    """Return whether either generic Kalmanson-splice footprint occurs."""

    order = tuple(int(label) for label in cyclic_order)
    position = {label: index for index, label in enumerate(order)}
    row_sets = {
        int(center): frozenset(int(value) for value in row)
        for center, row in rows.items()
    }
    centers = tuple(row_sets)

    for a in centers:
        for b in centers:
            for d in centers:
                if (
                    len({a, b, d}) != 3
                    or b not in row_sets[a]
                    or b not in row_sets[d]
                ):
                    continue
                for c in row_sets[a] & row_sets[b]:
                    for e in row_sets[b] & row_sets[d]:
                        roles = (a, b, c, d, e)
                        if len(set(roles)) == 5 and _is_dihedral_role_order(
                            roles, position, len(order)
                        ):
                            return True

    for b in centers:
        for c in centers:
            for d in centers:
                if len({b, c, d}) != 3:
                    continue
                for a in row_sets[b] & row_sets[c]:
                    for e in row_sets[b] & row_sets[d]:
                        for f in row_sets[c] & row_sets[d]:
                            roles = (a, b, c, d, e, f)
                            if len(set(roles)) == 6 and _is_dihedral_role_order(
                                roles, position, len(order)
                            ):
                                return True
    return False


def minimum_retained_private_halos(halo_count: int) -> int:
    """Return the slot-budget lower bound for retained-private halo roles."""

    if halo_count < 0:
        raise ValueError("halo count must be nonnegative")
    if halo_count > MAX_ACTIVE_HALO_COUNT:
        raise ValueError("an active retained-row cover cannot have this many halos")
    spare_slots = FREE_SLOT_COUNT - len(MISSING_CORE_ROLES) - halo_count
    return max(0, halo_count - spare_slots)


def _spare_kind(spare: int | None) -> str:
    if spare is None:
        return "none"
    if spare >= len(CORE_ORDER):
        return "duplicated_halo"
    if spare in MISSING_CORE_ROLES:
        return "duplicated_missing_core"
    return "required_anchor_reuse"


def _coverage_multisets(
    labels: frozenset[int],
    halo_count: int,
) -> tuple[tuple[int | None, Counter[int]], ...]:
    missing = labels - REQUIRED_COVERED_ROLES
    spare_count = FREE_SLOT_COUNT - len(missing)
    if spare_count < 0:
        return ()
    if spare_count == 0:
        return ((None, Counter(missing)),)
    if spare_count != 1:
        raise ValueError("coverage-first census is defined for four/five halos")
    results = []
    for spare in sorted(labels):
        multiset = Counter(missing)
        multiset[spare] += 1
        results.append((spare, multiset))
    return tuple(results)


def census_placement(
    gaps: Sequence[int],
) -> dict[str, Any]:
    """Exhaust one four/five-halo placement using the exact coverage budget."""

    normalized_gaps = tuple(int(gap) for gap in gaps)
    halo_count = len(normalized_gaps)
    if halo_count not in (4, 5):
        raise ValueError("slot-budget census supports exactly four or five halos")
    order = cyclic_order_for_gaps(normalized_gaps)
    labels = frozenset(order)
    halo_labels = frozenset(labels - set(CORE_ORDER))
    counts: Counter[str] = Counter()
    private_histogram: Counter[int] = Counter()
    spare_histogram: Counter[str] = Counter()
    representatives: dict[str, dict[str, Any]] = {}
    assigned: Rows = {}
    pair_counts: Counter[Pair] = Counter()

    def record(spare: int | None) -> None:
        _, unmatched = essential_row_matching(len(order), assigned)
        if unmatched:
            counts["matching_rejects"] += 1
            return
        counts["essential_covers"] += 1
        halo_indegrees = Counter(
            witness
            for row in assigned.values()
            for witness in row
            if witness in halo_labels
        )
        private_count = sum(halo_indegrees[label] == 1 for label in halo_labels)
        private_histogram[private_count] += 1
        spare_histogram[_spare_kind(spare)] += 1
        hinge = has_equilateral_hinge(assigned, order)
        splice = has_kalmanson_splice(assigned, order)
        classification = (
            "both"
            if hinge and splice
            else "hinge_only"
            if hinge
            else "splice_only"
            if splice
            else "motif_free"
        )
        counts[f"{classification}_covers"] += 1
        representatives.setdefault(
            classification,
            {
                "halo_gaps": list(normalized_gaps),
                "cyclic_order": list(order),
                "retained_rows": _rows_json(assigned),
                "retained_private_halo_count": private_count,
                "spare_kind": _spare_kind(spare),
            },
        )

    def search(
        index: int,
        remaining: Counter[int],
        spare: int | None,
    ) -> None:
        counts["search_states"] += 1
        if index == len(FRAGILE_CENTERS):
            if any(remaining.values()):
                raise AssertionError("coverage multiset was not exhausted")
            record(spare)
            return

        center = FRAGILE_CENTERS[index]
        available = sorted(
            label
            for label, multiplicity in remaining.items()
            if multiplicity
            and label != center
            and label not in REQUIRED_WITNESSES[center]
        )
        for left, right in combinations(available, 2):
            row = tuple(sorted((*REQUIRED_WITNESSES[center], left, right)))
            if not all(
                _selected_pair_ok(center, row, other, other_row, order)
                for other, other_row in assigned.items()
            ):
                counts["crossing_rejects"] += 1
                continue
            pairs = [_pair(a, b) for a, b in combinations(row, 2)]
            if any(pair_counts[pair] >= PAIR_CAP for pair in pairs):
                counts["pair_capacity_rejects"] += 1
                continue
            remaining[left] -= 1
            remaining[right] -= 1
            assigned[center] = row
            for pair in pairs:
                pair_counts[pair] += 1
            search(index + 1, remaining, spare)
            for pair in pairs:
                pair_counts[pair] -= 1
            del assigned[center]
            remaining[left] += 1
            remaining[right] += 1

    for spare, multiset in _coverage_multisets(labels, halo_count):
        search(0, multiset, spare)

    return {
        "halo_gaps": list(normalized_gaps),
        "cyclic_order": list(order),
        "counts": dict(sorted(counts.items())),
        "retained_private_halo_histogram": {
            str(key): value for key, value in sorted(private_histogram.items())
        },
        "spare_kind_histogram": dict(sorted(spare_histogram.items())),
        "classification_representatives": representatives,
    }


def _aggregate_halo_count(halo_count: int) -> dict[str, Any]:
    placements = []
    aggregate_counts: Counter[str] = Counter()
    private_histogram: Counter[str] = Counter()
    spare_histogram: Counter[str] = Counter()
    trace = sha256()
    representatives: dict[str, dict[str, Any]] = {}
    for gaps in combinations_with_replacement(CORE_ORDER, halo_count):
        placement = census_placement(gaps)
        placements.append(placement)
        aggregate_counts.update(placement["counts"])
        private_histogram.update(placement["retained_private_halo_histogram"])
        spare_histogram.update(placement["spare_kind_histogram"])
        representatives.update(
            {
                key: value
                for key, value in placement[
                    "classification_representatives"
                ].items()
                if key not in representatives
            }
        )
        trace.update(
            json.dumps(
                {
                    "gaps": placement["halo_gaps"],
                    "counts": placement["counts"],
                    "private": placement["retained_private_halo_histogram"],
                    "spare": placement["spare_kind_histogram"],
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
        )
    return {
        "halo_count": halo_count,
        "placement_count": len(placements),
        "minimum_retained_private_halos": minimum_retained_private_halos(
            halo_count
        ),
        "aggregate_counts": dict(sorted(aggregate_counts.items())),
        "retained_private_halo_histogram": dict(sorted(private_histogram.items())),
        "spare_kind_histogram": dict(sorted(spare_histogram.items())),
        "classification_representatives": representatives,
        "placement_trace_sha256": trace.hexdigest(),
    }


def halo_slot_budget_payload() -> dict[str, Any]:
    """Build the complete deterministic slot-budget packet."""

    four_halos = _aggregate_halo_count(4)
    five_halos = _aggregate_halo_count(5)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "slot_budget_lemma": {
            "core_role_count": len(CORE_ORDER),
            "required_covered_roles": sorted(REQUIRED_COVERED_ROLES),
            "missing_core_roles": sorted(MISSING_CORE_ROLES),
            "retained_row_count": len(FRAGILE_CENTERS),
            "free_slots_per_retained_row": FREE_SLOTS_PER_ROW,
            "total_free_slots": FREE_SLOT_COUNT,
            "maximum_active_halo_count": MAX_ACTIVE_HALO_COUNT,
            "proof_identity": "3 + halo_count <= 8",
            "four_halo_minimum_retained_private_halos": (
                minimum_retained_private_halos(4)
            ),
            "five_halo_minimum_retained_private_halos": (
                minimum_retained_private_halos(5)
            ),
        },
        "four_halos": four_halos,
        "five_halos": five_halos,
        "limitations": [
            "The fixed 23=27 quotient core and its four retained rows are assumed.",
            "Retained-private means occurrence in exactly one retained row only.",
            "Other selected rows or full rich classes may contain the same halo role.",
            "The four/five-halo census does not search full selected-row extensions.",
            "No Euclidean, n=11, n=12, general, or counterexample claim is made.",
        ],
        "conclusion": CONCLUSION,
        "provenance": PROVENANCE,
    }




def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert the exact slot lemma, census totals, and claim boundary."""

    for key, expected in (
        ("schema", SCHEMA),
        ("status", STATUS),
        ("trust", TRUST),
        ("claim_scope", CLAIM_SCOPE),
        ("conclusion", CONCLUSION),
        ("provenance", PROVENANCE),
    ):
        if payload.get(key) != expected:
            raise AssertionError(f"{key}: expected {expected!r}")

    lemma = payload.get("slot_budget_lemma")
    expected_lemma = {
        "core_role_count": 7,
        "required_covered_roles": [0, 2, 4, 5],
        "missing_core_roles": [1, 3, 6],
        "retained_row_count": 4,
        "free_slots_per_retained_row": 2,
        "total_free_slots": 8,
        "maximum_active_halo_count": 5,
        "proof_identity": "3 + halo_count <= 8",
        "four_halo_minimum_retained_private_halos": 3,
        "five_halo_minimum_retained_private_halos": 5,
    }
    if lemma != expected_lemma:
        raise AssertionError("slot-budget lemma changed")

    for halo_count, expected in EXPECTED_CENSUS.items():
        section = payload.get(f"{halo_count_word(halo_count)}_halos")
        if not isinstance(section, Mapping):
            raise AssertionError(f"missing {halo_count}-halo census")
        if section.get("halo_count") != halo_count:
            raise AssertionError(f"unexpected {halo_count}-halo label")
        if section.get("minimum_retained_private_halos") != (
            minimum_retained_private_halos(halo_count)
        ):
            raise AssertionError(f"unexpected {halo_count}-halo private bound")
        for key, value in expected.items():
            if section.get(key) != value:
                raise AssertionError(f"{halo_count}-halo {key} changed")


def halo_count_word(halo_count: int) -> str:
    """Return the stable payload key prefix for a checked halo count."""

    words = {4: "four", 5: "five"}
    try:
        return words[halo_count]
    except KeyError as error:
        raise ValueError("only four/five halo census keys exist") from error
__all__ = [
    "CLAIM_SCOPE",
    "CONCLUSION",
    "FREE_SLOT_COUNT",
    "MAX_ACTIVE_HALO_COUNT",
    "PROVENANCE",
    "SCHEMA",
    "STATUS",
    "TRUST",
    "census_placement",
    "assert_expected_payload",
    "halo_slot_budget_payload",
    "has_equilateral_hinge",
    "has_kalmanson_splice",
    "minimum_retained_private_halos",
]
