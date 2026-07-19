"""Exact finite audit for the period-three reverse-pair radius reduction.

The six labels are the two endpoint slots of each of three transition reverse
pairs. A partition records equality of distance from the first apex. A block
containing both slots of a pair is precisely the desired co-radial occurrence
at this combinatorial level.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterator


PAIR_SLOTS = ((0, 1), (2, 3), (4, 5))
EXPECTED_TOTAL_PARTITIONS = 203
EXPECTED_OCCURRENCE_FREE_PARTITIONS = 87
EXPECTED_LARGEST_CLASS_DISTRIBUTION = {1: 1, 2: 50, 3: 36}


def restricted_growth_partitions(size: int) -> Iterator[tuple[int, ...]]:
    """Yield canonical restricted-growth encodings of all set partitions."""
    if size < 0:
        raise ValueError("partition size must be nonnegative")
    if size == 0:
        yield ()
        return

    def visit(prefix: tuple[int, ...], maximum: int) -> Iterator[tuple[int, ...]]:
        if len(prefix) == size:
            yield prefix
            return
        for label in range(maximum + 2):
            yield from visit(prefix + (label,), max(maximum, label))

    yield from visit((0,), 0)


def has_complete_pair(partition: tuple[int, ...]) -> bool:
    """Return whether one reverse pair is co-radial in this partition."""
    if len(partition) != 6:
        raise ValueError("the period-three audit requires six endpoint slots")
    return any(partition[left] == partition[right] for left, right in PAIR_SLOTS)


def largest_class_size(partition: tuple[int, ...]) -> int:
    """Return the largest radius-equality block size."""
    if not partition:
        return 0
    return max(Counter(partition).values())


@dataclass(frozen=True)
class ThreeReversePairRadiusAudit:
    total_partitions: int
    occurrence_free_partitions: int
    largest_class_distribution: dict[int, int]
    maximum_occurrence_free_class_size: int
    four_hit_forces_complete_pair: bool
    three_hit_threshold_is_sharp: bool

    def to_json(self) -> dict[str, object]:
        return {
            "type": "three_reverse_pair_radius_partition_audit",
            "trust": "EXACT_FINITE_COMBINATORIAL_AUDIT",
            "pair_slots": [list(pair) for pair in PAIR_SLOTS],
            "total_partitions": self.total_partitions,
            "occurrence_free_partitions": self.occurrence_free_partitions,
            "largest_class_distribution": {
                str(size): count
                for size, count in sorted(
                    self.largest_class_distribution.items()
                )
            },
            "maximum_occurrence_free_class_size": (
                self.maximum_occurrence_free_class_size
            ),
            "four_hit_forces_complete_pair": (
                self.four_hit_forces_complete_pair
            ),
            "three_hit_threshold_is_sharp": self.three_hit_threshold_is_sharp,
            "interpretation": (
                "If one complete first-apex radius class contains at least "
                "four of the six period-three reverse-pair slots, it contains "
                "both endpoints of a reverse pair."
            ),
            "claims": {
                "proves_choice_free_four_hit_reduction": True,
                "proves_four_hit_geometric_producer": False,
                "proves_external_occurrence": False,
                "proves_erdos97": False,
                "changes_local_strongest_result": False,
            },
        }


def audit_three_reverse_pair_radius_partitions() -> ThreeReversePairRadiusAudit:
    partitions = list(restricted_growth_partitions(6))
    occurrence_free = [
        partition
        for partition in partitions
        if not has_complete_pair(partition)
    ]
    distribution = Counter(
        largest_class_size(partition) for partition in occurrence_free
    )
    maximum = max(distribution)
    return ThreeReversePairRadiusAudit(
        total_partitions=len(partitions),
        occurrence_free_partitions=len(occurrence_free),
        largest_class_distribution=dict(distribution),
        maximum_occurrence_free_class_size=maximum,
        four_hit_forces_complete_pair=maximum < 4,
        three_hit_threshold_is_sharp=distribution.get(3, 0) > 0,
    )


def matches_expected(audit: ThreeReversePairRadiusAudit) -> bool:
    return (
        audit.total_partitions == EXPECTED_TOTAL_PARTITIONS
        and audit.occurrence_free_partitions
        == EXPECTED_OCCURRENCE_FREE_PARTITIONS
        and audit.largest_class_distribution
        == EXPECTED_LARGEST_CLASS_DISTRIBUTION
        and audit.maximum_occurrence_free_class_size == 3
        and audit.four_hit_forces_complete_pair
        and audit.three_hit_threshold_is_sharp
    )
