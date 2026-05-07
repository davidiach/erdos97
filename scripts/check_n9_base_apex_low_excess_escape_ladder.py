#!/usr/bin/env python3
"""Independently validate the n=9 low-excess minimal escape-slice ladder."""

from __future__ import annotations

import argparse
import copy
import itertools
import json
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_base_apex_low_excess_escape_ladder.json"
)

N = 9
WITNESS_SIZE = 4
BASE_APEX_SLACK = 9
TOTAL_PROFILE_EXCESS_RANGE = [0, 6]
CAPACITY_DEFICIT_RELATION = "D = 9 - E"
CONTRADICTION_THRESHOLD = 3
STRICT_MINIMAL_RELEVANT_ESCAPE = 3

EXPECTED_SCHEMA = "erdos97.n9_base_apex_low_excess_escape_ladder.v1"
EXPECTED_STATUS = "EXPLORATORY_LEDGER_ONLY"
EXPECTED_TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
EXPECTED_CLAIM_SCOPE = (
    "Focused n=9 base-apex low-excess minimal escape-slice ladder "
    "bookkeeping; not a proof of n=9, not a counterexample, not a geometric "
    "realizability test, and not a global status update."
)
EXPECTED_INTERPRETATION = [
    "The ladder covers E=0..6, so D=9-E ranges from 9 down to 3.",
    "Every row uses the strict turn-cover threshold and the minimum relevant escape count r=3.",
    "Unassigned capacity is D-r and is not placed on side or length-4 bases by this report.",
    "The coupled counts quotient profile labels and r=3 escape placements by the same dihedral action.",
    "No individual coupled classes are emitted in this summary-only artifact.",
    "No proof of the n=9 case is claimed.",
]
EXPECTED_PROVENANCE = {
    "generator": "scripts/analyze_n9_base_apex_low_excess_escape_ladder.py",
    "command": (
        "python scripts/analyze_n9_base_apex_low_excess_escape_ladder.py "
        "--assert-expected --out "
        "data/certificates/n9_base_apex_low_excess_escape_ladder.json"
    ),
}
EXPECTED_SOURCE_ARTIFACTS = {
    "low_excess_ledgers": "data/certificates/n9_base_apex_low_excess_ledgers.json",
    "escape_budget": "data/certificates/n9_base_apex_escape_budget_report.json",
    "d3_escape_slice": "data/certificates/n9_base_apex_d3_escape_slice.json",
}
EXPECTED_TOP_LEVEL_KEYS = {
    "base_apex_slack",
    "capacity_deficit_relation",
    "claim_scope",
    "contradiction_threshold",
    "interpretation",
    "ladder_rows",
    "n",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "strict_escape_slice",
    "strict_minimal_relevant_escape",
    "total_profile_excess_range",
    "trust",
    "witness_size",
}
EXPECTED_LADDER_COUNTS = {
    "rung_count": 7,
    "total_unlabeled_profile_ledger_count": 30,
    "total_labelled_profile_sequence_count": 5005,
    "total_dihedral_profile_orbit_count": 318,
        "total_labelled_profile_escape_pair_count": 540540,
        "total_common_dihedral_pair_class_count": 30184,
    "total_common_dihedral_pair_orbit_size_counts": {
        "18": 29876,
        "9": 308,
    },
    "labelled_profile_sequence_count_by_total_profile_excess": {
        "0": 1,
        "1": 9,
        "2": 45,
        "3": 165,
        "4": 495,
        "5": 1287,
        "6": 3003,
    },
    "common_dihedral_pair_class_count_by_total_profile_excess": {
        "0": 8,
        "1": 56,
        "2": 280,
        "3": 1000,
        "4": 3000,
        "5": 7752,
        "6": 18088,
    },
}
MAX_COMPARISON_ERRORS = 25

ProfileSequence = tuple[int, ...]
EscapePlacement = tuple[tuple[int, ...], tuple[int, ...]]
CoupledKey = tuple[ProfileSequence, EscapePlacement]


def strict_int(value: Any) -> bool:
    """Return true only for JSON integers, excluding bool."""

    return type(value) is int


def binom2(value: int) -> int:
    """Return binom(value, 2)."""

    if value < 0:
        raise ValueError(f"value must be nonnegative, got {value}")
    return value * (value - 1) // 2


def integer_partitions(total: int, minimum: int = 1) -> Iterable[tuple[int, ...]]:
    """Yield nondecreasing positive integer partitions of total."""

    if total < 0:
        raise ValueError(f"total must be nonnegative, got {total}")
    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for rest in integer_partitions(total - first, first):
            yield (first, *rest)


@lru_cache(maxsize=None)
def distance_profiles(
    n: int = N,
    witness_size: int = WITNESS_SIZE,
) -> tuple[tuple[int, tuple[int, ...]], ...]:
    """Return independently enumerated profile-excess rows."""

    baseline = binom2(witness_size)
    rows = []
    for ascending_parts in integer_partitions(n - 1):
        parts = tuple(reversed(ascending_parts))
        if max(parts, default=0) < witness_size:
            continue
        excess = sum(binom2(part) for part in parts) - baseline
        rows.append((excess, parts))
    return tuple(sorted(rows, key=lambda row: (row[0], row[1])))


@lru_cache(maxsize=None)
def profile_excess_values(
    n: int = N,
    witness_size: int = WITNESS_SIZE,
) -> tuple[int, ...]:
    """Return sorted profile-excess values for a bad vertex."""

    return tuple(sorted({excess for excess, _parts in distance_profiles(n, witness_size)}))


def transform_profile_sequence(
    sequence: ProfileSequence,
    *,
    rotation: int,
    reflected: bool,
) -> ProfileSequence:
    """Transform a labelled profile sequence by a dihedral relabeling."""

    out: list[int | None] = [None] * N
    for label, value in enumerate(sequence):
        target = (rotation - label) % N if reflected else (label + rotation) % N
        out[target] = value
    if any(value is None for value in out):  # pragma: no cover - defensive
        raise AssertionError("dihedral map did not produce a complete profile")
    return tuple(int(value) for value in out if value is not None)


def transform_base_index(
    index: int,
    cyclic_length: int,
    *,
    rotation: int,
    reflected: bool,
) -> int:
    """Transform a cyclic base index under a dihedral relabeling."""

    if reflected:
        return (rotation - index - cyclic_length) % N
    return (index + rotation) % N


def transform_escape_placement(
    placement: EscapePlacement,
    *,
    rotation: int,
    reflected: bool,
) -> EscapePlacement:
    """Transform a length-2/length-3 escape placement by one dihedral map."""

    spoiled2, spoiled3 = placement
    return (
        tuple(
            sorted(
                transform_base_index(
                    index,
                    2,
                    rotation=rotation,
                    reflected=reflected,
                )
                for index in spoiled2
            )
        ),
        tuple(
            sorted(
                transform_base_index(
                    index,
                    3,
                    rotation=rotation,
                    reflected=reflected,
                )
                for index in spoiled3
            )
        ),
    )


def dihedral_ops() -> tuple[tuple[int, bool], ...]:
    """Return the 18 dihedral operations in stable order."""

    return tuple(
        (rotation, reflected)
        for rotation in range(N)
        for reflected in (False, True)
    )


@lru_cache(maxsize=None)
def profile_transforms(sequence: ProfileSequence) -> tuple[ProfileSequence, ...]:
    """Return all dihedral transforms of a profile sequence."""

    return tuple(
        transform_profile_sequence(
            sequence,
            rotation=rotation,
            reflected=reflected,
        )
        for rotation, reflected in dihedral_ops()
    )


@lru_cache(maxsize=None)
def escape_transforms(placement: EscapePlacement) -> tuple[EscapePlacement, ...]:
    """Return all dihedral transforms of an escape placement."""

    return tuple(
        transform_escape_placement(
            placement,
            rotation=rotation,
            reflected=reflected,
        )
        for rotation, reflected in dihedral_ops()
    )


def canonical_profile_sequence(sequence: ProfileSequence) -> ProfileSequence:
    """Return the dihedral-canonical labelled profile sequence."""

    return min(profile_transforms(sequence))


def canonical_escape_placement(placement: EscapePlacement) -> EscapePlacement:
    """Return a dihedral-canonical escape placement."""

    return min(escape_transforms(placement))


def canonical_coupled_pair(
    profile: ProfileSequence,
    placement: EscapePlacement,
) -> CoupledKey:
    """Return the common-dihedral canonical profile/escape pair."""

    return min(zip(profile_transforms(profile), escape_transforms(placement)))


def turn_clauses_from_saturation(
    saturated_length2: Iterable[int],
    saturated_length3: Iterable[int],
) -> tuple[tuple[int, int], ...]:
    """Return turn-cover clauses forced by length-2 and length-3 saturation."""

    saturated2 = {index % N for index in saturated_length2}
    saturated3 = {index % N for index in saturated_length3}
    clauses = []
    for index in range(N):
        if index in saturated3 and index in saturated2 and (index + 1) % N in saturated2:
            clauses.append(((index + 1) % N, (index + 2) % N))
    return tuple(clauses)


def minimum_turn_hitting_set_size(clauses: Iterable[tuple[int, int]]) -> int:
    """Return the minimum number of turns hitting all two-turn clauses."""

    clause_tuple = tuple(clauses)
    if not clause_tuple:
        return 0
    for size in range(N + 1):
        for selected in itertools.combinations(range(N), size):
            selected_set = set(selected)
            if all(left in selected_set or right in selected_set for left, right in clause_tuple):
                return size
    raise RuntimeError("no hitting set found")


def turn_cover_forces_contradiction(
    spoiled_length2: Iterable[int],
    spoiled_length3: Iterable[int],
    *,
    contradiction_threshold: int = CONTRADICTION_THRESHOLD,
) -> bool:
    """Return whether the remaining clauses force the turn contradiction."""

    all_indices = set(range(N))
    saturated_length2 = tuple(sorted(all_indices - {idx % N for idx in spoiled_length2}))
    saturated_length3 = tuple(sorted(all_indices - {idx % N for idx in spoiled_length3}))
    clauses = turn_clauses_from_saturation(saturated_length2, saturated_length3)
    return minimum_turn_hitting_set_size(clauses) >= contradiction_threshold


@lru_cache(maxsize=None)
def profile_sequences(total_profile_excess: int) -> tuple[ProfileSequence, ...]:
    """Return labelled profile-excess sequences with the requested total."""

    values = [
        value
        for value in profile_excess_values()
        if value <= total_profile_excess
    ]
    out: list[ProfileSequence] = []

    def search(position: int, remaining: int, current: list[int]) -> None:
        if position == N:
            if remaining == 0:
                out.append(tuple(current))
            return
        for value in values:
            if value > remaining:
                break
            current.append(value)
            search(position + 1, remaining - value, current)
            current.pop()

    search(0, total_profile_excess, [])
    return tuple(sorted(out))


@lru_cache(maxsize=None)
def escape_placements(
    relevant_deficit_count: int = STRICT_MINIMAL_RELEVANT_ESCAPE,
    contradiction_threshold: int = CONTRADICTION_THRESHOLD,
) -> tuple[EscapePlacement, ...]:
    """Return labelled strict-threshold minimal placements escaping turn cover."""

    placements: list[EscapePlacement] = []
    for count2 in range(relevant_deficit_count + 1):
        count3 = relevant_deficit_count - count2
        for spoiled2 in itertools.combinations(range(N), count2):
            for spoiled3 in itertools.combinations(range(N), count3):
                if not turn_cover_forces_contradiction(
                    spoiled2,
                    spoiled3,
                    contradiction_threshold=contradiction_threshold,
                ):
                    placements.append((tuple(spoiled2), tuple(spoiled3)))
    return tuple(sorted(placements))


def placement_payload(placement: EscapePlacement) -> dict[str, list[int]]:
    """Return a JSON-shaped escape placement."""

    spoiled2, spoiled3 = placement
    return {
        "spoiled_length2": [int(value) for value in spoiled2],
        "spoiled_length3": [int(value) for value in spoiled3],
    }


def json_counter(counter: Counter[int]) -> dict[str, int]:
    """Return a sorted counter with JSON string keys."""

    return {str(key): int(counter[key]) for key in sorted(counter)}


def escape_class_sort_key(placement: EscapePlacement) -> tuple[int, EscapePlacement]:
    """Return the stable ordering key for escape classes."""

    return (len(placement[0]), placement)


def profile_sequence_summary(
    total_profile_excess: int,
    capacity_deficit: int,
) -> dict[str, Any]:
    """Return labelled and dihedral profile-placement counts."""

    sequences = profile_sequences(total_profile_excess)
    multiset_counts = Counter(tuple(sorted(sequence)) for sequence in sequences)
    orbit_members: defaultdict[ProfileSequence, list[ProfileSequence]] = defaultdict(list)
    for sequence in sequences:
        orbit_members[canonical_profile_sequence(sequence)].append(sequence)
    return {
        "total_profile_excess": total_profile_excess,
        "capacity_deficit": capacity_deficit,
        "unlabeled_profile_ledger_count": len(multiset_counts),
        "labelled_profile_sequence_count": len(sequences),
        "dihedral_profile_orbit_count": len(orbit_members),
        "dihedral_profile_orbit_size_counts": json_counter(
            Counter(len(members) for members in orbit_members.values())
        ),
        "profile_multiset_counts": [
            {
                "excess_multiset": [int(value) for value in multiset],
                "labelled_sequence_count": int(count),
            }
            for multiset, count in sorted(multiset_counts.items())
        ],
    }


def escape_placement_summary() -> dict[str, Any]:
    """Return labelled and dihedral escape-placement counts."""

    placements = escape_placements()
    orbit_members: defaultdict[EscapePlacement, list[EscapePlacement]] = defaultdict(list)
    for placement in placements:
        orbit_members[canonical_escape_placement(placement)].append(placement)
    return {
        "contradiction_threshold": CONTRADICTION_THRESHOLD,
        "strict_minimal_relevant_escape": STRICT_MINIMAL_RELEVANT_ESCAPE,
        "labelled_escape_placement_count": len(placements),
        "dihedral_escape_class_count": len(orbit_members),
        "dihedral_escape_orbit_size_counts": json_counter(
            Counter(len(members) for members in orbit_members.values())
        ),
        "escape_classes": [
            {
                "canonical_escape_placement": placement_payload(placement),
                "labelled_placement_count": len(orbit_members[placement]),
            }
            for placement in sorted(orbit_members, key=escape_class_sort_key)
        ],
    }


def coupled_slice_summary(total_profile_excess: int) -> dict[str, Any]:
    """Return common-dihedral coupled profile/escape summary counts."""

    sequences = profile_sequences(total_profile_excess)
    placements = escape_placements()
    class_sizes: Counter[CoupledKey] = Counter()
    for sequence in sequences:
        for placement in placements:
            class_sizes[canonical_coupled_pair(sequence, placement)] += 1

    by_profile_multiset: Counter[tuple[int, ...]] = Counter()
    by_escape_class: Counter[EscapePlacement] = Counter()
    by_profile_and_escape: Counter[tuple[tuple[int, ...], EscapePlacement]] = Counter()
    for profile, placement in class_sizes:
        profile_multiset = tuple(sorted(profile))
        escape_class = canonical_escape_placement(placement)
        by_profile_multiset[profile_multiset] += 1
        by_escape_class[escape_class] += 1
        by_profile_and_escape[(profile_multiset, escape_class)] += 1

    return {
        "labelled_profile_escape_pair_count": len(sequences) * len(placements),
        "common_dihedral_pair_class_count": len(class_sizes),
        "common_dihedral_pair_orbit_size_counts": json_counter(
            Counter(class_sizes.values())
        ),
        "pair_class_count_by_profile_multiset": [
            {
                "excess_multiset": [int(value) for value in multiset],
                "common_dihedral_pair_class_count": int(count),
            }
            for multiset, count in sorted(by_profile_multiset.items())
        ],
        "pair_class_count_by_escape_class": [
            {
                "canonical_escape_placement": placement_payload(placement),
                "common_dihedral_pair_class_count": int(count),
            }
            for placement, count in sorted(
                by_escape_class.items(),
                key=lambda item: escape_class_sort_key(item[0]),
            )
        ],
        "pair_class_count_by_profile_multiset_and_escape_class": [
            {
                "excess_multiset": [int(value) for value in multiset],
                "canonical_escape_placement": placement_payload(placement),
                "common_dihedral_pair_class_count": int(count),
            }
            for (multiset, placement), count in sorted(
                by_profile_and_escape.items(),
                key=lambda item: (item[0][0], escape_class_sort_key(item[0][1])),
            )
        ],
    }


def strict_escape_slice_summary() -> dict[str, Any]:
    """Return the shared strict minimum escape-slice summary."""

    summary = escape_placement_summary()
    return {
        "contradiction_threshold": CONTRADICTION_THRESHOLD,
        "strict_minimal_relevant_escape": STRICT_MINIMAL_RELEVANT_ESCAPE,
        "total_relevant_placement_count": sum(1 for _ in itertools.combinations(range(18), 3)),
        "labelled_escape_placement_count": summary["labelled_escape_placement_count"],
        "dihedral_escape_class_count": summary["dihedral_escape_class_count"],
        "dihedral_escape_orbit_size_counts": summary["dihedral_escape_orbit_size_counts"],
        "remaining_minimum_forced_turn_count": {"2": summary["labelled_escape_placement_count"]},
    }


def ladder_row(total_profile_excess: int) -> dict[str, Any]:
    """Return one summary-only low-excess minimal escape-slice ladder row."""

    capacity_deficit = BASE_APEX_SLACK - total_profile_excess
    profile = profile_sequence_summary(total_profile_excess, capacity_deficit)
    coupled = coupled_slice_summary(total_profile_excess)
    return {
        "total_profile_excess": total_profile_excess,
        "capacity_deficit": capacity_deficit,
        "strict_minimal_relevant_escape": STRICT_MINIMAL_RELEVANT_ESCAPE,
        "unassigned_capacity_after_minimum_relevant_escape": (
            capacity_deficit - STRICT_MINIMAL_RELEVANT_ESCAPE
        ),
        "unlabeled_profile_ledger_count": profile["unlabeled_profile_ledger_count"],
        "labelled_profile_sequence_count": profile["labelled_profile_sequence_count"],
        "dihedral_profile_orbit_count": profile["dihedral_profile_orbit_count"],
        "dihedral_profile_orbit_size_counts": profile[
            "dihedral_profile_orbit_size_counts"
        ],
        "labelled_profile_escape_pair_count": coupled[
            "labelled_profile_escape_pair_count"
        ],
        "common_dihedral_pair_class_count": coupled[
            "common_dihedral_pair_class_count"
        ],
        "common_dihedral_pair_orbit_size_counts": coupled[
            "common_dihedral_pair_orbit_size_counts"
        ],
    }


def ladder_summary(rungs: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Return aggregate ladder counts pinned by the checker."""

    orbit_size_counts: Counter[int] = Counter()
    for rung in rungs:
        for size, count in rung["common_dihedral_pair_orbit_size_counts"].items():
            orbit_size_counts[int(size)] += int(count)

    summary = {
        "rung_count": len(rungs),
        "total_unlabeled_profile_ledger_count": sum(
            int(rung["unlabeled_profile_ledger_count"])
            for rung in rungs
        ),
        "total_labelled_profile_sequence_count": sum(
            int(rung["labelled_profile_sequence_count"])
            for rung in rungs
        ),
        "total_dihedral_profile_orbit_count": sum(
            int(rung["dihedral_profile_orbit_count"])
            for rung in rungs
        ),
        "total_labelled_profile_escape_pair_count": sum(
            int(rung["labelled_profile_escape_pair_count"])
            for rung in rungs
        ),
        "total_common_dihedral_pair_class_count": sum(
            int(rung["common_dihedral_pair_class_count"])
            for rung in rungs
        ),
        "total_common_dihedral_pair_orbit_size_counts": json_counter(orbit_size_counts),
        "labelled_profile_sequence_count_by_total_profile_excess": {
            str(rung["total_profile_excess"]): int(
                rung["labelled_profile_sequence_count"]
            )
            for rung in rungs
        },
        "common_dihedral_pair_class_count_by_total_profile_excess": {
            str(rung["total_profile_excess"]): int(
                rung["common_dihedral_pair_class_count"]
            )
            for rung in rungs
        },
    }
    if summary != EXPECTED_LADDER_COUNTS:
        raise AssertionError(
            f"unexpected ladder counts: expected {EXPECTED_LADDER_COUNTS!r}, got {summary!r}"
        )
    return summary


@lru_cache(maxsize=1)
def _expected_ladder_payload_cached() -> dict[str, Any]:
    """Return the recomputed expected payload."""

    ladder_rows = [
        ladder_row(total_profile_excess)
        for total_profile_excess in range(
            TOTAL_PROFILE_EXCESS_RANGE[0],
            TOTAL_PROFILE_EXCESS_RANGE[1] + 1,
        )
    ]
    ladder_summary(ladder_rows)
    return {
        "schema": EXPECTED_SCHEMA,
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": EXPECTED_CLAIM_SCOPE,
        "n": N,
        "witness_size": WITNESS_SIZE,
        "base_apex_slack": BASE_APEX_SLACK,
        "total_profile_excess_range": TOTAL_PROFILE_EXCESS_RANGE,
        "capacity_deficit_relation": CAPACITY_DEFICIT_RELATION,
        "contradiction_threshold": CONTRADICTION_THRESHOLD,
        "strict_minimal_relevant_escape": STRICT_MINIMAL_RELEVANT_ESCAPE,
        "source_artifacts": EXPECTED_SOURCE_ARTIFACTS,
        "strict_escape_slice": strict_escape_slice_summary(),
        "ladder_rows": ladder_rows,
        "interpretation": EXPECTED_INTERPRETATION,
        "provenance": EXPECTED_PROVENANCE,
    }


def expected_ladder_payload() -> dict[str, Any]:
    """Return a deep copy of the independently recomputed payload."""

    return copy.deepcopy(_expected_ladder_payload_cached())


def append_comparison_error(errors: list[str], message: str) -> None:
    """Append a comparison error while keeping output compact."""

    if len(errors) < MAX_COMPARISON_ERRORS:
        errors.append(message)


def compare_json(
    errors: list[str],
    label: str,
    actual: Any,
    expected: Any,
) -> None:
    """Compare JSON data with strict integer/bool typing and list ordering."""

    if len(errors) >= MAX_COMPARISON_ERRORS:
        return
    if strict_int(expected):
        if not strict_int(actual):
            append_comparison_error(
                errors,
                f"{label} must be int {expected!r}; got {actual!r} ({type(actual).__name__})",
            )
        elif actual != expected:
            append_comparison_error(
                errors,
                f"{label} mismatch: expected {expected!r}, got {actual!r}",
            )
        return
    if type(expected) is bool:
        if type(actual) is not bool:
            append_comparison_error(
                errors,
                f"{label} must be bool {expected!r}; got {actual!r} ({type(actual).__name__})",
            )
        elif actual != expected:
            append_comparison_error(
                errors,
                f"{label} mismatch: expected {expected!r}, got {actual!r}",
            )
        return
    if expected is None:
        if actual is not None:
            append_comparison_error(
                errors,
                f"{label} mismatch: expected None, got {actual!r}",
            )
        return
    if isinstance(expected, str):
        if not isinstance(actual, str) or actual != expected:
            append_comparison_error(
                errors,
                f"{label} mismatch: expected {expected!r}, got {actual!r}",
            )
        return
    if isinstance(expected, list):
        if not isinstance(actual, list):
            append_comparison_error(errors, f"{label} must be a list")
            return
        if len(actual) != len(expected):
            append_comparison_error(
                errors,
                f"{label} length mismatch: expected {len(expected)}, got {len(actual)}",
            )
            return
        for index, (actual_item, expected_item) in enumerate(zip(actual, expected)):
            compare_json(errors, f"{label}[{index}]", actual_item, expected_item)
        return
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            append_comparison_error(errors, f"{label} must be an object")
            return
        actual_keys = set(actual)
        expected_keys = set(expected)
        if actual_keys != expected_keys:
            append_comparison_error(
                errors,
                f"{label} keys mismatch: expected {sorted(expected_keys)!r}, got {sorted(actual_keys)!r}",
            )
            return
        for key in expected:
            compare_json(errors, f"{label}.{key}", actual[key], expected[key])
        return
    if actual != expected:
        append_comparison_error(
            errors,
            f"{label} mismatch: expected {expected!r}, got {actual!r}",
        )


def parse_escape_placement_payload(row: Any) -> EscapePlacement | None:
    """Return an escape-placement tuple when row shape is valid enough."""

    if not isinstance(row, dict):
        return None
    spoiled2 = row.get("spoiled_length2")
    spoiled3 = row.get("spoiled_length3")
    if not isinstance(spoiled2, list) or not isinstance(spoiled3, list):
        return None
    if not all(strict_int(value) for value in spoiled2 + spoiled3):
        return None
    return (tuple(spoiled2), tuple(spoiled3))


def validate_row_ordering(payload: dict[str, Any]) -> list[str]:
    """Return row-ordering errors for ladder and nested summary rows."""

    errors: list[str] = []
    rungs = payload.get("ladder_rows")
    if not isinstance(rungs, list):
        return ["ladder_rows must be a list ordered by total_profile_excess"]
    rung_keys: list[int] = []
    row_shape_ok = True
    for rung_index, rung in enumerate(rungs):
        if not isinstance(rung, dict):
            errors.append(f"ladder_rows[{rung_index}] must be an object")
            row_shape_ok = False
            continue
        total_profile_excess = rung.get("total_profile_excess")
        if not strict_int(total_profile_excess):
            errors.append(
                f"ladder_rows[{rung_index}].total_profile_excess must be an int"
            )
            row_shape_ok = False
            continue
        rung_keys.append(total_profile_excess)
    if rung_keys != sorted(rung_keys):
        errors.append("ladder_rows must be ordered by total_profile_excess")

    for rung_index, rung in enumerate(rungs):
        if not isinstance(rung, dict):
            continue
        total_profile_excess = rung.get("total_profile_excess")
        if not strict_int(total_profile_excess):
            continue
        expected_deficit = BASE_APEX_SLACK - total_profile_excess
        if rung.get("capacity_deficit") != expected_deficit:
            errors.append(f"ladder_rows[{rung_index}] must satisfy D = 9 - E")
        if (
            rung.get("unassigned_capacity_after_minimum_relevant_escape")
            != expected_deficit - STRICT_MINIMAL_RELEVANT_ESCAPE
        ):
            errors.append(f"ladder_rows[{rung_index}] has wrong unassigned capacity")
    if not row_shape_ok:
        return errors
    return errors


def validate_payload(payload: Any) -> list[str]:
    """Return validation errors for a loaded ladder artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    top_level_keys = set(payload)
    if top_level_keys != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(top_level_keys)!r}"
        )

    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str):
        errors.append("claim_scope must be a string")
    else:
        if claim_scope != EXPECTED_CLAIM_SCOPE:
            errors.append(
                f"claim_scope mismatch: expected {EXPECTED_CLAIM_SCOPE!r}, got {claim_scope!r}"
            )
        lowered = claim_scope.lower()
        for phrase in (
            "not a proof",
            "not a counterexample",
            "not a geometric realizability test",
            "not a global status update",
        ):
            if phrase not in lowered:
                errors.append(f"claim_scope must include {phrase!r}")

    if payload.get("provenance") != EXPECTED_PROVENANCE:
        errors.append("provenance mismatch")

    interpretation = payload.get("interpretation")
    if interpretation != EXPECTED_INTERPRETATION:
        errors.append("interpretation mismatch")
    elif not isinstance(interpretation, list) or not all(
        isinstance(item, str) for item in interpretation
    ):
        errors.append("interpretation must be the expected list of strings")

    errors.extend(validate_row_ordering(payload))

    try:
        expected = _expected_ladder_payload_cached()
    except AssertionError as exc:
        errors.append(f"independent recomputation failed: {exc}")
        return errors

    compare_errors: list[str] = []
    compare_json(compare_errors, "payload", payload, expected)
    errors.extend(compare_errors)
    if len(compare_errors) >= MAX_COMPARISON_ERRORS:
        errors.append("additional payload mismatches omitted")
    return errors


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def display_path(path: Path) -> str:
    """Return a stable repo-relative path when possible."""

    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    rows = object_payload.get("ladder_rows", [])
    escape = object_payload.get("strict_escape_slice", {})
    row_list = rows if isinstance(rows, list) else []
    object_rows = [row for row in row_list if isinstance(row, dict)]

    def int_sum(key: str) -> int | None:
        values = [row.get(key) for row in object_rows]
        if not all(strict_int(value) for value in values):
            return None
        return sum(int(value) for value in values)

    return {
        "ok": not errors,
        "artifact": display_path(path),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "n": object_payload.get("n"),
        "witness_size": object_payload.get("witness_size"),
        "rung_count": len(row_list),
        "total_unlabeled_profile_ledger_count": int_sum(
            "unlabeled_profile_ledger_count"
        ),
        "labelled_escape_placement_count": (
            escape.get("labelled_escape_placement_count")
            if isinstance(escape, dict)
            else None
        ),
        "total_common_dihedral_pair_class_count": int_sum(
            "common_dihedral_pair_class_count"
        ),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="fail if validation fails")
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 base-apex low-excess minimal escape-slice ladder artifact")
        print(f"artifact: {summary['artifact']}")
        print(f"rungs: {summary['rung_count']}")
        print(
            "profile/escape counts: "
            f"ledgers={summary['total_unlabeled_profile_ledger_count']}, "
            f"escape placements={summary['labelled_escape_placement_count']}, "
            f"coupled classes={summary['total_common_dihedral_pair_class_count']}"
        )
        if args.check:
            print("OK: independent low-excess escape-ladder checks passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
