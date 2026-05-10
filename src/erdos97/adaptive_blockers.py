"""Adaptive selected-witness peeling and radius-blocker helpers.

The routines here are combinatorial bookkeeping for the bridge program.  They
do not certify Euclidean realizability, a counterexample, or a general proof of
Erdos Problem #97.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Sequence


RichClasses = Sequence[Sequence[Sequence[int]]]


@dataclass(frozen=True)
class AdaptivePeelingStep:
    removed_center: int
    rich_class_index: int
    rich_class: list[int]
    internal_witnesses: list[int]
    chosen_selected_row: list[int]
    remaining_before: list[int]


@dataclass(frozen=True)
class AdaptivePeelingResult:
    success: bool
    seed: list[int] | None
    forward_order: list[int] | None
    selected_rows: dict[int, list[int]]
    removal_steps: list[AdaptivePeelingStep]
    blocker: list[int] | None


def _mask(vertices: Iterable[int]) -> int:
    out = 0
    for vertex in vertices:
        out |= 1 << int(vertex)
    return out


def _vertices(mask: int, n: int) -> list[int]:
    return [vertex for vertex in range(n) if mask & (1 << vertex)]


def _subset_vertices(vertices: Iterable[int], n: int, name: str) -> list[int]:
    out: list[int] = []
    seen: set[int] = set()
    for raw_vertex in vertices:
        vertex = int(raw_vertex)
        if vertex < 0 or vertex >= n:
            raise ValueError(f"{name} contains out-of-range label {vertex}")
        if vertex not in seen:
            out.append(vertex)
            seen.add(vertex)
    return out


def validate_rich_classes(rich_classes: RichClasses) -> None:
    """Validate a family of per-center rich distance classes.

    Each rich class represents one exact distance class of size at least four
    at its center.  This function checks only the finite incidence contract.
    """

    n = len(rich_classes)
    if n < 4:
        raise ValueError(f"expected at least four centers, got {n}")
    for center, classes in enumerate(rich_classes):
        if not classes:
            raise ValueError(f"center {center} has no rich classes")
        for class_index, row in enumerate(classes):
            row_set = set(int(label) for label in row)
            if len(row_set) != len(row):
                raise ValueError(
                    f"center {center} rich class {class_index} has repeated labels"
                )
            if len(row_set) < 4:
                raise ValueError(
                    f"center {center} rich class {class_index} has size {len(row_set)}"
                )
            if center in row_set:
                raise ValueError(
                    f"center {center} rich class {class_index} contains its center"
                )
            for label in row_set:
                if label < 0 or label >= n:
                    raise ValueError(
                        f"center {center} rich class {class_index} has "
                        f"out-of-range label {label}"
                    )


def singleton_rich_classes_from_pattern(
    selected_rows: Sequence[Sequence[int]],
) -> tuple[tuple[tuple[int, ...], ...], ...]:
    """Treat one fixed selected row per center as the only rich class."""

    return tuple((tuple(int(label) for label in row),) for row in selected_rows)


def is_radius_blocker(
    rich_classes: RichClasses,
    subset: Iterable[int],
    threshold: int = 3,
) -> bool:
    """Return whether ``subset`` is a radius-blocker for the rich classes."""

    validate_rich_classes(rich_classes)
    n = len(rich_classes)
    subset_vertices = _subset_vertices(subset, n, "subset")
    subset_mask = _mask(subset_vertices)
    subset_vertices = _vertices(subset_mask, n)
    if len(subset_vertices) < threshold + 1:
        return False
    for center in subset_vertices:
        for row in rich_classes[center]:
            if (_mask(row) & subset_mask).bit_count() >= threshold:
                return False
    return True


def first_blocker(
    rich_classes: RichClasses,
    min_size: int = 4,
    max_size: int | None = None,
) -> list[int] | None:
    """Return the first radius-blocker by cardinality and lexicographic order."""

    validate_rich_classes(rich_classes)
    n = len(rich_classes)
    if max_size is None:
        max_size = n
    for size in range(max(min_size, 4), min(max_size, n) + 1):
        for subset in combinations(range(n), size):
            if is_radius_blocker(rich_classes, subset):
                return list(subset)
    return None


def adaptive_reverse_peeling(
    rich_classes: RichClasses,
    threshold: int = 3,
) -> AdaptivePeelingResult:
    """Run the adaptive reverse-peeling/blocker alternative.

    If the process reaches a three-vertex seed, the returned ``selected_rows``
    and ``forward_order`` give an adaptive ear-order certificate.  If it stops
    earlier, the terminal set is a radius-blocker.
    """

    validate_rich_classes(rich_classes)
    if threshold != 3:
        raise ValueError("only the three-witness bridge threshold is supported")

    n = len(rich_classes)
    remaining_mask = (1 << n) - 1
    steps: list[AdaptivePeelingStep] = []
    selected_rows: dict[int, list[int]] = {}

    while remaining_mask.bit_count() > threshold:
        removed: AdaptivePeelingStep | None = None
        for center in _vertices(remaining_mask, n):
            for class_index, row in enumerate(rich_classes[center]):
                row_list = [int(label) for label in row]
                internal = [
                    label for label in row_list if remaining_mask & (1 << label)
                ]
                if len(internal) < threshold:
                    continue
                chosen = internal[:threshold]
                for label in row_list:
                    if label not in chosen:
                        chosen.append(label)
                    if len(chosen) == 4:
                        break
                removed = AdaptivePeelingStep(
                    removed_center=center,
                    rich_class_index=class_index,
                    rich_class=row_list,
                    internal_witnesses=internal[:threshold],
                    chosen_selected_row=chosen,
                    remaining_before=_vertices(remaining_mask, n),
                )
                break
            if removed is not None:
                break

        if removed is None:
            return AdaptivePeelingResult(
                success=False,
                seed=None,
                forward_order=None,
                selected_rows=selected_rows,
                removal_steps=steps,
                blocker=_vertices(remaining_mask, n),
            )

        steps.append(removed)
        selected_rows[removed.removed_center] = removed.chosen_selected_row
        remaining_mask &= ~(1 << removed.removed_center)

    seed = _vertices(remaining_mask, n)
    for center in seed:
        selected_rows[center] = [int(label) for label in rich_classes[center][0][:4]]
    forward_order = seed + [step.removed_center for step in reversed(steps)]
    return AdaptivePeelingResult(
        success=True,
        seed=seed,
        forward_order=forward_order,
        selected_rows=dict(sorted(selected_rows.items())),
        removal_steps=steps,
        blocker=None,
    )


def outside_pair_expansion_bound(outside_size: int) -> int:
    """Return the blocker-size upper bound from the outside-pair argument."""

    if outside_size < 0:
        raise ValueError("outside_size must be nonnegative")
    return outside_size * (outside_size - 1)
