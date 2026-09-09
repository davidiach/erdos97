"""Finite exact search for a witness-closed set of rich new vertices.

Only integer sets, bit masks, and cyclic-order comparisons are used. A returned
assignment is a necessary combinatorial control, NOT a planar realization.
The mandatory vertices must occur; every other new vertex is optional.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, permutations
from typing import Mapping, Sequence
import sys

from metric_filter import obstruction

if sys.flags.optimize:
    raise RuntimeError("Exact verification must not run with assertions disabled")


@dataclass(frozen=True)
class Model:
    adjacency: Mapping[int, Sequence[int]]
    old_support: Mapping[int, Sequence[int]]
    ranks: Mapping[int, int]
    mandatory: tuple[int, ...] = (42, 43)
    old_count: int = 9

    def validate(self) -> None:
        vertices = set(self.adjacency)
        if type(self.old_count) is not int or self.old_count < 0:
            raise ValueError("Invalid old-vertex count")
        if (not self.mandatory or len(set(self.mandatory)) != len(self.mandatory)
                or any(type(i) is not int or i < 0 for i in self.mandatory)):
            raise ValueError("Invalid mandatory vertices")
        if any(i not in self.ranks for i in range(self.old_count)):
            raise ValueError("Missing old cyclic rank")
        if any(type(value) is not int for value in self.ranks.values()):
            raise ValueError("Noninteger cyclic rank")
        if not set(self.mandatory) <= vertices:
            raise ValueError("A mandatory vertex is absent")
        if set(self.old_support) != vertices:
            raise ValueError("Old-support domain differs from vertex domain")
        for i, targets in self.adjacency.items():
            if type(i) is not int or i < 0:
                raise ValueError("Invalid new-vertex label")
            if any(type(j) is not int or j < 0 for j in targets):
                raise ValueError("Invalid target label")
            if len(set(targets)) != len(targets) or i in targets:
                raise ValueError("Repeated target or self-witness")
            if not set(targets) <= vertices:
                raise ValueError("Target lacks a possible rich row")
            old = self.old_support[i]
            if len(set(old)) != len(old) or len(old) > 4:
                raise ValueError("Invalid old-support count")
            if any(type(j) is not int or not 0 <= j < self.old_count for j in old):
                raise ValueError("Invalid old witness")
            if i + self.old_count not in self.ranks:
                raise ValueError("Missing source cyclic rank")
            if any(j not in self.ranks for j in old):
                raise ValueError("Missing old cyclic rank")


def set_bits(mask: int):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


class Search:
    def __init__(self, model: Model, node_limit: int | None = None):
        model.validate()
        self.model = model
        self.node_limit = node_limit
        self.nodes = 0
        self.metric_rejections = {"zero": 0, "inverse": 0}
        self.first_metric_certificate = None
        self.options = {}
        for i, adjacency in model.adjacency.items():
            fixed = sum(1 << j for j in model.old_support[i])
            need = 4 - len(model.old_support[i])
            self.options[i] = [
                (
                    sum(1 << j for j in selected),
                    fixed | sum(1 << (j + model.old_count) for j in selected),
                )
                for selected in combinations(sorted(adjacency), need)
            ]

    @lru_cache(maxsize=None)
    def can_cross(self, i: int, j: int, a: int, b: int) -> bool:
        """Allow every ordering within a tied insertion cell.

        Distinct circles with two shared witnesses require alternating centers
        and witnesses. This test is deliberately permissive about tied ranks.
        """
        labels = (i + self.model.old_count, j + self.model.old_count, a, b)
        values = [self.model.ranks[k] for k in labels]
        target = sorted(values)
        for order in permutations(range(4)):
            if [values[k] for k in order] != target:
                continue
            types = [int(k < 2) for k in order]
            if types in ([0, 1, 0, 1], [1, 0, 1, 0]):
                return True
        return False

    def compatible(self, i: int, row: int, j: int, other: int) -> bool:
        shared = row & other
        count = shared.bit_count()
        if count < 2:
            return True
        if count > 2:
            return False
        a, b = set_bits(shared)
        return self.can_cross(i, j, a, b)

    def run(self) -> dict:
        def visit(assigned: dict, required: int, domains: dict):
            self.nodes += 1
            if self.node_limit is not None and self.nodes > self.node_limit:
                raise TimeoutError("Exact row-search node guard reached")
            todo = required & ~sum(1 << i for i in assigned)
            if not todo:
                rows = {i: list(set_bits(row)) for i, (_, row) in assigned.items()}
                physical = {i + self.model.old_count: row for i, row in rows.items()}
                certificate = obstruction(physical, dict(self.model.ranks), self.model.old_count)
                if certificate is not None:
                    self.metric_rejections[certificate["type"]] += 1
                    if self.first_metric_certificate is None:
                        self.first_metric_certificate = {"rows": physical, **certificate}
                    return None
                return rows
            active = list(set_bits(todo))
            if any(not domains[i] for i in active):
                return None
            source = min(active, key=lambda i: (len(domains[i]), i))
            for option in domains[source]:
                targets, row = option
                if any(
                    not self.compatible(source, row, j, other)
                    for j, (_, other) in assigned.items()
                ):
                    continue
                selected = {**assigned, source: option}
                required_next = required | targets
                next_domains = {}
                unavailable = 0
                for j, choices in domains.items():
                    if j in selected:
                        continue
                    kept = [
                        choice for choice in choices
                        if self.compatible(source, row, j, choice[1])
                    ]
                    next_domains[j] = kept
                    if not kept:
                        unavailable |= 1 << j
                if required_next & unavailable:
                    continue
                # A vertex with no compatible rich row cannot be a witness.
                while unavailable:
                    newly_unavailable = 0
                    for j, choices in next_domains.items():
                        if not choices:
                            continue
                        kept = [choice for choice in choices if not choice[0] & unavailable]
                        next_domains[j] = kept
                        if not kept:
                            newly_unavailable |= 1 << j
                    if required_next & newly_unavailable:
                        break
                    unavailable = newly_unavailable
                else:
                    result = visit(selected, required_next, next_domains)
                    if result is not None:
                        return result
            return None

        try:
            result = visit({}, sum(1 << i for i in self.model.mandatory), self.options)
        except TimeoutError:
            return {"status": "unresolved", "nodes": self.nodes, "rows": None}
        return {
            "status": "exhausted" if result is None else "abstract_assignment",
            "nodes": self.nodes,
            "rows": result,
            "metric_rejections": self.metric_rejections,
            "first_metric_certificate": self.first_metric_certificate,
        }
