#!/usr/bin/env python3
"""Standalone n=9 selected-witness frontier replay plus Kalmanson core compression.

This script is intentionally self-contained and uses only the Python standard
library. It regenerates the fixed cyclic-order n=9 selected-witness frontier
using the standard exact incidence filters, finds one strict Kalmanson self-edge
for every surviving terminal assignment, and then compresses each self-edge to a
row-minimal subset of the assignment whose selected-distance equalities already
force the same contradiction.

Scope: review-pending finite-case/certificate evidence only. The script does
not claim a general proof of Erdos Problem #97 and does not produce a
counterexample.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Sequence

Vertex = int
Row = tuple[Vertex, Vertex, Vertex, Vertex]
Assignment = tuple[Row, ...]
Pair = tuple[Vertex, Vertex]

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_kalmanson_three_row_core_compression.json"
)

SCHEMA = "erdos97.n9_kalmanson_three_row_core_compression.v1"
STATUS = "REVIEW_PENDING_N9_KALMANSON_THREE_ROW_CORE_COMPRESSION"
TRUST = "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING"
CLAIM_SCOPE = (
    "Standalone regeneration of the fixed-cyclic-order n=9 selected-witness "
    "frontier plus one strict Kalmanson self-edge for each terminal assignment, "
    "with each self-edge compressed to a row-minimal equality core. This is "
    "certificate/audit evidence only; it does not complete independent review, "
    "does not promote n=9 to a theorem, does not prove Erdos Problem #97, and "
    "does not produce a counterexample."
)
PROVENANCE = {
    "generator": "scripts/check_n9_kalmanson_three_row_core_compression.py",
    "command": (
        "python scripts/check_n9_kalmanson_three_row_core_compression.py "
        "--write --assert-expected"
    ),
    "source_packet": "erdos97_progress_packet(11).zip",
}

EXPECTED_N = 9
EXPECTED_ROW_OPTIONS_PER_CENTER = 70
EXPECTED_RAW_ASSIGNMENT_COUNT = 40_353_607_000_000_000
EXPECTED_NODES_VISITED = 100_818
EXPECTED_TERMINAL_ASSIGNMENTS = 184
EXPECTED_KALMANSON_KILLS = 184
EXPECTED_UNKILLED = 0
EXPECTED_KALMANSON_KIND_COUNTS = {"K1": 150, "K2": 34}
EXPECTED_DISTINCT_ROW0_CHOICES = 32
EXPECTED_FRONTIER_SHA256 = "3e6e208cd4212f9275eba2f0be9e32558da9b77544304d33d09abc953feeee9d"
EXPECTED_COMPRESSED_SHA256 = (
    "55edb73475517dcc4e8413cdb84082957bc8426d2d67bd25cc28502ef3c124c0"
)
EXPECTED_FIRST_CORE_SIZE_HISTOGRAM = {"3": 90, "4": 53, "5": 31, "6": 6, "7": 4}
EXPECTED_BEST_CORE_SIZE_HISTOGRAM = {"3": 184}
EXPECTED_BEST_CORE_SIZE_BY_KIND = {"K1": {"3": 95}, "K2": {"3": 89}}
EXPECTED_FIRST_CORE_SIGNATURES = 93
EXPECTED_BEST_CORE_SIGNATURES = 56

FORBIDDEN_CLAIMS = (
    "general proof of Erdos Problem #97",
    "counterexample to Erdos Problem #97",
    "n=9 is proved",
    "official/global status update",
    "source-of-truth strongest result",
    "independent review complete",
)


def canonical_pair(a: int, b: int) -> Pair:
    if a == b:
        raise ValueError("distance pair has repeated endpoint")
    return (a, b) if a < b else (b, a)


def cyclic_between(x: int, a: int, b: int) -> bool:
    if a < b:
        return a < x < b
    return x > a or x < b


def chords_cross(a: int, b: int, c: int, d: int) -> bool:
    if len({a, b, c, d}) < 4:
        return False
    return cyclic_between(c, a, b) != cyclic_between(d, a, b)


def row_compatible(center_a: int, row_a: Row, center_b: int, row_b: Row) -> bool:
    """Necessary selected-row compatibility in the fixed cyclic order."""
    common = set(row_a).intersection(row_b)
    if len(common) > 2:
        return False
    if len(common) == 2:
        x, y = tuple(common)
        return chords_cross(center_a, center_b, x, y)
    return True


class DSU:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1


def enumerate_selected_witness_frontier(n: int) -> tuple[list[Assignment], dict[str, Any]]:
    """Enumerate terminal row systems surviving exact selected-witness filters."""
    vertices = tuple(range(n))
    rows: dict[int, list[Row]] = {
        i: [tuple(c) for c in combinations([v for v in vertices if v != i], 4)]
        for i in vertices
    }
    row_pairs: dict[Row, tuple[Pair, ...]] = {
        r: tuple(canonical_pair(a, b) for a, b in combinations(r, 2))
        for center_rows in rows.values()
        for r in center_rows
    }

    compat: dict[tuple[int, int], dict[Row, set[Row]]] = {}
    for i in vertices:
        for j in vertices:
            if i >= j:
                continue
            table: dict[Row, set[Row]] = {}
            for ri in rows[i]:
                table[ri] = {rj for rj in rows[j] if row_compatible(i, ri, j, rj)}
            compat[(i, j)] = table

    def compat_rows(i: int, ri: Row, j: int, rj: Row) -> bool:
        if i < j:
            return rj in compat[(i, j)][ri]
        return ri in compat[(j, i)][rj]

    def valid_options(center: int, assigned: dict[int, Row], pair_counts: dict[Pair, int]) -> list[Row]:
        out: list[Row] = []
        for row in rows[center]:
            if any(pair_counts.get(p, 0) >= 2 for p in row_pairs[row]):
                continue
            ok = True
            for other_center, other_row in assigned.items():
                if not compat_rows(center, row, other_center, other_row):
                    ok = False
                    break
            if ok:
                out.append(row)
        return out

    terminals: list[Assignment] = []
    assigned: dict[int, Row] = {}
    pair_counts: dict[Pair, int] = {}
    nodes = 0
    dead_by_depth: Counter[int] = Counter()
    branch_histogram: Counter[int] = Counter()

    def rec() -> None:
        nonlocal nodes
        nodes += 1
        if len(assigned) == n:
            terminals.append(tuple(assigned[i] for i in vertices))
            return

        best_center: int | None = None
        best_options: list[Row] | None = None
        for center in vertices:
            if center in assigned:
                continue
            options = valid_options(center, assigned, pair_counts)
            if best_options is None or len(options) < len(best_options):
                best_center = center
                best_options = options
                if not options:
                    break

        assert best_center is not None and best_options is not None
        branch_histogram[len(best_options)] += 1
        if not best_options:
            dead_by_depth[len(assigned)] += 1
            return

        for row in best_options:
            assigned[best_center] = row
            for p in row_pairs[row]:
                pair_counts[p] = pair_counts.get(p, 0) + 1
            rec()
            for p in row_pairs[row]:
                new_value = pair_counts[p] - 1
                if new_value:
                    pair_counts[p] = new_value
                else:
                    del pair_counts[p]
            del assigned[best_center]

    rec()
    stats = {
        "nodes_visited": nodes,
        "dead_by_depth": {str(k): v for k, v in sorted(dead_by_depth.items())},
        "branch_histogram": {str(k): v for k, v in sorted(branch_histogram.items())},
    }
    return sorted(terminals), stats


def validate_terminal(n: int, assignment: Assignment) -> None:
    pair_counts: Counter[Pair] = Counter()
    for center, row in enumerate(assignment):
        if len(row) != 4 or len(set(row)) != 4:
            raise AssertionError(f"bad row shape at center {center}: {row}")
        if center in row:
            raise AssertionError(f"center {center} appears in its own row")
        for p in combinations(row, 2):
            pair_counts[canonical_pair(*p)] += 1
    too_many = {p: c for p, c in pair_counts.items() if c > 2}
    if too_many:
        raise AssertionError(f"witness-pair capacity violation: {too_many}")
    for i in range(n):
        for j in range(i + 1, n):
            if not row_compatible(i, assignment[i], j, assignment[j]):
                raise AssertionError(f"row-pair incompatibility at centers {i},{j}")


def quotient_distance_classes(n: int, assignment: Assignment, row_indices: Iterable[int] | None = None) -> dict[Pair, int]:
    pairs = [canonical_pair(a, b) for a, b in combinations(range(n), 2)]
    pair_index = {p: i for i, p in enumerate(pairs)}
    dsu = DSU(len(pairs))
    if row_indices is None:
        active = range(n)
    else:
        active = tuple(row_indices)
    for center in active:
        row = assignment[center]
        base: int | None = None
        for witness in row:
            idx = pair_index[canonical_pair(center, witness)]
            if base is None:
                base = idx
            else:
                dsu.union(base, idx)
    root_to_class: dict[int, int] = {}
    quotient: dict[Pair, int] = {}
    for p in pairs:
        root = dsu.find(pair_index[p])
        if root not in root_to_class:
            root_to_class[root] = len(root_to_class)
        quotient[p] = root_to_class[root]
    return quotient


def class_multiset(quotient: dict[Pair, int], pairs: Sequence[Pair]) -> tuple[int, ...]:
    return tuple(sorted(quotient[canonical_pair(*p)] for p in pairs))


def all_kalmanson_candidates(n: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for a, b, c, d in combinations(range(n), 4):
        out.append(
            {
                "kind": "K1",
                "description": "D_ab + D_cd < D_ac + D_bd",
                "quadrilateral": [a, b, c, d],
                "left_pairs": [canonical_pair(a, b), canonical_pair(c, d)],
                "right_pairs": [canonical_pair(a, c), canonical_pair(b, d)],
            }
        )
        out.append(
            {
                "kind": "K2",
                "description": "D_ad + D_bc < D_ac + D_bd",
                "quadrilateral": [a, b, c, d],
                "left_pairs": [canonical_pair(a, d), canonical_pair(b, c)],
                "right_pairs": [canonical_pair(a, c), canonical_pair(b, d)],
            }
        )
    return out


def candidate_is_self_edge(n: int, assignment: Assignment, candidate: dict[str, Any], row_indices: Iterable[int] | None = None) -> bool:
    quotient = quotient_distance_classes(n, assignment, row_indices=row_indices)
    return class_multiset(quotient, candidate["left_pairs"]) == class_multiset(quotient, candidate["right_pairs"])


def normalize_candidate_for_json(candidate: dict[str, Any], quotient: dict[Pair, int]) -> dict[str, Any]:
    left_classes = class_multiset(quotient, candidate["left_pairs"])
    right_classes = class_multiset(quotient, candidate["right_pairs"])
    return {
        "kind": candidate["kind"],
        "description": candidate["description"],
        "quadrilateral": candidate["quadrilateral"],
        "left_pairs": [list(p) for p in candidate["left_pairs"]],
        "right_pairs": [list(p) for p in candidate["right_pairs"]],
        "left_classes": list(left_classes),
        "right_classes": list(right_classes),
    }


def find_first_kalmanson_self_edge(n: int, assignment: Assignment) -> dict[str, Any] | None:
    quotient = quotient_distance_classes(n, assignment)
    for candidate in all_kalmanson_candidates(n):
        if class_multiset(quotient, candidate["left_pairs"]) == class_multiset(quotient, candidate["right_pairs"]):
            return normalize_candidate_for_json(candidate, quotient)
    return None


def find_all_kalmanson_self_edges(n: int, assignment: Assignment) -> list[dict[str, Any]]:
    quotient = quotient_distance_classes(n, assignment)
    out: list[dict[str, Any]] = []
    for candidate in all_kalmanson_candidates(n):
        if class_multiset(quotient, candidate["left_pairs"]) == class_multiset(quotient, candidate["right_pairs"]):
            out.append(normalize_candidate_for_json(candidate, quotient))
    return out


def candidate_from_json(cert: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": cert["kind"],
        "description": cert.get("description", ""),
        "quadrilateral": list(cert["quadrilateral"]),
        "left_pairs": [tuple(p) for p in cert["left_pairs"]],
        "right_pairs": [tuple(p) for p in cert["right_pairs"]],
    }


def subset_masks_by_size(n: int) -> list[tuple[int, tuple[int, ...]]]:
    masks: list[tuple[int, tuple[int, ...]]] = []
    for size in range(n + 1):
        for subset in combinations(range(n), size):
            mask = sum(1 << i for i in subset)
            masks.append((mask, subset))
    return masks


def compress_candidate_core(n: int, assignment: Assignment, cert: dict[str, Any]) -> dict[str, Any]:
    """Find a row-minimal subset that already gives this Kalmanson self-edge."""
    candidate = candidate_from_json(cert)
    checked_by_size: Counter[int] = Counter()
    for mask, subset in subset_masks_by_size(n):
        checked_by_size[len(subset)] += 1
        if candidate_is_self_edge(n, assignment, candidate, row_indices=subset):
            # Exhaustive size-ordered search proves no smaller subset worked.
            return {
                "row_indices": list(subset),
                "row_count": len(subset),
                "mask": mask,
                "minimality": "row-minimal by exhaustive subset search in increasing cardinality",
                "subsets_checked_before_first_hit_by_size": {
                    str(k): checked_by_size[k] for k in sorted(checked_by_size)
                },
            }
    raise AssertionError("full assignment was a self-edge, but no subset reproduced it")




def find_best_kalmanson_core(n: int, assignment: Assignment) -> tuple[dict[str, Any], dict[str, Any]]:
    """Find a row-minimal core over all strict Kalmanson inequalities."""
    candidates = all_kalmanson_candidates(n)
    checked_by_size: Counter[int] = Counter()
    for mask, subset in subset_masks_by_size(n):
        checked_by_size[len(subset)] += 1
        quotient = quotient_distance_classes(n, assignment, row_indices=subset)
        for candidate in candidates:
            if class_multiset(quotient, candidate["left_pairs"]) == class_multiset(quotient, candidate["right_pairs"]):
                cert = normalize_candidate_for_json(candidate, quotient)
                core = {
                    "row_indices": list(subset),
                    "row_count": len(subset),
                    "mask": mask,
                    "minimality": "row-minimal over all Kalmanson self-edges by exhaustive subset search in increasing cardinality",
                    "subsets_checked_before_first_hit_by_size": {
                        str(k): checked_by_size[k] for k in sorted(checked_by_size)
                    },
                }
                return cert, core
    raise AssertionError("full assignment has no Kalmanson core")

def relabel_pair(pair: Pair, perm: Sequence[int]) -> Pair:
    return canonical_pair(perm[pair[0]], perm[pair[1]])


def dihedral_permutations(n: int) -> list[tuple[int, ...]]:
    perms: list[tuple[int, ...]] = []
    for shift in range(n):
        perms.append(tuple((i + shift) % n for i in range(n)))
    for shift in range(n):
        perms.append(tuple((shift - i) % n for i in range(n)))
    # Preserve order but remove duplicates for small n paranoia.
    return list(dict.fromkeys(perms))


def partial_core_signature(n: int, assignment: Assignment, row_indices: Sequence[int]) -> str:
    """Canonicalize the selected rows in a core under cyclic dihedral relabeling."""
    rows = [(center, assignment[center]) for center in row_indices]
    best: str | None = None
    for perm in dihedral_permutations(n):
        relabelled = []
        for center, row in rows:
            relabelled.append((perm[center], tuple(sorted(perm[x] for x in row))))
        text = json.dumps(sorted(relabelled), separators=(",", ":"))
        if best is None or text < best:
            best = text
    assert best is not None
    return hashlib.sha256(best.encode("utf-8")).hexdigest()[:16]


def canonical_json(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_payload(n: int, *, include_records: bool = True) -> dict[str, Any]:
    if n != EXPECTED_N:
        raise ValueError("this artifact is calibrated for n=9")

    terminals, search_stats = enumerate_selected_witness_frontier(n)
    records: list[dict[str, Any]] = []
    kind_counts: Counter[str] = Counter()
    row0_counts: Counter[Row] = Counter()
    first_core_size_counts: Counter[int] = Counter()
    best_core_size_counts: Counter[int] = Counter()
    all_self_edge_counts: Counter[int] = Counter()
    first_core_signature_counts: Counter[str] = Counter()
    best_core_signature_counts: Counter[str] = Counter()
    first_core_size_by_kind: dict[str, Counter[int]] = defaultdict(Counter)
    best_core_size_by_kind: dict[str, Counter[int]] = defaultdict(Counter)

    frontier_records_for_hash: list[dict[str, Any]] = []

    for idx, assignment in enumerate(terminals):
        validate_terminal(n, assignment)
        cert = find_first_kalmanson_self_edge(n, assignment)
        if cert is None:
            raise AssertionError(f"terminal assignment {idx} has no Kalmanson self-edge")
        all_edges = find_all_kalmanson_self_edges(n, assignment)
        core = compress_candidate_core(n, assignment, cert)
        sig = partial_core_signature(n, assignment, core["row_indices"])
        best_cert, best_core = find_best_kalmanson_core(n, assignment)
        best_sig = partial_core_signature(n, assignment, best_core["row_indices"])
        kind = cert["kind"]
        best_kind = best_cert["kind"]

        kind_counts[kind] += 1
        row0_counts[assignment[0]] += 1
        first_core_size_counts[core["row_count"]] += 1
        best_core_size_counts[best_core["row_count"]] += 1
        all_self_edge_counts[len(all_edges)] += 1
        first_core_signature_counts[sig] += 1
        best_core_signature_counts[best_sig] += 1
        first_core_size_by_kind[kind][core["row_count"]] += 1
        best_core_size_by_kind[best_kind][best_core["row_count"]] += 1

        # Reconstruct the exact certificate shape used by the existing repo
        # frontier replay script so the digest can be compared byte-for-byte.
        repo_style_cert = {
            "quadrilateral": cert["quadrilateral"],
            "kind": f"{cert['kind']}: {cert['description']}",
            "left_pairs": cert["left_pairs"],
            "right_pairs": cert["right_pairs"],
            "left_classes": cert["left_classes"],
            "right_classes": cert["right_classes"],
        }
        frontier_records_for_hash.append(
            {
                "assignment_index": idx,
                "rows": [[int(x) for x in row] for row in assignment],
                "certificate": repo_style_cert,
            }
        )
        if include_records:
            records.append(
                {
                    "assignment_index": idx,
                    "rows": [[int(x) for x in row] for row in assignment],
                    "first_kalmanson_self_edge": cert,
                    "all_kalmanson_self_edge_count": len(all_edges),
                    "first_self_edge_minimal_core": core,
                    "first_self_edge_minimal_core_rows": [
                        {"center": c, "row": list(assignment[c])} for c in core["row_indices"]
                    ],
                    "first_self_edge_dihedral_core_signature16": sig,
                    "best_kalmanson_self_edge": best_cert,
                    "best_kalmanson_minimal_core": best_core,
                    "best_kalmanson_minimal_core_rows": [
                        {"center": c, "row": list(assignment[c])} for c in best_core["row_indices"]
                    ],
                    "best_kalmanson_dihedral_core_signature16": best_sig,
                }
            )

    frontier_payload = {"n": n, "records": frontier_records_for_hash}
    frontier_sha = hashlib.sha256(canonical_json(frontier_payload)).hexdigest()
    compressed_payload = {"n": n, "records": records}
    compressed_sha = hashlib.sha256(canonical_json(compressed_payload)).hexdigest()

    first_core_signature_top = [
        {"signature16": sig, "count": count} for sig, count in first_core_signature_counts.most_common(20)
    ]
    best_core_signature_top = [
        {"signature16": sig, "count": count} for sig, count in best_core_signature_counts.most_common(20)
    ]

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n,
        "row_size": 4,
        "cyclic_order": list(range(n)),
        "raw_options_per_center": math.comb(n - 1, 4),
        "raw_assignment_count": math.comb(n - 1, 4) ** n,
        "necessary_filters": [
            "row intersection cap |S_i cap S_j| <= 2",
            "two-overlap radical-axis crossing/bisection predicate in cyclic order 0..8",
            "witness-pair capacity: each unordered witness pair occurs in at most two selected rows",
        ],
        "terminal_assignments_after_filters": len(terminals),
        "terminal_assignments_killed_by_first_kalmanson_self_edge": len(terminals),
        "unkilled_terminal_assignments": 0,
        "kalmanson_kind_counts": dict(sorted(kind_counts.items())),
        "nodes_visited": search_stats["nodes_visited"],
        "dead_by_depth": search_stats["dead_by_depth"],
        "branch_histogram": search_stats["branch_histogram"],
        "distinct_row0_choices_in_frontier": len(row0_counts),
        "row0_histogram_top10": [
            {"row0": list(row), "count": count} for row, count in row0_counts.most_common(10)
        ],
        "core_compression": {
            "row_minimality_verified_by_exhaustive_subset_search": True,
            "first_self_edge_minimal_core_size_histogram": {str(k): v for k, v in sorted(first_core_size_counts.items())},
            "first_self_edge_minimal_core_size_by_kalmanson_kind": {
                kind: {str(k): v for k, v in sorted(counter.items())}
                for kind, counter in sorted(first_core_size_by_kind.items())
            },
            "first_self_edge_max_minimal_core_rows": max(first_core_size_counts) if first_core_size_counts else None,
            "first_self_edge_min_minimal_core_rows": min(first_core_size_counts) if first_core_size_counts else None,
            "first_self_edge_distinct_dihedral_core_signatures16": len(first_core_signature_counts),
            "first_self_edge_dihedral_core_signature_top20": first_core_signature_top,
            "best_kalmanson_minimal_core_size_histogram": {str(k): v for k, v in sorted(best_core_size_counts.items())},
            "best_kalmanson_minimal_core_size_by_kalmanson_kind": {
                kind: {str(k): v for k, v in sorted(counter.items())}
                for kind, counter in sorted(best_core_size_by_kind.items())
            },
            "best_kalmanson_max_minimal_core_rows": max(best_core_size_counts) if best_core_size_counts else None,
            "best_kalmanson_min_minimal_core_rows": min(best_core_size_counts) if best_core_size_counts else None,
            "best_kalmanson_distinct_dihedral_core_signatures16": len(best_core_signature_counts),
            "best_kalmanson_dihedral_core_signature_top20": best_core_signature_top,
            "all_kalmanson_self_edge_count_histogram": {
                str(k): v for k, v in sorted(all_self_edge_counts.items())
            },
        },
        "frontier_replay_compatibility": {
            "frontier_certificate_sha256_matches_repo_script_expectation": frontier_sha == EXPECTED_FRONTIER_SHA256,
            "frontier_certificate_sha256": frontier_sha,
            "expected_frontier_certificate_sha256": EXPECTED_FRONTIER_SHA256,
        },
        "compressed_certificate_sha256": compressed_sha,
        "review_independence": {
            "imports_erdos97_package_modules": False,
            "reads_stored_kalmanson_certificate": False,
            "regenerates_frontier": True,
            "uses_python_standard_library_only": True,
        },
        "interpretation_warnings": [
            "This is review-pending finite-case corroboration and compression evidence only.",
            "It relies on the selected-witness finite encoding, the two-overlap crossing predicate, and the strict Kalmanson inequality convention.",
            "It does not prove Erdos Problem #97, produce a counterexample, or update official/global status.",
        ],
        "not_claimed": list(FORBIDDEN_CLAIMS),
        "provenance": dict(PROVENANCE),
    }
    if include_records:
        payload["records"] = records
    return payload


def summary_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key != "records"}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def assert_expected_payload(payload: dict[str, Any]) -> None:
    errors: list[str] = []
    expected_scalars = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": EXPECTED_N,
        "raw_options_per_center": EXPECTED_ROW_OPTIONS_PER_CENTER,
        "raw_assignment_count": EXPECTED_RAW_ASSIGNMENT_COUNT,
        "terminal_assignments_after_filters": EXPECTED_TERMINAL_ASSIGNMENTS,
        "terminal_assignments_killed_by_first_kalmanson_self_edge": EXPECTED_KALMANSON_KILLS,
        "unkilled_terminal_assignments": EXPECTED_UNKILLED,
        "nodes_visited": EXPECTED_NODES_VISITED,
        "distinct_row0_choices_in_frontier": EXPECTED_DISTINCT_ROW0_CHOICES,
    }
    for key, expected in expected_scalars.items():
        if payload.get(key) != expected:
            errors.append(f"{key}: expected {expected!r}, got {payload.get(key)!r}")
    if payload.get("kalmanson_kind_counts") != EXPECTED_KALMANSON_KIND_COUNTS:
        errors.append(
            "kalmanson_kind_counts: expected "
            f"{EXPECTED_KALMANSON_KIND_COUNTS!r}, got {payload.get('kalmanson_kind_counts')!r}"
        )
    compression = payload.get("core_compression", {})
    if not isinstance(compression, dict):
        errors.append("core_compression must be a dict")
        compression = {}
    expected_compression = {
        "first_self_edge_minimal_core_size_histogram": EXPECTED_FIRST_CORE_SIZE_HISTOGRAM,
        "best_kalmanson_minimal_core_size_histogram": EXPECTED_BEST_CORE_SIZE_HISTOGRAM,
        "best_kalmanson_minimal_core_size_by_kalmanson_kind": EXPECTED_BEST_CORE_SIZE_BY_KIND,
        "first_self_edge_distinct_dihedral_core_signatures16": EXPECTED_FIRST_CORE_SIGNATURES,
        "best_kalmanson_distinct_dihedral_core_signatures16": EXPECTED_BEST_CORE_SIGNATURES,
    }
    for key, expected in expected_compression.items():
        if compression.get(key) != expected:
            errors.append(f"core_compression.{key}: expected {expected!r}, got {compression.get(key)!r}")
    if payload.get("compressed_certificate_sha256") != EXPECTED_COMPRESSED_SHA256:
        errors.append(
            "compressed_certificate_sha256: expected "
            f"{EXPECTED_COMPRESSED_SHA256!r}, got {payload.get('compressed_certificate_sha256')!r}"
        )
    compat = payload.get("frontier_replay_compatibility", {})
    if not compat.get("frontier_certificate_sha256_matches_repo_script_expectation"):
        errors.append("frontier certificate sha256 does not match expected repo-script hash")
    records = payload.get("records")
    if records is not None:
        if not isinstance(records, list):
            errors.append("records must be a list when present")
        elif len(records) != EXPECTED_TERMINAL_ASSIGNMENTS:
            errors.append(f"records: expected {EXPECTED_TERMINAL_ASSIGNMENTS}, got {len(records)}")
    text_blob = json.dumps(payload, sort_keys=True)
    for forbidden in FORBIDDEN_CLAIMS:
        if forbidden in text_blob and forbidden not in payload.get("not_claimed", []):
            errors.append(f"forbidden overclaim appears outside not_claimed: {forbidden}")
    if errors:
        raise AssertionError("\n".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=EXPECTED_N)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write the generated artifact")
    parser.add_argument("--check", action="store_true", help="compare regenerated payload with --artifact")
    parser.add_argument("--assert-expected", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument("--summary-json", action="store_true", help="print summary JSON without records")
    args = parser.parse_args()

    if args.n != EXPECTED_N:
        parser.error("this checker is calibrated and expected-count checked for n=9 only")

    payload = build_payload(args.n, include_records=True)
    if args.assert_expected:
        assert_expected_payload(payload)
    if args.check:
        stored = load_json(args.artifact)
        if stored != payload:
            raise AssertionError(f"{args.artifact} does not match regenerated payload")
    if args.write:
        write_json(args.artifact, payload)

    if args.summary_json:
        print(json.dumps(summary_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        summary = summary_payload(payload)
        print("n=9 Kalmanson self-edge core compression")
        print(f"terminal assignments: {summary['terminal_assignments_after_filters']}")
        print(f"killed by first Kalmanson self-edge: {summary['terminal_assignments_killed_by_first_kalmanson_self_edge']}")
        print(f"unkilled: {summary['unkilled_terminal_assignments']}")
        print(
            "first-self-edge minimal core size histogram: "
            f"{summary['core_compression']['first_self_edge_minimal_core_size_histogram']}"
        )
        print(f"best-core histogram: {summary['core_compression']['best_kalmanson_minimal_core_size_histogram']}")
        print(f"best distinct dihedral core signatures: {summary['core_compression']['best_kalmanson_distinct_dihedral_core_signatures16']}")
        print(f"frontier sha256: {summary['frontier_replay_compatibility']['frontier_certificate_sha256']}")
        print(f"compressed sha256: {summary['compressed_certificate_sha256']}")
        if args.write:
            print(f"wrote {args.artifact}")
        if args.assert_expected:
            print("OK: expected n=9 frontier replay counts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
