"""Exploratory n=9 base-apex slack ledger.

This module is finite bookkeeping for research planning. It separates
per-vertex distance-profile excess from unused base-apex capacity. It does not
claim a proof of the n=9 case.
"""

from __future__ import annotations

import itertools
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable


@dataclass(frozen=True)
class DistanceProfile:
    """One partition of the other vertices at a center."""

    parts: tuple[int, ...]
    isosceles_pairs: int
    excess: int


@dataclass(frozen=True)
class ExcessDistribution:
    """One sorted distribution of profile excess across all vertices."""

    excesses: tuple[int, ...]
    total_profile_excess: int
    capacity_deficit: int


@dataclass(frozen=True)
class CyclicBaseFamily:
    """A cyclic base family, grouped by shorter cyclic length."""

    cyclic_length: int
    base_count: int
    capacity_per_base: int
    total_capacity: int


@dataclass(frozen=True)
class TurnCoverDiagnostic:
    """Turn-cover clauses forced by saturated length-2 and length-3 diagonals."""

    n: int
    saturated_length2: tuple[int, ...]
    saturated_length3: tuple[int, ...]
    turn_clauses: tuple[tuple[int, int], ...]
    minimum_forced_turns: int
    contradiction_threshold: int
    forces_turn_contradiction: bool


@dataclass(frozen=True)
class TurnCoverEscape:
    """Smallest length-2/length-3 capacity deficit escaping the diagnostic."""

    n: int
    contradiction_threshold: int
    minimum_capacity_deficit: int
    spoiled_length2: tuple[int, ...]
    spoiled_length3: tuple[int, ...]
    remaining_turn_clauses: tuple[tuple[int, int], ...]
    remaining_minimum_forced_turns: int


@dataclass(frozen=True)
class ProfileLedgerCase:
    """One profile-excess distribution decorated with turn-cover status."""

    excesses: tuple[int, ...]
    total_profile_excess: int
    capacity_deficit: int
    forced_by_turn_cover: bool
    profile_multiset: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class ProfileAssumptionSummary:
    """Effect of allowing only a selected set of profile-excess values."""

    allowed_excesses: tuple[int, ...]
    distribution_count: int
    forced_by_turn_cover_count: int
    unresolved_by_turn_cover_count: int
    minimum_total_profile_excess: int | None
    maximum_total_profile_excess: int | None


@dataclass(frozen=True)
class DeficitPlacementClass:
    """One dihedral class of relevant length-2/length-3 saturation failures."""

    n: int
    relevant_deficit_count: int
    contradiction_threshold: int
    spoiled_length2: tuple[int, ...]
    spoiled_length3: tuple[int, ...]
    placement_count: int
    remaining_minimum_forced_turns: int
    remaining_turn_clause_count: int


def binom2(value: int) -> int:
    """Return ``binom(value, 2)`` for a nonnegative integer."""

    if value < 0:
        raise ValueError(f"value must be nonnegative, got {value}")
    return value * (value - 1) // 2


def integer_partitions(total: int, minimum: int = 1) -> Iterable[tuple[int, ...]]:
    """Yield nondecreasing positive integer partitions of ``total``."""

    if total < 0:
        raise ValueError(f"total must be nonnegative, got {total}")
    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for rest in integer_partitions(total - first, first):
            yield (first, *rest)


def distance_profiles(n: int = 9, witness_size: int = 4) -> list[DistanceProfile]:
    """Return possible bad-vertex profiles for an ``n``-gon.

    Profiles are nondecreasing partitions of the other ``n - 1`` vertices with
    at least one distance class of size ``witness_size`` or larger.
    """

    if n <= witness_size:
        raise ValueError(f"n must exceed witness_size, got n={n}")
    baseline = binom2(witness_size)
    profiles = []
    for ascending_parts in integer_partitions(n - 1):
        parts = tuple(reversed(ascending_parts))
        if max(parts, default=0) < witness_size:
            continue
        pairs = sum(binom2(part) for part in parts)
        profiles.append(
            DistanceProfile(
                parts=parts,
                isosceles_pairs=pairs,
                excess=pairs - baseline,
            )
        )
    return sorted(profiles, key=lambda profile: (profile.excess, profile.parts))


def profiles_by_excess(n: int = 9, witness_size: int = 4) -> dict[int, list[tuple[int, ...]]]:
    """Group possible profiles by profile excess."""

    grouped: dict[int, list[tuple[int, ...]]] = {}
    for profile in distance_profiles(n, witness_size):
        grouped.setdefault(profile.excess, []).append(profile.parts)
    return grouped


def profile_excess_values(n: int = 9, witness_size: int = 4) -> tuple[int, ...]:
    """Return the sorted excess values available to a bad vertex."""

    return tuple(sorted(profiles_by_excess(n, witness_size)))


def base_apex_slack(n: int, witness_size: int = 4) -> int:
    """Return the upper-minus-baseline base-apex slack."""

    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    return n * (n - 2) - binom2(witness_size) * n


def excess_distributions(
    n: int = 9,
    witness_size: int = 4,
    *,
    total_excess_limit: int | None = None,
) -> list[ExcessDistribution]:
    """Return sorted profile-excess distributions within the slack budget.

    The distributions are unlabeled: ``(0,1,2)`` and ``(2,1,0)`` are the same
    record. Each record carries the remaining base-apex capacity deficit.
    """

    slack = base_apex_slack(n, witness_size)
    if total_excess_limit is None:
        total_excess_limit = slack
    if total_excess_limit < 0:
        raise ValueError(f"total_excess_limit must be nonnegative, got {total_excess_limit}")
    limit = min(slack, total_excess_limit)
    values = [value for value in profile_excess_values(n, witness_size) if value <= limit]
    out: list[ExcessDistribution] = []

    def search(start_index: int, slots_left: int, remaining: int, current: list[int]) -> None:
        if slots_left == 0:
            total = sum(current)
            out.append(
                ExcessDistribution(
                    excesses=tuple(current),
                    total_profile_excess=total,
                    capacity_deficit=slack - total,
                )
            )
            return
        for index in range(start_index, len(values)):
            value = values[index]
            if value > remaining:
                break
            current.append(value)
            search(index, slots_left - 1, remaining - value, current)
            current.pop()

    search(0, n, limit, [])
    return sorted(out, key=lambda row: (row.total_profile_excess, row.excesses))


def cyclic_base_families(n: int = 9) -> list[CyclicBaseFamily]:
    """Return cyclic base families by shorter cyclic length."""

    if n < 3:
        raise ValueError(f"n must be at least 3, got {n}")
    families = []
    for cyclic_length in range(1, n // 2 + 1):
        base_count = n if cyclic_length * 2 != n else n // 2
        capacity_per_base = 1 if cyclic_length == 1 else 2
        families.append(
            CyclicBaseFamily(
                cyclic_length=cyclic_length,
                base_count=base_count,
                capacity_per_base=capacity_per_base,
                total_capacity=base_count * capacity_per_base,
            )
        )
    return families


def guaranteed_full_bases(
    n: int = 9,
    capacity_deficit: int = 0,
    cyclic_length: int = 2,
) -> int:
    """Conservative lower bound on fully saturated bases in one cyclic family.

    A single missing apex can spoil full saturation of one base. With no
    geometric information about where deficits land, this is the only
    unconditional family-level guarantee.
    """

    if capacity_deficit < 0:
        raise ValueError(f"capacity_deficit must be nonnegative, got {capacity_deficit}")
    family = next(
        (
            candidate
            for candidate in cyclic_base_families(n)
            if candidate.cyclic_length == cyclic_length
        ),
        None,
    )
    if family is None:
        raise ValueError(f"cyclic_length {cyclic_length} is not available for n={n}")
    return max(0, family.base_count - capacity_deficit)


def turn_clauses_from_saturation(
    n: int = 9,
    saturated_length2: Iterable[int] | None = None,
    saturated_length3: Iterable[int] | None = None,
) -> tuple[tuple[int, int], ...]:
    """Return turn clauses forced by saturated length-2/length-3 diagonals.

    The length-2 diagonal with index ``i`` is the base ``{v_i, v_{i+2}}``.
    Its saturation forces ``|v_i v_{i+1}| = |v_{i+1} v_{i+2}|``.

    The length-3 diagonal with index ``i`` is the base ``{v_i, v_{i+3}}``.
    If it is saturated, the short-side apex is either ``v_{i+1}`` or
    ``v_{i+2}``. When the adjacent length-2 diagonals ``i`` and ``i+1`` are
    also saturated, this forces at least one of the turns ``i+1`` or ``i+2``
    to equal ``2*pi/3``.
    """

    if n < 4:
        raise ValueError(f"n must be at least 4, got {n}")
    if saturated_length2 is None:
        saturated_length2_set = set(range(n))
    else:
        saturated_length2_set = {idx % n for idx in saturated_length2}
    if saturated_length3 is None:
        saturated_length3_set = set(range(n))
    else:
        saturated_length3_set = {idx % n for idx in saturated_length3}

    clauses = []
    for idx in range(n):
        if (
            idx in saturated_length3_set
            and idx in saturated_length2_set
            and (idx + 1) % n in saturated_length2_set
        ):
            clauses.append(((idx + 1) % n, (idx + 2) % n))
    return tuple(clauses)


def minimum_turn_hitting_set_size(
    n: int,
    clauses: Iterable[tuple[int, int]],
) -> int:
    """Return the minimum number of turns hitting all two-turn clauses."""

    clause_tuple = tuple(clauses)
    if not clause_tuple:
        return 0
    for size in range(n + 1):
        for selected in itertools.combinations(range(n), size):
            selected_set = set(selected)
            if all(a in selected_set or b in selected_set for a, b in clause_tuple):
                return size
    raise RuntimeError("no hitting set found")


def turn_cover_diagnostic(
    n: int = 9,
    *,
    spoiled_length2: Iterable[int] = (),
    spoiled_length3: Iterable[int] = (),
    contradiction_threshold: int = 3,
) -> TurnCoverDiagnostic:
    """Return the turn-cover diagnostic after spoiling selected bases.

    ``contradiction_threshold=3`` uses strict positivity of all other exterior
    turns: three turns of size ``2*pi/3`` already exhaust the total turn budget.
    ``contradiction_threshold=4`` is the more conservative "forced turns alone
    exceed ``2*pi``" threshold used in the octagon proof note.
    """

    if contradiction_threshold <= 0:
        raise ValueError(
            f"contradiction_threshold must be positive, got {contradiction_threshold}"
        )
    all_indices = set(range(n))
    saturated_length2 = tuple(sorted(all_indices - {idx % n for idx in spoiled_length2}))
    saturated_length3 = tuple(sorted(all_indices - {idx % n for idx in spoiled_length3}))
    clauses = turn_clauses_from_saturation(n, saturated_length2, saturated_length3)
    minimum_forced_turns = minimum_turn_hitting_set_size(n, clauses)
    return TurnCoverDiagnostic(
        n=n,
        saturated_length2=saturated_length2,
        saturated_length3=saturated_length3,
        turn_clauses=clauses,
        minimum_forced_turns=minimum_forced_turns,
        contradiction_threshold=contradiction_threshold,
        forces_turn_contradiction=minimum_forced_turns >= contradiction_threshold,
    )


@lru_cache(maxsize=None)
def minimum_capacity_deficit_to_escape_turn_cover(
    n: int = 9,
    *,
    contradiction_threshold: int = 3,
) -> TurnCoverEscape:
    """Find the smallest length-2/length-3 deficit escaping turn-cover closure."""

    if n > 12:
        raise ValueError("brute-force escape search is intended for n <= 12")
    masks_by_size: dict[int, list[tuple[int, ...]]] = {size: [] for size in range(n + 1)}
    for mask in range(1 << n):
        spoiled = tuple(idx for idx in range(n) if (mask >> idx) & 1)
        masks_by_size[len(spoiled)].append(spoiled)

    for cost in range(2 * n + 1):
        for cost2 in range(max(0, cost - n), min(n, cost) + 1):
            cost3 = cost - cost2
            for spoiled2 in masks_by_size[cost2]:
                for spoiled3 in masks_by_size[cost3]:
                    diagnostic = turn_cover_diagnostic(
                        n,
                        spoiled_length2=spoiled2,
                        spoiled_length3=spoiled3,
                        contradiction_threshold=contradiction_threshold,
                    )
                    if not diagnostic.forces_turn_contradiction:
                        return TurnCoverEscape(
                            n=n,
                            contradiction_threshold=contradiction_threshold,
                            minimum_capacity_deficit=cost,
                            spoiled_length2=spoiled2,
                            spoiled_length3=spoiled3,
                            remaining_turn_clauses=diagnostic.turn_clauses,
                            remaining_minimum_forced_turns=diagnostic.minimum_forced_turns,
                        )
    raise RuntimeError("no escaping deficit pattern found")


def capacity_deficit_forces_turn_cover(
    capacity_deficit: int,
    n: int = 9,
    *,
    contradiction_threshold: int = 3,
) -> bool:
    """Return whether any placement of this deficit still forces turn closure."""

    if capacity_deficit < 0:
        raise ValueError(f"capacity_deficit must be nonnegative, got {capacity_deficit}")
    escape = minimum_capacity_deficit_to_escape_turn_cover(
        n,
        contradiction_threshold=contradiction_threshold,
    )
    return capacity_deficit < escape.minimum_capacity_deficit


def transform_base_index(
    n: int,
    index: int,
    cyclic_length: int,
    *,
    rotation: int = 0,
    reflected: bool = False,
) -> int:
    """Transform a cyclic base index under a dihedral relabeling.

    The base indexed by ``i`` and cyclic length ``k`` is ``{v_i, v_{i+k}}``.
    A reflection sends it to the base indexed by ``rotation - i - k``.
    """

    if reflected:
        return (rotation - index - cyclic_length) % n
    return (index + rotation) % n


def canonical_deficit_placement(
    n: int,
    spoiled_length2: Iterable[int],
    spoiled_length3: Iterable[int],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return a dihedral canonical key for spoiled length-2/length-3 bases."""

    spoiled2 = tuple(spoiled_length2)
    spoiled3 = tuple(spoiled_length3)
    keys = []
    for rotation in range(n):
        for reflected in (False, True):
            keys.append(
                (
                    tuple(
                        sorted(
                            transform_base_index(
                                n,
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
                                n,
                                index,
                                3,
                                rotation=rotation,
                                reflected=reflected,
                            )
                            for index in spoiled3
                        )
                    ),
                )
            )
    return min(keys)


def deficit_placement_classes(
    n: int = 9,
    *,
    relevant_deficit_count: int | None = None,
    contradiction_threshold: int = 3,
    escaping_only: bool = True,
) -> list[DeficitPlacementClass]:
    """Return dihedral classes of length-2/length-3 deficit placements."""

    if relevant_deficit_count is None:
        relevant_deficit_count = minimum_capacity_deficit_to_escape_turn_cover(
            n,
            contradiction_threshold=contradiction_threshold,
        ).minimum_capacity_deficit
    if relevant_deficit_count < 0:
        raise ValueError(
            f"relevant_deficit_count must be nonnegative, got {relevant_deficit_count}"
        )
    grouped: Counter[tuple[tuple[int, ...], tuple[int, ...]]] = Counter()
    for count2 in range(max(0, relevant_deficit_count - n), min(n, relevant_deficit_count) + 1):
        count3 = relevant_deficit_count - count2
        for spoiled2 in itertools.combinations(range(n), count2):
            for spoiled3 in itertools.combinations(range(n), count3):
                diagnostic = turn_cover_diagnostic(
                    n,
                    spoiled_length2=spoiled2,
                    spoiled_length3=spoiled3,
                    contradiction_threshold=contradiction_threshold,
                )
                if escaping_only and diagnostic.forces_turn_contradiction:
                    continue
                if not escaping_only and not diagnostic.forces_turn_contradiction:
                    continue
                grouped[canonical_deficit_placement(n, spoiled2, spoiled3)] += 1

    out = []
    for (spoiled2, spoiled3), placement_count in grouped.items():
        diagnostic = turn_cover_diagnostic(
            n,
            spoiled_length2=spoiled2,
            spoiled_length3=spoiled3,
            contradiction_threshold=contradiction_threshold,
        )
        out.append(
            DeficitPlacementClass(
                n=n,
                relevant_deficit_count=relevant_deficit_count,
                contradiction_threshold=contradiction_threshold,
                spoiled_length2=spoiled2,
                spoiled_length3=spoiled3,
                placement_count=placement_count,
                remaining_minimum_forced_turns=diagnostic.minimum_forced_turns,
                remaining_turn_clause_count=len(diagnostic.turn_clauses),
            )
        )
    return sorted(
        out,
        key=lambda row: (
            len(row.spoiled_length2),
            row.spoiled_length2,
            row.spoiled_length3,
        ),
    )


def minimum_escape_motif_summary(
    n: int = 9,
    *,
    contradiction_threshold: int = 3,
) -> dict[str, object]:
    """Summarize minimum relevant-deficit motifs escaping turn cover."""

    classes = deficit_placement_classes(
        n,
        contradiction_threshold=contradiction_threshold,
    )
    relevant_deficit_count = (
        classes[0].relevant_deficit_count
        if classes
        else minimum_capacity_deficit_to_escape_turn_cover(
            n,
            contradiction_threshold=contradiction_threshold,
        ).minimum_capacity_deficit
    )
    return {
        "contradiction_threshold": contradiction_threshold,
        "relevant_deficit_count": relevant_deficit_count,
        "raw_escaping_placement_count": sum(row.placement_count for row in classes),
        "dihedral_class_count": len(classes),
        "classes": [
            {
                "spoiled_length2": list(row.spoiled_length2),
                "spoiled_length3": list(row.spoiled_length3),
                "placement_count": row.placement_count,
                "remaining_minimum_forced_turns": row.remaining_minimum_forced_turns,
                "remaining_turn_clause_count": row.remaining_turn_clause_count,
            }
            for row in classes
        ],
    }


def turn_cover_distribution_summary(
    n: int = 9,
    witness_size: int = 4,
    *,
    contradiction_threshold: int = 3,
) -> dict[str, object]:
    """Summarize which excess distributions are closed by turn-cover alone."""

    distributions = excess_distributions(n, witness_size)
    escape = minimum_capacity_deficit_to_escape_turn_cover(
        n,
        contradiction_threshold=contradiction_threshold,
    )
    forced = [
        row
        for row in distributions
        if row.capacity_deficit < escape.minimum_capacity_deficit
    ]
    deficit_counts = Counter(row.capacity_deficit for row in distributions)
    return {
        "contradiction_threshold": contradiction_threshold,
        "minimum_capacity_deficit_to_escape": escape.minimum_capacity_deficit,
        "distribution_count": len(distributions),
        "forced_by_turn_cover_count": len(forced),
        "unresolved_by_turn_cover_count": len(distributions) - len(forced),
        "capacity_deficit_counts": {
            str(deficit): deficit_counts[deficit]
            for deficit in sorted(deficit_counts)
        },
    }


def _canonical_profile_for_excess(
    n: int = 9,
    witness_size: int = 4,
) -> dict[int, tuple[int, ...]]:
    """Return the unique profile for each n=9 excess value.

    The current n=9 table has one profile per excess. If a future ``n`` has
    collisions, this helper intentionally fails so callers do not silently pick
    an arbitrary profile.
    """

    grouped = profiles_by_excess(n, witness_size)
    ambiguous = {excess: profiles for excess, profiles in grouped.items() if len(profiles) != 1}
    if ambiguous:
        raise ValueError(f"profile excess is not unique for this n: {ambiguous}")
    return {excess: profiles[0] for excess, profiles in grouped.items()}


def profile_ledger_cases(
    n: int = 9,
    witness_size: int = 4,
    *,
    contradiction_threshold: int = 3,
    forced_by_turn_cover: bool | None = None,
) -> list[ProfileLedgerCase]:
    """Return profile-excess ledgers decorated by turn-cover status."""

    profile_by_excess = _canonical_profile_for_excess(n, witness_size)
    cases = []
    for row in excess_distributions(n, witness_size):
        forced = capacity_deficit_forces_turn_cover(
            row.capacity_deficit,
            n,
            contradiction_threshold=contradiction_threshold,
        )
        if forced_by_turn_cover is not None and forced != forced_by_turn_cover:
            continue
        cases.append(
            ProfileLedgerCase(
                excesses=row.excesses,
                total_profile_excess=row.total_profile_excess,
                capacity_deficit=row.capacity_deficit,
                forced_by_turn_cover=forced,
                profile_multiset=tuple(profile_by_excess[value] for value in row.excesses),
            )
        )
    return cases


def profile_assumption_summary(
    allowed_excesses: Iterable[int],
    n: int = 9,
    witness_size: int = 4,
    *,
    contradiction_threshold: int = 3,
) -> ProfileAssumptionSummary:
    """Summarize turn-cover closure under a profile-excess restriction."""

    allowed = tuple(sorted(set(allowed_excesses)))
    cases = [
        case
        for case in profile_ledger_cases(
            n,
            witness_size,
            contradiction_threshold=contradiction_threshold,
        )
        if set(case.excesses).issubset(allowed)
    ]
    forced_count = sum(1 for case in cases if case.forced_by_turn_cover)
    totals = [case.total_profile_excess for case in cases]
    return ProfileAssumptionSummary(
        allowed_excesses=allowed,
        distribution_count=len(cases),
        forced_by_turn_cover_count=forced_count,
        unresolved_by_turn_cover_count=len(cases) - forced_count,
        minimum_total_profile_excess=min(totals) if totals else None,
        maximum_total_profile_excess=max(totals) if totals else None,
    )


def profile_assumption_summaries(
    n: int = 9,
    witness_size: int = 4,
    *,
    contradiction_threshold: int = 3,
) -> list[ProfileAssumptionSummary]:
    """Return standard summaries for increasingly permissive profile assumptions."""

    return [
        profile_assumption_summary(
            allowed,
            n,
            witness_size,
            contradiction_threshold=contradiction_threshold,
        )
        for allowed in [
            (0, 1),
            (0, 1, 2),
            (0, 1, 2, 3),
            (0, 1, 2, 3, 4, 5, 6),
        ]
    ]


def ledger_summary(n: int = 9, witness_size: int = 4) -> dict[str, object]:
    """Return a JSON-serializable summary of the n=9 slack ledger."""

    profiles = distance_profiles(n, witness_size)
    grouped = profiles_by_excess(n, witness_size)
    distributions = excess_distributions(n, witness_size)
    strict_escape = minimum_capacity_deficit_to_escape_turn_cover(
        n,
        contradiction_threshold=3,
    )
    conservative_escape = minimum_capacity_deficit_to_escape_turn_cover(
        n,
        contradiction_threshold=4,
    )
    return {
        "n": n,
        "status": "EXPLORATORY_LEDGER_ONLY",
        "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
        "witness_size": witness_size,
        "base_apex_slack": base_apex_slack(n, witness_size),
        "profile_count": len(profiles),
        "profile_excess_values": list(profile_excess_values(n, witness_size)),
        "profiles_by_excess": {
            str(excess): [list(parts) for parts in parts_list]
            for excess, parts_list in grouped.items()
        },
        "unlabeled_excess_distribution_count": len(distributions),
        "cyclic_base_families": [
            {
                "cyclic_length": family.cyclic_length,
                "base_count": family.base_count,
                "capacity_per_base": family.capacity_per_base,
                "total_capacity": family.total_capacity,
            }
            for family in cyclic_base_families(n)
        ],
        "turn_cover_escape": {
            "strict_positive_threshold": {
                "contradiction_threshold": strict_escape.contradiction_threshold,
                "minimum_capacity_deficit_to_escape": (
                    strict_escape.minimum_capacity_deficit
                ),
                "example_spoiled_length2": list(strict_escape.spoiled_length2),
                "example_spoiled_length3": list(strict_escape.spoiled_length3),
                "remaining_minimum_forced_turns": (
                    strict_escape.remaining_minimum_forced_turns
                ),
            },
            "sum_exceeds_threshold": {
                "contradiction_threshold": conservative_escape.contradiction_threshold,
                "minimum_capacity_deficit_to_escape": (
                    conservative_escape.minimum_capacity_deficit
                ),
                "example_spoiled_length2": list(conservative_escape.spoiled_length2),
                "example_spoiled_length3": list(conservative_escape.spoiled_length3),
                "remaining_minimum_forced_turns": (
                    conservative_escape.remaining_minimum_forced_turns
                ),
            },
        },
        "turn_cover_distribution_summary": {
            "strict_positive_threshold": turn_cover_distribution_summary(
                n,
                witness_size,
                contradiction_threshold=3,
            ),
            "sum_exceeds_threshold": turn_cover_distribution_summary(
                n,
                witness_size,
                contradiction_threshold=4,
            ),
        },
        "profile_assumption_summaries": [
            {
                "allowed_excesses": list(summary.allowed_excesses),
                "distribution_count": summary.distribution_count,
                "forced_by_turn_cover_count": summary.forced_by_turn_cover_count,
                "unresolved_by_turn_cover_count": summary.unresolved_by_turn_cover_count,
                "minimum_total_profile_excess": summary.minimum_total_profile_excess,
                "maximum_total_profile_excess": summary.maximum_total_profile_excess,
            }
            for summary in profile_assumption_summaries(n, witness_size)
        ],
        "minimum_escape_motif_summary": {
            "strict_positive_threshold": minimum_escape_motif_summary(
                n,
                contradiction_threshold=3,
            ),
            "sum_exceeds_threshold": minimum_escape_motif_summary(
                n,
                contradiction_threshold=4,
            ),
        },
        "notes": [
            "No proof of the n=9 case is claimed.",
            "Profile excess E and capacity deficit D satisfy E + D = base_apex_slack.",
            "The previous shorthand sum s_i = 9 is only the fully saturated special case.",
            "Turn-cover escape counts are conditional on length-2/length-3 saturation implications only.",
            "Anti-concentration alone does not close n=9 in this ledger; low profile excess leaves capacity deficit to control.",
        ],
    }


def profile_ledger_case_payload(row: ProfileLedgerCase) -> dict[str, object]:
    """Return a JSON-shaped profile-ledger row."""

    return {
        "excesses": list(row.excesses),
        "total_profile_excess": row.total_profile_excess,
        "capacity_deficit": row.capacity_deficit,
        "forced_by_turn_cover": row.forced_by_turn_cover,
        "profile_multiset": [list(profile) for profile in row.profile_multiset],
    }


def deficit_placement_payload(row: DeficitPlacementClass) -> dict[str, object]:
    """Return a JSON-shaped deficit-placement row."""

    return {
        "n": row.n,
        "relevant_deficit_count": row.relevant_deficit_count,
        "contradiction_threshold": row.contradiction_threshold,
        "spoiled_length2": list(row.spoiled_length2),
        "spoiled_length3": list(row.spoiled_length3),
        "placement_count": row.placement_count,
        "remaining_minimum_forced_turns": row.remaining_minimum_forced_turns,
        "remaining_turn_clause_count": row.remaining_turn_clause_count,
    }


def low_excess_ledger_report(n: int = 9, witness_size: int = 4) -> dict[str, object]:
    """Return the focused unresolved low-excess ledger report.

    This is a generated review artifact for the n=9 base-apex workstream. It
    records which profile-excess distributions the strict turn-cover diagnostic
    does not close, together with the minimum relevant deficit motifs. It is
    intentionally bookkeeping only.
    """

    unresolved = profile_ledger_cases(
        n,
        witness_size,
        contradiction_threshold=3,
        forced_by_turn_cover=False,
    )
    total_excess_counts = Counter(row.total_profile_excess for row in unresolved)
    capacity_deficit_counts = Counter(row.capacity_deficit for row in unresolved)
    strict_motifs = deficit_placement_classes(
        n,
        contradiction_threshold=3,
    )
    conservative_motifs = deficit_placement_classes(
        n,
        contradiction_threshold=4,
    )
    strict_summary = turn_cover_distribution_summary(
        n,
        witness_size,
        contradiction_threshold=3,
    )
    conservative_summary = turn_cover_distribution_summary(
        n,
        witness_size,
        contradiction_threshold=4,
    )

    return {
        "schema": "erdos97.n9_base_apex_low_excess_ledgers.v1",
        "status": "EXPLORATORY_LEDGER_ONLY",
        "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
        "claim_scope": (
            "Focused n=9 base-apex low-excess bookkeeping; not a proof of n=9, "
            "not a counterexample, and not a global status update."
        ),
        "n": n,
        "witness_size": witness_size,
        "base_apex_slack": base_apex_slack(n, witness_size),
        "strict_turn_cover_summary": strict_summary,
        "conservative_turn_cover_summary": conservative_summary,
        "strict_unresolved_profile_ledger_count": len(unresolved),
        "strict_unresolved_count_by_total_profile_excess": {
            str(excess): total_excess_counts[excess]
            for excess in sorted(total_excess_counts)
        },
        "strict_unresolved_count_by_capacity_deficit": {
            str(deficit): capacity_deficit_counts[deficit]
            for deficit in sorted(capacity_deficit_counts)
        },
        "strict_unresolved_profile_ledgers": [
            profile_ledger_case_payload(row) for row in unresolved
        ],
        "strict_minimum_escape_motif_classes": [
            deficit_placement_payload(row) for row in strict_motifs
        ],
        "conservative_minimum_escape_motif_classes": [
            deficit_placement_payload(row) for row in conservative_motifs
        ],
        "notes": [
            "No proof of the n=9 case is claimed.",
            "These are exactly the profile ledgers not closed by the strict turn-cover diagnostic.",
            "For the strict threshold, unresolved ledgers have E <= 6 and D >= 3.",
            "The motif classes only record length-2/length-3 saturation deficits relevant to this diagnostic.",
        ],
        "provenance": {
            "generator": "scripts/explore_n9_base_apex.py",
            "command": (
                "python scripts/explore_n9_base_apex.py --low-excess-report "
                "--out data/certificates/n9_base_apex_low_excess_ledgers.json"
            ),
        },
    }
