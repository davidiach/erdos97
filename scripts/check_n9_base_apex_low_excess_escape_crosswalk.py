#!/usr/bin/env python3
"""Independently validate the n=9 low-excess escape crosswalk artifact."""

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
    ROOT
    / "data"
    / "certificates"
    / "n9_base_apex_low_excess_escape_crosswalk.json"
)

N = 9
WITNESS_SIZE = 4
BASE_APEX_SLACK = 9
TOTAL_PROFILE_EXCESS_RANGE = [0, 6]
CAPACITY_DEFICIT_RELATION = "D = 9 - E"
CONTRADICTION_THRESHOLD = 3
STRICT_MINIMAL_RELEVANT_ESCAPE = 3

EXPECTED_SCHEMA = "erdos97.n9_base_apex_low_excess_escape_crosswalk.v1"
EXPECTED_STATUS = "EXPLORATORY_LEDGER_ONLY"
EXPECTED_TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
EXPECTED_CLAIM_SCOPE = (
    "Focused n=9 base-apex low-excess profile/escape crosswalk bookkeeping; "
    "not a proof of n=9, not a counterexample, not a geometric "
    "realizability test, and not a global status update."
)
EXPECTED_INTERPRETATION = [
    "Rows cross low-excess profile ledgers E=0..6 with strict-threshold r=3 escape classes.",
    "Matrix entries count common-dihedral profile/escape pair classes, not geometric realizations.",
    "Profile-excess sequences record labelled vertex excesses only.",
    "Escape classes record length-2/length-3 deficits in the turn-cover diagnostic only.",
    "Unassigned capacity D-r is not placed on side or length-4 bases by this artifact.",
    "No proof of the n=9 case is claimed.",
]
EXPECTED_PROVENANCE = {
    "generator": "scripts/analyze_n9_base_apex_low_excess_escape_crosswalk.py",
    "command": (
        "python scripts/analyze_n9_base_apex_low_excess_escape_crosswalk.py "
        "--assert-expected --out "
        "data/certificates/n9_base_apex_low_excess_escape_crosswalk.json"
    ),
}
EXPECTED_SOURCE_ARTIFACTS = {
    "low_excess_ledgers": "data/certificates/n9_base_apex_low_excess_ledgers.json",
    "escape_budget": "data/certificates/n9_base_apex_escape_budget_report.json",
    "d3_escape_slice": "data/certificates/n9_base_apex_d3_escape_slice.json",
    "low_excess_escape_ladder": (
        "data/certificates/n9_base_apex_low_excess_escape_ladder.json"
    ),
}
EXPECTED_TOP_LEVEL_KEYS = {
    "base_apex_slack",
    "capacity_deficit_relation",
    "claim_scope",
    "contradiction_threshold",
    "crosswalk_matrix",
    "crosswalk_rows",
    "escape_classes",
    "interpretation",
    "matrix_summary",
    "n",
    "profile_ledger_rows",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "strict_minimal_relevant_escape",
    "total_profile_excess_range",
    "trust",
    "witness_size",
}
EXPECTED_ESCAPE_CLASSES = [
    {
        "escape_class_id": "X00",
        "canonical_escape_placement": {
            "spoiled_length2": [0, 2],
            "spoiled_length3": [3],
        },
        "labelled_placement_count": 18,
    },
    {
        "escape_class_id": "X01",
        "canonical_escape_placement": {
            "spoiled_length2": [0, 2],
            "spoiled_length3": [5],
        },
        "labelled_placement_count": 9,
    },
    {
        "escape_class_id": "X02",
        "canonical_escape_placement": {
            "spoiled_length2": [0, 3],
            "spoiled_length3": [1],
        },
        "labelled_placement_count": 9,
    },
    {
        "escape_class_id": "X03",
        "canonical_escape_placement": {
            "spoiled_length2": [0, 4],
            "spoiled_length3": [5],
        },
        "labelled_placement_count": 18,
    },
    {
        "escape_class_id": "X04",
        "canonical_escape_placement": {
            "spoiled_length2": [0, 1, 3],
            "spoiled_length3": [],
        },
        "labelled_placement_count": 18,
    },
    {
        "escape_class_id": "X05",
        "canonical_escape_placement": {
            "spoiled_length2": [0, 1, 5],
            "spoiled_length3": [],
        },
        "labelled_placement_count": 9,
    },
    {
        "escape_class_id": "X06",
        "canonical_escape_placement": {
            "spoiled_length2": [0, 2, 4],
            "spoiled_length3": [],
        },
        "labelled_placement_count": 9,
    },
    {
        "escape_class_id": "X07",
        "canonical_escape_placement": {
            "spoiled_length2": [0, 2, 5],
            "spoiled_length3": [],
        },
        "labelled_placement_count": 18,
    },
]
EXPECTED_MATRIX_SUMMARY = {
    "profile_ledger_count": 30,
    "escape_class_count": 8,
    "matrix_cell_count": 240,
    "nonzero_matrix_cell_count": 240,
    "total_labelled_profile_sequence_count": 5005,
    "labelled_escape_placement_count": 108,
    "total_labelled_profile_escape_pair_count": 540540,
    "total_common_dihedral_pair_class_count": 30184,
    "common_dihedral_pair_orbit_size_counts": {
        "18": 29876,
        "9": 308,
    },
    "profile_ledger_count_by_total_profile_excess": {
        "0": 1,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 5,
        "5": 7,
        "6": 11,
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
    "labelled_profile_escape_pair_count_by_total_profile_excess": {
        "0": 108,
        "1": 972,
        "2": 4860,
        "3": 17820,
        "4": 53460,
        "5": 138996,
        "6": 324324,
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
    "common_dihedral_pair_class_count_by_escape_class": {
        "X00": 5005,
        "X01": 2541,
        "X02": 2541,
        "X03": 5005,
        "X04": 5005,
        "X05": 2541,
        "X06": 2541,
        "X07": 5005,
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
    """Return sorted profile-excess values for one bad vertex."""

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
    """Return the dihedral-canonical escape placement."""

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
    """Return labelled strict-threshold r=3 placements escaping turn cover."""

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


def escape_class_rows() -> tuple[dict[str, Any], dict[EscapePlacement, str], dict[str, list[EscapePlacement]]]:
    """Return escape-class payload rows and member lookup tables."""

    members: defaultdict[EscapePlacement, list[EscapePlacement]] = defaultdict(list)
    for placement in escape_placements():
        members[canonical_escape_placement(placement)].append(placement)

    rows: list[dict[str, Any]] = []
    placement_to_id: dict[EscapePlacement, str] = {}
    id_to_members: dict[str, list[EscapePlacement]] = {}
    for index, placement in enumerate(sorted(members, key=escape_class_sort_key)):
        class_id = f"X{index:02d}"
        class_members = sorted(members[placement])
        placement_to_id[placement] = class_id
        id_to_members[class_id] = class_members
        diagnostic_clauses = turn_clauses_from_saturation(
            sorted(set(range(N)) - set(placement[0])),
            sorted(set(range(N)) - set(placement[1])),
        )
        rows.append(
            {
                "escape_class_id": class_id,
                "canonical_escape_placement": placement_payload(placement),
                "labelled_placement_count": len(class_members),
                "remaining_minimum_forced_turns": minimum_turn_hitting_set_size(
                    diagnostic_clauses
                ),
                "remaining_turn_clause_count": len(diagnostic_clauses),
            }
        )
    return tuple(rows), placement_to_id, id_to_members


def profile_ledger_groups() -> tuple[dict[tuple[int, ...], list[ProfileSequence]], ...]:
    """Return low-excess profile ledgers grouped by sorted excess multiset."""

    groups: list[dict[tuple[int, ...], list[ProfileSequence]]] = []
    for total_profile_excess in range(
        TOTAL_PROFILE_EXCESS_RANGE[0],
        TOTAL_PROFILE_EXCESS_RANGE[1] + 1,
    ):
        by_multiset: defaultdict[tuple[int, ...], list[ProfileSequence]] = defaultdict(list)
        for sequence in profile_sequences(total_profile_excess):
            by_multiset[tuple(sorted(sequence))].append(sequence)
        groups.append(dict(sorted(by_multiset.items())))
    return tuple(groups)


def profile_ledger_rows() -> tuple[dict[str, Any], dict[str, list[ProfileSequence]]]:
    """Return profile-ledger rows and their labelled sequence members."""

    rows: list[dict[str, Any]] = []
    id_to_sequences: dict[str, list[ProfileSequence]] = {}
    for group in profile_ledger_groups():
        for multiset, sequences in group.items():
            class_id = f"P{len(rows):02d}"
            orbit_members: defaultdict[ProfileSequence, list[ProfileSequence]] = defaultdict(list)
            for sequence in sequences:
                orbit_members[canonical_profile_sequence(sequence)].append(sequence)
            total_profile_excess = sum(multiset)
            id_to_sequences[class_id] = list(sequences)
            rows.append(
                {
                    "profile_ledger_id": class_id,
                    "total_profile_excess": total_profile_excess,
                    "capacity_deficit": BASE_APEX_SLACK - total_profile_excess,
                    "excess_multiset": [int(value) for value in multiset],
                    "labelled_profile_sequence_count": len(sequences),
                    "dihedral_profile_orbit_count": len(orbit_members),
                    "dihedral_profile_orbit_size_counts": json_counter(
                        Counter(len(members) for members in orbit_members.values())
                    ),
                }
            )
    return tuple(rows), id_to_sequences


def crosswalk_cell(
    profile_row: dict[str, Any],
    profile_sequences_for_row: Sequence[ProfileSequence],
    escape_row: dict[str, Any],
    escape_members: Sequence[EscapePlacement],
) -> dict[str, Any]:
    """Return one profile-ledger by escape-class matrix cell."""

    class_sizes: Counter[CoupledKey] = Counter()
    for sequence in profile_sequences_for_row:
        for placement in escape_members:
            class_sizes[canonical_coupled_pair(sequence, placement)] += 1

    labelled_profile_count = int(profile_row["labelled_profile_sequence_count"])
    labelled_escape_count = int(escape_row["labelled_placement_count"])
    return {
        "profile_ledger_id": profile_row["profile_ledger_id"],
        "escape_class_id": escape_row["escape_class_id"],
        "total_profile_excess": profile_row["total_profile_excess"],
        "capacity_deficit": profile_row["capacity_deficit"],
        "excess_multiset": profile_row["excess_multiset"],
        "canonical_escape_placement": escape_row["canonical_escape_placement"],
        "labelled_profile_sequence_count": labelled_profile_count,
        "labelled_escape_placement_count": labelled_escape_count,
        "labelled_profile_escape_pair_count": (
            labelled_profile_count * labelled_escape_count
        ),
        "common_dihedral_pair_class_count": len(class_sizes),
        "common_dihedral_pair_orbit_size_counts": json_counter(
            Counter(class_sizes.values())
        ),
    }


def crosswalk_rows(
    profiles: Sequence[dict[str, Any]],
    profile_members: dict[str, list[ProfileSequence]],
    escapes: Sequence[dict[str, Any]],
    escape_members: dict[str, list[EscapePlacement]],
) -> list[dict[str, Any]]:
    """Return flat profile-ledger by escape-class crosswalk rows."""

    rows = []
    for profile_row in profiles:
        profile_id = str(profile_row["profile_ledger_id"])
        for escape_row in escapes:
            escape_id = str(escape_row["escape_class_id"])
            rows.append(
                crosswalk_cell(
                    profile_row,
                    profile_members[profile_id],
                    escape_row,
                    escape_members[escape_id],
                )
            )
    return rows


def crosswalk_matrix(
    profiles: Sequence[dict[str, Any]],
    escapes: Sequence[dict[str, Any]],
    rows: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Return the matrix view of the flat crosswalk rows."""

    by_cell = {
        (row["profile_ledger_id"], row["escape_class_id"]): row
        for row in rows
    }
    escape_ids = [str(row["escape_class_id"]) for row in escapes]
    matrix_rows = []
    for profile in profiles:
        profile_id = str(profile["profile_ledger_id"])
        matrix_rows.append(
            {
                "profile_ledger_id": profile_id,
                "total_profile_excess": profile["total_profile_excess"],
                "capacity_deficit": profile["capacity_deficit"],
                "excess_multiset": profile["excess_multiset"],
                "common_dihedral_pair_class_counts": {
                    escape_id: by_cell[(profile_id, escape_id)][
                        "common_dihedral_pair_class_count"
                    ]
                    for escape_id in escape_ids
                },
            }
        )
    return {
        "escape_class_ids": escape_ids,
        "rows": matrix_rows,
    }


def add_count(counter: Counter[int], value: Any, amount: int = 1) -> None:
    """Increment an integer counter from a JSON value."""

    if not strict_int(value):
        raise TypeError(f"expected integer counter value, got {value!r}")
    counter[int(value)] += amount


def matrix_summary(
    profiles: Sequence[dict[str, Any]],
    escapes: Sequence[dict[str, Any]],
    rows: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Return aggregate crosswalk counts pinned by the checker."""

    profile_count_by_total: Counter[int] = Counter()
    profile_sequence_count_by_total: Counter[int] = Counter()
    labelled_pair_count_by_total: Counter[int] = Counter()
    common_class_count_by_total: Counter[int] = Counter()
    common_class_count_by_escape: Counter[str] = Counter()
    orbit_size_counts: Counter[int] = Counter()

    for profile in profiles:
        total = int(profile["total_profile_excess"])
        profile_count_by_total[total] += 1
        profile_sequence_count_by_total[total] += int(
            profile["labelled_profile_sequence_count"]
        )
    for row in rows:
        total = int(row["total_profile_excess"])
        class_count = int(row["common_dihedral_pair_class_count"])
        labelled_pair_count_by_total[total] += int(
            row["labelled_profile_escape_pair_count"]
        )
        common_class_count_by_total[total] += class_count
        common_class_count_by_escape[str(row["escape_class_id"])] += class_count
        for orbit_size, count in row["common_dihedral_pair_orbit_size_counts"].items():
            orbit_size_counts[int(orbit_size)] += int(count)

    summary = {
        "profile_ledger_count": len(profiles),
        "escape_class_count": len(escapes),
        "matrix_cell_count": len(rows),
        "nonzero_matrix_cell_count": sum(
            1
            for row in rows
            if int(row["common_dihedral_pair_class_count"]) > 0
        ),
        "total_labelled_profile_sequence_count": sum(
            int(row["labelled_profile_sequence_count"]) for row in profiles
        ),
        "labelled_escape_placement_count": sum(
            int(row["labelled_placement_count"]) for row in escapes
        ),
        "total_labelled_profile_escape_pair_count": sum(
            int(row["labelled_profile_escape_pair_count"]) for row in rows
        ),
        "total_common_dihedral_pair_class_count": sum(
            int(row["common_dihedral_pair_class_count"]) for row in rows
        ),
        "common_dihedral_pair_orbit_size_counts": json_counter(orbit_size_counts),
        "profile_ledger_count_by_total_profile_excess": json_counter(
            profile_count_by_total
        ),
        "labelled_profile_sequence_count_by_total_profile_excess": json_counter(
            profile_sequence_count_by_total
        ),
        "labelled_profile_escape_pair_count_by_total_profile_excess": json_counter(
            labelled_pair_count_by_total
        ),
        "common_dihedral_pair_class_count_by_total_profile_excess": json_counter(
            common_class_count_by_total
        ),
        "common_dihedral_pair_class_count_by_escape_class": {
            escape_id: int(common_class_count_by_escape[escape_id])
            for escape_id in sorted(common_class_count_by_escape)
        },
    }
    if summary != EXPECTED_MATRIX_SUMMARY:
        raise AssertionError(
            f"unexpected matrix summary: expected {EXPECTED_MATRIX_SUMMARY!r}, got {summary!r}"
        )
    return summary


@lru_cache(maxsize=1)
def _expected_crosswalk_payload_cached() -> dict[str, Any]:
    """Return the recomputed expected crosswalk payload."""

    escapes, _escape_to_id, escape_members = escape_class_rows()
    profiles, profile_members = profile_ledger_rows()
    rows = crosswalk_rows(profiles, profile_members, escapes, escape_members)
    matrix = crosswalk_matrix(profiles, escapes, rows)
    summary = matrix_summary(profiles, escapes, rows)
    payload = {
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
        "escape_classes": list(escapes),
        "profile_ledger_rows": list(profiles),
        "crosswalk_matrix": matrix,
        "crosswalk_rows": rows,
        "matrix_summary": summary,
        "interpretation": EXPECTED_INTERPRETATION,
        "provenance": EXPECTED_PROVENANCE,
    }
    assert_expected_crosswalk_counts(payload)
    return payload


def expected_crosswalk_payload() -> dict[str, Any]:
    """Return a deep copy of the independently recomputed payload."""

    return copy.deepcopy(_expected_crosswalk_payload_cached())


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


def assert_expected_crosswalk_counts(payload: dict[str, Any]) -> None:
    """Assert stable expected counts for the crosswalk/matrix payload."""

    if payload.get("schema") != EXPECTED_SCHEMA:
        raise AssertionError("unexpected schema")
    if payload.get("status") != EXPECTED_STATUS:
        raise AssertionError("unexpected status")
    if payload.get("trust") != EXPECTED_TRUST:
        raise AssertionError("unexpected trust label")
    if payload.get("n") != N or payload.get("witness_size") != WITNESS_SIZE:
        raise AssertionError("unexpected n or witness_size")
    if payload.get("base_apex_slack") != BASE_APEX_SLACK:
        raise AssertionError("unexpected base-apex slack")

    escape_rows = payload.get("escape_classes")
    if not isinstance(escape_rows, list):
        raise AssertionError("missing escape classes")
    trimmed_escape_rows = [
        {
            "escape_class_id": row["escape_class_id"],
            "canonical_escape_placement": row["canonical_escape_placement"],
            "labelled_placement_count": row["labelled_placement_count"],
        }
        for row in escape_rows
    ]
    if trimmed_escape_rows != EXPECTED_ESCAPE_CLASSES:
        raise AssertionError("unexpected escape classes")

    summary = payload.get("matrix_summary")
    if summary != EXPECTED_MATRIX_SUMMARY:
        raise AssertionError("unexpected matrix summary")


def _list_order_values(
    rows: Any,
    key: str,
) -> tuple[list[Any], bool]:
    if not isinstance(rows, list):
        return [], False
    values: list[Any] = []
    ok = True
    for row in rows:
        if not isinstance(row, dict) or not strict_int(row.get(key)):
            ok = False
        values.append(row.get(key) if isinstance(row, dict) else None)
    return values, ok


def validate_row_ordering(payload: dict[str, Any]) -> list[str]:
    """Return row-ordering and simple arithmetic-shape errors."""

    errors: list[str] = []
    profiles = payload.get("profile_ledger_rows")
    if not isinstance(profiles, list):
        errors.append("profile_ledger_rows must be a list")
    else:
        profile_order = []
        for index, row in enumerate(profiles):
            if not isinstance(row, dict):
                errors.append(f"profile_ledger_rows[{index}] must be an object")
                continue
            profile_id = row.get("profile_ledger_id")
            expected_id = f"P{index:02d}"
            if profile_id != expected_id:
                errors.append(
                    f"profile_ledger_rows[{index}].profile_ledger_id must be {expected_id}"
                )
            total = row.get("total_profile_excess")
            deficit = row.get("capacity_deficit")
            multiset = row.get("excess_multiset")
            if not strict_int(total):
                errors.append(
                    f"profile_ledger_rows[{index}].total_profile_excess must be an int"
                )
                continue
            if not strict_int(deficit):
                errors.append(
                    f"profile_ledger_rows[{index}].capacity_deficit must be an int"
                )
            elif deficit != BASE_APEX_SLACK - total:
                errors.append(f"profile_ledger_rows[{index}] must satisfy D = 9 - E")
            if not isinstance(multiset, list) or not all(strict_int(value) for value in multiset):
                errors.append(
                    f"profile_ledger_rows[{index}].excess_multiset must be a list of ints"
                )
                continue
            profile_order.append((total, tuple(multiset)))
        if profile_order != sorted(profile_order):
            errors.append("profile_ledger_rows must be ordered by total_profile_excess then excess_multiset")

    escapes = payload.get("escape_classes")
    if not isinstance(escapes, list):
        errors.append("escape_classes must be a list")
    else:
        for index, row in enumerate(escapes):
            if not isinstance(row, dict):
                errors.append(f"escape_classes[{index}] must be an object")
                continue
            expected_id = f"X{index:02d}"
            if row.get("escape_class_id") != expected_id:
                errors.append(f"escape_classes[{index}].escape_class_id must be {expected_id}")

    crosswalk = payload.get("crosswalk_rows")
    if not isinstance(crosswalk, list):
        errors.append("crosswalk_rows must be a list")
    else:
        keys = []
        for index, row in enumerate(crosswalk):
            if not isinstance(row, dict):
                errors.append(f"crosswalk_rows[{index}] must be an object")
                continue
            profile_id = row.get("profile_ledger_id")
            escape_id = row.get("escape_class_id")
            if not isinstance(profile_id, str) or not isinstance(escape_id, str):
                errors.append(
                    f"crosswalk_rows[{index}] must have string profile_ledger_id and escape_class_id"
                )
                continue
            keys.append((profile_id, escape_id))
            count = row.get("common_dihedral_pair_class_count")
            if not strict_int(count):
                errors.append(
                    f"crosswalk_rows[{index}].common_dihedral_pair_class_count must be an int"
                )
        if keys != sorted(keys):
            errors.append("crosswalk_rows must be ordered by profile_ledger_id then escape_class_id")

    matrix = payload.get("crosswalk_matrix")
    if not isinstance(matrix, dict):
        errors.append("crosswalk_matrix must be an object")
    else:
        matrix_rows = matrix.get("rows")
        matrix_ids = matrix.get("escape_class_ids")
        escape_count = len(escapes) if isinstance(escapes, list) else 0
        expected_escape_ids = [f"X{index:02d}" for index in range(escape_count)]
        if matrix_ids != expected_escape_ids:
            errors.append("crosswalk_matrix.escape_class_ids are out of order")
        if not isinstance(matrix_rows, list):
            errors.append("crosswalk_matrix.rows must be a list")
        else:
            row_ids = []
            for index, row in enumerate(matrix_rows):
                if not isinstance(row, dict):
                    errors.append(f"crosswalk_matrix.rows[{index}] must be an object")
                    continue
                expected_id = f"P{index:02d}"
                if row.get("profile_ledger_id") != expected_id:
                    errors.append(
                        f"crosswalk_matrix.rows[{index}].profile_ledger_id must be {expected_id}"
                    )
                row_ids.append(row.get("profile_ledger_id"))
                counts = row.get("common_dihedral_pair_class_counts")
                if not isinstance(counts, dict):
                    errors.append(
                        f"crosswalk_matrix.rows[{index}].common_dihedral_pair_class_counts must be an object"
                    )
                elif set(counts) != set(expected_escape_ids):
                    errors.append(
                        f"crosswalk_matrix.rows[{index}] must have one count per escape class"
                    )
                elif not all(strict_int(value) for value in counts.values()):
                    errors.append(
                        f"crosswalk_matrix.rows[{index}].common_dihedral_pair_class_counts must be ints"
                    )
            if row_ids != sorted(row_ids):
                errors.append("crosswalk_matrix.rows must be ordered by profile_ledger_id")
    return errors


def validate_payload(payload: Any) -> list[str]:
    """Return validation errors for a loaded crosswalk/matrix artifact."""

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
    if payload.get("interpretation") != EXPECTED_INTERPRETATION:
        errors.append("interpretation mismatch")
    elif not isinstance(payload.get("interpretation"), list) or not all(
        isinstance(item, str) for item in payload.get("interpretation", [])
    ):
        errors.append("interpretation must be the expected list of strings")

    errors.extend(validate_row_ordering(payload))

    try:
        expected = _expected_crosswalk_payload_cached()
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


def _sum_crosswalk_int(rows: Any, key: str) -> int | None:
    if not isinstance(rows, list):
        return None
    values = [row.get(key) for row in rows if isinstance(row, dict)]
    if len(values) != len(rows) or not all(strict_int(value) for value in values):
        return None
    return sum(int(value) for value in values)


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    profiles = object_payload.get("profile_ledger_rows", [])
    escapes = object_payload.get("escape_classes", [])
    crosswalk = object_payload.get("crosswalk_rows", [])
    summary = object_payload.get("matrix_summary", {})
    return {
        "ok": not errors,
        "artifact": display_path(path),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "n": object_payload.get("n"),
        "witness_size": object_payload.get("witness_size"),
        "profile_ledger_count": len(profiles) if isinstance(profiles, list) else None,
        "escape_class_count": len(escapes) if isinstance(escapes, list) else None,
        "matrix_cell_count": len(crosswalk) if isinstance(crosswalk, list) else None,
        "total_common_dihedral_pair_class_count": _sum_crosswalk_int(
            crosswalk,
            "common_dihedral_pair_class_count",
        ),
        "summary_total_common_dihedral_pair_class_count": (
            summary.get("total_common_dihedral_pair_class_count")
            if isinstance(summary, dict)
            else None
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
        print("n=9 base-apex low-excess escape crosswalk/matrix artifact")
        print(f"artifact: {summary['artifact']}")
        print(
            "matrix: "
            f"profiles={summary['profile_ledger_count']}, "
            f"escapes={summary['escape_class_count']}, "
            f"cells={summary['matrix_cell_count']}"
        )
        print(
            "common-dihedral classes: "
            f"{summary['total_common_dihedral_pair_class_count']}"
        )
        if args.check:
            print("OK: independent low-excess escape-crosswalk checks passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
