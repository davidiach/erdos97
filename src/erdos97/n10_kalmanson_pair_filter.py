"""Independent Python replay for the n=10 Kalmanson pair filter.

The filter quotients ordinary pair-distance variables by the selected spoke
equalities of a partial assignment.  It rejects the assignment if one strict
Kalmanson row becomes zero, or if two strict rows become exact negatives.

Everything here is finite fixed-order bookkeeping.  In particular, an escape
would not be a Euclidean realization and an exhaustive closure would not prove
Erdos Problem #97 beyond the stated ten-label domain.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from math import gcd
from typing import Mapping

from erdos97.generic_vertex_search import Assignment, GenericVertexSearch, UnionFind


N = 10
KALMANSON_KINDS = ("K1", "K2")

PairTerm = tuple[int, int]
StrictTerms = tuple[PairTerm, PairTerm, PairTerm, PairTerm]


@dataclass(frozen=True)
class KalmansonPairSliceResult:
    """Deterministic counts for one interval of fixed row-zero choices."""

    row0_start: int
    row0_end: int
    nodes: int
    self_edge_prunes: int
    inverse_pair_prunes: int
    full_assignments: int

    @property
    def closed(self) -> bool:
        return self.full_assignments == 0

    def to_dict(self) -> dict[str, int | bool]:
        return {
            "row0_start": self.row0_start,
            "row0_end": self.row0_end,
            "nodes": self.nodes,
            "self_edge_prunes": self.self_edge_prunes,
            "inverse_pair_prunes": self.inverse_pair_prunes,
            "full_assignments": self.full_assignments,
            "closed": self.closed,
        }


class N10KalmansonPairSearch:
    """Exact labelled n=10 search with one/two-inequality pruning."""

    def __init__(self) -> None:
        self.base = GenericVertexSearch(N)
        self.strict_rows = self._strict_rows()

    def _strict_rows(self) -> tuple[StrictTerms, ...]:
        rows: list[StrictTerms] = []
        for a, b, c, d in combinations(range(N), 4):
            rows.append(
                (
                    (self.base._pair_index(a, c), +1),
                    (self.base._pair_index(b, d), +1),
                    (self.base._pair_index(a, b), -1),
                    (self.base._pair_index(c, d), -1),
                )
            )
            rows.append(
                (
                    (self.base._pair_index(a, c), +1),
                    (self.base._pair_index(b, d), +1),
                    (self.base._pair_index(a, d), -1),
                    (self.base._pair_index(b, c), -1),
                )
            )
        return tuple(rows)

    def quotient_vectors(
        self,
        assignment: Mapping[int, int],
    ) -> tuple[tuple[int, ...], ...]:
        """Return every reduced strict Kalmanson coefficient vector."""
        quotient = UnionFind(len(self.base.pairs))
        for center, row_mask in assignment.items():
            selected_pairs = self.base.selected_pair_indices[(center, row_mask)]
            for pair_index in selected_pairs[1:]:
                quotient.union(selected_pairs[0], pair_index)

        vectors: list[tuple[int, ...]] = []
        for terms in self.strict_rows:
            coefficients = [0] * len(self.base.pairs)
            for pair_index, coefficient in terms:
                coefficients[quotient.find(pair_index)] += coefficient
            vectors.append(tuple(coefficients))
        return tuple(vectors)

    def status(self, assignment: Mapping[int, int]) -> str:
        """Return ``ok``, ``self_edge``, or ``inverse_pair`` exactly.

        Nonzero quotient vectors are divided by the gcd of their coefficients,
        so inverse pairs include every positive scalar-opposite pair.
        """
        seen: set[tuple[int, ...]] = set()
        for vector in self.quotient_vectors(assignment):
            if not any(vector):
                return "self_edge"
            divisor = 0
            for coefficient in vector:
                divisor = gcd(divisor, abs(coefficient))
            primitive = tuple(coefficient // divisor for coefficient in vector)
            inverse = tuple(-coefficient for coefficient in primitive)
            if inverse in seen:
                return "inverse_pair"
            seen.add(primitive)
        return "ok"

    def rows_status(self, rows: tuple[tuple[int, ...], ...]) -> str:
        """Convenience wrapper accepting explicit witness rows."""
        if len(rows) != N:
            raise ValueError(f"expected {N} rows, got {len(rows)}")
        assignment: Assignment = {}
        for center, witnesses in enumerate(rows):
            if len(witnesses) != 4 or len(set(witnesses)) != 4:
                raise ValueError(f"row {center} must have four distinct witnesses")
            if any(
                isinstance(witness, bool)
                or not isinstance(witness, int)
                or not 0 <= witness < N
                for witness in witnesses
            ):
                raise ValueError(f"row {center} has an out-of-range witness")
            if center in witnesses:
                raise ValueError(f"row {center} cannot contain its center")
            assignment[center] = self.base._mask(witnesses)
        return self.status(assignment)

    def search_slice(self, row0_start: int, row0_end: int) -> KalmansonPairSliceResult:
        """Exhaust one half-open interval of labelled row-zero choices."""
        choice_count = self.base.row0_choice_count
        if not 0 <= row0_start <= row0_end <= choice_count:
            raise ValueError("invalid row-zero slice")

        nodes = 0
        full = 0
        prunes: Counter[str] = Counter()

        def recurse(
            assignment: Assignment,
            indegrees: list[int],
            pair_counts: list[int],
        ) -> None:
            nonlocal full, nodes
            nodes += 1
            if len(assignment) == N:
                full += 1
                return

            best_center: int | None = None
            best_options: list[int] | None = None
            for center in range(N):
                if center in assignment:
                    continue
                options = self.base.valid_options_for_center(
                    center,
                    assignment,
                    indegrees,
                    pair_counts,
                )
                if best_options is None or len(options) < len(best_options):
                    best_center = center
                    best_options = options
                    if not options:
                        break
            if not best_options:
                return

            assert best_center is not None
            for row_mask in best_options:
                assignment[best_center] = row_mask
                for witness in self.base.mask_bits[row_mask]:
                    indegrees[witness] += 1
                for pair_index in self.base.row_pair_indices[row_mask]:
                    pair_counts[pair_index] += 1

                status = self.status(assignment)
                if status == "ok":
                    recurse(assignment, indegrees, pair_counts)
                else:
                    prunes[status] += 1

                for pair_index in self.base.row_pair_indices[row_mask]:
                    pair_counts[pair_index] -= 1
                for witness in self.base.mask_bits[row_mask]:
                    indegrees[witness] -= 1
                del assignment[best_center]

        for row0_index in range(row0_start, row0_end):
            row0 = self.base.options[0][row0_index]
            assignment: Assignment = {0: row0}
            indegrees = [0] * N
            pair_counts = [0] * len(self.base.pairs)
            for witness in self.base.mask_bits[row0]:
                indegrees[witness] += 1
            for pair_index in self.base.row_pair_indices[row0]:
                pair_counts[pair_index] += 1
            status = self.status(assignment)
            if status == "ok":
                recurse(assignment, indegrees, pair_counts)
            else:
                prunes[status] += 1

        return KalmansonPairSliceResult(
            row0_start=row0_start,
            row0_end=row0_end,
            nodes=nodes,
            self_edge_prunes=prunes["self_edge"],
            inverse_pair_prunes=prunes["inverse_pair"],
            full_assignments=full,
        )
