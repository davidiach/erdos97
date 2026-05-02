#!/usr/bin/env python3
"""Exact checker for Kalmanson/Farkas certificates in Erdős #97 handoffs.

A checked certificate proves only the finite statement encoded in its JSON:
selected-distance equalities + one fixed cyclic order + strict convex
quadrilateral Kalmanson distance inequalities are inconsistent.

It does not prove Erdős #97, does not produce a counterexample, and does not
kill an abstract selected-witness pattern across all cyclic orders.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, NamedTuple, Sequence, Tuple

Pair = Tuple[int, int]
Term = Tuple[Pair, int]


class DSU:
    def __init__(self, items: Iterable[Pair]):
        self.parent: Dict[Pair, Pair] = {x: x for x in items}

    def find(self, x: Pair) -> Pair:
        p = self.parent[x]
        if p != x:
            self.parent[x] = self.find(p)
        return self.parent[x]

    def union(self, a: Pair, b: Pair) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def pair(a: int, b: int) -> Pair:
    if a == b:
        raise ValueError(f"degenerate pair ({a},{b})")
    return (a, b) if a < b else (b, a)


def row_witnesses(n: int, offsets: Sequence[int], i: int) -> List[int]:
    return sorted(((i + int(d)) % n for d in offsets))


def build_distance_classes(n: int, offsets: Sequence[int]) -> Mapping[Pair, int]:
    """Quotient unordered pair-distance variables by selected row equalities only."""
    pairs = [pair(a, b) for a, b in combinations(range(n), 2)]
    dsu = DSU(pairs)
    for i in range(n):
        witnesses = row_witnesses(n, offsets, i)
        if i in witnesses or len(set(witnesses)) != 4:
            raise ValueError(f"bad witness row {i}: {witnesses}")
        base = pair(i, witnesses[0])
        for w in witnesses[1:]:
            dsu.union(base, pair(i, w))
    roots: MutableMapping[Pair, int] = {}
    for p in pairs:
        r = dsu.find(p)
        roots.setdefault(r, len(roots))
    return {p: roots[dsu.find(p)] for p in pairs}


def inequality_terms(kind: str, quad: Sequence[int]) -> List[Term]:
    """Coefficient terms for one strict Kalmanson inequality.

    For vertices a,b,c,d in cyclic order:
      K1: d(a,c)+d(b,d) > d(a,b)+d(c,d)
      K2: d(a,c)+d(b,d) > d(a,d)+d(b,c)
    """
    if len(quad) != 4:
        raise ValueError(f"Kalmanson inequality needs four vertices, got {quad!r}")
    a, b, c, d = (int(x) for x in quad)
    if kind == "K1_diag_gt_sides":
        return [(pair(a, c), +1), (pair(b, d), +1), (pair(a, b), -1), (pair(c, d), -1)]
    if kind == "K2_diag_gt_other":
        return [(pair(a, c), +1), (pair(b, d), +1), (pair(a, d), -1), (pair(b, c), -1)]
    raise ValueError(f"unknown inequality kind: {kind}")


class CertificateCheckResult(NamedTuple):
    path: str | None
    pattern: str
    n: int
    status: str
    positive_inequalities: int
    distance_classes_after_selected_equalities: int
    weight_sum: int
    max_weight: int
    zero_sum_verified: bool
    claim_strength: str


def check_certificate_dict(cert: Mapping[str, object], path: str | None = None) -> CertificateCheckResult:
    pattern_obj = cert["pattern"]  # type: ignore[index]
    if not isinstance(pattern_obj, Mapping):
        raise ValueError("pattern must be an object")
    n = int(pattern_obj["n"])  # type: ignore[index]
    offsets = [int(x) for x in pattern_obj["circulant_offsets"]]  # type: ignore[index]
    pattern_name = str(pattern_obj.get("name", "<unnamed>"))

    order = [int(x) for x in cert["cyclic_order"]]  # type: ignore[index]
    if sorted(order) != list(range(n)):
        raise ValueError("cyclic_order is not a permutation of labels 0..n-1")
    pos = {v: k for k, v in enumerate(order)}

    classes = build_distance_classes(n, offsets)
    total: MutableMapping[int, int] = defaultdict(int)
    positive_count = 0
    weight_sum = 0
    max_weight = 0

    inequalities = cert["inequalities"]  # type: ignore[index]
    if not isinstance(inequalities, list):
        raise ValueError("inequalities must be a list")

    for item in inequalities:
        if not isinstance(item, Mapping):
            raise ValueError(f"inequality item is not an object: {item!r}")
        weight = int(item["weight"])
        if weight <= 0:
            raise ValueError(f"non-positive weight: {weight}")
        positive_count += 1
        weight_sum += weight
        max_weight = max(max_weight, weight)

        quad = [int(x) for x in item["quad"]]
        if len(quad) != 4 or len(set(quad)) != 4:
            raise ValueError(f"bad quadrilateral: {quad}")
        if any(x not in pos for x in quad):
            raise ValueError(f"quad contains a vertex outside cyclic_order: {quad}")
        if [pos[x] for x in quad] != sorted(pos[x] for x in quad):
            raise ValueError(f"quad is not listed in the supplied cyclic order: {quad}")

        for p, coef in inequality_terms(str(item["kind"]), quad):
            total[classes[p]] += weight * coef

    if "num_inequalities" in cert and int(cert["num_inequalities"]) != positive_count:  # type: ignore[index]
        raise ValueError("stored num_inequalities does not match listed inequalities")
    if "weight_sum" in cert and int(cert["weight_sum"]) != weight_sum:  # type: ignore[index]
        raise ValueError("stored weight_sum does not match listed weights")

    nonzero = {k: v for k, v in total.items() if v != 0}
    if nonzero:
        raise AssertionError(f"weighted coefficient sum is not zero: {nonzero}")

    return CertificateCheckResult(
        path=path,
        pattern=pattern_name,
        n=n,
        status=str(cert.get("status", "<unspecified>")),
        positive_inequalities=positive_count,
        distance_classes_after_selected_equalities=len(set(classes.values())),
        weight_sum=weight_sum,
        max_weight=max_weight,
        zero_sum_verified=True,
        claim_strength=str(cert.get("claim_strength", "Exact obstruction for this fixed selected-witness pattern and fixed cyclic order only.")),
    )


def check_certificate_file(path: Path) -> CertificateCheckResult:
    return check_certificate_dict(json.loads(path.read_text(encoding="utf-8")), path=str(path))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificates", nargs="+", type=Path, help="Kalmanson certificate JSON path(s) to verify.")
    parser.add_argument("--summary-json", action="store_true", help="Print machine-readable JSON summary.")
    args = parser.parse_args(argv)

    results = [check_certificate_file(path) for path in args.certificates]
    if args.summary_json:
        payload = [result._asdict() for result in results]
        print(json.dumps(payload[0] if len(payload) == 1 else payload, indent=2, sort_keys=True))
        return 0

    for result in results:
        print("certificate OK")
        print(f"path={result.path}")
        print(f"pattern={result.pattern} n={result.n}")
        print(f"status={result.status}")
        print(f"positive inequalities={result.positive_inequalities}")
        print(f"distance classes after selected equalities={result.distance_classes_after_selected_equalities}")
        print(f"weight sum={result.weight_sum}")
        print(f"max weight={result.max_weight}")
        print("weighted sum of strict Kalmanson inequalities is 0 > 0, so this fixed pattern/order is impossible")
        print("claim strength: fixed selected-witness pattern plus fixed cyclic order only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
