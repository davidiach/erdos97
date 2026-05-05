"""Exact quotient-cone certificates for selected-witness patterns.

This module generalizes the existing fixed-order Kalmanson/Farkas checker.
It works with arbitrary selected-witness rows, quotients ordinary pair-distance
variables by the selected equalities, and verifies strict linear inequality
certificates whose reduced coefficient vector is coordinatewise nonpositive.

The checker is finite exact bookkeeping. A valid certificate obstructs only the
encoded selected-witness system in the encoded cyclic order.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Mapping, MutableMapping, Sequence

from erdos97.stuck_sets import validate_selected_pattern

Pair = tuple[int, int]
Term = tuple[Pair, int]
Pattern = Sequence[Sequence[int]]

KALMANSON_KINDS = ("K1_diag_gt_sides", "K2_diag_gt_other")


@dataclass(frozen=True)
class DistanceQuotient:
    """Selected-distance quotient over unordered pair variables."""

    n: int
    pair_class: Mapping[Pair, int]
    class_members: tuple[tuple[Pair, ...], ...]

    @property
    def class_count(self) -> int:
        return len(self.class_members)


@dataclass(frozen=True)
class StrictRow:
    """One strict linear inequality row after selected-distance quotienting."""

    source: str
    vector: tuple[int, ...]
    terms: tuple[Term, ...]
    metadata: Mapping[str, object]


@dataclass(frozen=True)
class QuotientConeCheckResult:
    """Summary of one exact quotient-cone certificate check."""

    pattern: str
    n: int
    status: str
    strict_rows: int
    distance_classes: int
    weight_sum: int
    max_weight: int
    coefficient_positive_count: int
    coefficient_negative_count: int
    coefficient_zero_count: int
    combined_nonzero_coefficient_count: int
    zero_sum_verified: bool
    nonpositive_sum_verified: bool
    claim_strength: str


class UnionFind:
    """Deterministic union-find over unordered pairs."""

    def __init__(self, items: Iterable[Pair]) -> None:
        self.parent = {item: item for item in items}

    def find(self, item: Pair) -> Pair:
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left: Pair, right: Pair) -> None:
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left == root_right:
            return
        if root_right < root_left:
            root_left, root_right = root_right, root_left
        self.parent[root_right] = root_left


def pair(left: int, right: int) -> Pair:
    """Return a normalized unordered pair."""

    if left == right:
        raise ValueError(f"loop pair is not allowed: ({left}, {right})")
    return (left, right) if left < right else (right, left)


def rows_from_circulant_offsets(n: int, offsets: Sequence[int]) -> list[list[int]]:
    """Return selected rows from a circulant offset rule."""

    rows: list[list[int]] = []
    residues = [int(offset) % n for offset in offsets]
    for center in range(n):
        row = sorted((center + residue) % n for residue in residues)
        rows.append(row)
    validate_selected_pattern(rows)
    return rows


def selected_distance_quotient(rows: Pattern) -> DistanceQuotient:
    """Build the quotient by selected row equalities."""

    validate_selected_pattern(rows)
    n = len(rows)
    all_pairs = [pair(left, right) for left, right in combinations(range(n), 2)]
    uf = UnionFind(all_pairs)
    for center, witnesses in enumerate(rows):
        base = pair(center, int(witnesses[0]))
        for witness in witnesses[1:]:
            uf.union(base, pair(center, int(witness)))

    root_index: MutableMapping[Pair, int] = {}
    pair_class: dict[Pair, int] = {}
    members: dict[int, list[Pair]] = {}
    for item in all_pairs:
        root = uf.find(item)
        class_index = root_index.setdefault(root, len(root_index))
        pair_class[item] = class_index
        members.setdefault(class_index, []).append(item)
    class_members = tuple(tuple(members[idx]) for idx in range(len(members)))
    return DistanceQuotient(
        n=n,
        pair_class=pair_class,
        class_members=class_members,
    )


def vector_from_terms(quotient: DistanceQuotient, terms: Sequence[Term]) -> tuple[int, ...]:
    """Reduce pair-coefficient terms to the selected-distance quotient."""

    vector = [0] * quotient.class_count
    for raw_pair, coefficient in terms:
        vector[quotient.pair_class[pair(*raw_pair)]] += int(coefficient)
    return tuple(vector)


def kalmanson_terms(kind: str, quad: Sequence[int]) -> tuple[Term, ...]:
    """Return coefficient terms for one strict Kalmanson inequality.

    For vertices ``a,b,c,d`` in cyclic order:

    - ``K1_diag_gt_sides``: ``d(a,c)+d(b,d)>d(a,b)+d(c,d)``
    - ``K2_diag_gt_other``: ``d(a,c)+d(b,d)>d(a,d)+d(b,c)``
    """

    if len(quad) != 4 or len(set(quad)) != 4:
        raise ValueError(f"Kalmanson row needs four distinct vertices, got {quad!r}")
    a, b, c, d = (int(label) for label in quad)
    if kind == "K1_diag_gt_sides":
        return (
            (pair(a, c), +1),
            (pair(b, d), +1),
            (pair(a, b), -1),
            (pair(c, d), -1),
        )
    if kind == "K2_diag_gt_other":
        return (
            (pair(a, c), +1),
            (pair(b, d), +1),
            (pair(a, d), -1),
            (pair(b, c), -1),
        )
    raise ValueError(f"unknown Kalmanson kind: {kind}")


def kalmanson_row(
    quotient: DistanceQuotient,
    kind: str,
    quad: Sequence[int],
) -> StrictRow:
    """Return one reduced Kalmanson strict row."""

    terms = kalmanson_terms(kind, quad)
    return StrictRow(
        source="kalmanson",
        vector=vector_from_terms(quotient, terms),
        terms=terms,
        metadata={"kind": kind, "quad": [int(label) for label in quad]},
    )


def altman_gap_row(
    quotient: DistanceQuotient,
    order: Sequence[int],
    gap_order: int,
) -> StrictRow:
    """Return the strict Altman gap row ``U_{k+1} - U_k > 0``.

    The coefficient convention intentionally matches
    :mod:`erdos97.altman_diagonal_sums`: for each cyclic chord order, we sum
    over all starting vertices in the supplied cyclic order.
    """

    n = quotient.n
    if not 1 <= gap_order < n // 2:
        raise ValueError(f"gap_order must be in [1,{n // 2 - 1}], got {gap_order}")
    _validate_order(order, n)
    terms: list[Term] = []
    for idx, source in enumerate(order):
        left_target = order[(idx + gap_order) % n]
        right_target = order[(idx + gap_order + 1) % n]
        terms.append((pair(source, right_target), +1))
        terms.append((pair(source, left_target), -1))
    return StrictRow(
        source="altman_gap",
        vector=vector_from_terms(quotient, terms),
        terms=tuple(terms),
        metadata={"gap_order": gap_order},
    )


def strict_row_from_certificate_item(
    quotient: DistanceQuotient,
    order: Sequence[int],
    item: Mapping[str, object],
) -> StrictRow:
    """Parse one strict row item from the generalized certificate format."""

    source = str(item.get("source", ""))
    if source in ("", "kalmanson") and "quad" in item:
        kind = str(item["kind"])
        quad = [int(label) for label in item["quad"]]  # type: ignore[index]
        _validate_quad_order(quad, order)
        return kalmanson_row(quotient, kind, quad)
    if source == "altman_gap":
        return altman_gap_row(quotient, order, int(item["gap_order"]))
    raise ValueError(f"unsupported strict row item: {item!r}")


def selected_rows_from_certificate(cert: Mapping[str, object]) -> tuple[str, list[list[int]]]:
    """Extract selected rows from a generalized or legacy certificate."""

    pattern = cert.get("pattern")
    if not isinstance(pattern, Mapping):
        raise ValueError("certificate pattern must be an object")
    name = str(pattern.get("name", cert.get("pattern_name", "<unnamed>")))
    if "selected_rows" in pattern:
        rows = [[int(label) for label in row] for row in pattern["selected_rows"]]  # type: ignore[index]
        validate_selected_pattern(rows)
        return name, rows
    if "rows" in pattern:
        rows = [[int(label) for label in row] for row in pattern["rows"]]  # type: ignore[index]
        validate_selected_pattern(rows)
        return name, rows
    if "circulant_offsets" in pattern:
        n = int(pattern["n"])
        offsets = [int(offset) for offset in pattern["circulant_offsets"]]  # type: ignore[index]
        return name, rows_from_circulant_offsets(n, offsets)
    raise ValueError("certificate pattern must include selected_rows, rows, or circulant_offsets")


def strict_items_from_certificate(cert: Mapping[str, object]) -> list[Mapping[str, object]]:
    """Return strict row items from generalized or legacy certificate shapes."""

    if "strict_rows" in cert:
        items = cert["strict_rows"]
    elif "inequalities" in cert:
        items = cert["inequalities"]
    else:
        raise ValueError("certificate must include strict_rows or inequalities")
    if not isinstance(items, list):
        raise ValueError("strict row collection must be a list")
    if not all(isinstance(item, Mapping) for item in items):
        raise ValueError("every strict row item must be an object")
    return list(items)


def check_quotient_cone_certificate(
    cert: Mapping[str, object],
) -> QuotientConeCheckResult:
    """Verify an exact quotient-cone certificate.

    A certificate is valid when a nonzero nonnegative integer combination of
    strict rows reduces to a coordinatewise nonpositive vector after selected
    equalities are quotiented. Since all ordinary distances are nonnegative,
    this contradicts the strict positivity of the same combination.
    """

    pattern_name, rows = selected_rows_from_certificate(cert)
    n = len(rows)
    order = [int(label) for label in cert["cyclic_order"]]  # type: ignore[index]
    _validate_order(order, n)
    quotient = selected_distance_quotient(rows)

    total = [0] * quotient.class_count
    strict_count = 0
    weight_sum = 0
    max_weight = 0
    for item in strict_items_from_certificate(cert):
        weight = int(item["weight"])
        if weight <= 0:
            raise ValueError(f"strict row weight must be positive, got {weight}")
        strict_row = strict_row_from_certificate_item(quotient, order, item)
        strict_count += 1
        weight_sum += weight
        max_weight = max(max_weight, weight)
        for idx, coefficient in enumerate(strict_row.vector):
            total[idx] += weight * coefficient

    if strict_count == 0:
        raise ValueError("certificate has no strict rows")
    if "num_inequalities" in cert and int(cert["num_inequalities"]) != strict_count:
        raise ValueError("stored num_inequalities does not match listed strict rows")
    if "weight_sum" in cert and int(cert["weight_sum"]) != weight_sum:
        raise ValueError("stored weight_sum does not match listed weights")

    if any(value > 0 for value in total):
        positive = {idx: value for idx, value in enumerate(total) if value > 0}
        raise AssertionError(f"combined coefficient vector is not nonpositive: {positive}")

    positive_count = sum(1 for value in total if value > 0)
    negative_count = sum(1 for value in total if value < 0)
    zero_count = len(total) - positive_count - negative_count
    combined_nonzero_count = sum(1 for value in total if value != 0)
    zero_sum = all(value == 0 for value in total)
    return QuotientConeCheckResult(
        pattern=pattern_name,
        n=n,
        status=str(
            cert.get(
                "status",
                "EXACT_QUOTIENT_CONE_OBSTRUCTION_FOR_FIXED_PATTERN_AND_ORDER",
            )
        ),
        strict_rows=strict_count,
        distance_classes=quotient.class_count,
        weight_sum=weight_sum,
        max_weight=max_weight,
        coefficient_positive_count=positive_count,
        coefficient_negative_count=negative_count,
        coefficient_zero_count=zero_count,
        combined_nonzero_coefficient_count=combined_nonzero_count,
        zero_sum_verified=zero_sum,
        nonpositive_sum_verified=True,
        claim_strength=str(
            cert.get(
                "claim_strength",
                "Exact obstruction for this fixed selected-witness pattern and fixed cyclic order only.",
            )
        ),
    )


def footprint_summary(cert: Mapping[str, object]) -> dict[str, object]:
    """Return a compact equality-footprint summary for a certificate."""

    pattern_name, rows = selected_rows_from_certificate(cert)
    n = len(rows)
    order = [int(label) for label in cert["cyclic_order"]]  # type: ignore[index]
    _validate_order(order, n)
    quotient = selected_distance_quotient(rows)
    items = strict_items_from_certificate(cert)

    source_counts: Counter[str] = Counter()
    kind_counts: Counter[str] = Counter()
    label_counts: Counter[int] = Counter()
    touched_classes: set[int] = set()
    touched_pairs: set[Pair] = set()
    row_centers: set[int] = set()
    for item in items:
        strict_row = strict_row_from_certificate_item(quotient, order, item)
        source_counts[strict_row.source] += 1
        if "kind" in strict_row.metadata:
            kind_counts[str(strict_row.metadata["kind"])] += 1
        for raw_pair, _coefficient in strict_row.terms:
            normalized = pair(*raw_pair)
            touched_pairs.add(normalized)
            touched_classes.add(quotient.pair_class[normalized])
            label_counts.update(normalized)
            row_centers.update(_selected_centers_for_pair(rows, normalized))

    class_sizes = [len(members) for members in quotient.class_members]
    touched_class_sizes = [
        len(quotient.class_members[class_idx])
        for class_idx in sorted(touched_classes)
    ]
    check = check_quotient_cone_certificate(cert)
    return {
        "type": "quotient_cone_equality_footprint_v1",
        "pattern": pattern_name,
        "n": n,
        "strict_rows": len(items),
        "distance_classes": quotient.class_count,
        "source_counts": dict(sorted(source_counts.items())),
        "kind_counts": dict(sorted(kind_counts.items())),
        "label_support_size": len(label_counts),
        "label_support": sorted(label_counts),
        "touched_pair_count": len(touched_pairs),
        "touched_distance_class_count": len(touched_classes),
        "touched_selected_center_count": len(row_centers),
        "touched_selected_centers": sorted(row_centers),
        "distance_class_size_histogram": _histogram(class_sizes),
        "touched_class_size_histogram": _histogram(touched_class_sizes),
        "zero_sum_verified": check.zero_sum_verified,
        "nonpositive_sum_verified": check.nonpositive_sum_verified,
        "claim_strength": check.claim_strength,
        "semantics": (
            "Footprint only: this records which quotient classes and selected "
            "rows a checked fixed-order certificate uses. It is not an "
            "all-order obstruction and not a counterexample."
        ),
    }


def _selected_centers_for_pair(rows: Pattern, target_pair: Pair) -> list[int]:
    left, right = target_pair
    centers = []
    for center, witnesses in enumerate(rows):
        witness_set = set(witnesses)
        if left in witness_set and right in witness_set:
            centers.append(center)
    return centers


def _histogram(values: Sequence[int]) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(values).items())}


def _validate_order(order: Sequence[int], n: int) -> None:
    if len(order) != n or set(order) != set(range(n)):
        missing = sorted(set(range(n)) - set(order))
        extra = sorted(set(order) - set(range(n)))
        raise ValueError(f"cyclic order is not a permutation; missing={missing}, extra={extra}")


def _validate_quad_order(quad: Sequence[int], order: Sequence[int]) -> None:
    position = {label: idx for idx, label in enumerate(order)}
    if any(label not in position for label in quad):
        raise ValueError(f"quad contains label outside cyclic order: {quad}")
    positions = [position[label] for label in quad]
    if positions != sorted(positions):
        raise ValueError(f"quad is not listed in supplied cyclic order: {quad}")
