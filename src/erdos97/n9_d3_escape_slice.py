"""Coupled D=3 escape slice for the n=9 base-apex ledger.

This module is finite diagnostic bookkeeping. It couples the sharp strict
turn-cover escape budget ``D=3, r=3`` with the labelled profile-excess
placements of total excess ``E=6``. It does not prove the n=9 case and does
not claim a counterexample.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations

from erdos97.n9_base_apex import (
    canonical_deficit_placement,
    profile_excess_values,
    transform_base_index,
    turn_cover_diagnostic,
)

N = 9
WITNESS_SIZE = 4
TOTAL_PROFILE_EXCESS = 6
CAPACITY_DEFICIT = 3
RELEVANT_DEFICIT_COUNT = 3
CONTRADICTION_THRESHOLD = 3

EXPECTED_PROFILE_SEQUENCE_COUNT = 3003
EXPECTED_PROFILE_DIHEDRAL_ORBIT_COUNT = 185
EXPECTED_PROFILE_ORBIT_SIZE_COUNTS = {3: 2, 9: 33, 18: 150}
EXPECTED_ESCAPE_PLACEMENT_COUNT = 108
EXPECTED_ESCAPE_DIHEDRAL_CLASS_COUNT = 8
EXPECTED_ESCAPE_ORBIT_SIZE_COUNTS = {9: 4, 18: 4}
EXPECTED_LABELLED_COUPLED_PAIR_COUNT = 324_324
EXPECTED_COMMON_DIHEDRAL_PAIR_CLASS_COUNT = 18_088
EXPECTED_COMMON_DIHEDRAL_ORBIT_SIZE_COUNTS = {9: 140, 18: 17_948}


ProfileSequence = tuple[int, ...]
EscapePlacement = tuple[tuple[int, ...], tuple[int, ...]]
CoupledKey = tuple[ProfileSequence, EscapePlacement]


def json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    """Return a sorted counter with JSON string keys."""

    return {str(key): int(counter[key]) for key in sorted(counter)}


def profile_sequences(
    total_profile_excess: int = TOTAL_PROFILE_EXCESS,
) -> list[ProfileSequence]:
    """Return labelled profile-excess sequences with the requested total."""

    values = [
        value
        for value in profile_excess_values(N, WITNESS_SIZE)
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
    return sorted(out)


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


def canonical_profile_sequence(sequence: ProfileSequence) -> ProfileSequence:
    """Return the dihedral-canonical labelled profile sequence."""

    return min(
        transform_profile_sequence(sequence, rotation=rotation, reflected=reflected)
        for rotation in range(N)
        for reflected in (False, True)
    )


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
                    N,
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
                    N,
                    index,
                    3,
                    rotation=rotation,
                    reflected=reflected,
                )
                for index in spoiled3
            )
        ),
    )


def escape_placements() -> list[EscapePlacement]:
    """Return labelled strict-threshold r=3 placements escaping turn cover."""

    placements: list[EscapePlacement] = []
    for count2 in range(RELEVANT_DEFICIT_COUNT + 1):
        count3 = RELEVANT_DEFICIT_COUNT - count2
        for spoiled2 in combinations(range(N), count2):
            for spoiled3 in combinations(range(N), count3):
                diagnostic = turn_cover_diagnostic(
                    spoiled_length2=spoiled2,
                    spoiled_length3=spoiled3,
                    contradiction_threshold=CONTRADICTION_THRESHOLD,
                )
                if not diagnostic.forces_turn_contradiction:
                    placements.append((tuple(spoiled2), tuple(spoiled3)))
    return sorted(placements)


def placement_payload(placement: EscapePlacement) -> dict[str, list[int]]:
    """Return a JSON-shaped escape placement."""

    spoiled2, spoiled3 = placement
    return {
        "spoiled_length2": [int(value) for value in spoiled2],
        "spoiled_length3": [int(value) for value in spoiled3],
    }


def canonical_coupled_pair(
    profile: ProfileSequence,
    placement: EscapePlacement,
) -> CoupledKey:
    """Return the common-dihedral canonical profile/escape pair."""

    return min(
        (
            transform_profile_sequence(
                profile,
                rotation=rotation,
                reflected=reflected,
            ),
            transform_escape_placement(
                placement,
                rotation=rotation,
                reflected=reflected,
            ),
        )
        for rotation in range(N)
        for reflected in (False, True)
    )


def profile_sequence_summary(sequences: list[ProfileSequence]) -> dict[str, object]:
    """Return labelled and dihedral profile-placement counts."""

    multiset_counts = Counter(tuple(sorted(sequence)) for sequence in sequences)
    orbit_members: defaultdict[ProfileSequence, list[ProfileSequence]] = defaultdict(list)
    for sequence in sequences:
        orbit_members[canonical_profile_sequence(sequence)].append(sequence)
    return {
        "total_profile_excess": TOTAL_PROFILE_EXCESS,
        "capacity_deficit": CAPACITY_DEFICIT,
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


def escape_placement_summary(placements: list[EscapePlacement]) -> dict[str, object]:
    """Return labelled and dihedral escape-placement counts."""

    orbit_members: defaultdict[EscapePlacement, list[EscapePlacement]] = defaultdict(list)
    for placement in placements:
        orbit_members[
            canonical_deficit_placement(N, placement[0], placement[1])
        ].append(placement)
    return {
        "contradiction_threshold": CONTRADICTION_THRESHOLD,
        "relevant_deficit_count": RELEVANT_DEFICIT_COUNT,
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
            for placement in sorted(
                orbit_members,
                key=lambda item: (len(item[0]), item),
            )
        ],
    }


def coupled_slice_summary(
    sequences: list[ProfileSequence],
    placements: list[EscapePlacement],
) -> dict[str, object]:
    """Return common-dihedral coupled profile/escape summary counts."""

    class_sizes: Counter[CoupledKey] = Counter()
    for sequence in sequences:
        for placement in placements:
            class_sizes[canonical_coupled_pair(sequence, placement)] += 1

    by_profile_multiset: Counter[tuple[int, ...]] = Counter()
    by_escape_class: Counter[EscapePlacement] = Counter()
    by_profile_and_escape: Counter[tuple[tuple[int, ...], EscapePlacement]] = Counter()
    for profile, placement in class_sizes:
        profile_multiset = tuple(sorted(profile))
        escape_class = canonical_deficit_placement(N, placement[0], placement[1])
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
                key=lambda item: (len(item[0][0]), item[0]),
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
                key=lambda item: (item[0][0], len(item[0][1][0]), item[0][1]),
            )
        ],
    }


def d3_escape_slice_report() -> dict[str, object]:
    """Return the generated D=3 coupled escape-slice report."""

    sequences = profile_sequences()
    placements = escape_placements()
    payload = {
        "schema": "erdos97.n9_base_apex_d3_escape_slice.v1",
        "status": "EXPLORATORY_LEDGER_ONLY",
        "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
        "claim_scope": (
            "Focused n=9 base-apex D=3,r=3 coupled escape-slice bookkeeping; "
            "not a proof of n=9, not a counterexample, not a geometric "
            "realizability test, and not a global status update."
        ),
        "n": N,
        "witness_size": WITNESS_SIZE,
        "total_profile_excess": TOTAL_PROFILE_EXCESS,
        "capacity_deficit": CAPACITY_DEFICIT,
        "relevant_deficit_count": RELEVANT_DEFICIT_COUNT,
        "source_artifacts": {
            "low_excess_ledgers": "data/certificates/n9_base_apex_low_excess_ledgers.json",
            "escape_budget": "data/certificates/n9_base_apex_escape_budget_report.json",
            "selected_baseline_overlay": (
                "data/certificates/n9_selected_baseline_escape_budget_overlay.json"
            ),
        },
        "profile_slice": profile_sequence_summary(sequences),
        "escape_slice": escape_placement_summary(placements),
        "coupled_slice": coupled_slice_summary(sequences, placements),
        "interpretation": [
            "This is the sharp strict-threshold D=3 slice where no leftover budget remains after the minimum relevant escape.",
            "Profile-excess sequences record labelled vertex excesses only, not actual geometric distance-class realizations.",
            "Escape placements record length-2/length-3 deficits in the current turn-cover diagnostic only.",
            "Common-dihedral pair classes couple those two labelled structures under the same cyclic relabeling action.",
            "No proof of the n=9 case is claimed.",
        ],
        "provenance": {
            "generator": "scripts/analyze_n9_d3_escape_slice.py",
            "command": (
                "python scripts/analyze_n9_d3_escape_slice.py --assert-expected "
                "--out data/certificates/n9_base_apex_d3_escape_slice.json"
            ),
        },
    }
    assert_expected_counts(payload)
    return payload


def assert_expected_counts(payload: dict[str, object]) -> None:
    """Assert stable expected counts for the D=3 escape-slice report."""

    profile = payload["profile_slice"]
    escape = payload["escape_slice"]
    coupled = payload["coupled_slice"]
    if not isinstance(profile, dict) or not isinstance(escape, dict):
        raise AssertionError("missing profile or escape slice")
    if not isinstance(coupled, dict):
        raise AssertionError("missing coupled slice")
    if profile["labelled_profile_sequence_count"] != EXPECTED_PROFILE_SEQUENCE_COUNT:
        raise AssertionError("unexpected profile sequence count")
    if profile["dihedral_profile_orbit_count"] != EXPECTED_PROFILE_DIHEDRAL_ORBIT_COUNT:
        raise AssertionError("unexpected profile orbit count")
    if profile["dihedral_profile_orbit_size_counts"] != json_counter(
        Counter(EXPECTED_PROFILE_ORBIT_SIZE_COUNTS)
    ):
        raise AssertionError("unexpected profile orbit size counts")
    if escape["labelled_escape_placement_count"] != EXPECTED_ESCAPE_PLACEMENT_COUNT:
        raise AssertionError("unexpected escape placement count")
    if escape["dihedral_escape_class_count"] != EXPECTED_ESCAPE_DIHEDRAL_CLASS_COUNT:
        raise AssertionError("unexpected escape class count")
    if escape["dihedral_escape_orbit_size_counts"] != json_counter(
        Counter(EXPECTED_ESCAPE_ORBIT_SIZE_COUNTS)
    ):
        raise AssertionError("unexpected escape orbit size counts")
    if (
        coupled["labelled_profile_escape_pair_count"]
        != EXPECTED_LABELLED_COUPLED_PAIR_COUNT
    ):
        raise AssertionError("unexpected labelled coupled pair count")
    if (
        coupled["common_dihedral_pair_class_count"]
        != EXPECTED_COMMON_DIHEDRAL_PAIR_CLASS_COUNT
    ):
        raise AssertionError("unexpected common-dihedral class count")
    if coupled["common_dihedral_pair_orbit_size_counts"] != json_counter(
        Counter(EXPECTED_COMMON_DIHEDRAL_ORBIT_SIZE_COUNTS)
    ):
        raise AssertionError("unexpected common-dihedral orbit size counts")
