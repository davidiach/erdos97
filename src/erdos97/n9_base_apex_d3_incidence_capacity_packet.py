"""Incidence-capacity packet ledger for all n=9 base-apex D=3 rows.

This module extends the P19 pilot to every representative row in the D=3
escape-frontier packet. It is finite bookkeeping only: it records profile
options, displayed length-2/length-3 capacity deficits, and target capacity
totals. It does not decide incidence completeness or geometric realizability.
"""

from __future__ import annotations

import math
from typing import Any

from erdos97.n9_base_apex import cyclic_base_families, profiles_by_excess
from erdos97.n9_base_apex_d3_escape_frontier_packet import (
    d3_escape_frontier_packet_report,
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


def full_capacity_totals_by_cyclic_length() -> dict[str, int]:
    """Return full cyclic base-apex capacities for a nonagon."""

    return {
        str(family.cyclic_length): int(family.total_capacity)
        for family in cyclic_base_families(N)
    }


def target_capacity_totals(
    canonical_escape_placement: dict[str, list[int]],
) -> dict[str, int]:
    """Return capacity targets after the row's displayed deficits."""

    totals = full_capacity_totals_by_cyclic_length()
    spoiled2 = canonical_escape_placement["spoiled_length2"]
    spoiled3 = canonical_escape_placement["spoiled_length3"]
    totals["2"] -= len(spoiled2)
    totals["3"] -= len(spoiled3)
    return totals


def deficient_base_chords(
    canonical_escape_placement: dict[str, list[int]],
) -> list[dict[str, Any]]:
    """Return the deficient length-2 and length-3 base chords."""

    rows: list[dict[str, Any]] = []
    for cyclic_length in (2, 3):
        key = f"spoiled_length{cyclic_length}"
        for base_index in canonical_escape_placement[key]:
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


def labelled_profile_option_count(profile: list[int]) -> int:
    """Return labelled partitions of eight other vertices into profile blocks."""

    remaining_vertices = N - 1
    if sum(profile) != remaining_vertices:
        raise ValueError(f"profile must sum to {remaining_vertices}: {profile!r}")
    numerator = math.factorial(remaining_vertices)
    denominator = 1
    multiplicities: dict[int, int] = {}
    for part in profile:
        denominator *= math.factorial(part)
        multiplicities[part] = multiplicities.get(part, 0) + 1
    for multiplicity in multiplicities.values():
        denominator *= math.factorial(multiplicity)
    return numerator // denominator


def profile_option_counts_by_excess() -> dict[str, dict[str, Any]]:
    """Return pinned profile option counts for D=3 excess values 0 through 6."""

    grouped = profiles_by_excess(N, WITNESS_SIZE)
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
    excess_multiset: list[int],
) -> dict[str, dict[str, Any]]:
    """Return profile option counts for the excess values used by one row."""

    all_counts = profile_option_counts_by_excess()
    return {str(excess): all_counts[str(excess)] for excess in sorted(set(excess_multiset))}


def profile_ledger_id_by_multiset(
    packet_rows: list[dict[str, Any]],
) -> dict[tuple[int, ...], str]:
    """Return P19..P29 ids for the D=3 profile multisets."""

    profiles = sorted({tuple(row["excess_multiset"]) for row in packet_rows})
    if len(profiles) != EXPECTED_COUNTS["profile_multiset_count"]:
        raise AssertionError("unexpected D=3 profile multiset count")
    return {
        profile: f"P{PROFILE_LEDGER_ID_START + index:02d}"
        for index, profile in enumerate(profiles)
    }


def incidence_capacity_rows() -> list[dict[str, Any]]:
    """Return all 88 D=3 incidence-capacity bookkeeping rows."""

    packet = d3_escape_frontier_packet_report()
    packet_rows = packet.get("representatives")
    if not isinstance(packet_rows, list):
        raise AssertionError("D=3 packet representatives are missing")

    profile_ids = profile_ledger_id_by_multiset(packet_rows)
    rows: list[dict[str, Any]] = []
    for packet_row in packet_rows:
        if not isinstance(packet_row, dict):
            raise AssertionError("D=3 packet representative row is malformed")
        placement = packet_row["canonical_escape_placement"]
        if not isinstance(placement, dict):
            raise AssertionError("missing canonical escape placement")
        excess_multiset = [int(value) for value in packet_row["excess_multiset"]]
        capacity_totals = target_capacity_totals(placement)
        row = {
            "representative_id": packet_row["representative_id"],
            "profile_ledger_id": profile_ids[tuple(excess_multiset)],
            "representative_profile_sequence": excess_multiset,
            "excess_multiset": excess_multiset,
            "escape_class_id": packet_row["escape_class_id"],
            "canonical_escape_placement": placement,
            "common_dihedral_pair_class_count": packet_row[
                "common_dihedral_pair_class_count"
            ],
            "target_capacity_totals_by_cyclic_length": capacity_totals,
            "target_capacity_total": sum(capacity_totals.values()),
            "deficient_base_chords": deficient_base_chords(placement),
            "labelled_profile_sequence_count": packet_row[
                "labelled_profile_sequence_count"
            ],
            "labelled_escape_placement_count": packet_row[
                "labelled_escape_placement_count"
            ],
            "profile_option_counts": row_profile_option_counts(excess_multiset),
            "realizability_state": "UNKNOWN",
            "incidence_state": "UNKNOWN",
            "state_scope": "bookkeeping-only",
            "interpretation_warning": EXPECTED_INTERPRETATION_WARNING,
        }
        rows.append(row)
    return rows


def d3_incidence_capacity_packet_report() -> dict[str, Any]:
    """Return the generated all-row D=3 incidence-capacity packet ledger."""

    source = d3_escape_frontier_packet_report()
    rows = incidence_capacity_rows()
    profile_ids = sorted({row["profile_ledger_id"] for row in rows})
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
        "profile_multiset_count": source["profile_multiset_count"],
        "escape_class_count": source["escape_class_count"],
        "representative_count": source["representative_count"],
        "profile_ledger_ids": profile_ids,
        "source_representative_ids": [
            row["representative_id"] for row in source["representatives"]
        ],
        "full_capacity_totals_by_cyclic_length": (
            full_capacity_totals_by_cyclic_length()
        ),
        "target_capacity_total": 60,
        "labelled_profile_sequence_count": source["labelled_profile_sequence_count"],
        "labelled_escape_placement_count": source["labelled_escape_placement_count"],
        "common_dihedral_pair_class_count": source[
            "common_dihedral_pair_class_count"
        ],
        "common_dihedral_pair_orbit_size_counts": source[
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


def assert_expected_packet_counts(payload: dict[str, Any]) -> None:
    """Assert stable expected counts for the all-row D=3 packet ledger."""

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
    if [row.get("representative_id") for row in rows] != [
        f"R{index:03d}" for index in range(EXPECTED_COUNTS["representative_count"])
    ]:
        raise AssertionError("unexpected representative ids")
    if [row.get("profile_ledger_id") for row in rows[::8]] != [
        f"P{index:02d}" for index in range(19, 30)
    ]:
        raise AssertionError("unexpected profile ledger ids")
    if {
        row.get("escape_class_id") for row in rows
    } != {f"X{index:02d}" for index in range(8)}:
        raise AssertionError("unexpected escape class ids")
    row_total = sum(int(row["common_dihedral_pair_class_count"]) for row in rows)
    if row_total != EXPECTED_COUNTS["common_dihedral_pair_class_count"]:
        raise AssertionError("row common-dihedral counts do not sum to total")
    if any(row.get("target_capacity_total") != 60 for row in rows):
        raise AssertionError("unexpected row target capacity total")
