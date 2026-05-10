"""Rich-triple closure and bootstrap-core capacity helpers.

This module is bridge bookkeeping.  It treats the per-center rich classes as
full distance classes, so distinct classes at the same center must be disjoint.
The routines do not certify Euclidean realizability, a counterexample, or a
general proof of Erdos Problem #97.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb
from typing import Iterable, Sequence

from erdos97.adaptive_blockers import (
    RichClasses,
    singleton_rich_classes_from_pattern,
    validate_rich_classes,
)


@dataclass(frozen=True)
class ClosureStep:
    added_center: int
    rich_class_index: int
    rich_class: list[int]
    trigger_witnesses: list[int]
    closure_before: list[int]


@dataclass(frozen=True)
class ClosureResult:
    seed: list[int]
    closure: list[int]
    order: list[int]
    steps: list[ClosureStep]
    generates_all: bool


@dataclass(frozen=True)
class RankSearchResult:
    rank_leq_limit: bool
    limit: int
    generating_seed: list[int] | None
    generating_closure: ClosureResult | None
    checked_seed_count: int
    largest_closure_size: int
    largest_closure_seed: list[int] | None


@dataclass(frozen=True)
class RichClassPrivateSlice:
    rich_class_index: int
    rich_class: list[int]
    intersection_with_deletion_closure: list[int]
    private_halo_witnesses: list[int]
    private_pair_count: int


@dataclass(frozen=True)
class DeletionClosureAudit:
    core_vertex: int
    seed: list[int]
    closure: list[int]
    core_vertex_not_generated: bool
    private_halo: list[int]
    rich_class_slices: list[RichClassPrivateSlice]


@dataclass(frozen=True)
class BootstrapCoreAudit:
    core: list[int]
    outside: list[int]
    core_generates_all: bool
    inclusion_minimal: bool
    private_halo_requirement_ok: bool
    deletion_closures: list[DeletionClosureAudit]
    private_pair_lower_bound: int
    private_pair_count: int
    cyclic_capacity_sum: int
    lower_bound_capacity_ok: bool
    weighted_capacity_ok: bool
    outside_runs: list[list[int]]


def _mask(vertices: Iterable[int]) -> int:
    out = 0
    for vertex in vertices:
        out |= 1 << int(vertex)
    return out


def _vertices(mask: int, n: int) -> list[int]:
    return [vertex for vertex in range(n) if mask & (1 << vertex)]


def _dedupe_vertices(vertices: Iterable[int], n: int, name: str) -> list[int]:
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


def validate_full_rich_classes(rich_classes: RichClasses) -> None:
    """Validate finite full-rich-class data used by bootstrap-core tools."""

    validate_rich_classes(rich_classes)
    for center, classes in enumerate(rich_classes):
        seen: set[int] = set()
        for class_index, row in enumerate(classes):
            row_set = {int(label) for label in row}
            overlap = sorted(seen & row_set)
            if overlap:
                raise ValueError(
                    f"center {center} rich class {class_index} overlaps "
                    f"an earlier class at labels {overlap}"
                )
            seen.update(row_set)


def closure(seed: Iterable[int], rich_classes: RichClasses) -> ClosureResult:
    """Compute rich-triple closure from ``seed``.

    A center is added once three current vertices lie in one of its full rich
    classes.  The deterministic order is by smallest center, then smallest rich
    class index.
    """

    validate_full_rich_classes(rich_classes)
    n = len(rich_classes)
    seed_vertices = _dedupe_vertices(seed, n, "seed")
    closure_mask = _mask(seed_vertices)
    row_masks = [
        [_mask(int(label) for label in row) for row in classes]
        for classes in rich_classes
    ]
    steps: list[ClosureStep] = []
    order = list(seed_vertices)

    changed = True
    while changed:
        changed = False
        for center in range(n):
            if closure_mask & (1 << center):
                continue
            for class_index, row_mask in enumerate(row_masks[center]):
                internal_mask = row_mask & closure_mask
                if internal_mask.bit_count() < 3:
                    continue
                trigger = _vertices(internal_mask, n)[:3]
                steps.append(
                    ClosureStep(
                        added_center=center,
                        rich_class_index=class_index,
                        rich_class=[int(label) for label in rich_classes[center][class_index]],
                        trigger_witnesses=trigger,
                        closure_before=_vertices(closure_mask, n),
                    )
                )
                closure_mask |= 1 << center
                order.append(center)
                changed = True
                break

    closure_vertices = _vertices(closure_mask, n)
    return ClosureResult(
        seed=seed_vertices,
        closure=closure_vertices,
        order=order,
        steps=steps,
        generates_all=len(closure_vertices) == n,
    )


def is_generator(seed: Iterable[int], rich_classes: RichClasses) -> bool:
    """Return whether ``seed`` rich-triple-generates all labels."""

    return closure(seed, rich_classes).generates_all


def search_generating_seed(
    rich_classes: RichClasses,
    limit: int = 3,
) -> RankSearchResult:
    """Search all seeds of size at most ``limit`` for a generator."""

    validate_full_rich_classes(rich_classes)
    n = len(rich_classes)
    checked = 0
    largest_size = -1
    largest_seed: list[int] | None = None

    for size in range(1, min(limit, n) + 1):
        for seed in combinations(range(n), size):
            checked += 1
            result = closure(seed, rich_classes)
            if len(result.closure) > largest_size:
                largest_size = len(result.closure)
                largest_seed = list(seed)
            if result.generates_all:
                return RankSearchResult(
                    rank_leq_limit=True,
                    limit=limit,
                    generating_seed=list(seed),
                    generating_closure=result,
                    checked_seed_count=checked,
                    largest_closure_size=len(result.closure),
                    largest_closure_seed=list(seed),
                )

    return RankSearchResult(
        rank_leq_limit=False,
        limit=limit,
        generating_seed=None,
        generating_closure=None,
        checked_seed_count=checked,
        largest_closure_size=max(largest_size, 0),
        largest_closure_seed=largest_seed,
    )


def is_inclusion_minimal_generator(
    core: Iterable[int],
    rich_classes: RichClasses,
) -> bool:
    """Return whether ``core`` generates all labels and no proper deletion does."""

    validate_full_rich_classes(rich_classes)
    n = len(rich_classes)
    core_vertices = _dedupe_vertices(core, n, "core")
    if not closure(core_vertices, rich_classes).generates_all:
        return False
    return all(
        not closure(
            [vertex for vertex in core_vertices if vertex != removed],
            rich_classes,
        ).generates_all
        for removed in core_vertices
    )


def outside_vertices(core: Iterable[int], n: int) -> list[int]:
    """Return vertices outside ``core`` in label order."""

    core_set = set(_dedupe_vertices(core, n, "core"))
    return [vertex for vertex in range(n) if vertex not in core_set]


def outside_runs(
    core: Iterable[int],
    n: int,
    order: Sequence[int] | None = None,
) -> list[list[int]]:
    """Return maximal cyclic runs of outside vertices in ``order``."""

    if order is None:
        order = list(range(n))
    if sorted(int(label) for label in order) != list(range(n)):
        raise ValueError("order must be a permutation of range(n)")

    core_set = set(_dedupe_vertices(core, n, "core"))
    if not core_set:
        raise ValueError("core must be nonempty")
    outside_flags = [int(label) not in core_set for label in order]
    if not any(outside_flags):
        return []
    if all(outside_flags):
        return [[int(label) for label in order]]

    start = next(idx for idx, is_outside in enumerate(outside_flags) if not is_outside)
    runs: list[list[int]] = []
    current: list[int] = []
    for offset in range(1, n + 1):
        idx = (start + offset) % n
        label = int(order[idx])
        if outside_flags[idx]:
            current.append(label)
        elif current:
            runs.append(current)
            current = []
    if current:
        runs.append(current)
    return runs


def cyclic_pair_capacity(
    pair: tuple[int, int],
    core: Iterable[int],
    n: int,
    order: Sequence[int] | None = None,
) -> int:
    """Return the number of open arcs between ``pair`` containing core labels."""

    if order is None:
        order = list(range(n))
    if sorted(int(label) for label in order) != list(range(n)):
        raise ValueError("order must be a permutation of range(n)")
    a, b = int(pair[0]), int(pair[1])
    if a == b:
        raise ValueError("pair must contain two distinct labels")
    if a < 0 or a >= n or b < 0 or b >= n:
        raise ValueError("pair contains out-of-range label")

    core_set = set(_dedupe_vertices(core, n, "core"))
    if not core_set:
        raise ValueError("core must be nonempty")
    pos = {int(label): idx for idx, label in enumerate(order)}
    a_pos, b_pos = pos[a], pos[b]
    arc_ab = {
        int(order[idx % n])
        for idx in range(a_pos + 1, b_pos if a_pos < b_pos else b_pos + n)
    }
    arc_ba = set(range(n)) - arc_ab - {a, b}
    return int(bool(arc_ab & core_set)) + int(bool(arc_ba & core_set))


def cyclic_capacity_sum(
    core: Iterable[int],
    n: int,
    order: Sequence[int] | None = None,
) -> int:
    """Return the total cyclic outside-pair capacity for ``core``."""

    core_vertices = _dedupe_vertices(core, n, "core")
    outside = outside_vertices(core_vertices, n)
    return sum(
        cyclic_pair_capacity((a, b), core_vertices, n, order)
        for a, b in combinations(outside, 2)
    )


def cyclic_capacity_from_runs(runs: Sequence[Sequence[int]]) -> int:
    """Return ``2*C(|O|,2) - sum_R C(|R|,2)`` from outside runs."""

    outside_size = sum(len(run) for run in runs)
    return 2 * comb(outside_size, 2) - sum(comb(len(run), 2) for run in runs)


def audit_bootstrap_core(
    core: Iterable[int],
    rich_classes: RichClasses,
    order: Sequence[int] | None = None,
) -> BootstrapCoreAudit:
    """Audit deletion closures, private halos, and weighted capacity."""

    validate_full_rich_classes(rich_classes)
    n = len(rich_classes)
    core_vertices = _dedupe_vertices(core, n, "core")
    outside = outside_vertices(core_vertices, n)
    outside_set = set(outside)
    core_closure = closure(core_vertices, rich_classes)
    deletion_audits: list[DeletionClosureAudit] = []
    private_pair_count = 0
    private_pair_lower_bound = 0
    private_halo_requirement_ok = True

    for removed in core_vertices:
        seed = [vertex for vertex in core_vertices if vertex != removed]
        deletion = closure(seed, rich_classes)
        deletion_set = set(deletion.closure)
        private_halo = sorted(outside_set - deletion_set)
        slices: list[RichClassPrivateSlice] = []
        for class_index, row in enumerate(rich_classes[removed]):
            row_vertices = [int(label) for label in row]
            private_witnesses = sorted(set(row_vertices) & set(private_halo))
            intersection = sorted(set(row_vertices) & deletion_set)
            pair_count = comb(len(private_witnesses), 2)
            private_pair_count += pair_count
            private_pair_lower_bound += comb(max(len(row_vertices) - 2, 0), 2)
            private_halo_requirement_ok = (
                private_halo_requirement_ok
                and len(intersection) <= 2
                and len(private_witnesses) >= max(len(row_vertices) - 2, 0)
            )
            slices.append(
                RichClassPrivateSlice(
                    rich_class_index=class_index,
                    rich_class=row_vertices,
                    intersection_with_deletion_closure=intersection,
                    private_halo_witnesses=private_witnesses,
                    private_pair_count=pair_count,
                )
            )
        deletion_audits.append(
            DeletionClosureAudit(
                core_vertex=removed,
                seed=seed,
                closure=deletion.closure,
                core_vertex_not_generated=removed not in deletion_set,
                private_halo=private_halo,
                rich_class_slices=slices,
            )
        )

    runs = outside_runs(core_vertices, n, order)
    capacity = cyclic_capacity_sum(core_vertices, n, order)
    run_capacity = cyclic_capacity_from_runs(runs)
    if capacity != run_capacity:
        raise AssertionError("cyclic capacity and run formula disagree")
    return BootstrapCoreAudit(
        core=core_vertices,
        outside=outside,
        core_generates_all=core_closure.generates_all,
        inclusion_minimal=is_inclusion_minimal_generator(core_vertices, rich_classes),
        private_halo_requirement_ok=private_halo_requirement_ok,
        deletion_closures=deletion_audits,
        private_pair_lower_bound=private_pair_lower_bound,
        private_pair_count=private_pair_count,
        cyclic_capacity_sum=capacity,
        lower_bound_capacity_ok=private_pair_lower_bound <= capacity,
        weighted_capacity_ok=private_pair_count <= capacity,
        outside_runs=runs,
    )


def audit_fixed_selected_pattern_as_rich_classes(
    selected_rows: Sequence[Sequence[int]],
    core: Iterable[int],
    order: Sequence[int] | None = None,
) -> BootstrapCoreAudit:
    """Audit one fixed selected row per center as a singleton rich family."""

    rich_classes = singleton_rich_classes_from_pattern(selected_rows)
    return audit_bootstrap_core(core, rich_classes, order)
