"""D=3 escape-frontier representative packet for the n=9 base-apex ledger.

This module is finite diagnostic bookkeeping. It narrows the existing
low-excess profile/escape crosswalk to the sharp frontier ``E=6, D=3, r=3``
and stores one compact representative row per profile-multiset/escape-class
cell. The rows are attack-planning targets only; they are not proof,
counterexample, or geometric-realizability claims.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from erdos97.n9_base_apex import canonical_deficit_placement
from erdos97.n9_d3_escape_slice import (
    canonical_coupled_pair,
    escape_placements,
    json_counter,
    placement_payload,
    profile_sequences,
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
EXPECTED_COUNTS = {
    "profile_multiset_count": 11,
    "escape_class_count": 8,
    "representative_count": 88,
    "labelled_profile_sequence_count": 3003,
    "labelled_escape_placement_count": 108,
    "common_dihedral_pair_class_count": 18088,
    "common_dihedral_pair_orbit_size_counts": {"18": 17948, "9": 140},
}

ProfileSequence = tuple[int, ...]
EscapePlacement = tuple[tuple[int, ...], tuple[int, ...]]
CoupledKey = tuple[ProfileSequence, EscapePlacement]


def _escape_sort_key(placement: EscapePlacement) -> tuple[int, EscapePlacement]:
    """Return stable ordering for escape classes."""

    return (len(placement[0]), placement)


def escape_class_rows(
    placements: list[EscapePlacement],
) -> tuple[list[dict[str, Any]], dict[EscapePlacement, str]]:
    """Return canonical escape-class rows and a canonical-placement id map."""

    members: defaultdict[EscapePlacement, list[EscapePlacement]] = defaultdict(list)
    for placement in placements:
        canonical = canonical_deficit_placement(N, placement[0], placement[1])
        members[canonical].append(placement)

    rows: list[dict[str, Any]] = []
    canonical_to_id: dict[EscapePlacement, str] = {}
    for index, placement in enumerate(sorted(members, key=_escape_sort_key)):
        escape_id = f"X{index:02d}"
        canonical_to_id[placement] = escape_id
        rows.append(
            {
                "escape_class_id": escape_id,
                "canonical_escape_placement": placement_payload(placement),
                "labelled_escape_placement_count": len(members[placement]),
            }
        )
    return rows, canonical_to_id


def representative_rows_and_summary() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return representative rows and compact summary counts."""

    sequences = profile_sequences(TOTAL_PROFILE_EXCESS)
    placements = escape_placements()
    profile_counts = Counter(tuple(sorted(sequence)) for sequence in sequences)

    class_sizes: Counter[CoupledKey] = Counter()
    for sequence in sequences:
        for placement in placements:
            class_sizes[canonical_coupled_pair(sequence, placement)] += 1

    by_profile_escape: Counter[tuple[ProfileSequence, EscapePlacement]] = Counter()
    for profile, placement in class_sizes:
        canonical_escape = canonical_deficit_placement(N, placement[0], placement[1])
        by_profile_escape[(tuple(sorted(profile)), canonical_escape)] += 1

    escape_rows, _canonical_to_id = escape_class_rows(placements)
    rows: list[dict[str, Any]] = []
    for profile in sorted(profile_counts):
        for escape_row in escape_rows:
            placement = escape_row["canonical_escape_placement"]
            escape = (
                tuple(placement["spoiled_length2"]),
                tuple(placement["spoiled_length3"]),
            )
            rows.append(
                {
                    "representative_id": f"R{len(rows):03d}",
                    "representative_profile_sequence": [
                        int(value) for value in profile
                    ],
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
            f"unexpected representative summary: expected {EXPECTED_COUNTS!r}, "
            f"got {summary!r}"
        )
    return rows, summary


def d3_escape_frontier_packet_report() -> dict[str, Any]:
    """Return the generated E=6,D=3 escape-frontier representative packet."""

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


def assert_expected_packet_counts(payload: dict[str, Any]) -> None:
    """Assert stable expected counts for the D=3 escape-frontier packet."""

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

    if payload.get("interpretation") != EXPECTED_INTERPRETATION:
        raise AssertionError("unexpected interpretation")
    if payload.get("source_artifacts") != EXPECTED_SOURCE_ARTIFACTS:
        raise AssertionError("unexpected source artifacts")
    if payload.get("provenance") != EXPECTED_PROVENANCE:
        raise AssertionError("unexpected provenance")

    rows = payload.get("representatives")
    if not isinstance(rows, list):
        raise AssertionError("representatives must be a list")
    if len(rows) != EXPECTED_COUNTS["representative_count"]:
        raise AssertionError("unexpected representative row count")
    row_total = sum(
        int(row["common_dihedral_pair_class_count"])
        for row in rows
        if isinstance(row, dict)
        and type(row.get("common_dihedral_pair_class_count")) is int
    )
    if row_total != EXPECTED_COUNTS["common_dihedral_pair_class_count"]:
        raise AssertionError("representative row counts do not sum to total")
