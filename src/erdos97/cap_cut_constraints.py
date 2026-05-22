"""Centered cap-cut and squared-chord superadditivity constraints.

The checks in this module are exact finite bookkeeping over selected-witness
rows and a supplied cyclic order.  They generate necessary strict inequalities
for a geometric realization, but they do not claim that any surviving abstract
system is realizable.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Sequence

from erdos97.quotient_cone import DistanceQuotient, Term, pair, selected_distance_quotient
from erdos97.stuck_sets import validate_selected_pattern

Pattern = Sequence[Sequence[int]]


@dataclass(frozen=True)
class CapCutRow:
    """One strict linear squared-distance inequality."""

    kind: str
    center: int
    terms: tuple[Term, ...]
    metadata: dict[str, object]


@dataclass(frozen=True)
class PairRoleCount:
    """Role counts for one unordered witness-witness pair."""

    pair: tuple[int, int]
    outer: int
    adjacent: int
    skipped: int

    @property
    def total_selected_row_occurrences(self) -> int:
        return self.outer + self.adjacent + self.skipped

    @property
    def outer_dominant(self) -> bool:
        return self.outer > self.adjacent

    @property
    def pair_cap_compatible(self) -> bool:
        return self.total_selected_row_occurrences <= 2

    @property
    def corrected_outer_dominant_type(self) -> tuple[int, int] | None:
        if not self.outer_dominant or not self.pair_cap_compatible:
            return None
        return (self.outer, self.adjacent)


@dataclass(frozen=True)
class UnitSuperadditivityCertificate:
    """Unit-weight sum of selected-row chain superadditivity inequalities."""

    status: str
    quotient: DistanceQuotient
    combined_coefficients: tuple[int, ...]
    coefficient_positive_count: int
    coefficient_negative_count: int
    coefficient_zero_count: int
    strict_row_count: int
    selected_distance_class_count: int

    @property
    def obstructed(self) -> bool:
        return self.status == "EXACT_UNIT_SUPERADDITIVITY_OBSTRUCTION"


def validate_cyclic_order(order: Sequence[int], n: int) -> None:
    """Validate that ``order`` is a cyclic ordering of labels ``0..n-1``."""

    if len(order) != n:
        raise ValueError(f"order length {len(order)} does not match n={n}")
    if set(order) != set(range(n)):
        raise ValueError("order must be a permutation of 0..n-1")


def angular_witness_order(
    order: Sequence[int],
    center: int,
    witnesses: Sequence[int],
) -> tuple[int, ...]:
    """Return witnesses in boundary order around the hull vertex ``center``."""

    n = len(order)
    validate_cyclic_order(order, n)
    positions = {label: idx for idx, label in enumerate(order)}
    if center not in positions:
        raise ValueError(f"center {center} is missing from order")
    center_pos = positions[center]
    missing = [witness for witness in witnesses if witness not in positions]
    if missing:
        raise ValueError(f"witness {missing[0]} is missing from order")
    return tuple(
        sorted(
            (int(witness) for witness in witnesses),
            key=lambda witness: (positions[witness] - center_pos) % n,
        )
    )


def open_arc_not_containing_center(
    order: Sequence[int],
    a: int,
    b: int,
    center: int,
) -> tuple[int, ...]:
    """Return the open boundary arc from ``a`` to ``b`` not containing ``center``."""

    n = len(order)
    validate_cyclic_order(order, n)
    positions = {label: idx for idx, label in enumerate(order)}
    for label in (a, b, center):
        if label not in positions:
            raise ValueError(f"label {label} is missing from order")
    if len({a, b, center}) != 3:
        raise ValueError("a, b, and center must be distinct")

    def forward_arc(start: int, end: int) -> list[int]:
        out: list[int] = []
        pos = (positions[start] + 1) % n
        end_pos = positions[end]
        while pos != end_pos:
            out.append(int(order[pos]))
            pos = (pos + 1) % n
        return out

    arc_ab = forward_arc(a, b)
    arc_ba = forward_arc(b, a)
    if center in arc_ab and center in arc_ba:
        raise AssertionError("center cannot lie in both open arcs")
    if center not in arc_ab:
        return tuple(arc_ab)
    return tuple(arc_ba)


def superadditivity_terms(a: int, b: int, c: int) -> tuple[Term, ...]:
    """Return terms for ``D_ac - D_ab - D_bc > 0``."""

    return ((pair(a, c), +1), (pair(a, b), -1), (pair(b, c), -1))


def cap_cut_terms(center: int, a: int, b: int, x: int) -> tuple[Term, ...]:
    """Return terms for the centered cap-cut inequality.

    The row is
    ``2D_ix - D_ax - D_bx + D_ab - D_ia - D_ib > 0``.
    """

    return (
        (pair(center, x), +2),
        (pair(a, x), -1),
        (pair(b, x), -1),
        (pair(a, b), +1),
        (pair(center, a), -1),
        (pair(center, b), -1),
    )


def selected_superadditivity_rows(
    rows: Pattern,
    order: Sequence[int] | None = None,
) -> list[CapCutRow]:
    """Generate selected-witness triple superadditivity inequalities."""

    validate_selected_pattern(rows)
    n = len(rows)
    if order is None:
        order = list(range(n))
    validate_cyclic_order(order, n)

    output: list[CapCutRow] = []
    for center, witnesses in enumerate(rows):
        ordered = angular_witness_order(order, center, witnesses)
        for left_index, middle_index, right_index in combinations(range(4), 3):
            a = ordered[left_index]
            b = ordered[middle_index]
            c = ordered[right_index]
            output.append(
                CapCutRow(
                    kind="selected_superadditivity",
                    center=center,
                    terms=superadditivity_terms(a, b, c),
                    metadata={
                        "witness_order": list(ordered),
                        "triple": [a, b, c],
                    },
                )
            )
    return output


def chain_superadditivity_rows(
    rows: Pattern,
    order: Sequence[int] | None = None,
) -> list[CapCutRow]:
    """Generate one four-witness chain inequality per selected row."""

    validate_selected_pattern(rows)
    n = len(rows)
    if order is None:
        order = list(range(n))
    validate_cyclic_order(order, n)

    output: list[CapCutRow] = []
    for center, witnesses in enumerate(rows):
        w0, w1, w2, w3 = angular_witness_order(order, center, witnesses)
        terms: tuple[Term, ...] = (
            (pair(w0, w3), +1),
            (pair(w0, w1), -1),
            (pair(w1, w2), -1),
            (pair(w2, w3), -1),
        )
        output.append(
            CapCutRow(
                kind="selected_chain_superadditivity",
                center=center,
                terms=terms,
                metadata={"witness_order": [w0, w1, w2, w3]},
            )
        )
    return output


def cap_cut_rows(
    rows: Pattern,
    order: Sequence[int] | None = None,
) -> list[CapCutRow]:
    """Generate centered cap-cut inequalities for selected tied pairs."""

    validate_selected_pattern(rows)
    n = len(rows)
    if order is None:
        order = list(range(n))
    validate_cyclic_order(order, n)

    output: list[CapCutRow] = []
    for center, witnesses in enumerate(rows):
        ordered = angular_witness_order(order, center, witnesses)
        for a, b in combinations(ordered, 2):
            for x in open_arc_not_containing_center(order, a, b, center):
                if x in (a, b):
                    continue
                output.append(
                    CapCutRow(
                        kind="centered_cap_cut",
                        center=center,
                        terms=cap_cut_terms(center, a, b, x),
                        metadata={
                            "tied_pair": [a, b],
                            "cap_vertex": x,
                            "witness_order": list(ordered),
                        },
                    )
                )
    return output


def pair_role_counts(
    rows: Pattern,
    order: Sequence[int] | None = None,
) -> list[PairRoleCount]:
    """Return outer, adjacent, and skipped role counts for witness pairs."""

    validate_selected_pattern(rows)
    n = len(rows)
    if order is None:
        order = list(range(n))
    validate_cyclic_order(order, n)

    outer: Counter[tuple[int, int]] = Counter()
    adjacent: Counter[tuple[int, int]] = Counter()
    skipped: Counter[tuple[int, int]] = Counter()

    for center, witnesses in enumerate(rows):
        ordered = angular_witness_order(order, center, witnesses)
        outer[pair(ordered[0], ordered[3])] += 1
        for left, right in zip(ordered, ordered[1:]):
            adjacent[pair(left, right)] += 1
        for left, right in ((ordered[0], ordered[2]), (ordered[1], ordered[3])):
            skipped[pair(left, right)] += 1

    all_pairs = sorted(set(outer) | set(adjacent) | set(skipped))
    return [
        PairRoleCount(
            pair=item,
            outer=outer[item],
            adjacent=adjacent[item],
            skipped=skipped[item],
        )
        for item in all_pairs
    ]


def unit_chain_superadditivity_certificate(
    rows: Pattern,
    order: Sequence[int] | None = None,
) -> UnitSuperadditivityCertificate:
    """Check the unit-weight chain-superadditivity obstruction.

    Summing one strict chain inequality per row gives a certificate whenever
    the reduced selected-distance quotient coefficient vector is coordinatewise
    nonpositive.  If it is zero, the sum gives ``0 > 0``.  If some coefficients
    are negative, positivity of squared distances makes the left-hand side
    strictly negative, again contradicting the strict positive sum.
    """

    validate_selected_pattern(rows)
    quotient = selected_distance_quotient(rows)
    rows_to_sum = chain_superadditivity_rows(rows, order)
    combined = [0] * quotient.class_count
    for strict_row in rows_to_sum:
        for raw_pair, coefficient in strict_row.terms:
            class_index = quotient.pair_class[pair(*raw_pair)]
            combined[class_index] += coefficient
    coefficients = tuple(combined)
    positive = sum(1 for value in coefficients if value > 0)
    negative = sum(1 for value in coefficients if value < 0)
    zero = len(coefficients) - positive - negative
    status = (
        "EXACT_UNIT_SUPERADDITIVITY_OBSTRUCTION"
        if positive == 0 and (negative > 0 or zero == len(coefficients))
        else "PASS_UNIT_SUPERADDITIVITY"
    )
    return UnitSuperadditivityCertificate(
        status=status,
        quotient=quotient,
        combined_coefficients=coefficients,
        coefficient_positive_count=positive,
        coefficient_negative_count=negative,
        coefficient_zero_count=zero,
        strict_row_count=len(rows_to_sum),
        selected_distance_class_count=quotient.class_count,
    )


def cap_cut_report(
    rows: Pattern,
    order: Sequence[int] | None = None,
    *,
    include_cap_cuts: bool = True,
) -> dict[str, object]:
    """Return a JSON-friendly diagnostic report for one selected system."""

    validate_selected_pattern(rows)
    n = len(rows)
    if order is None:
        order = list(range(n))
    validate_cyclic_order(order, n)

    selected_triples = selected_superadditivity_rows(rows, order)
    chains = chain_superadditivity_rows(rows, order)
    cuts = cap_cut_rows(rows, order) if include_cap_cuts else []
    role_counts = pair_role_counts(rows, order)
    unit = unit_chain_superadditivity_certificate(rows, order)
    outer_dominant = [row for row in role_counts if row.outer_dominant]
    corrected_types = sorted(
        {
            row.corrected_outer_dominant_type
            for row in outer_dominant
            if row.corrected_outer_dominant_type is not None
        }
    )

    return {
        "schema": "erdos97.cap_cut_constraints.v1",
        "trust": "RESEARCH_PACKET_LOCAL_NECESSARY_CONDITIONS",
        "claim_scope": (
            "Necessary strict inequalities for one fixed selected-witness "
            "system and cyclic order; not a proof of Erdos #97."
        ),
        "n": n,
        "order": list(order),
        "selected_row_count": len(rows),
        "selected_superadditivity_row_count": len(selected_triples),
        "chain_superadditivity_row_count": len(chains),
        "cap_cut_row_count": len(cuts),
        "unit_chain_superadditivity": {
            "status": unit.status,
            "obstructed": unit.obstructed,
            "strict_row_count": unit.strict_row_count,
            "selected_distance_class_count": unit.selected_distance_class_count,
            "coefficient_positive_count": unit.coefficient_positive_count,
            "coefficient_negative_count": unit.coefficient_negative_count,
            "coefficient_zero_count": unit.coefficient_zero_count,
        },
        "outer_dominance": {
            "outer_dominant_pair_count": len(outer_dominant),
            "pair_cap_compatible_outer_dominant_types": [
                list(item) for item in corrected_types
            ],
            "note": (
                "Under the witness-pair cap, corrected outer-dominant types "
                "can only be [1, 0] or [2, 0]."
            ),
        },
        "pair_role_counts": [
            {
                "pair": list(row.pair),
                "outer": row.outer,
                "adjacent": row.adjacent,
                "skipped": row.skipped,
                "total_selected_row_occurrences": row.total_selected_row_occurrences,
                "outer_dominant": row.outer_dominant,
                "pair_cap_compatible": row.pair_cap_compatible,
                "corrected_outer_dominant_type": (
                    list(row.corrected_outer_dominant_type)
                    if row.corrected_outer_dominant_type is not None
                    else None
                ),
            }
            for row in role_counts
        ],
    }
