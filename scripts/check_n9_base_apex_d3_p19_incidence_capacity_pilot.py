#!/usr/bin/env python3
"""Validate the n=9 D=3 P19 incidence-capacity pilot ledger."""

from __future__ import annotations

import argparse
import copy
import itertools
import json
import math
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
    / "n9_base_apex_d3_p19_incidence_capacity_pilot.json"
)

N = 9
WITNESS_SIZE = 4
TOTAL_PROFILE_EXCESS = 6
CAPACITY_DEFICIT = 3
RELEVANT_DEFICIT_COUNT = 3
CONTRADICTION_THRESHOLD = 3
PROFILE_LEDGER_ID = "P19"
PROFILE_MULTISET = [0, 0, 0, 0, 0, 0, 0, 0, 6]
SOURCE_REPRESENTATIVE_IDS = [f"R{index:03d}" for index in range(8)]

EXPECTED_SCHEMA = "erdos97.n9_base_apex_d3_p19_incidence_capacity_pilot.v1"
EXPECTED_STATUS = "EXPLORATORY_LEDGER_ONLY"
EXPECTED_TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
EXPECTED_CLAIM_SCOPE = (
    "Focused n=9 base-apex D=3 P19 incidence-capacity pilot ledger for rows "
    "R000..R007; not a proof of n=9, not a counterexample, not an "
    "incidence-completeness result, not a geometric realizability test, and "
    "not a global status update."
)
EXPECTED_INTERPRETATION_WARNING = (
    "Bookkeeping-only warning: these rows do not decide feasibility, "
    "realizability, or incidence completeness."
)
EXPECTED_INTERPRETATION = [
    "The pilot is restricted to D=3 packet rows R000..R007, profile ledger P19, and escape classes X00..X07.",
    "Profile option counts are labelled partitions of the eight non-center vertices by the displayed distance-profile shapes.",
    "Target capacity totals subtract only the displayed length-2 and length-3 deficient base chords from the cyclic base-apex capacities.",
    "Realizability and incidence-completeness states are UNKNOWN and bookkeeping-only.",
    "No proof of the n=9 case is claimed.",
]
EXPECTED_SOURCE_ARTIFACTS = {
    "d3_escape_frontier_packet": (
        "data/certificates/n9_base_apex_d3_escape_frontier_packet.json"
    ),
    "low_excess_escape_crosswalk": (
        "data/certificates/n9_base_apex_low_excess_escape_crosswalk.json"
    ),
}
EXPECTED_PROVENANCE = {
    "generator": "scripts/analyze_n9_base_apex_d3_p19_incidence_capacity_pilot.py",
    "command": (
        "python scripts/analyze_n9_base_apex_d3_p19_incidence_capacity_pilot.py "
        "--assert-expected --out "
        "data/certificates/n9_base_apex_d3_p19_incidence_capacity_pilot.json"
    ),
}
EXPECTED_PROFILE_OPTION_COUNTS = {
    "0": {
        "distance_profile": [4, 1, 1, 1, 1],
        "labelled_option_count": 70,
    },
    "6": {
        "distance_profile": [4, 4],
        "labelled_option_count": 35,
    },
}
EXPECTED_COMMON_DIHEDRAL_COUNTS = [9, 5, 5, 9, 9, 5, 5, 9]
EXPECTED_TOP_LEVEL_KEYS = {
    "capacity_deficit",
    "claim_scope",
    "common_dihedral_pair_class_count",
    "escape_class_count",
    "full_capacity_totals_by_cyclic_length",
    "incidence_state",
    "interpretation",
    "interpretation_warning",
    "labelled_profile_sequence_count",
    "n",
    "profile_ledger_id",
    "profile_multiset",
    "profile_option_counts",
    "provenance",
    "realizability_state",
    "relevant_deficit_count",
    "representative_count",
    "rows",
    "schema",
    "source_artifacts",
    "source_representative_ids",
    "state_scope",
    "status",
    "target_capacity_total",
    "total_profile_excess",
    "trust",
    "witness_size",
}
EXPECTED_ROW_KEYS = {
    "canonical_escape_placement",
    "common_dihedral_pair_class_count",
    "deficient_base_chords",
    "escape_class_id",
    "excess_multiset",
    "incidence_state",
    "interpretation_warning",
    "labelled_escape_placement_count",
    "labelled_profile_sequence_count",
    "profile_ledger_id",
    "profile_option_counts",
    "realizability_state",
    "representative_id",
    "representative_profile_sequence",
    "state_scope",
    "target_capacity_totals_by_cyclic_length",
}
EXPECTED_CHORD_KEYS = {"base_index", "chord", "cyclic_length"}
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
def profiles_by_excess() -> dict[int, list[tuple[int, ...]]]:
    """Return independently enumerated n=9 distance profiles by excess."""

    baseline = binom2(WITNESS_SIZE)
    grouped: defaultdict[int, list[tuple[int, ...]]] = defaultdict(list)
    for ascending_parts in integer_partitions(N - 1):
        parts = tuple(reversed(ascending_parts))
        if max(parts, default=0) < WITNESS_SIZE:
            continue
        excess = sum(binom2(part) for part in parts) - baseline
        grouped[excess].append(parts)
    return {key: sorted(value) for key, value in grouped.items()}


@lru_cache(maxsize=None)
def profile_excess_values() -> tuple[int, ...]:
    """Return sorted profile-excess values for one bad n=9 vertex."""

    return tuple(sorted(profiles_by_excess()))


@lru_cache(maxsize=1)
def profile_sequences() -> tuple[ProfileSequence, ...]:
    """Return labelled profile-excess sequences with total E=6."""

    values = [
        value
        for value in profile_excess_values()
        if value <= TOTAL_PROFILE_EXCESS
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

    search(0, TOTAL_PROFILE_EXCESS, [])
    return tuple(sorted(out))


@lru_cache(maxsize=1)
def p19_profile_sequences() -> tuple[ProfileSequence, ...]:
    """Return the labelled P19 sequences only."""

    target = tuple(PROFILE_MULTISET)
    return tuple(sequence for sequence in profile_sequences() if tuple(sorted(sequence)) == target)


def labelled_profile_option_count(profile: Sequence[int]) -> int:
    """Return labelled partitions of eight other vertices into profile blocks."""

    remaining_vertices = N - 1
    if sum(profile) != remaining_vertices:
        raise ValueError(f"profile must sum to {remaining_vertices}: {profile!r}")
    denominator = 1
    multiplicities: Counter[int] = Counter()
    for part in profile:
        denominator *= math.factorial(part)
        multiplicities[int(part)] += 1
    for multiplicity in multiplicities.values():
        denominator *= math.factorial(multiplicity)
    return math.factorial(remaining_vertices) // denominator


def profile_option_counts() -> dict[str, dict[str, Any]]:
    """Return independently recomputed P19 profile option counts."""

    out: dict[str, dict[str, Any]] = {}
    grouped = profiles_by_excess()
    for excess in (0, 6):
        profiles = grouped[excess]
        if len(profiles) != 1:
            raise AssertionError(f"expected one profile for excess {excess}")
        profile = [int(value) for value in profiles[0]]
        out[str(excess)] = {
            "distance_profile": profile,
            "labelled_option_count": labelled_profile_option_count(profile),
        }
    if out != EXPECTED_PROFILE_OPTION_COUNTS:
        raise AssertionError("unexpected profile option counts")
    return out


def transform_profile_sequence(
    sequence: ProfileSequence,
    *,
    rotation: int,
    reflected: bool,
) -> ProfileSequence:
    """Transform a labelled profile sequence by one dihedral relabeling."""

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
    """Transform a cyclic base index under one dihedral relabeling."""

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
    """Return turn-cover clauses forced by saturated length-2/3 bases."""

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
) -> bool:
    """Return whether the remaining saturated bases force the turn closure."""

    all_indices = set(range(N))
    saturated_length2 = tuple(sorted(all_indices - {idx % N for idx in spoiled_length2}))
    saturated_length3 = tuple(sorted(all_indices - {idx % N for idx in spoiled_length3}))
    clauses = turn_clauses_from_saturation(saturated_length2, saturated_length3)
    return minimum_turn_hitting_set_size(clauses) >= CONTRADICTION_THRESHOLD


@lru_cache(maxsize=1)
def escape_placements() -> tuple[EscapePlacement, ...]:
    """Return labelled strict-threshold r=3 placements escaping turn cover."""

    placements: list[EscapePlacement] = []
    for count2 in range(RELEVANT_DEFICIT_COUNT + 1):
        count3 = RELEVANT_DEFICIT_COUNT - count2
        for spoiled2 in itertools.combinations(range(N), count2):
            for spoiled3 in itertools.combinations(range(N), count3):
                if not turn_cover_forces_contradiction(spoiled2, spoiled3):
                    placements.append((tuple(spoiled2), tuple(spoiled3)))
    return tuple(sorted(placements))


def placement_payload(placement: EscapePlacement) -> dict[str, list[int]]:
    """Return a JSON-shaped escape placement."""

    spoiled2, spoiled3 = placement
    return {
        "spoiled_length2": [int(value) for value in spoiled2],
        "spoiled_length3": [int(value) for value in spoiled3],
    }


def escape_sort_key(placement: EscapePlacement) -> tuple[int, EscapePlacement]:
    """Return stable ordering for escape classes."""

    return (len(placement[0]), placement)


@lru_cache(maxsize=1)
def escape_class_rows() -> tuple[dict[str, Any], ...]:
    """Return canonical escape-class rows and labelled member counts."""

    members: defaultdict[EscapePlacement, list[EscapePlacement]] = defaultdict(list)
    for placement in escape_placements():
        members[canonical_escape_placement(placement)].append(placement)

    rows: list[dict[str, Any]] = []
    for index, placement in enumerate(sorted(members, key=escape_sort_key)):
        rows.append(
            {
                "escape_class_id": f"X{index:02d}",
                "canonical_escape_placement": placement_payload(placement),
                "labelled_escape_placement_count": len(members[placement]),
            }
        )
    return tuple(rows)


def parse_escape(row: dict[str, Any]) -> EscapePlacement:
    """Return an escape placement tuple from an escape class row."""

    placement = row["canonical_escape_placement"]
    return (
        tuple(placement["spoiled_length2"]),
        tuple(placement["spoiled_length3"]),
    )


def full_capacity_totals_by_cyclic_length() -> dict[str, int]:
    """Return full cyclic base-apex capacities for a nonagon."""

    return {"1": 9, "2": 18, "3": 18, "4": 18}


def target_capacity_totals(placement: EscapePlacement) -> dict[str, int]:
    """Return capacity targets after the displayed deficits."""

    totals = full_capacity_totals_by_cyclic_length()
    totals["2"] -= len(placement[0])
    totals["3"] -= len(placement[1])
    return totals


def deficient_base_chords(placement: EscapePlacement) -> list[dict[str, Any]]:
    """Return the deficient length-2 and length-3 base chords."""

    rows: list[dict[str, Any]] = []
    for cyclic_length, spoiled in ((2, placement[0]), (3, placement[1])):
        for base_index in spoiled:
            rows.append(
                {
                    "cyclic_length": cyclic_length,
                    "base_index": int(base_index),
                    "chord": [
                        int(base_index),
                        int((base_index + cyclic_length) % N),
                    ],
                }
            )
    return rows


@lru_cache(maxsize=1)
def expected_rows() -> tuple[dict[str, Any], ...]:
    """Return independently recomputed expected P19 pilot rows."""

    sequences = p19_profile_sequences()
    placements = escape_placements()
    class_sizes: Counter[CoupledKey] = Counter()
    for sequence in sequences:
        for placement in placements:
            class_sizes[canonical_coupled_pair(sequence, placement)] += 1

    by_escape: Counter[EscapePlacement] = Counter()
    for _profile, placement in class_sizes:
        by_escape[canonical_escape_placement(placement)] += 1

    options = profile_option_counts()
    rows = []
    for index, escape_row in enumerate(escape_class_rows()):
        placement = parse_escape(escape_row)
        rows.append(
            {
                "representative_id": f"R{index:03d}",
                "profile_ledger_id": PROFILE_LEDGER_ID,
                "representative_profile_sequence": PROFILE_MULTISET,
                "excess_multiset": PROFILE_MULTISET,
                "escape_class_id": escape_row["escape_class_id"],
                "canonical_escape_placement": escape_row[
                    "canonical_escape_placement"
                ],
                "common_dihedral_pair_class_count": int(by_escape[placement]),
                "target_capacity_totals_by_cyclic_length": target_capacity_totals(
                    placement
                ),
                "deficient_base_chords": deficient_base_chords(placement),
                "labelled_profile_sequence_count": len(sequences),
                "labelled_escape_placement_count": int(
                    escape_row["labelled_escape_placement_count"]
                ),
                "profile_option_counts": options,
                "realizability_state": "UNKNOWN",
                "incidence_state": "UNKNOWN",
                "state_scope": "bookkeeping-only",
                "interpretation_warning": EXPECTED_INTERPRETATION_WARNING,
            }
        )
    counts = [row["common_dihedral_pair_class_count"] for row in rows]
    if counts != EXPECTED_COMMON_DIHEDRAL_COUNTS:
        raise AssertionError(f"unexpected common-dihedral counts: {counts!r}")
    return tuple(rows)


@lru_cache(maxsize=1)
def _expected_pilot_payload_cached() -> dict[str, Any]:
    """Return the independently recomputed expected pilot payload."""

    rows = [dict(row) for row in expected_rows()]
    payload = {
        "schema": EXPECTED_SCHEMA,
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": EXPECTED_CLAIM_SCOPE,
        "n": N,
        "witness_size": WITNESS_SIZE,
        "profile_ledger_id": PROFILE_LEDGER_ID,
        "profile_multiset": PROFILE_MULTISET,
        "source_representative_ids": SOURCE_REPRESENTATIVE_IDS,
        "escape_class_count": len(rows),
        "representative_count": len(rows),
        "total_profile_excess": TOTAL_PROFILE_EXCESS,
        "capacity_deficit": CAPACITY_DEFICIT,
        "relevant_deficit_count": RELEVANT_DEFICIT_COUNT,
        "full_capacity_totals_by_cyclic_length": (
            full_capacity_totals_by_cyclic_length()
        ),
        "target_capacity_total": 60,
        "labelled_profile_sequence_count": len(p19_profile_sequences()),
        "profile_option_counts": profile_option_counts(),
        "common_dihedral_pair_class_count": sum(
            row["common_dihedral_pair_class_count"] for row in rows
        ),
        "realizability_state": "UNKNOWN",
        "incidence_state": "UNKNOWN",
        "state_scope": "bookkeeping-only",
        "rows": rows,
        "interpretation_warning": EXPECTED_INTERPRETATION_WARNING,
        "interpretation": EXPECTED_INTERPRETATION,
        "source_artifacts": EXPECTED_SOURCE_ARTIFACTS,
        "provenance": EXPECTED_PROVENANCE,
    }
    assert_expected_pilot_counts(payload)
    return payload


def expected_pilot_payload() -> dict[str, Any]:
    """Return a deep copy of the independently recomputed pilot payload."""

    return copy.deepcopy(_expected_pilot_payload_cached())


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


def parse_int_list(value: Any, label: str, errors: list[str]) -> list[int] | None:
    """Return a strict integer list or append a field error."""

    if not isinstance(value, list):
        errors.append(f"{label} must be a list of ints")
        return None
    if not all(strict_int(item) for item in value):
        errors.append(f"{label} must be a list of ints")
        return None
    return [int(item) for item in value]


def parse_escape_placement_payload(
    value: Any,
    label: str,
    errors: list[str],
) -> EscapePlacement | None:
    """Return an escape-placement tuple when a row field is well shaped."""

    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return None
    if set(value) != {"spoiled_length2", "spoiled_length3"}:
        errors.append(f"{label} keys mismatch")
        return None
    spoiled2 = parse_int_list(
        value.get("spoiled_length2"),
        f"{label}.spoiled_length2",
        errors,
    )
    spoiled3 = parse_int_list(
        value.get("spoiled_length3"),
        f"{label}.spoiled_length3",
        errors,
    )
    if spoiled2 is None or spoiled3 is None:
        return None
    if spoiled2 != sorted(spoiled2) or len(set(spoiled2)) != len(spoiled2):
        errors.append(f"{label}.spoiled_length2 must be sorted unique ints")
    if spoiled3 != sorted(spoiled3) or len(set(spoiled3)) != len(spoiled3):
        errors.append(f"{label}.spoiled_length3 must be sorted unique ints")
    if any(value < 0 or value >= N for value in [*spoiled2, *spoiled3]):
        errors.append(f"{label} indices must be in range 0..{N - 1}")
    if len(spoiled2) + len(spoiled3) != RELEVANT_DEFICIT_COUNT:
        errors.append(
            f"{label} must contain {RELEVANT_DEFICIT_COUNT} relevant deficits"
        )
    return (tuple(spoiled2), tuple(spoiled3))


def parse_length_totals(
    value: Any,
    label: str,
    errors: list[str],
) -> dict[str, int] | None:
    """Return strict cyclic-length totals or append field errors."""

    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return None
    if set(value) != {"1", "2", "3", "4"}:
        errors.append(f"{label} keys mismatch")
        return None
    if not all(strict_int(item) for item in value.values()):
        errors.append(f"{label} values must be ints")
        return None
    return {str(key): int(value[key]) for key in ("1", "2", "3", "4")}


def validate_profile_option_counts(
    value: Any,
    label: str,
    errors: list[str],
) -> None:
    """Validate profile option count structure."""

    if value != EXPECTED_PROFILE_OPTION_COUNTS:
        errors.append(f"{label} mismatch")
        compare_json(errors, label, value, EXPECTED_PROFILE_OPTION_COUNTS)


def validate_deficient_base_chords(
    value: Any,
    placement: EscapePlacement | None,
    label: str,
    errors: list[str],
) -> None:
    """Validate deficient base chord rows."""

    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return
    for index, chord_row in enumerate(value):
        row_label = f"{label}[{index}]"
        if not isinstance(chord_row, dict):
            errors.append(f"{row_label} must be an object")
            continue
        if set(chord_row) != EXPECTED_CHORD_KEYS:
            errors.append(f"{row_label} keys mismatch")
        for key in ("cyclic_length", "base_index"):
            if not strict_int(chord_row.get(key)):
                errors.append(f"{row_label}.{key} must be an int")
        chord = parse_int_list(chord_row.get("chord"), f"{row_label}.chord", errors)
        if chord is not None and len(chord) != 2:
            errors.append(f"{row_label}.chord must have length 2")
    if placement is not None and value != deficient_base_chords(placement):
        errors.append(f"{label} does not match canonical_escape_placement")


def validate_rows(payload: dict[str, Any]) -> list[str]:
    """Return row shape, ordering, and derived-count errors."""

    errors: list[str] = []
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return ["rows must be a list"]

    row_ids: list[str] = []
    escape_ids: list[str] = []
    row_counts: list[int] = []
    for index, row in enumerate(rows):
        label = f"rows[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        if set(row) != EXPECTED_ROW_KEYS:
            errors.append(f"{label} keys mismatch")

        expected_id = f"R{index:03d}"
        representative_id = row.get("representative_id")
        if representative_id != expected_id:
            errors.append(f"{label}.representative_id must be {expected_id}")
        if isinstance(representative_id, str):
            row_ids.append(representative_id)

        expected_escape_id = f"X{index:02d}"
        escape_id = row.get("escape_class_id")
        if escape_id != expected_escape_id:
            errors.append(f"{label}.escape_class_id must be {expected_escape_id}")
        if isinstance(escape_id, str):
            escape_ids.append(escape_id)

        for key, expected in (
            ("profile_ledger_id", PROFILE_LEDGER_ID),
            ("representative_profile_sequence", PROFILE_MULTISET),
            ("excess_multiset", PROFILE_MULTISET),
            ("labelled_profile_sequence_count", 9),
            ("realizability_state", "UNKNOWN"),
            ("incidence_state", "UNKNOWN"),
            ("state_scope", "bookkeeping-only"),
            ("interpretation_warning", EXPECTED_INTERPRETATION_WARNING),
        ):
            if row.get(key) != expected:
                errors.append(f"{label}.{key} mismatch")

        for key in (
            "common_dihedral_pair_class_count",
            "labelled_escape_placement_count",
            "labelled_profile_sequence_count",
        ):
            if not strict_int(row.get(key)):
                errors.append(f"{label}.{key} must be an int")

        if strict_int(row.get("common_dihedral_pair_class_count")):
            row_counts.append(int(row["common_dihedral_pair_class_count"]))

        placement = parse_escape_placement_payload(
            row.get("canonical_escape_placement"),
            f"{label}.canonical_escape_placement",
            errors,
        )
        if placement is not None and canonical_escape_placement(placement) != placement:
            errors.append(f"{label}.canonical_escape_placement is not canonical")

        totals = parse_length_totals(
            row.get("target_capacity_totals_by_cyclic_length"),
            f"{label}.target_capacity_totals_by_cyclic_length",
            errors,
        )
        if placement is not None and totals is not None:
            expected_totals = target_capacity_totals(placement)
            if totals != expected_totals:
                errors.append(
                    f"{label}.target_capacity_totals_by_cyclic_length does not match deficits"
                )
            if sum(totals.values()) != 60:
                errors.append(
                    f"{label}.target_capacity_totals_by_cyclic_length must sum to 60"
                )

        validate_deficient_base_chords(
            row.get("deficient_base_chords"),
            placement,
            f"{label}.deficient_base_chords",
            errors,
        )
        validate_profile_option_counts(
            row.get("profile_option_counts"),
            f"{label}.profile_option_counts",
            errors,
        )

    if row_ids != SOURCE_REPRESENTATIVE_IDS:
        errors.append("rows must be ordered R000..R007")
    if escape_ids != [f"X{index:02d}" for index in range(8)]:
        errors.append("rows must be ordered X00..X07")
    if row_counts == EXPECTED_COMMON_DIHEDRAL_COUNTS:
        return errors
    errors.append(
        f"row common-dihedral counts mismatch: expected {EXPECTED_COMMON_DIHEDRAL_COUNTS!r}, got {row_counts!r}"
    )
    return errors


def assert_expected_pilot_counts(payload: dict[str, Any]) -> None:
    """Assert stable expected counts for the P19 pilot ledger."""

    expected = {
        "schema": EXPECTED_SCHEMA,
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": EXPECTED_CLAIM_SCOPE,
        "n": N,
        "witness_size": WITNESS_SIZE,
        "profile_ledger_id": PROFILE_LEDGER_ID,
        "profile_multiset": PROFILE_MULTISET,
        "source_representative_ids": SOURCE_REPRESENTATIVE_IDS,
        "escape_class_count": 8,
        "representative_count": 8,
        "total_profile_excess": TOTAL_PROFILE_EXCESS,
        "capacity_deficit": CAPACITY_DEFICIT,
        "relevant_deficit_count": RELEVANT_DEFICIT_COUNT,
        "full_capacity_totals_by_cyclic_length": {"1": 9, "2": 18, "3": 18, "4": 18},
        "target_capacity_total": 60,
        "labelled_profile_sequence_count": 9,
        "profile_option_counts": EXPECTED_PROFILE_OPTION_COUNTS,
        "common_dihedral_pair_class_count": 56,
        "realizability_state": "UNKNOWN",
        "incidence_state": "UNKNOWN",
        "state_scope": "bookkeeping-only",
        "interpretation_warning": EXPECTED_INTERPRETATION_WARNING,
        "interpretation": EXPECTED_INTERPRETATION,
        "source_artifacts": EXPECTED_SOURCE_ARTIFACTS,
        "provenance": EXPECTED_PROVENANCE,
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            raise AssertionError(f"unexpected {key}")

    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise AssertionError("rows must be a list")
    if len(rows) != 8:
        raise AssertionError("unexpected row count")
    if [row.get("representative_id") for row in rows] != SOURCE_REPRESENTATIVE_IDS:
        raise AssertionError("unexpected representative ids")
    if [
        row.get("common_dihedral_pair_class_count") for row in rows
    ] != EXPECTED_COMMON_DIHEDRAL_COUNTS:
        raise AssertionError("unexpected row common-dihedral counts")


def resolve_source_artifact_path(
    payload: dict[str, Any],
    source_key: str,
    errors: list[str],
) -> Path | None:
    """Return the repo-local path declared for a source artifact."""

    source_artifacts = payload.get("source_artifacts")
    if not isinstance(source_artifacts, dict):
        errors.append("source_artifacts must be an object")
        return None
    source_path = source_artifacts.get(source_key)
    if not isinstance(source_path, str):
        errors.append(f"source_artifacts.{source_key} must be a string")
        return None
    if source_path != EXPECTED_SOURCE_ARTIFACTS[source_key]:
        return None
    return ROOT / source_path


def load_source_artifact(path: Path, label: str, errors: list[str]) -> Any | None:
    """Load a declared source artifact, reporting checker-friendly errors."""

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{label} source artifact is missing: {path.as_posix()}")
    except json.JSONDecodeError as exc:
        errors.append(f"{label} source artifact is not valid JSON: {exc}")
    return None


def validate_d3_packet_source(payload: dict[str, Any], errors: list[str]) -> None:
    """Validate P19 rows against the checked-in D=3 packet artifact."""

    path = resolve_source_artifact_path(
        payload,
        "d3_escape_frontier_packet",
        errors,
    )
    if path is None:
        return
    source = load_source_artifact(path, "d3_escape_frontier_packet", errors)
    if not isinstance(source, dict):
        errors.append("d3_escape_frontier_packet source must be an object")
        return
    representatives = source.get("representatives")
    if not isinstance(representatives, list):
        errors.append("d3_escape_frontier_packet.representatives must be a list")
        return
    source_rows = representatives[: len(SOURCE_REPRESENTATIVE_IDS)]
    source_row_ids = [
        row.get("representative_id")
        for row in source_rows
        if isinstance(row, dict)
    ]
    if source_row_ids != SOURCE_REPRESENTATIVE_IDS:
        errors.append(
            "d3_escape_frontier_packet source rows are not ordered R000..R007"
        )
        return

    rows = payload.get("rows")
    if not isinstance(rows, list):
        return
    for index, (row, source_row) in enumerate(zip(rows, source_rows, strict=True)):
        if not isinstance(row, dict) or not isinstance(source_row, dict):
            errors.append(f"d3_escape_frontier_packet source row {index} malformed")
            continue
        for key in (
            "representative_id",
            "representative_profile_sequence",
            "excess_multiset",
            "escape_class_id",
            "canonical_escape_placement",
            "common_dihedral_pair_class_count",
            "labelled_profile_sequence_count",
            "labelled_escape_placement_count",
        ):
            if row.get(key) != source_row.get(key):
                errors.append(
                    "rows[{index}] does not match d3_escape_frontier_packet "
                    "source field {key}".format(index=index, key=key)
                )


def validate_crosswalk_source(payload: dict[str, Any], errors: list[str]) -> None:
    """Validate P19 rows against the checked-in low-excess crosswalk artifact."""

    path = resolve_source_artifact_path(
        payload,
        "low_excess_escape_crosswalk",
        errors,
    )
    if path is None:
        return
    source = load_source_artifact(path, "low_excess_escape_crosswalk", errors)
    if not isinstance(source, dict):
        errors.append("low_excess_escape_crosswalk source must be an object")
        return

    crosswalk_rows = source.get("crosswalk_rows")
    if not isinstance(crosswalk_rows, list):
        errors.append("low_excess_escape_crosswalk.crosswalk_rows must be a list")
        return
    p19_by_escape = {
        row.get("escape_class_id"): row
        for row in crosswalk_rows
        if isinstance(row, dict) and row.get("profile_ledger_id") == PROFILE_LEDGER_ID
    }
    p19_escape_ids = sorted(
        escape_id for escape_id in p19_by_escape if isinstance(escape_id, str)
    )
    if p19_escape_ids != [f"X{index:02d}" for index in range(8)]:
        errors.append("low_excess_escape_crosswalk source is missing P19/X00..X07")
        return

    matrix = source.get("crosswalk_matrix")
    matrix_rows = matrix.get("rows") if isinstance(matrix, dict) else None
    matrix_p19 = None
    if isinstance(matrix_rows, list):
        for row in matrix_rows:
            if (
                isinstance(row, dict)
                and row.get("profile_ledger_id") == PROFILE_LEDGER_ID
            ):
                matrix_p19 = row
                break
    if not isinstance(matrix_p19, dict):
        errors.append("low_excess_escape_crosswalk source is missing P19 matrix row")
    else:
        counts = matrix_p19.get("common_dihedral_pair_class_counts")
        expected_counts = {
            f"X{index:02d}": EXPECTED_COMMON_DIHEDRAL_COUNTS[index]
            for index in range(8)
        }
        if counts != expected_counts:
            errors.append("low_excess_escape_crosswalk P19 matrix counts mismatch")

    rows = payload.get("rows")
    if not isinstance(rows, list):
        return
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        source_row = p19_by_escape.get(row.get("escape_class_id"))
        if not isinstance(source_row, dict):
            continue
        for key in (
            "profile_ledger_id",
            "excess_multiset",
            "escape_class_id",
            "canonical_escape_placement",
            "common_dihedral_pair_class_count",
            "labelled_profile_sequence_count",
            "labelled_escape_placement_count",
        ):
            if row.get(key) != source_row.get(key):
                errors.append(
                    "rows[{index}] does not match low_excess_escape_crosswalk "
                    "source field {key}".format(index=index, key=key)
                )
        expected_pair_count = (
            row.get("labelled_profile_sequence_count"),
            row.get("labelled_escape_placement_count"),
        )
        if all(strict_int(value) for value in expected_pair_count):
            pair_count = int(expected_pair_count[0]) * int(expected_pair_count[1])
            if source_row.get("labelled_profile_escape_pair_count") != pair_count:
                errors.append(
                    "low_excess_escape_crosswalk P19/X row labelled pair count "
                    f"mismatch for rows[{index}]"
                )


def validate_source_artifacts(payload: dict[str, Any], errors: list[str]) -> None:
    """Validate that declared source artifacts still project to the pilot rows."""

    validate_d3_packet_source(payload, errors)
    validate_crosswalk_source(payload, errors)


def validate_payload(payload: Any) -> list[str]:
    """Return validation errors for a loaded P19 pilot artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    if set(payload) != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(payload)!r}"
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
            "not an incidence-completeness result",
            "not a geometric realizability test",
            "not a global status update",
        ):
            if phrase not in lowered:
                errors.append(f"claim_scope must include {phrase!r}")

    if payload.get("interpretation_warning") != EXPECTED_INTERPRETATION_WARNING:
        errors.append("interpretation_warning mismatch")
    if payload.get("interpretation") != EXPECTED_INTERPRETATION:
        errors.append("interpretation mismatch")
    if payload.get("provenance") != EXPECTED_PROVENANCE:
        errors.append("provenance mismatch")
    if payload.get("source_artifacts") != EXPECTED_SOURCE_ARTIFACTS:
        errors.append("source_artifacts mismatch")
    else:
        validate_source_artifacts(payload, errors)

    for key, expected in {
        "schema": EXPECTED_SCHEMA,
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "n": N,
        "witness_size": WITNESS_SIZE,
        "profile_ledger_id": PROFILE_LEDGER_ID,
        "profile_multiset": PROFILE_MULTISET,
        "source_representative_ids": SOURCE_REPRESENTATIVE_IDS,
        "escape_class_count": 8,
        "representative_count": 8,
        "total_profile_excess": TOTAL_PROFILE_EXCESS,
        "capacity_deficit": CAPACITY_DEFICIT,
        "relevant_deficit_count": RELEVANT_DEFICIT_COUNT,
        "full_capacity_totals_by_cyclic_length": {"1": 9, "2": 18, "3": 18, "4": 18},
        "target_capacity_total": 60,
        "labelled_profile_sequence_count": 9,
        "profile_option_counts": EXPECTED_PROFILE_OPTION_COUNTS,
        "common_dihedral_pair_class_count": 56,
        "realizability_state": "UNKNOWN",
        "incidence_state": "UNKNOWN",
        "state_scope": "bookkeeping-only",
    }.items():
        compare_json(errors, key, payload.get(key), expected)

    validate_profile_option_counts(
        payload.get("profile_option_counts"),
        "profile_option_counts",
        errors,
    )
    errors.extend(validate_rows(payload))

    try:
        expected_payload = _expected_pilot_payload_cached()
    except AssertionError as exc:
        errors.append(f"independent recomputation failed: {exc}")
        return errors

    compare_errors: list[str] = []
    compare_json(compare_errors, "payload", payload, expected_payload)
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


def _sum_row_int(rows: Any, key: str) -> int | None:
    if not isinstance(rows, list):
        return None
    values = [row.get(key) for row in rows if isinstance(row, dict)]
    if len(values) != len(rows) or not all(strict_int(value) for value in values):
        return None
    return sum(int(value) for value in values)


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    rows = object_payload.get("rows", [])
    return {
        "ok": not errors,
        "artifact": display_path(path),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "profile_ledger_id": object_payload.get("profile_ledger_id"),
        "profile_multiset": object_payload.get("profile_multiset"),
        "representative_count": len(rows) if isinstance(rows, list) else None,
        "source_representative_ids": object_payload.get("source_representative_ids"),
        "common_dihedral_pair_class_count": _sum_row_int(
            rows,
            "common_dihedral_pair_class_count",
        ),
        "summary_common_dihedral_pair_class_count": object_payload.get(
            "common_dihedral_pair_class_count"
        ),
        "realizability_state": object_payload.get("realizability_state"),
        "incidence_state": object_payload.get("incidence_state"),
        "state_scope": object_payload.get("state_scope"),
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
        print("n=9 D=3 P19 incidence-capacity pilot artifact")
        print(f"artifact: {summary['artifact']}")
        print(
            "rows: "
            f"profile={summary['profile_ledger_id']}, "
            f"representatives={summary['representative_count']}"
        )
        print(
            "common-dihedral classes: "
            f"{summary['common_dihedral_pair_class_count']}"
        )
        if args.check:
            print("OK: independent P19 incidence-capacity checks passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
