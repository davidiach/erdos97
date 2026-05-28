"""Constructive finite-descent helpers for vertex-circle quotient lemmas.

The helpers here turn a finite closed descent region in the strict quotient graph
into an explicit strict-cycle certificate.  They are local lemma infrastructure:
they do not prove the full n=9 case, do not claim a counterexample, and do not
change the official/global status of Erdos Problem #97.
"""

from __future__ import annotations

from typing import Any

from erdos97.vertex_circle_quotient_replay import (
    ClosedDescentRegion,
    Pair,
    StrictInequality,
    pair,
)


def extract_closed_descent_cycle(
    region: ClosedDescentRegion,
) -> tuple[StrictInequality, ...]:
    """Extract a strict cycle from a finite closed descent region.

    A closed descent region supplies a finite nonempty class set ``H`` and one
    witness strict edge ``C -> f(C)`` for every ``C`` in ``H``, with ``f(C)``
    again in ``H``.  Repeated descent from any start class must repeat a class,
    and the repeated tail is a directed strict cycle.  This function makes that
    finite-descent corollary constructive and deterministic.
    """

    classes = _normalized_region_classes(region)
    class_set = set(classes)
    successors = _successor_edges(region, class_set)
    missing = sorted(class_set - set(successors))
    if missing:
        raise ValueError(
            f"closed descent region is missing witness edge for class {missing[0]}"
        )

    start = min(classes)
    seen_at: dict[Pair, int] = {}
    trail: list[StrictInequality] = []
    current = start
    while current not in seen_at:
        seen_at[current] = len(trail)
        edge = successors[current]
        trail.append(edge)
        current = edge.inner_class

    cycle = tuple(trail[seen_at[current] :])
    _validate_cycle(cycle)
    return cycle


def closed_descent_cycle_to_json(region: ClosedDescentRegion) -> dict[str, Any]:
    """Return a JSON-safe certificate for the extracted descent cycle."""

    cycle = extract_closed_descent_cycle(region)
    return {
        "type": "strict_quotient_closed_descent_cycle",
        "class_count": len(region.classes),
        "cycle_length": len(cycle),
        "classes": [list(cls) for cls in _normalized_region_classes(region)],
        "cycle_edges": [_strict_inequality_to_json(edge) for edge in cycle],
    }


def _normalized_region_classes(region: ClosedDescentRegion) -> tuple[Pair, ...]:
    classes = tuple(sorted({pair(cls[0], cls[1]) for cls in region.classes}))
    if not classes:
        raise ValueError("closed descent region must be nonempty")
    return classes


def _successor_edges(
    region: ClosedDescentRegion,
    class_set: set[Pair],
) -> dict[Pair, StrictInequality]:
    successors: dict[Pair, StrictInequality] = {}
    for edge in region.witness_edges:
        source = edge.outer_class
        target = edge.inner_class
        if source not in class_set:
            raise ValueError(
                f"closed descent witness starts outside region: {source}"
            )
        if target not in class_set:
            raise ValueError(f"closed descent witness leaves region: {target}")
        if source in successors:
            raise ValueError(
                f"closed descent region has multiple witness edges for {source}"
            )
        successors[source] = edge
    return successors


def _validate_cycle(cycle: tuple[StrictInequality, ...]) -> None:
    if not cycle:
        raise ValueError("closed descent extraction produced an empty cycle")
    for index, edge in enumerate(cycle):
        next_edge = cycle[(index + 1) % len(cycle)]
        if edge.inner_class != next_edge.outer_class:
            raise ValueError("closed descent extraction produced a broken cycle")


def _strict_inequality_to_json(edge: StrictInequality) -> dict[str, Any]:
    return {
        "row": edge.row,
        "witness_order": list(edge.witness_order),
        "outer_interval": list(edge.outer_interval),
        "inner_interval": list(edge.inner_interval),
        "outer_pair": list(edge.outer_pair),
        "inner_pair": list(edge.inner_pair),
        "outer_class": list(edge.outer_class),
        "inner_class": list(edge.inner_class),
    }
