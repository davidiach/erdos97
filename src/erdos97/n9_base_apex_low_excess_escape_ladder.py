"""Low-excess minimal escape-slice ladder for the n=9 base-apex ledger.

This module is finite diagnostic bookkeeping. It couples profile-excess
levels ``E=0..6`` with the strict-threshold minimum relevant escape count
``r=3`` and capacity deficit ``D=9-E``. It is summary-only: no individual
coupled classes are emitted, and no geometric realizability claim is made.
"""

from __future__ import annotations

from collections import Counter, defaultdict

from erdos97.n9_base_apex import (
    base_apex_slack,
    deficit_placement_classes,
    escape_relevant_deficit_counts,
    minimum_capacity_deficit_to_escape_turn_cover,
)
from erdos97.n9_d3_escape_slice import (
    canonical_coupled_pair,
    canonical_profile_sequence,
    escape_placements,
    json_counter,
    profile_sequences,
)

N = 9
WITNESS_SIZE = 4
STRICT_CONTRADICTION_THRESHOLD = 3
MAX_TOTAL_PROFILE_EXCESS = 6
STRICT_MINIMAL_RELEVANT_ESCAPE = 3

EXPECTED_ESCAPE_LABELLED_PLACEMENT_COUNT = 108
EXPECTED_ESCAPE_DIHEDRAL_CLASS_COUNT = 8
EXPECTED_ESCAPE_ORBIT_SIZE_COUNTS = {9: 4, 18: 4}
EXPECTED_ESCAPE_RELEVANT_COUNTS = {
    "total_relevant_placement_count": 816,
    "labelled_placement_count": 108,
    "dihedral_class_count": 8,
    "remaining_minimum_forced_turn_count": {"2": 108},
}
EXPECTED_LADDER_ROWS = {
    0: {
        "capacity_deficit": 9,
        "unassigned_capacity_after_minimum_relevant_escape": 6,
        "unlabeled_profile_ledger_count": 1,
        "labelled_profile_sequence_count": 1,
        "dihedral_profile_orbit_count": 1,
        "dihedral_profile_orbit_size_counts": {"1": 1},
        "labelled_profile_escape_pair_count": 108,
        "common_dihedral_pair_class_count": 8,
        "common_dihedral_pair_orbit_size_counts": {"9": 4, "18": 4},
    },
    1: {
        "capacity_deficit": 8,
        "unassigned_capacity_after_minimum_relevant_escape": 5,
        "unlabeled_profile_ledger_count": 1,
        "labelled_profile_sequence_count": 9,
        "dihedral_profile_orbit_count": 1,
        "dihedral_profile_orbit_size_counts": {"9": 1},
        "labelled_profile_escape_pair_count": 972,
        "common_dihedral_pair_class_count": 56,
        "common_dihedral_pair_orbit_size_counts": {"9": 4, "18": 52},
    },
    2: {
        "capacity_deficit": 7,
        "unassigned_capacity_after_minimum_relevant_escape": 4,
        "unlabeled_profile_ledger_count": 2,
        "labelled_profile_sequence_count": 45,
        "dihedral_profile_orbit_count": 5,
        "dihedral_profile_orbit_size_counts": {"9": 5},
        "labelled_profile_escape_pair_count": 4860,
        "common_dihedral_pair_class_count": 280,
        "common_dihedral_pair_orbit_size_counts": {"9": 20, "18": 260},
    },
    3: {
        "capacity_deficit": 6,
        "unassigned_capacity_after_minimum_relevant_escape": 3,
        "unlabeled_profile_ledger_count": 3,
        "labelled_profile_sequence_count": 165,
        "dihedral_profile_orbit_count": 12,
        "dihedral_profile_orbit_size_counts": {"3": 1, "9": 4, "18": 7},
        "labelled_profile_escape_pair_count": 17820,
        "common_dihedral_pair_class_count": 1000,
        "common_dihedral_pair_orbit_size_counts": {"9": 20, "18": 980},
    },
    4: {
        "capacity_deficit": 5,
        "unassigned_capacity_after_minimum_relevant_escape": 2,
        "unlabeled_profile_ledger_count": 5,
        "labelled_profile_sequence_count": 495,
        "dihedral_profile_orbit_count": 35,
        "dihedral_profile_orbit_size_counts": {"9": 15, "18": 20},
        "labelled_profile_escape_pair_count": 53460,
        "common_dihedral_pair_class_count": 3000,
        "common_dihedral_pair_orbit_size_counts": {"9": 60, "18": 2940},
    },
    5: {
        "capacity_deficit": 4,
        "unassigned_capacity_after_minimum_relevant_escape": 1,
        "unlabeled_profile_ledger_count": 7,
        "labelled_profile_sequence_count": 1287,
        "dihedral_profile_orbit_count": 79,
        "dihedral_profile_orbit_size_counts": {"9": 15, "18": 64},
        "labelled_profile_escape_pair_count": 138996,
        "common_dihedral_pair_class_count": 7752,
        "common_dihedral_pair_orbit_size_counts": {"9": 60, "18": 7692},
    },
    6: {
        "capacity_deficit": 3,
        "unassigned_capacity_after_minimum_relevant_escape": 0,
        "unlabeled_profile_ledger_count": 11,
        "labelled_profile_sequence_count": 3003,
        "dihedral_profile_orbit_count": 185,
        "dihedral_profile_orbit_size_counts": {"3": 2, "9": 33, "18": 150},
        "labelled_profile_escape_pair_count": 324324,
        "common_dihedral_pair_class_count": 18088,
        "common_dihedral_pair_orbit_size_counts": {"9": 140, "18": 17948},
    },
}


ProfileSequence = tuple[int, ...]
EscapePlacement = tuple[tuple[int, ...], tuple[int, ...]]
CoupledKey = tuple[ProfileSequence, EscapePlacement]


def profile_ladder_row(
    total_profile_excess: int,
    placements: list[EscapePlacement],
) -> dict[str, object]:
    """Return one summary row for a fixed total profile excess ``E``."""

    slack = base_apex_slack(N, WITNESS_SIZE)
    if total_profile_excess < 0 or total_profile_excess > slack:
        raise ValueError(
            f"total_profile_excess must be in [0, {slack}], "
            f"got {total_profile_excess}"
        )

    sequences = profile_sequences(total_profile_excess)
    profile_orbits: defaultdict[ProfileSequence, list[ProfileSequence]] = defaultdict(
        list
    )
    for sequence in sequences:
        profile_orbits[canonical_profile_sequence(sequence)].append(sequence)

    coupled_class_sizes: Counter[CoupledKey] = Counter()
    for sequence in sequences:
        for placement in placements:
            coupled_class_sizes[canonical_coupled_pair(sequence, placement)] += 1

    capacity_deficit = slack - total_profile_excess
    return {
        "total_profile_excess": total_profile_excess,
        "capacity_deficit": capacity_deficit,
        "strict_minimal_relevant_escape": STRICT_MINIMAL_RELEVANT_ESCAPE,
        "unassigned_capacity_after_minimum_relevant_escape": (
            capacity_deficit - STRICT_MINIMAL_RELEVANT_ESCAPE
        ),
        "unlabeled_profile_ledger_count": len(
            Counter(tuple(sorted(sequence)) for sequence in sequences)
        ),
        "labelled_profile_sequence_count": len(sequences),
        "dihedral_profile_orbit_count": len(profile_orbits),
        "dihedral_profile_orbit_size_counts": json_counter(
            Counter(len(members) for members in profile_orbits.values())
        ),
        "labelled_profile_escape_pair_count": len(sequences) * len(placements),
        "common_dihedral_pair_class_count": len(coupled_class_sizes),
        "common_dihedral_pair_orbit_size_counts": json_counter(
            Counter(coupled_class_sizes.values())
        ),
    }


def strict_escape_summary(placements: list[EscapePlacement]) -> dict[str, object]:
    """Return the shared strict-threshold minimum escape summary."""

    classes = deficit_placement_classes(
        N,
        relevant_deficit_count=STRICT_MINIMAL_RELEVANT_ESCAPE,
        contradiction_threshold=STRICT_CONTRADICTION_THRESHOLD,
    )
    escape_counts = escape_relevant_deficit_counts(
        N,
        relevant_deficit_count=STRICT_MINIMAL_RELEVANT_ESCAPE,
        contradiction_threshold=STRICT_CONTRADICTION_THRESHOLD,
    )
    return {
        "contradiction_threshold": STRICT_CONTRADICTION_THRESHOLD,
        "strict_minimal_relevant_escape": STRICT_MINIMAL_RELEVANT_ESCAPE,
        "total_relevant_placement_count": escape_counts[
            "total_relevant_placement_count"
        ],
        "labelled_escape_placement_count": len(placements),
        "dihedral_escape_class_count": len(classes),
        "dihedral_escape_orbit_size_counts": json_counter(
            Counter(row.placement_count for row in classes)
        ),
        "remaining_minimum_forced_turn_count": escape_counts[
            "remaining_minimum_forced_turn_count"
        ],
    }


def low_excess_escape_ladder_report() -> dict[str, object]:
    """Return the generated low-excess minimal escape-slice ladder report."""

    slack = base_apex_slack(N, WITNESS_SIZE)
    escape = minimum_capacity_deficit_to_escape_turn_cover(
        N,
        contradiction_threshold=STRICT_CONTRADICTION_THRESHOLD,
    )
    if escape.minimum_capacity_deficit != STRICT_MINIMAL_RELEVANT_ESCAPE:
        raise AssertionError("strict minimum relevant escape count changed")

    placements = escape_placements()
    payload = {
        "schema": "erdos97.n9_base_apex_low_excess_escape_ladder.v1",
        "status": "EXPLORATORY_LEDGER_ONLY",
        "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
        "claim_scope": (
            "Focused n=9 base-apex low-excess minimal escape-slice ladder "
            "bookkeeping; not a proof of n=9, not a counterexample, not a "
            "geometric realizability test, and not a global status update."
        ),
        "n": N,
        "witness_size": WITNESS_SIZE,
        "base_apex_slack": slack,
        "total_profile_excess_range": [0, MAX_TOTAL_PROFILE_EXCESS],
        "capacity_deficit_relation": "D = 9 - E",
        "contradiction_threshold": STRICT_CONTRADICTION_THRESHOLD,
        "strict_minimal_relevant_escape": STRICT_MINIMAL_RELEVANT_ESCAPE,
        "source_artifacts": {
            "low_excess_ledgers": "data/certificates/n9_base_apex_low_excess_ledgers.json",
            "escape_budget": "data/certificates/n9_base_apex_escape_budget_report.json",
            "d3_escape_slice": "data/certificates/n9_base_apex_d3_escape_slice.json",
        },
        "strict_escape_slice": strict_escape_summary(placements),
        "ladder_rows": [
            profile_ladder_row(total_profile_excess, placements)
            for total_profile_excess in range(MAX_TOTAL_PROFILE_EXCESS + 1)
        ],
        "interpretation": [
            "The ladder covers E=0..6, so D=9-E ranges from 9 down to 3.",
            "Every row uses the strict turn-cover threshold and the minimum relevant escape count r=3.",
            "Unassigned capacity is D-r and is not placed on side or length-4 bases by this report.",
            "The coupled counts quotient profile labels and r=3 escape placements by the same dihedral action.",
            "No individual coupled classes are emitted in this summary-only artifact.",
            "No proof of the n=9 case is claimed.",
        ],
        "provenance": {
            "generator": "scripts/analyze_n9_base_apex_low_excess_escape_ladder.py",
            "command": (
                "python scripts/analyze_n9_base_apex_low_excess_escape_ladder.py "
                "--assert-expected --out "
                "data/certificates/n9_base_apex_low_excess_escape_ladder.json"
            ),
        },
    }
    assert_expected_ladder_counts(payload)
    return payload


def assert_expected_ladder_counts(payload: dict[str, object]) -> None:
    """Assert stable expected counts for the low-excess escape ladder."""

    if payload.get("schema") != "erdos97.n9_base_apex_low_excess_escape_ladder.v1":
        raise AssertionError("unexpected schema")
    if payload.get("status") != "EXPLORATORY_LEDGER_ONLY":
        raise AssertionError("unexpected status")
    if payload.get("trust") != "FINITE_BOOKKEEPING_NOT_A_PROOF":
        raise AssertionError("unexpected trust label")
    if payload.get("n") != N or payload.get("witness_size") != WITNESS_SIZE:
        raise AssertionError("unexpected n or witness_size")
    if payload.get("base_apex_slack") != base_apex_slack(N, WITNESS_SIZE):
        raise AssertionError("unexpected base-apex slack")

    escape = payload.get("strict_escape_slice")
    if not isinstance(escape, dict):
        raise AssertionError("missing strict escape slice")
    expected_escape = {
        "contradiction_threshold": STRICT_CONTRADICTION_THRESHOLD,
        "strict_minimal_relevant_escape": STRICT_MINIMAL_RELEVANT_ESCAPE,
        "total_relevant_placement_count": EXPECTED_ESCAPE_RELEVANT_COUNTS[
            "total_relevant_placement_count"
        ],
        "labelled_escape_placement_count": EXPECTED_ESCAPE_LABELLED_PLACEMENT_COUNT,
        "dihedral_escape_class_count": EXPECTED_ESCAPE_DIHEDRAL_CLASS_COUNT,
        "dihedral_escape_orbit_size_counts": json_counter(
            Counter(EXPECTED_ESCAPE_ORBIT_SIZE_COUNTS)
        ),
        "remaining_minimum_forced_turn_count": EXPECTED_ESCAPE_RELEVANT_COUNTS[
            "remaining_minimum_forced_turn_count"
        ],
    }
    if escape != expected_escape:
        raise AssertionError("unexpected strict escape slice")

    rows = payload.get("ladder_rows")
    if not isinstance(rows, list):
        raise AssertionError("missing ladder rows")
    expected_rows = []
    for total_profile_excess, expected in EXPECTED_LADDER_ROWS.items():
        row = {"total_profile_excess": total_profile_excess}
        row["strict_minimal_relevant_escape"] = STRICT_MINIMAL_RELEVANT_ESCAPE
        row.update(expected)
        expected_rows.append(row)
    if rows != expected_rows:
        raise AssertionError("unexpected ladder row counts")
