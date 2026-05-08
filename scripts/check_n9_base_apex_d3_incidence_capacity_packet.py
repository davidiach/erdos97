#!/usr/bin/env python3
"""Validate the full n=9 D=3 incidence-capacity packet ledger."""

from __future__ import annotations

import argparse
import copy
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
    / "n9_base_apex_d3_incidence_capacity_packet.json"
)

N = 9
WITNESS_SIZE = 4
TOTAL_PROFILE_EXCESS = 6
CAPACITY_DEFICIT = 3
RELEVANT_DEFICIT_COUNT = 3
CONTRADICTION_THRESHOLD = 3
PROFILE_LEDGER_ID_START = 19

EXPECTED_SCHEMA = "erdos97.n9_base_apex_d3_incidence_capacity_packet.v1"
EXPECTED_STATUS = "EXPLORATORY_LEDGER_ONLY"
EXPECTED_TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
EXPECTED_CLAIM_SCOPE = (
    "Full n=9 base-apex D=3 incidence-capacity packet ledger for all 88 D=3 "
    "packet rows; not a proof of n=9, not a counterexample, not an "
    "incidence-completeness result, not a geometric realizability test, and "
    "not a global status update."
)
EXPECTED_INTERPRETATION_WARNING = (
    "Bookkeeping-only warning: these rows do not decide feasibility, "
    "realizability, or incidence completeness."
)
EXPECTED_INTERPRETATION = [
    "The packet covers all 88 rows from the D=3 escape-frontier representative packet.",
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
    "generator": "scripts/analyze_n9_base_apex_d3_incidence_capacity_packet.py",
    "command": (
        "python scripts/analyze_n9_base_apex_d3_incidence_capacity_packet.py "
        "--assert-expected --out "
        "data/certificates/n9_base_apex_d3_incidence_capacity_packet.json"
    ),
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
EXPECTED_PROFILE_OPTION_COUNTS_BY_EXCESS = {
    "0": {
        "distance_profile": [4, 1, 1, 1, 1],
        "labelled_option_count": 70,
    },
    "1": {
        "distance_profile": [4, 2, 1, 1],
        "labelled_option_count": 420,
    },
    "2": {
        "distance_profile": [4, 2, 2],
        "labelled_option_count": 210,
    },
    "3": {
        "distance_profile": [4, 3, 1],
        "labelled_option_count": 280,
    },
    "4": {
        "distance_profile": [5, 1, 1, 1],
        "labelled_option_count": 56,
    },
    "5": {
        "distance_profile": [5, 2, 1],
        "labelled_option_count": 168,
    },
    "6": {
        "distance_profile": [4, 4],
        "labelled_option_count": 35,
    },
}
EXPECTED_TOP_LEVEL_KEYS = {
    "capacity_deficit",
    "claim_scope",
    "common_dihedral_pair_class_count",
    "common_dihedral_pair_orbit_size_counts",
    "contradiction_threshold",
    "escape_class_count",
    "full_capacity_totals_by_cyclic_length",
    "incidence_state",
    "interpretation",
    "interpretation_warning",
    "labelled_escape_placement_count",
    "labelled_profile_sequence_count",
    "n",
    "profile_ledger_ids",
    "profile_multiset_count",
    "profile_option_counts_by_excess",
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
    "target_capacity_total",
    "target_capacity_totals_by_cyclic_length",
}
EXPECTED_CHORD_KEYS = {"base_index", "chord", "cyclic_length"}
MAX_COMPARISON_ERRORS = 25

EscapePlacement = tuple[tuple[int, ...], tuple[int, ...]]


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


@lru_cache(maxsize=1)
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


def profile_option_counts_by_excess() -> dict[str, dict[str, Any]]:
    """Return independently recomputed profile option counts for excess 0..6."""

    grouped = profiles_by_excess()
    out: dict[str, dict[str, Any]] = {}
    for excess in range(TOTAL_PROFILE_EXCESS + 1):
        profiles = grouped[excess]
        if len(profiles) != 1:
            raise AssertionError(f"expected one profile for excess {excess}")
        profile = [int(value) for value in profiles[0]]
        out[str(excess)] = {
            "distance_profile": profile,
            "labelled_option_count": labelled_profile_option_count(profile),
        }
    if out != EXPECTED_PROFILE_OPTION_COUNTS_BY_EXCESS:
        raise AssertionError("unexpected D=3 profile option counts")
    return out


def row_profile_option_counts(
    excess_multiset: Sequence[int],
) -> dict[str, dict[str, Any]]:
    """Return profile option counts for one row's distinct excess values."""

    all_counts = profile_option_counts_by_excess()
    return {str(excess): all_counts[str(excess)] for excess in sorted(set(excess_multiset))}


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


def parse_escape_placement_unchecked(row: dict[str, Any]) -> EscapePlacement:
    """Return an escape placement tuple from a trusted source row."""

    placement = row["canonical_escape_placement"]
    return (
        tuple(int(value) for value in placement["spoiled_length2"]),
        tuple(int(value) for value in placement["spoiled_length3"]),
    )


def profile_ledger_id_by_multiset(
    source_rows: Sequence[dict[str, Any]],
) -> dict[tuple[int, ...], str]:
    """Return P19..P29 ids for source D=3 profile multisets."""

    profiles = sorted({tuple(row["excess_multiset"]) for row in source_rows})
    if len(profiles) != EXPECTED_COUNTS["profile_multiset_count"]:
        raise AssertionError("unexpected D=3 profile multiset count")
    return {
        profile: f"P{PROFILE_LEDGER_ID_START + index:02d}"
        for index, profile in enumerate(profiles)
    }


def source_artifact_path(source_key: str) -> Path:
    """Return the expected path for one source artifact."""

    return ROOT / EXPECTED_SOURCE_ARTIFACTS[source_key]


def load_json(path: Path) -> Any:
    """Load JSON from a path."""

    return json.loads(path.read_text(encoding="utf-8"))


def load_source_artifact(path: Path, label: str, errors: list[str]) -> Any | None:
    """Load a declared source artifact, reporting checker-friendly errors."""

    try:
        return load_json(path)
    except FileNotFoundError:
        errors.append(f"{label} source artifact is missing: {path.as_posix()}")
    except json.JSONDecodeError as exc:
        errors.append(f"{label} source artifact is not valid JSON: {exc}")
    return None


def d3_source_representatives(errors: list[str]) -> list[dict[str, Any]]:
    """Return the checked-in D=3 representative rows."""

    source = load_source_artifact(
        source_artifact_path("d3_escape_frontier_packet"),
        "d3_escape_frontier_packet",
        errors,
    )
    if not isinstance(source, dict):
        errors.append("d3_escape_frontier_packet source must be an object")
        return []
    for key, expected in EXPECTED_COUNTS.items():
        if source.get(key) != expected:
            errors.append(f"d3_escape_frontier_packet.{key} mismatch")
    representatives = source.get("representatives")
    if not isinstance(representatives, list):
        errors.append("d3_escape_frontier_packet.representatives must be a list")
        return []
    if len(representatives) != EXPECTED_COUNTS["representative_count"]:
        errors.append("d3_escape_frontier_packet representative count mismatch")
    return [row for row in representatives if isinstance(row, dict)]


@lru_cache(maxsize=1)
def _expected_packet_payload_cached() -> dict[str, Any]:
    """Return the expected packet payload derived from checked source data."""

    source_errors: list[str] = []
    source_rows = d3_source_representatives(source_errors)
    if source_errors:
        raise AssertionError("; ".join(source_errors))
    profile_ids = profile_ledger_id_by_multiset(source_rows)
    rows = []
    for source_row in source_rows:
        profile = [int(value) for value in source_row["excess_multiset"]]
        placement = parse_escape_placement_unchecked(source_row)
        capacity_totals = target_capacity_totals(placement)
        rows.append(
            {
                "representative_id": source_row["representative_id"],
                "profile_ledger_id": profile_ids[tuple(profile)],
                "representative_profile_sequence": profile,
                "excess_multiset": profile,
                "escape_class_id": source_row["escape_class_id"],
                "canonical_escape_placement": source_row[
                    "canonical_escape_placement"
                ],
                "common_dihedral_pair_class_count": source_row[
                    "common_dihedral_pair_class_count"
                ],
                "target_capacity_totals_by_cyclic_length": capacity_totals,
                "target_capacity_total": sum(capacity_totals.values()),
                "deficient_base_chords": deficient_base_chords(placement),
                "labelled_profile_sequence_count": source_row[
                    "labelled_profile_sequence_count"
                ],
                "labelled_escape_placement_count": source_row[
                    "labelled_escape_placement_count"
                ],
                "profile_option_counts": row_profile_option_counts(profile),
                "realizability_state": "UNKNOWN",
                "incidence_state": "UNKNOWN",
                "state_scope": "bookkeeping-only",
                "interpretation_warning": EXPECTED_INTERPRETATION_WARNING,
            }
        )

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
        "profile_multiset_count": EXPECTED_COUNTS["profile_multiset_count"],
        "escape_class_count": EXPECTED_COUNTS["escape_class_count"],
        "representative_count": EXPECTED_COUNTS["representative_count"],
        "profile_ledger_ids": sorted(set(profile_ids.values())),
        "source_representative_ids": [
            f"R{index:03d}" for index in range(EXPECTED_COUNTS["representative_count"])
        ],
        "full_capacity_totals_by_cyclic_length": (
            full_capacity_totals_by_cyclic_length()
        ),
        "target_capacity_total": 60,
        "labelled_profile_sequence_count": EXPECTED_COUNTS[
            "labelled_profile_sequence_count"
        ],
        "labelled_escape_placement_count": EXPECTED_COUNTS[
            "labelled_escape_placement_count"
        ],
        "common_dihedral_pair_class_count": EXPECTED_COUNTS[
            "common_dihedral_pair_class_count"
        ],
        "common_dihedral_pair_orbit_size_counts": EXPECTED_COUNTS[
            "common_dihedral_pair_orbit_size_counts"
        ],
        "profile_option_counts_by_excess": profile_option_counts_by_excess(),
        "realizability_state": "UNKNOWN",
        "incidence_state": "UNKNOWN",
        "state_scope": "bookkeeping-only",
        "rows": rows,
        "interpretation_warning": EXPECTED_INTERPRETATION_WARNING,
        "interpretation": EXPECTED_INTERPRETATION,
        "source_artifacts": EXPECTED_SOURCE_ARTIFACTS,
        "provenance": EXPECTED_PROVENANCE,
    }
    assert_expected_packet_counts(payload)
    return payload


def expected_packet_payload() -> dict[str, Any]:
    """Return a deep copy of the expected all-row packet payload."""

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


def parse_int_tuple_quiet(value: Any) -> tuple[int, ...] | None:
    """Return an integer tuple for source joins, or None for malformed values."""

    if not isinstance(value, list) or not all(strict_int(item) for item in value):
        return None
    return tuple(int(item) for item in value)


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
    """Return strict cyclic-length totals when well shaped."""

    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return None
    if set(value) != {"1", "2", "3", "4"}:
        errors.append(f"{label} keys mismatch")
        return None
    if not all(strict_int(item) for item in value.values()):
        errors.append(f"{label} values must be ints")
        return None
    return {str(key): int(total) for key, total in value.items()}


def validate_profile_option_counts(
    value: Any,
    expected: dict[str, dict[str, Any]],
    label: str,
    errors: list[str],
) -> None:
    """Validate profile option counts."""

    if value != expected:
        errors.append(f"{label} mismatch")
    compare_json(errors, label, value, expected)


def validate_deficient_base_chords(
    value: Any,
    placement: EscapePlacement | None,
    label: str,
    errors: list[str],
) -> None:
    """Validate displayed deficient base chords against the escape placement."""

    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return
    for index, chord in enumerate(value):
        chord_label = f"{label}[{index}]"
        if not isinstance(chord, dict):
            errors.append(f"{chord_label} must be an object")
            continue
        if set(chord) != EXPECTED_CHORD_KEYS:
            errors.append(f"{chord_label} keys mismatch")
        for key in ("cyclic_length", "base_index"):
            if not strict_int(chord.get(key)):
                errors.append(f"{chord_label}.{key} must be an int")
        chord_vertices = parse_int_list(
            chord.get("chord"),
            f"{chord_label}.chord",
            errors,
        )
        if chord_vertices is not None and len(chord_vertices) != 2:
            errors.append(f"{chord_label}.chord must have length 2")
    if placement is not None and value != deficient_base_chords(placement):
        errors.append(f"{label} does not match canonical_escape_placement")


def validate_rows(payload: dict[str, Any]) -> list[str]:
    """Return row shape, state, capacity, and ordering errors."""

    errors: list[str] = []
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return ["rows must be a list"]

    row_keys: list[tuple[list[int], str]] = []
    row_counts: list[int] = []
    source_ids: list[str] = []
    profile_ids: list[str] = []
    allowed_excesses = set(range(TOTAL_PROFILE_EXCESS + 1))
    profile_id_by_multiset: dict[tuple[int, ...], str] = {}

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
            source_ids.append(representative_id)

        profile_id = row.get("profile_ledger_id")
        if not isinstance(profile_id, str):
            errors.append(f"{label}.profile_ledger_id must be a string")
        else:
            profile_ids.append(profile_id)

        profile = parse_int_list(
            row.get("representative_profile_sequence"),
            f"{label}.representative_profile_sequence",
            errors,
        )
        multiset = parse_int_list(
            row.get("excess_multiset"),
            f"{label}.excess_multiset",
            errors,
        )
        if profile is not None:
            profile_is_valid_for_options = True
            if len(profile) != N:
                errors.append(
                    f"{label}.representative_profile_sequence must have length {N}"
                )
                profile_is_valid_for_options = False
            if profile != sorted(profile):
                errors.append(
                    f"{label}.representative_profile_sequence must be sorted"
                )
                profile_is_valid_for_options = False
            if sum(profile) != TOTAL_PROFILE_EXCESS:
                errors.append(
                    f"{label}.representative_profile_sequence must sum to "
                    f"{TOTAL_PROFILE_EXCESS}"
                )
                profile_is_valid_for_options = False
            if any(value not in allowed_excesses for value in profile):
                errors.append(
                    f"{label}.representative_profile_sequence contains unknown profile excess"
                )
                profile_is_valid_for_options = False
        else:
            profile_is_valid_for_options = False
        if profile is not None and multiset is not None and profile != multiset:
            errors.append(
                f"{label}.excess_multiset must match representative_profile_sequence"
            )
        if profile is not None and isinstance(profile_id, str):
            profile_id_by_multiset.setdefault(tuple(profile), profile_id)

        escape_id = row.get("escape_class_id")
        if not isinstance(escape_id, str):
            errors.append(f"{label}.escape_class_id must be a string")
        elif profile is not None:
            row_keys.append((profile, escape_id))

        for key, expected in (
            ("realizability_state", "UNKNOWN"),
            ("incidence_state", "UNKNOWN"),
            ("state_scope", "bookkeeping-only"),
            ("interpretation_warning", EXPECTED_INTERPRETATION_WARNING),
            ("target_capacity_total", 60),
        ):
            if row.get(key) != expected:
                errors.append(f"{label}.{key} mismatch")

        for key in (
            "common_dihedral_pair_class_count",
            "labelled_escape_placement_count",
            "labelled_profile_sequence_count",
            "target_capacity_total",
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
        if profile_is_valid_for_options:
            validate_profile_option_counts(
                row.get("profile_option_counts"),
                row_profile_option_counts(profile),
                f"{label}.profile_option_counts",
                errors,
            )

    expected_source_ids = [
        f"R{index:03d}" for index in range(EXPECTED_COUNTS["representative_count"])
    ]
    if source_ids != expected_source_ids:
        errors.append("rows must be ordered R000..R087")
    if row_keys != sorted(row_keys):
        errors.append("rows must be ordered by profile sequence then escape_class_id")
    expected_profile_ids = [f"P{index:02d}" for index in range(19, 30)]
    if sorted(set(profile_ids)) != expected_profile_ids:
        errors.append("profile ledger ids must be P19..P29")
    if [profile_id_by_multiset[key] for key in sorted(profile_id_by_multiset)] != expected_profile_ids:
        errors.append("profile ledger ids do not match sorted profile multisets")
    if row_counts and sum(row_counts) != EXPECTED_COUNTS["common_dihedral_pair_class_count"]:
        errors.append("row common-dihedral counts do not sum to summary total")
    return errors


def assert_expected_packet_counts(payload: dict[str, Any]) -> None:
    """Assert stable expected counts for the all-row packet ledger."""

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
        "profile_ledger_ids": [f"P{index:02d}" for index in range(19, 30)],
        "source_representative_ids": [
            f"R{index:03d}" for index in range(EXPECTED_COUNTS["representative_count"])
        ],
        "full_capacity_totals_by_cyclic_length": {"1": 9, "2": 18, "3": 18, "4": 18},
        "target_capacity_total": 60,
        "profile_option_counts_by_excess": EXPECTED_PROFILE_OPTION_COUNTS_BY_EXCESS,
        "realizability_state": "UNKNOWN",
        "incidence_state": "UNKNOWN",
        "state_scope": "bookkeeping-only",
        "interpretation_warning": EXPECTED_INTERPRETATION_WARNING,
        "interpretation": EXPECTED_INTERPRETATION,
        "source_artifacts": EXPECTED_SOURCE_ARTIFACTS,
        "provenance": EXPECTED_PROVENANCE,
    }.items():
        if payload.get(key) != expected:
            raise AssertionError(f"unexpected {key}")

    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise AssertionError("rows must be a list")
    if len(rows) != EXPECTED_COUNTS["representative_count"]:
        raise AssertionError("unexpected row count")
    row_total = sum(
        int(row["common_dihedral_pair_class_count"])
        for row in rows
        if isinstance(row, dict)
        and strict_int(row.get("common_dihedral_pair_class_count"))
    )
    if row_total != EXPECTED_COUNTS["common_dihedral_pair_class_count"]:
        raise AssertionError("row common-dihedral counts do not sum to total")


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


def validate_d3_packet_source(payload: dict[str, Any], errors: list[str]) -> None:
    """Validate rows against the checked-in D=3 packet artifact."""

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
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return
    if len(representatives) < len(rows):
        errors.append("d3_escape_frontier_packet has too few source rows")
        return
    for index, (row, source_row) in enumerate(zip(rows, representatives, strict=False)):
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
            if key not in source_row:
                errors.append(
                    "d3_escape_frontier_packet source row "
                    f"{index} missing field {key}"
                )
            source_value = source_row.get(key)
            if row.get(key) != source_value:
                errors.append(
                    "rows[{index}] does not match d3_escape_frontier_packet "
                    "source field {key}".format(index=index, key=key)
                )


def validate_crosswalk_source(payload: dict[str, Any], errors: list[str]) -> None:
    """Validate rows against the checked-in low-excess crosswalk artifact."""

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

    d3_by_key: dict[tuple[tuple[int, ...], str], dict[str, Any]] = {}
    d3_row_count = 0
    for source_index, row in enumerate(crosswalk_rows):
        if not isinstance(row, dict):
            continue
        if (
            row.get("total_profile_excess") == TOTAL_PROFILE_EXCESS
            and row.get("capacity_deficit") == CAPACITY_DEFICIT
        ):
            d3_row_count += 1
            source_multiset = parse_int_tuple_quiet(row.get("excess_multiset"))
            source_escape_id = row.get("escape_class_id")
            if source_multiset is None or not isinstance(source_escape_id, str):
                errors.append(
                    "low_excess_escape_crosswalk source D=3 row "
                    f"{source_index} has malformed key fields"
                )
                continue
            key = (source_multiset, source_escape_id)
            if key in d3_by_key:
                errors.append(
                    "low_excess_escape_crosswalk duplicate D=3 row key "
                    f"at source row {source_index}: {key!r}"
                )
                continue
            d3_by_key[key] = row
    if d3_row_count != EXPECTED_COUNTS["representative_count"]:
        errors.append("low_excess_escape_crosswalk D=3 row count mismatch")
    if len(d3_by_key) != EXPECTED_COUNTS["representative_count"]:
        errors.append("low_excess_escape_crosswalk D=3 unique row count mismatch")
        return

    rows = payload.get("rows")
    if not isinstance(rows, list):
        return
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        row_multiset = parse_int_tuple_quiet(row.get("excess_multiset"))
        row_escape_id = row.get("escape_class_id")
        if row_multiset is None or not isinstance(row_escape_id, str):
            errors.append(
                "low_excess_escape_crosswalk source join skipped malformed "
                f"payload row {index}"
            )
            continue
        key = (
            row_multiset,
            row_escape_id,
        )
        source_row = d3_by_key.get(key)
        if not isinstance(source_row, dict):
            errors.append(
                "low_excess_escape_crosswalk source is missing row "
                f"{index}: {key!r}"
            )
            continue
        for field in (
            "profile_ledger_id",
            "excess_multiset",
            "escape_class_id",
            "canonical_escape_placement",
            "common_dihedral_pair_class_count",
            "labelled_profile_sequence_count",
            "labelled_escape_placement_count",
        ):
            if row.get(field) != source_row.get(field):
                errors.append(
                    "rows[{index}] does not match low_excess_escape_crosswalk "
                    "source field {field}".format(index=index, field=field)
                )
        pair_count_values = (
            row.get("labelled_profile_sequence_count"),
            row.get("labelled_escape_placement_count"),
        )
        if all(strict_int(value) for value in pair_count_values):
            pair_count = int(pair_count_values[0]) * int(pair_count_values[1])
            if source_row.get("labelled_profile_escape_pair_count") != pair_count:
                errors.append(
                    "low_excess_escape_crosswalk labelled pair count mismatch "
                    f"for rows[{index}]"
                )


def validate_source_artifacts(payload: dict[str, Any], errors: list[str]) -> None:
    """Validate that declared source artifacts still project to the packet rows."""

    validate_d3_packet_source(payload, errors)
    validate_crosswalk_source(payload, errors)


def validate_payload(payload: Any) -> list[str]:
    """Return validation errors for a loaded all-row packet artifact."""

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
        "total_profile_excess": TOTAL_PROFILE_EXCESS,
        "capacity_deficit": CAPACITY_DEFICIT,
        "relevant_deficit_count": RELEVANT_DEFICIT_COUNT,
        "contradiction_threshold": CONTRADICTION_THRESHOLD,
        **EXPECTED_COUNTS,
        "profile_ledger_ids": [f"P{index:02d}" for index in range(19, 30)],
        "source_representative_ids": [
            f"R{index:03d}" for index in range(EXPECTED_COUNTS["representative_count"])
        ],
        "full_capacity_totals_by_cyclic_length": {"1": 9, "2": 18, "3": 18, "4": 18},
        "target_capacity_total": 60,
        "profile_option_counts_by_excess": EXPECTED_PROFILE_OPTION_COUNTS_BY_EXCESS,
        "realizability_state": "UNKNOWN",
        "incidence_state": "UNKNOWN",
        "state_scope": "bookkeeping-only",
    }.items():
        compare_json(errors, key, payload.get(key), expected)

    validate_profile_option_counts(
        payload.get("profile_option_counts_by_excess"),
        EXPECTED_PROFILE_OPTION_COUNTS_BY_EXCESS,
        "profile_option_counts_by_excess",
        errors,
    )
    errors.extend(validate_rows(payload))

    try:
        expected_payload = _expected_packet_payload_cached()
    except AssertionError as exc:
        errors.append(f"independent source projection failed: {exc}")
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
        "profile_multiset_count": object_payload.get("profile_multiset_count"),
        "escape_class_count": object_payload.get("escape_class_count"),
        "representative_count": len(rows) if isinstance(rows, list) else None,
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
        print("n=9 D=3 incidence-capacity packet artifact")
        print(f"artifact: {summary['artifact']}")
        print(
            "rows: "
            f"profiles={summary['profile_multiset_count']}, "
            f"escapes={summary['escape_class_count']}, "
            f"representatives={summary['representative_count']}"
        )
        print(
            "common-dihedral classes: "
            f"{summary['common_dihedral_pair_class_count']}"
        )
        if args.check:
            print("OK: independent D=3 incidence-capacity checks passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
