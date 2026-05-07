"""P19 incidence-capacity pilot ledger for the n=9 D=3 packet.

This module is finite bookkeeping for the current base-apex D=3 packet. It
focuses on profile ledger ``P19`` with excess multiset ``[0,0,0,0,0,0,0,0,6]``
and copies only rows ``R000`` through ``R007`` from the packet. The report is
an attack-planning ledger only: it is not a proof, a counterexample, an
incidence-completeness result, or a geometric-realizability test.
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
PROFILE_LEDGER_ID = "P19"
PROFILE_MULTISET = [0, 0, 0, 0, 0, 0, 0, 0, 6]
SOURCE_REPRESENTATIVE_IDS = [f"R{index:03d}" for index in range(8)]
EXPECTED_COMMON_DIHEDRAL_COUNTS = [9, 5, 5, 9, 9, 5, 5, 9]
EXPECTED_COMMON_DIHEDRAL_TOTAL = 56
EXPECTED_LABELLED_PROFILE_SEQUENCE_COUNT = 9
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


def profile_option_counts() -> dict[str, dict[str, Any]]:
    """Return pinned profile option counts for the two P19 excess values."""

    grouped = profiles_by_excess(N, WITNESS_SIZE)
    out: dict[str, dict[str, Any]] = {}
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
        raise AssertionError("unexpected P19 profile option counts")
    return out


def p19_rows() -> list[dict[str, Any]]:
    """Return the eight P19 pilot rows derived from the D=3 packet."""

    packet = d3_escape_frontier_packet_report()
    packet_rows = packet.get("representatives")
    if not isinstance(packet_rows, list):
        raise AssertionError("D=3 packet representatives are missing")

    selected = packet_rows[: len(SOURCE_REPRESENTATIVE_IDS)]
    options = profile_option_counts()
    rows: list[dict[str, Any]] = []
    for index, packet_row in enumerate(selected):
        if packet_row.get("representative_id") != SOURCE_REPRESENTATIVE_IDS[index]:
            raise AssertionError("unexpected source representative order")
        if packet_row.get("excess_multiset") != PROFILE_MULTISET:
            raise AssertionError("unexpected P19 source profile multiset")

        placement = packet_row["canonical_escape_placement"]
        if not isinstance(placement, dict):
            raise AssertionError("missing canonical escape placement")
        row = {
            "representative_id": packet_row["representative_id"],
            "profile_ledger_id": PROFILE_LEDGER_ID,
            "representative_profile_sequence": PROFILE_MULTISET,
            "excess_multiset": PROFILE_MULTISET,
            "escape_class_id": packet_row["escape_class_id"],
            "canonical_escape_placement": placement,
            "common_dihedral_pair_class_count": packet_row[
                "common_dihedral_pair_class_count"
            ],
            "target_capacity_totals_by_cyclic_length": target_capacity_totals(
                placement
            ),
            "deficient_base_chords": deficient_base_chords(placement),
            "labelled_profile_sequence_count": packet_row[
                "labelled_profile_sequence_count"
            ],
            "labelled_escape_placement_count": packet_row[
                "labelled_escape_placement_count"
            ],
            "profile_option_counts": options,
            "realizability_state": "UNKNOWN",
            "incidence_state": "UNKNOWN",
            "state_scope": "bookkeeping-only",
            "interpretation_warning": EXPECTED_INTERPRETATION_WARNING,
        }
        rows.append(row)
    return rows


def p19_incidence_capacity_pilot_report() -> dict[str, Any]:
    """Return the generated P19 incidence-capacity pilot ledger."""

    rows = p19_rows()
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
        "target_capacity_total": sum(
            rows[0]["target_capacity_totals_by_cyclic_length"].values()
        ),
        "labelled_profile_sequence_count": (
            EXPECTED_LABELLED_PROFILE_SEQUENCE_COUNT
        ),
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


def assert_expected_pilot_counts(payload: dict[str, Any]) -> None:
    """Assert stable expected counts for the P19 pilot ledger."""

    for key, expected in {
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
        "labelled_profile_sequence_count": EXPECTED_LABELLED_PROFILE_SEQUENCE_COUNT,
        "profile_option_counts": EXPECTED_PROFILE_OPTION_COUNTS,
        "common_dihedral_pair_class_count": EXPECTED_COMMON_DIHEDRAL_TOTAL,
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
    if [row.get("representative_id") for row in rows] != SOURCE_REPRESENTATIVE_IDS:
        raise AssertionError("unexpected row ids")
    if [
        row.get("common_dihedral_pair_class_count") for row in rows
    ] != EXPECTED_COMMON_DIHEDRAL_COUNTS:
        raise AssertionError("unexpected common-dihedral row counts")
    if {
        row.get("escape_class_id") for row in rows
    } != {f"X{index:02d}" for index in range(8)}:
        raise AssertionError("unexpected escape class ids")
