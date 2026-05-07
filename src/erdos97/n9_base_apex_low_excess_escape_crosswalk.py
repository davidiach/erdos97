"""Low-excess profile/escape crosswalk for the n=9 base-apex ledger.

This module is finite diagnostic bookkeeping. It expands the low-excess
``E=0..6`` ladder into profile-ledger rows crossed with the strict ``r=3``
escape classes. The report stores summary rows only: no individual coupled
profile/escape classes are emitted, and no geometric realizability claim is
made.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
from typing import Any, Sequence

from erdos97.n9_base_apex import (
    base_apex_slack,
    minimum_capacity_deficit_to_escape_turn_cover,
    turn_cover_diagnostic,
)
from erdos97.n9_d3_escape_slice import (
    escape_placements,
    json_counter,
    placement_payload,
    profile_sequences,
    transform_escape_placement,
    transform_profile_sequence,
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
    "not a proof of n=9, not a counterexample, not a geometric realizability "
    "test, and not a global status update."
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

ProfileSequence = tuple[int, ...]
EscapePlacement = tuple[tuple[int, ...], tuple[int, ...]]
CoupledKey = tuple[ProfileSequence, EscapePlacement]


def _dihedral_ops() -> tuple[tuple[int, bool], ...]:
    """Return the 18 dihedral operations in stable order."""

    return tuple(
        (rotation, reflected)
        for rotation in range(N)
        for reflected in (False, True)
    )


@lru_cache(maxsize=None)
def _profile_transforms(sequence: ProfileSequence) -> tuple[ProfileSequence, ...]:
    """Return cached profile transforms under all dihedral operations."""

    return tuple(
        transform_profile_sequence(
            sequence,
            rotation=rotation,
            reflected=reflected,
        )
        for rotation, reflected in _dihedral_ops()
    )


@lru_cache(maxsize=None)
def _escape_transforms(placement: EscapePlacement) -> tuple[EscapePlacement, ...]:
    """Return cached escape-placement transforms under all dihedral operations."""

    return tuple(
        transform_escape_placement(
            placement,
            rotation=rotation,
            reflected=reflected,
        )
        for rotation, reflected in _dihedral_ops()
    )


def _canonical_profile_sequence(sequence: ProfileSequence) -> ProfileSequence:
    """Return the dihedral-canonical labelled profile sequence."""

    return min(_profile_transforms(sequence))


def _canonical_escape_placement(placement: EscapePlacement) -> EscapePlacement:
    """Return the dihedral-canonical escape placement."""

    return min(_escape_transforms(placement))


def _canonical_coupled_pair(
    profile: ProfileSequence,
    placement: EscapePlacement,
) -> CoupledKey:
    """Return the common-dihedral canonical profile/escape pair."""

    return min(zip(_profile_transforms(profile), _escape_transforms(placement)))


def _escape_class_sort_key(placement: EscapePlacement) -> tuple[int, EscapePlacement]:
    """Return the stable ordering key for strict escape classes."""

    return (len(placement[0]), placement)


def escape_class_rows(
    placements: Sequence[EscapePlacement],
) -> tuple[list[dict[str, Any]], dict[str, list[EscapePlacement]]]:
    """Return strict ``r=3`` escape-class rows and member lookup."""

    members: defaultdict[EscapePlacement, list[EscapePlacement]] = defaultdict(list)
    for placement in placements:
        members[_canonical_escape_placement(placement)].append(placement)

    rows: list[dict[str, Any]] = []
    id_to_members: dict[str, list[EscapePlacement]] = {}
    for index, placement in enumerate(sorted(members, key=_escape_class_sort_key)):
        class_id = f"X{index:02d}"
        class_members = sorted(members[placement])
        id_to_members[class_id] = class_members
        diagnostic = turn_cover_diagnostic(
            N,
            spoiled_length2=placement[0],
            spoiled_length3=placement[1],
            contradiction_threshold=CONTRADICTION_THRESHOLD,
        )
        rows.append(
            {
                "escape_class_id": class_id,
                "canonical_escape_placement": placement_payload(placement),
                "labelled_placement_count": len(class_members),
                "remaining_minimum_forced_turns": (
                    diagnostic.minimum_forced_turns
                ),
                "remaining_turn_clause_count": len(diagnostic.turn_clauses),
            }
        )
    return rows, id_to_members


def profile_ledger_rows() -> tuple[list[dict[str, Any]], dict[str, list[ProfileSequence]]]:
    """Return low-excess profile-ledger rows and labelled members."""

    rows: list[dict[str, Any]] = []
    id_to_sequences: dict[str, list[ProfileSequence]] = {}
    for total_profile_excess in range(
        TOTAL_PROFILE_EXCESS_RANGE[0],
        TOTAL_PROFILE_EXCESS_RANGE[1] + 1,
    ):
        by_multiset: defaultdict[tuple[int, ...], list[ProfileSequence]] = defaultdict(
            list
        )
        for sequence in profile_sequences(total_profile_excess):
            by_multiset[tuple(sorted(sequence))].append(sequence)

        for multiset, sequences in sorted(by_multiset.items()):
            class_id = f"P{len(rows):02d}"
            orbit_members: defaultdict[ProfileSequence, list[ProfileSequence]]
            orbit_members = defaultdict(list)
            for sequence in sequences:
                orbit_members[_canonical_profile_sequence(sequence)].append(sequence)
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
    return rows, id_to_sequences


def crosswalk_cell(
    profile_row: dict[str, Any],
    profile_members: Sequence[ProfileSequence],
    escape_row: dict[str, Any],
    escape_members: Sequence[EscapePlacement],
) -> dict[str, Any]:
    """Return one profile-ledger by escape-class matrix cell."""

    class_sizes: Counter[CoupledKey] = Counter()
    for sequence in profile_members:
        for placement in escape_members:
            class_sizes[_canonical_coupled_pair(sequence, placement)] += 1

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

    by_cell = {(row["profile_ledger_id"], row["escape_class_id"]): row for row in rows}
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


def matrix_summary(
    profiles: Sequence[dict[str, Any]],
    escapes: Sequence[dict[str, Any]],
    rows: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Return aggregate crosswalk counts pinned by the artifact."""

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
            1 for row in rows if int(row["common_dihedral_pair_class_count"]) > 0
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
            f"unexpected matrix summary: expected {EXPECTED_MATRIX_SUMMARY!r}, "
            f"got {summary!r}"
        )
    return summary


def low_excess_escape_crosswalk_report() -> dict[str, Any]:
    """Return the generated low-excess profile/escape crosswalk report."""

    slack = base_apex_slack(N, WITNESS_SIZE)
    if slack != BASE_APEX_SLACK:
        raise AssertionError("base-apex slack changed")
    escape = minimum_capacity_deficit_to_escape_turn_cover(
        N,
        contradiction_threshold=CONTRADICTION_THRESHOLD,
    )
    if escape.minimum_capacity_deficit != STRICT_MINIMAL_RELEVANT_ESCAPE:
        raise AssertionError("strict minimum relevant escape count changed")

    escapes, escape_members = escape_class_rows(escape_placements())
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
        "base_apex_slack": slack,
        "total_profile_excess_range": TOTAL_PROFILE_EXCESS_RANGE,
        "capacity_deficit_relation": CAPACITY_DEFICIT_RELATION,
        "contradiction_threshold": CONTRADICTION_THRESHOLD,
        "strict_minimal_relevant_escape": STRICT_MINIMAL_RELEVANT_ESCAPE,
        "source_artifacts": EXPECTED_SOURCE_ARTIFACTS,
        "escape_classes": escapes,
        "profile_ledger_rows": profiles,
        "crosswalk_matrix": matrix,
        "crosswalk_rows": rows,
        "matrix_summary": summary,
        "interpretation": EXPECTED_INTERPRETATION,
        "provenance": EXPECTED_PROVENANCE,
    }
    assert_expected_crosswalk_counts(payload)
    return payload


def assert_expected_crosswalk_counts(payload: dict[str, Any]) -> None:
    """Assert stable expected counts for the low-excess crosswalk report."""

    if payload.get("schema") != EXPECTED_SCHEMA:
        raise AssertionError("unexpected schema")
    if payload.get("status") != EXPECTED_STATUS:
        raise AssertionError("unexpected status")
    if payload.get("trust") != EXPECTED_TRUST:
        raise AssertionError("unexpected trust label")
    if payload.get("claim_scope") != EXPECTED_CLAIM_SCOPE:
        raise AssertionError("unexpected claim scope")
    if payload.get("n") != N or payload.get("witness_size") != WITNESS_SIZE:
        raise AssertionError("unexpected n or witness_size")
    if payload.get("base_apex_slack") != BASE_APEX_SLACK:
        raise AssertionError("unexpected base-apex slack")
    if payload.get("interpretation") != EXPECTED_INTERPRETATION:
        raise AssertionError("unexpected interpretation")
    if payload.get("provenance") != EXPECTED_PROVENANCE:
        raise AssertionError("unexpected provenance")

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

    if payload.get("matrix_summary") != EXPECTED_MATRIX_SUMMARY:
        raise AssertionError("unexpected matrix summary")
