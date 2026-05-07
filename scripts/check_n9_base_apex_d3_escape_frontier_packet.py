#!/usr/bin/env python3
"""Validate the n=9 base-apex D=3 escape-frontier representative packet."""

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
    / "n9_base_apex_d3_escape_frontier_packet.json"
)

N = 9
WITNESS_SIZE = 4
TOTAL_PROFILE_EXCESS = 6
CAPACITY_DEFICIT = 3
RELEVANT_DEFICIT_COUNT = 3
CONTRADICTION_THRESHOLD = 3

EXPECTED_SCHEMA = "erdos97.n9_base_apex_d3_escape_frontier_packet.v1"
EXPECTED_STATUS = "EXPLORATORY_LEDGER_ONLY"
EXPECTED_TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
EXPECTED_CLAIM_SCOPE = (
    "Focused n=9 base-apex D=3,r=3 escape-frontier representative packet "
    "bookkeeping; not a proof of n=9, not a counterexample, not a geometric "
    "realizability test, and not a global status update."
)
EXPECTED_INTERPRETATION = [
    "The packet emits one representative row for each D=3 profile-multiset by strict r=3 escape-class cell.",
    "Representative profile sequences are sorted profile-excess multisets used as compact row representatives, not geometric distance-class realizations.",
    "Canonical escape placements record length-2/length-3 deficits in the current turn-cover diagnostic only.",
    "Common-dihedral pair class counts quotient profile labels and escape placements by the same dihedral relabeling action.",
    "Rows are finite bookkeeping representatives, not certificates that any cell is realizable or impossible.",
    "No proof of the n=9 case is claimed.",
]
EXPECTED_PROVENANCE = {
    "generator": "scripts/analyze_n9_base_apex_d3_escape_frontier_packet.py",
    "command": (
        "python scripts/analyze_n9_base_apex_d3_escape_frontier_packet.py "
        "--assert-expected --out "
        "data/certificates/n9_base_apex_d3_escape_frontier_packet.json"
    ),
}
EXPECTED_SOURCE_ARTIFACTS = {
    "d3_escape_slice": "data/certificates/n9_base_apex_d3_escape_slice.json",
    "low_excess_escape_crosswalk": (
        "data/certificates/n9_base_apex_low_excess_escape_crosswalk.json"
    ),
}
EXPECTED_TOP_LEVEL_KEYS = {
    "capacity_deficit",
    "claim_scope",
    "common_dihedral_pair_class_count",
    "common_dihedral_pair_orbit_size_counts",
    "contradiction_threshold",
    "escape_class_count",
    "interpretation",
    "labelled_escape_placement_count",
    "labelled_profile_sequence_count",
    "n",
    "profile_multiset_count",
    "provenance",
    "relevant_deficit_count",
    "representative_count",
    "representatives",
    "schema",
    "source_artifacts",
    "status",
    "total_profile_excess",
    "trust",
    "witness_size",
}
EXPECTED_REPRESENTATIVE_KEYS = {
    "canonical_escape_placement",
    "common_dihedral_pair_class_count",
    "escape_class_id",
    "excess_multiset",
    "labelled_escape_placement_count",
    "labelled_profile_sequence_count",
    "representative_id",
    "representative_profile_sequence",
}
EXPECTED_COUNTS = {
    "profile_multiset_count": 11,
    "escape_class_count": 8,
    "representative_count": 88,
    "labelled_profile_sequence_count": 3003,
    "labelled_escape_placement_count": 108,
    "common_dihedral_pair_class_count": 18088,
    "common_dihedral_pair_orbit_size_counts": {"18": 17948, "9": 140},
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
def distance_profiles() -> tuple[tuple[int, tuple[int, ...]], ...]:
    """Return independently enumerated n=9 distance-profile excess rows."""

    baseline = binom2(WITNESS_SIZE)
    rows = []
    for ascending_parts in integer_partitions(N - 1):
        parts = tuple(reversed(ascending_parts))
        if max(parts, default=0) < WITNESS_SIZE:
            continue
        excess = sum(binom2(part) for part in parts) - baseline
        rows.append((excess, parts))
    return tuple(sorted(rows, key=lambda row: (row[0], row[1])))


@lru_cache(maxsize=None)
def profile_excess_values() -> tuple[int, ...]:
    """Return sorted profile-excess values for one bad n=9 vertex."""

    return tuple(sorted({excess for excess, _parts in distance_profiles()}))


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


def json_counter(counter: Counter[int]) -> dict[str, int]:
    """Return a sorted counter with JSON string keys."""

    return {str(key): int(counter[key]) for key in sorted(counter)}


def escape_sort_key(placement: EscapePlacement) -> tuple[int, EscapePlacement]:
    """Return stable ordering for escape classes."""

    return (len(placement[0]), placement)


@lru_cache(maxsize=1)
def escape_class_rows() -> tuple[dict[str, Any], ...]:
    """Return canonical escape-class rows."""

    members: defaultdict[EscapePlacement, list[EscapePlacement]] = defaultdict(list)
    for placement in escape_placements():
        members[canonical_escape_placement(placement)].append(placement)

    rows = []
    for index, placement in enumerate(sorted(members, key=escape_sort_key)):
        rows.append(
            {
                "escape_class_id": f"X{index:02d}",
                "canonical_escape_placement": placement_payload(placement),
                "labelled_escape_placement_count": len(members[placement]),
            }
        )
    return tuple(rows)


def parse_expected_escape(row: dict[str, Any]) -> EscapePlacement:
    """Return an expected escape placement tuple from a generated row."""

    placement = row["canonical_escape_placement"]
    return (
        tuple(placement["spoiled_length2"]),
        tuple(placement["spoiled_length3"]),
    )


@lru_cache(maxsize=1)
def representative_rows_and_summary() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return expected representative rows and compact summary counts."""

    sequences = profile_sequences()
    placements = escape_placements()
    profile_counts = Counter(tuple(sorted(sequence)) for sequence in sequences)

    class_sizes: Counter[CoupledKey] = Counter()
    for sequence in sequences:
        for placement in placements:
            class_sizes[canonical_coupled_pair(sequence, placement)] += 1

    by_profile_escape: Counter[tuple[ProfileSequence, EscapePlacement]] = Counter()
    for profile, placement in class_sizes:
        by_profile_escape[
            (tuple(sorted(profile)), canonical_escape_placement(placement))
        ] += 1

    escape_rows = escape_class_rows()
    rows: list[dict[str, Any]] = []
    for profile in sorted(profile_counts):
        for escape_row in escape_rows:
            escape = parse_expected_escape(escape_row)
            rows.append(
                {
                    "representative_id": f"R{len(rows):03d}",
                    "representative_profile_sequence": [int(value) for value in profile],
                    "excess_multiset": [int(value) for value in profile],
                    "labelled_profile_sequence_count": int(profile_counts[profile]),
                    "escape_class_id": escape_row["escape_class_id"],
                    "canonical_escape_placement": escape_row[
                        "canonical_escape_placement"
                    ],
                    "labelled_escape_placement_count": int(
                        escape_row["labelled_escape_placement_count"]
                    ),
                    "common_dihedral_pair_class_count": int(
                        by_profile_escape[(profile, escape)]
                    ),
                }
            )

    summary = {
        "profile_multiset_count": len(profile_counts),
        "escape_class_count": len(escape_rows),
        "representative_count": len(rows),
        "labelled_profile_sequence_count": len(sequences),
        "labelled_escape_placement_count": len(placements),
        "common_dihedral_pair_class_count": len(class_sizes),
        "common_dihedral_pair_orbit_size_counts": json_counter(
            Counter(class_sizes.values())
        ),
    }
    if summary != EXPECTED_COUNTS:
        raise AssertionError(
            f"unexpected representative summary: expected {EXPECTED_COUNTS!r}, got {summary!r}"
        )
    return rows, summary


@lru_cache(maxsize=1)
def _expected_packet_payload_cached() -> dict[str, Any]:
    """Return the independently recomputed expected packet payload."""

    rows, summary = representative_rows_and_summary()
    payload = {
        "schema": EXPECTED_SCHEMA,
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": EXPECTED_CLAIM_SCOPE,
        "n": N,
        "witness_size": WITNESS_SIZE,
        "total_profile_excess": TOTAL_PROFILE_EXCESS,
        "capacity_deficit": CAPACITY_DEFICIT,
        "relevant_deficit_count": RELEVANT_DEFICIT_COUNT,
        "contradiction_threshold": CONTRADICTION_THRESHOLD,
        "profile_multiset_count": summary["profile_multiset_count"],
        "escape_class_count": summary["escape_class_count"],
        "representative_count": summary["representative_count"],
        "labelled_profile_sequence_count": summary[
            "labelled_profile_sequence_count"
        ],
        "labelled_escape_placement_count": summary[
            "labelled_escape_placement_count"
        ],
        "common_dihedral_pair_class_count": summary[
            "common_dihedral_pair_class_count"
        ],
        "common_dihedral_pair_orbit_size_counts": summary[
            "common_dihedral_pair_orbit_size_counts"
        ],
        "representatives": rows,
        "interpretation": EXPECTED_INTERPRETATION,
        "source_artifacts": EXPECTED_SOURCE_ARTIFACTS,
        "provenance": EXPECTED_PROVENANCE,
    }
    assert_expected_packet_counts(payload)
    return payload


def expected_packet_payload() -> dict[str, Any]:
    """Return a deep copy of the independently recomputed packet."""

    return copy.deepcopy(_expected_packet_payload_cached())


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
    spoiled2 = parse_int_list(value.get("spoiled_length2"), f"{label}.spoiled_length2", errors)
    spoiled3 = parse_int_list(value.get("spoiled_length3"), f"{label}.spoiled_length3", errors)
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


def validate_representatives(payload: dict[str, Any]) -> list[str]:
    """Return representative row shape and ordering errors."""

    errors: list[str] = []
    rows = payload.get("representatives")
    if not isinstance(rows, list):
        return ["representatives must be a list"]

    row_keys: list[tuple[tuple[int, ...], str]] = []
    seen_ids: set[str] = set()
    allowed_profile_values = set(profile_excess_values())
    for index, row in enumerate(rows):
        label = f"representatives[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} must be an object")
            continue
        if set(row) != EXPECTED_REPRESENTATIVE_KEYS:
            errors.append(f"{label} keys mismatch")

        expected_id = f"R{index:03d}"
        representative_id = row.get("representative_id")
        if representative_id != expected_id:
            errors.append(f"{label}.representative_id must be {expected_id}")
        elif representative_id in seen_ids:
            errors.append(f"{label}.representative_id is duplicated")
        seen_ids.add(str(representative_id))

        profile = parse_int_list(
            row.get("representative_profile_sequence"),
            f"{label}.representative_profile_sequence",
            errors,
        )
        multiset = parse_int_list(row.get("excess_multiset"), f"{label}.excess_multiset", errors)
        if profile is not None:
            if len(profile) != N:
                errors.append(f"{label}.representative_profile_sequence must have length {N}")
            if profile != sorted(profile):
                errors.append(f"{label}.representative_profile_sequence must be sorted")
            if sum(profile) != TOTAL_PROFILE_EXCESS:
                errors.append(
                    f"{label}.representative_profile_sequence must sum to {TOTAL_PROFILE_EXCESS}"
                )
            if any(value not in allowed_profile_values for value in profile):
                errors.append(
                    f"{label}.representative_profile_sequence contains unknown profile excess"
                )
        if profile is not None and multiset is not None and profile != multiset:
            errors.append(f"{label}.excess_multiset must match representative_profile_sequence")

        escape_id = row.get("escape_class_id")
        if not isinstance(escape_id, str):
            errors.append(f"{label}.escape_class_id must be a string")
        placement = parse_escape_placement_payload(
            row.get("canonical_escape_placement"),
            f"{label}.canonical_escape_placement",
            errors,
        )

        for key in (
            "labelled_profile_sequence_count",
            "labelled_escape_placement_count",
            "common_dihedral_pair_class_count",
        ):
            if not strict_int(row.get(key)):
                errors.append(f"{label}.{key} must be an int")

        if profile is not None and isinstance(escape_id, str):
            row_keys.append((tuple(profile), escape_id))
        if placement is not None and canonical_escape_placement(placement) != placement:
            errors.append(f"{label}.canonical_escape_placement is not canonical")

    if row_keys != sorted(row_keys):
        errors.append("representatives must be ordered by profile sequence then escape_class_id")
    return errors


def assert_expected_packet_counts(payload: dict[str, Any]) -> None:
    """Assert stable expected counts for the representative packet."""

    for key, expected in {
        "schema": EXPECTED_SCHEMA,
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": EXPECTED_CLAIM_SCOPE,
        "n": N,
        "witness_size": WITNESS_SIZE,
        "total_profile_excess": TOTAL_PROFILE_EXCESS,
        "capacity_deficit": CAPACITY_DEFICIT,
        "relevant_deficit_count": RELEVANT_DEFICIT_COUNT,
        "contradiction_threshold": CONTRADICTION_THRESHOLD,
        **EXPECTED_COUNTS,
    }.items():
        if payload.get(key) != expected:
            raise AssertionError(f"unexpected {key}")

    rows = payload.get("representatives")
    if not isinstance(rows, list):
        raise AssertionError("representatives must be a list")
    if len(rows) != EXPECTED_COUNTS["representative_count"]:
        raise AssertionError("unexpected representative row count")
    row_total = sum(
        int(row["common_dihedral_pair_class_count"])
        for row in rows
        if isinstance(row, dict) and strict_int(row.get("common_dihedral_pair_class_count"))
    )
    if row_total != EXPECTED_COUNTS["common_dihedral_pair_class_count"]:
        raise AssertionError("representative row counts do not sum to total")


def validate_payload(payload: Any) -> list[str]:
    """Return validation errors for a loaded representative packet."""

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

    if payload.get("interpretation") != EXPECTED_INTERPRETATION:
        errors.append("interpretation mismatch")
    elif not all(isinstance(item, str) for item in payload.get("interpretation", [])):
        errors.append("interpretation must be the expected list of strings")

    if payload.get("provenance") != EXPECTED_PROVENANCE:
        errors.append("provenance mismatch")
    if payload.get("source_artifacts") != EXPECTED_SOURCE_ARTIFACTS:
        errors.append("source_artifacts mismatch")

    errors.extend(validate_representatives(payload))

    try:
        expected = _expected_packet_payload_cached()
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


def _sum_representative_int(rows: Any, key: str) -> int | None:
    if not isinstance(rows, list):
        return None
    values = [row.get(key) for row in rows if isinstance(row, dict)]
    if len(values) != len(rows) or not all(strict_int(value) for value in values):
        return None
    return sum(int(value) for value in values)


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    rows = object_payload.get("representatives", [])
    return {
        "ok": not errors,
        "artifact": display_path(path),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "n": object_payload.get("n"),
        "witness_size": object_payload.get("witness_size"),
        "profile_multiset_count": object_payload.get("profile_multiset_count"),
        "escape_class_count": object_payload.get("escape_class_count"),
        "representative_count": len(rows) if isinstance(rows, list) else None,
        "common_dihedral_pair_class_count": _sum_representative_int(
            rows,
            "common_dihedral_pair_class_count",
        ),
        "summary_common_dihedral_pair_class_count": object_payload.get(
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
        print("n=9 base-apex D=3 escape-frontier representative packet")
        print(f"artifact: {summary['artifact']}")
        print(
            "representatives: "
            f"profiles={summary['profile_multiset_count']}, "
            f"escapes={summary['escape_class_count']}, "
            f"rows={summary['representative_count']}"
        )
        print(
            "common-dihedral classes: "
            f"{summary['common_dihedral_pair_class_count']}"
        )
        if args.check:
            print("OK: independent D=3 escape-frontier packet checks passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
