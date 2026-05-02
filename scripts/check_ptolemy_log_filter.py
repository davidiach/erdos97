#!/usr/bin/env python3
"""Exact Ptolemy-log obstruction verifier for fixed selected-witness patterns.

This is retained in the merged round-two handoff as a method note and
regression example, not as the headline result. It verifies the clean
natural-order C17_skew certificate:

    S_i = {i-7, i-2, i+4, i+8} mod 17.

For a selected row i whose witnesses are a,b,c,d in cyclic/angular order around
p_i, the four witness points are concyclic, so Ptolemy gives

    d_ac d_bd = d_ab d_cd + d_bc d_da.

Thus each side product is strictly smaller than the diagonal product; in log
form, for example,

    log d_ac + log d_bd - log d_bc - log d_da > 0.

If a positive integer sum of such strict inequalities has identically zero
left-hand side after selected-distance equalities, the fixed selected
pattern/order is impossible. This is a fixed-pattern certificate only; it is
not a general proof and it is not a counterexample.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Mapping, MutableMapping, Sequence, Tuple

Pair = Tuple[int, int]
Row = List[int]
SCHEMA = "erdos97.round2.ptolemy_log_certificate.v1"


def sorted_pair(a: int, b: int) -> Pair:
    if a == b:
        raise ValueError(f"degenerate distance pair ({a},{b})")
    return (a, b) if a < b else (b, a)


def circulant_pattern(n: int, offsets: Sequence[int]) -> Dict[int, Tuple[int, ...]]:
    return {i: tuple((i + int(o)) % n for o in offsets) for i in range(n)}


def equality_classes(n: int, selected_sets: Mapping[int, Sequence[int]]) -> Tuple[Dict[Pair, int], Dict[int, List[Pair]]]:
    """Quotient unordered distances by selected row equalities only."""
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    parent: Dict[Pair, Pair] = {p: p for p in pairs}

    def find(x: Pair) -> Pair:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: Pair, b: Pair) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if ra > rb:
            ra, rb = rb, ra
        parent[rb] = ra

    if sorted(selected_sets) != list(range(n)):
        raise ValueError("selected_witness_sets must contain exactly rows 0..n-1")

    for i, witnesses in selected_sets.items():
        int_witnesses = [int(w) for w in witnesses]
        if len(int_witnesses) != 4:
            raise ValueError(f"row {i} has {len(int_witnesses)} witnesses; expected 4")
        if len(set(int_witnesses)) != 4:
            raise ValueError(f"row {i} has repeated witnesses: {int_witnesses}")
        if i in int_witnesses:
            raise ValueError(f"row {i} selects itself")
        if any(w < 0 or w >= n for w in int_witnesses):
            raise ValueError(f"row {i} has witness outside 0..n-1: {int_witnesses}")
        edges = [sorted_pair(i, w) for w in int_witnesses]
        first = edges[0]
        for edge in edges[1:]:
            union(first, edge)

    reps: MutableMapping[Pair, List[Pair]] = defaultdict(list)
    for p in pairs:
        reps[find(p)].append(p)

    label: Dict[Pair, int] = {}
    rep_by_label: Dict[int, List[Pair]] = {}
    for idx, rep in enumerate(sorted(reps)):
        class_pairs = sorted(reps[rep])
        rep_by_label[idx] = class_pairs
        for p in class_pairs:
            label[p] = idx
    return label, rep_by_label


def row_order(center: int, witnesses: Sequence[int], cyclic_order: Sequence[int]) -> Tuple[int, int, int, int]:
    """Witness angular order around center in a strictly convex polygon.

    In a strictly convex polygon, as one walks around the boundary starting just
    after a vertex, the rays from that vertex to the other boundary vertices
    rotate monotonically. Therefore sorting witness positions by boundary order
    relative to the center gives the same circular/angular order used by
    Ptolemy's theorem.
    """
    if len(witnesses) != 4:
        raise ValueError("Ptolemy row requires exactly four witnesses")
    pos = {v: k for k, v in enumerate(cyclic_order)}
    if center not in pos:
        raise ValueError(f"center {center} absent from cyclic_order")
    if any(int(w) not in pos for w in witnesses):
        raise ValueError(f"some witnesses absent from cyclic_order: {witnesses}")
    n = len(cyclic_order)
    cpos = pos[center]
    return tuple(sorted((int(w) for w in witnesses), key=lambda w: (pos[w] - cpos) % n))  # type: ignore[return-value]


def ptolemy_log_rows(selected_sets: Mapping[int, Sequence[int]], cyclic_order: Sequence[int], labels: Mapping[Pair, int]) -> Tuple[List[Row], List[dict]]:
    """Build both strict Ptolemy-log inequalities for every selected row."""
    m = max(labels.values()) + 1
    rows: List[Row] = []
    descriptions: List[dict] = []
    for center in sorted(selected_sets):
        a, b, c, d = row_order(center, selected_sets[center], cyclic_order)
        diag = [sorted_pair(a, c), sorted_pair(b, d)]
        rhs_options = [[sorted_pair(a, b), sorted_pair(c, d)], [sorted_pair(b, c), sorted_pair(d, a)]]
        for local_index, rhs_pairs in enumerate(rhs_options):
            vector = [0] * m
            for p in diag:
                vector[labels[p]] += 1
            for p in rhs_pairs:
                vector[labels[p]] -= 1
            rows.append(vector)
            descriptions.append({
                "row": center,
                "local_ptolemy_inequality": local_index,
                "witness_order": [a, b, c, d],
                "positive_pairs": [list(p) for p in diag],
                "negative_pairs": [list(p) for p in rhs_pairs],
            })
    return rows, descriptions


def weighted_row_sum(rows: Sequence[Sequence[int]], support: Sequence[int], weights: Sequence[int]) -> List[int]:
    if len(support) != len(weights):
        raise ValueError("certificate_support and certificate_weights have different lengths")
    if not support:
        raise ValueError("empty certificate support")
    width = len(rows[0])
    total = [0] * width
    for idx, weight in zip(support, weights):
        if weight <= 0:
            raise ValueError("certificate weights must be positive integers")
        if idx < 0 or idx >= len(rows):
            raise ValueError(f"row index {idx} out of range")
        for j, value in enumerate(rows[idx]):
            total[j] += weight * value
    return total


def build_c17_skew_certificate() -> dict:
    n = 17
    offsets = [-7, -2, 4, 8]
    cyclic_order = list(range(n))
    selected_sets = circulant_pattern(n, offsets)
    labels, rep_by_label = equality_classes(n, selected_sets)
    rows, descriptions = ptolemy_log_rows(selected_sets, cyclic_order, labels)
    support = list(range(1, 2 * n, 2))
    weights = [1] * n
    total = weighted_row_sum(rows, support, weights)
    return {
        "schema": SCHEMA,
        "role": "METHOD_NOTE_REGRESSION",
        "trust": "EXACT_OBSTRUCTION for the fixed selected pattern/order only",
        "status_note": "Alternate exact certificate for a pattern already killed by existing repo filters; useful as a clean telescoping example and verifier regression, not as a live-wall status update.",
        "pattern": "C17_skew",
        "n": n,
        "offsets": offsets,
        "cyclic_order": cyclic_order,
        "selected_witness_sets": {str(k): list(v) for k, v in selected_sets.items()},
        "distance_class_count": len(rep_by_label),
        "distance_classes": {str(k): [list(pair) for pair in pairs] for k, pairs in rep_by_label.items()},
        "inequality_semantics": "row vector v means sum_j v[j]*log(distance_class_j) > 0, derived from one strict Ptolemy product inequality for a selected witness quadruple",
        "ptolemy_log_rows": rows,
        "ptolemy_log_row_descriptions": descriptions,
        "certificate_support": support,
        "certificate_weights": weights,
        "certificate_sum": total,
        "verified_zero_sum": all(value == 0 for value in total),
        "conclusion": "A positive integer sum of strict inequalities has identically zero left-hand side after selected-distance equalities; contradiction.",
    }


def _int_keyed_selected_sets(raw: Mapping[str, Sequence[int]] | Mapping[int, Sequence[int]]) -> Dict[int, Tuple[int, ...]]:
    return {int(k): tuple(int(x) for x in v) for k, v in raw.items()}


def _validate_offsets_match_selected_sets(n: int, offsets: Sequence[int], selected_sets: Mapping[int, Sequence[int]]) -> bool:
    expected = circulant_pattern(n, offsets)
    if sorted(selected_sets) != list(range(n)):
        raise ValueError("selected_witness_sets must contain exactly rows 0..n-1")
    mismatches = []
    for row in range(n):
        expected_set = set(expected[row])
        actual_set = set(int(x) for x in selected_sets[row])
        if actual_set != expected_set:
            mismatches.append((row, sorted(expected_set), sorted(actual_set)))
    if mismatches:
        preview = "; ".join(f"row {r}: expected {e}, got {a}" for r, e, a in mismatches[:3])
        raise ValueError(f"selected_witness_sets do not match offsets: {preview}")
    return True


def verify_certificate_object(certificate: Mapping[str, object]) -> dict:
    if certificate.get("schema") != SCHEMA:
        raise ValueError(f"unsupported schema: {certificate.get('schema')!r}")
    n = int(certificate["n"])  # type: ignore[index]
    cyclic_order = [int(x) for x in certificate["cyclic_order"]]  # type: ignore[index]
    if sorted(cyclic_order) != list(range(n)):
        raise ValueError("cyclic_order is not a permutation of range(n)")
    selected_sets = _int_keyed_selected_sets(certificate["selected_witness_sets"])  # type: ignore[arg-type,index]
    offsets_match = False
    if "offsets" in certificate:
        offsets = [int(x) for x in certificate["offsets"]]  # type: ignore[index]
        offsets_match = _validate_offsets_match_selected_sets(n, offsets, selected_sets)
    labels, rep_by_label = equality_classes(n, selected_sets)
    rows, descriptions = ptolemy_log_rows(selected_sets, cyclic_order, labels)
    if certificate.get("ptolemy_log_rows") is not None and list(certificate["ptolemy_log_rows"]) != rows:  # type: ignore[index,arg-type]
        raise ValueError("stored ptolemy_log_rows do not match recomputed rows")
    if certificate.get("ptolemy_log_row_descriptions") is not None and list(certificate["ptolemy_log_row_descriptions"]) != descriptions:  # type: ignore[index,arg-type]
        raise ValueError("stored ptolemy_log_row_descriptions do not match recomputed descriptions")
    support = [int(x) for x in certificate["certificate_support"]]  # type: ignore[index]
    weights = [int(x) for x in certificate["certificate_weights"]]  # type: ignore[index]
    total = weighted_row_sum(rows, support, weights)
    if certificate.get("certificate_sum") is not None and list(certificate["certificate_sum"]) != total:  # type: ignore[index,arg-type]
        raise ValueError("stored certificate_sum does not match recomputed sum")
    if certificate.get("distance_class_count") is not None and int(certificate["distance_class_count"]) != len(rep_by_label):  # type: ignore[index]
        raise ValueError("stored distance_class_count does not match recomputed classes")
    if not all(value == 0 for value in total):
        raise ValueError("certificate row sum is not zero")
    return {
        "schema": SCHEMA,
        "role": certificate.get("role", "METHOD_NOTE_REGRESSION"),
        "pattern": certificate.get("pattern"),
        "n": n,
        "offset_selected_sets_match": offsets_match,
        "distance_class_count": len(rep_by_label),
        "ptolemy_log_inequality_count": len(rows),
        "certificate_support_size": len(support),
        "max_abs_certificate_sum": max(abs(value) for value in total),
        "verified_zero_sum": True,
        "claim_strength": "fixed selected-witness pattern plus fixed cyclic order only",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate_path", nargs="?", type=Path, help="JSON certificate to verify; equivalent to --certificate.")
    parser.add_argument("--certificate", type=Path, help="JSON certificate to verify. Defaults to the built-in C17 certificate.")
    parser.add_argument("--emit-certificate", type=Path, help="Write the generated built-in C17 certificate to this path.")
    parser.add_argument("--summary-json", action="store_true", help="Print verification summary as JSON instead of plain text.")
    args = parser.parse_args(argv)
    if args.certificate and args.certificate_path:
        raise SystemExit("provide either positional certificate_path or --certificate, not both")
    if args.emit_certificate:
        cert = build_c17_skew_certificate()
        args.emit_certificate.parent.mkdir(parents=True, exist_ok=True)
        args.emit_certificate.write_text(json.dumps(cert, indent=2) + "\n", encoding="utf-8")
    path = args.certificate or args.certificate_path
    certificate = json.loads(path.read_text(encoding="utf-8")) if path else build_c17_skew_certificate()
    summary = verify_certificate_object(certificate)
    if args.summary_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"pattern: {summary['pattern']}")
        print(f"role: {summary['role']}")
        print(f"n: {summary['n']}")
        print(f"offset_selected_sets_match: {summary['offset_selected_sets_match']}")
        print(f"distance_classes: {summary['distance_class_count']}")
        print(f"ptolemy_log_inequalities: {summary['ptolemy_log_inequality_count']}")
        print(f"certificate_support_size: {summary['certificate_support_size']}")
        print(f"max_abs_certificate_sum: {summary['max_abs_certificate_sum']}")
        print("VERIFIED: positive integer sum of strict inequalities has zero vector sum.")
        print("Conclusion: exact obstruction for this fixed selected pattern/order only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
