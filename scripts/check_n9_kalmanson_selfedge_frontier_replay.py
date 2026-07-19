#!/usr/bin/env python3
"""Regenerate the n=9 selected-witness frontier and Kalmanson self-edges.

This checker is intentionally self-contained: it imports no ``erdos97`` package
modules and uses no stored n=9 Kalmanson certificate as generation or search
input. In ``--check`` mode, it compares the stored artifact only after fresh
generation. It regenerates the fixed-cyclic-order n=9 selected-witness frontier
from the exact incidence filters, then finds one strict Kalmanson self-edge for
every terminal assignment. The result is primary-route review evidence under
still-open gates; it is not an n=9 promotion, a general proof, or a
counterexample.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Sequence

Vertex = int
Row = tuple[Vertex, Vertex, Vertex, Vertex]
Assignment = tuple[Row, ...]
Pair = tuple[Vertex, Vertex]

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_kalmanson_selfedge_frontier_replay.json"
)

SCHEMA = "erdos97.n9_kalmanson_selfedge_frontier_replay.v1"
STATUS = "REVIEW_PENDING_N9_KALMANSON_SELFEDGE_FRONTIER_REPLAY"
TRUST = "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING"
CLAIM_SCOPE = (
    "Self-contained regeneration of the review-pending n=9 selected-witness "
    "frontier plus one strict Kalmanson self-edge certificate for each of the "
    "184 terminal assignments. It imports no erdos97 package modules and uses "
    "no stored Kalmanson certificate as generation or search input; --check "
    "compares the artifact only after fresh generation. This is primary-route "
    "review evidence under still-open gates: it does not complete independent "
    "review, does not promote n=9 to a theorem, does not prove Erdos Problem "
    "#97, produce a counterexample, or update the official/global status "
    "or the repo source-of-truth strongest local result."
)
PROVENANCE = {
    "generator": "scripts/check_n9_kalmanson_selfedge_frontier_replay.py",
    "command": (
        "python scripts/check_n9_kalmanson_selfedge_frontier_replay.py "
        "--write --assert-expected"
    ),
    "source_packet": "erdos97_progress_n9_kalmanson.zip",
}

EXPECTED_N = 9
EXPECTED_ROW_OPTIONS_PER_CENTER = 70
EXPECTED_RAW_ASSIGNMENT_COUNT = 40_353_607_000_000_000
EXPECTED_NODES_VISITED = 100_818
EXPECTED_TERMINAL_ASSIGNMENTS = 184
EXPECTED_KALMANSON_KILLS = 184
EXPECTED_UNKILLED = 0
EXPECTED_CERTIFICATE_SHA256 = (
    "3e6e208cd4212f9275eba2f0be9e32558da9b77544304d33d09abc953feeee9d"
)
EXPECTED_FRONTIER_ASSIGNMENT_SHA256 = (
    "dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55"
)
EXPECTED_KALMANSON_KIND_COUNTS = {"K1": 150, "K2": 34}
EXPECTED_DISTINCT_ROW0_CHOICES = 32
FORBIDDEN_CLAIMS = (
    "n=9 is proved",
    "independent review complete",
    "source-of-truth strongest result",
    "official/global status update",
    "counterexample to Erdos Problem #97",
    "general proof of Erdos Problem #97",
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

    def valid_options(
        center: int,
        assigned: dict[int, Row],
        pair_counts: dict[Pair, int],
    ) -> list[Row]:
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


def quotient_distance_classes(n: int, assignment: Assignment) -> dict[Pair, int]:
    pairs = [canonical_pair(a, b) for a, b in combinations(range(n), 2)]
    pair_index = {p: i for i, p in enumerate(pairs)}
    dsu = DSU(len(pairs))
    for center, row in enumerate(assignment):
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


def class_multiset(quotient: dict[Pair, int], pairs: Sequence[Pair]) -> tuple[int, int]:
    return tuple(sorted(quotient[canonical_pair(*p)] for p in pairs))  # type: ignore[return-value]


def find_kalmanson_self_edge(n: int, assignment: Assignment) -> dict[str, Any] | None:
    quotient = quotient_distance_classes(n, assignment)
    for a, b, c, d in combinations(range(n), 4):
        candidates = [
            (
                "K1: D_ab + D_cd < D_ac + D_bd",
                (canonical_pair(a, b), canonical_pair(c, d)),
                (canonical_pair(a, c), canonical_pair(b, d)),
            ),
            (
                "K2: D_ad + D_bc < D_ac + D_bd",
                (canonical_pair(a, d), canonical_pair(b, c)),
                (canonical_pair(a, c), canonical_pair(b, d)),
            ),
        ]
        for kind, left, right in candidates:
            left_classes = class_multiset(quotient, left)
            right_classes = class_multiset(quotient, right)
            if left_classes == right_classes:
                return {
                    "quadrilateral": [a, b, c, d],
                    "kind": kind,
                    "left_pairs": [list(p) for p in left],
                    "right_pairs": [list(p) for p in right],
                    "left_classes": list(left_classes),
                    "right_classes": list(right_classes),
                }
    return None


def canonical_json(obj: object) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def build_result(n: int, *, include_certificates: bool = True) -> dict[str, Any]:
    if n != EXPECTED_N:
        raise ValueError("this checker is calibrated for n=9 only")
    terminals, search_stats = enumerate_selected_witness_frontier(n)
    records: list[dict[str, Any]] = []
    kind_counts: Counter[str] = Counter()
    row0_counts: Counter[Row] = Counter()
    for idx, assignment in enumerate(terminals):
        validate_terminal(n, assignment)
        cert = find_kalmanson_self_edge(n, assignment)
        if cert is None:
            raise AssertionError(f"terminal assignment {idx} has no Kalmanson self-edge")
        kind_counts[cert["kind"].split(":", 1)[0]] += 1
        row0_counts[assignment[0]] += 1
        records.append(
            {
                "assignment_index": idx,
                "rows": [[int(x) for x in row] for row in assignment],
                "certificate": cert,
            }
        )

    certificate_payload = {"n": n, "records": records}
    certificate_sha256 = hashlib.sha256(canonical_json(certificate_payload)).hexdigest()
    frontier_assignment_sha256 = hashlib.sha256(canonical_json(sorted(terminals))).hexdigest()
    raw_options_per_center = math.comb(n - 1, 4)
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n,
        "row_size": 4,
        "raw_options_per_center": raw_options_per_center,
        "raw_assignment_count": raw_options_per_center**n,
        "necessary_filters": [
            "row intersection cap |S_i cap S_j| <= 2",
            "two-overlap radical-axis crossing/bisection predicate",
            "witness-pair capacity: each unordered witness pair occurs in at most two selected rows",
        ],
        "terminal_assignments_after_filters": len(terminals),
        "terminal_assignments_killed_by_kalmanson_self_edge": len(records),
        "unkilled_terminal_assignments": len(terminals) - len(records),
        "kalmanson_kind_counts": dict(sorted(kind_counts.items())),
        "nodes_visited": search_stats["nodes_visited"],
        "dead_by_depth": search_stats["dead_by_depth"],
        "distinct_row0_choices_in_frontier": len(row0_counts),
        "frontier_assignment_sha256": frontier_assignment_sha256,
        "row0_histogram_top10": [
            {"row0": list(row), "count": count} for row, count in row0_counts.most_common(10)
        ],
        "certificate_sha256": certificate_sha256,
        "review_independence": {
            "imports_erdos97_package_modules": False,
            "reads_stored_kalmanson_certificate": False,
            "regenerates_frontier": True,
            "uses_python_standard_library_only": True,
        },
        "interpretation_warnings": [
            "This is primary-route finite-case evidence under still-open review gates.",
            "It relies on the standard selected-witness necessary filters and strict Kalmanson inequality convention.",
            "It does not prove n=9, prove Erdos Problem #97, produce a counterexample, or update official/global status.",
        ],
        "not_claimed": list(FORBIDDEN_CLAIMS),
        "provenance": dict(PROVENANCE),
    }
    if include_certificates:
        result["certificates"] = records
    return result


def summary_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the artifact payload without the 184 full certificate records."""

    return {key: value for key, value in payload.items() if key != "certificates"}


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
        "terminal_assignments_killed_by_kalmanson_self_edge": EXPECTED_KALMANSON_KILLS,
        "unkilled_terminal_assignments": EXPECTED_UNKILLED,
        "nodes_visited": EXPECTED_NODES_VISITED,
        "distinct_row0_choices_in_frontier": EXPECTED_DISTINCT_ROW0_CHOICES,
        "certificate_sha256": EXPECTED_CERTIFICATE_SHA256,
        "frontier_assignment_sha256": EXPECTED_FRONTIER_ASSIGNMENT_SHA256,
    }
    for key, expected in expected_scalars.items():
        if payload.get(key) != expected:
            errors.append(f"{key}: expected {expected!r}, got {payload.get(key)!r}")
    if payload.get("kalmanson_kind_counts") != EXPECTED_KALMANSON_KIND_COUNTS:
        errors.append(
            "kalmanson_kind_counts: expected "
            f"{EXPECTED_KALMANSON_KIND_COUNTS!r}, got {payload.get('kalmanson_kind_counts')!r}"
        )
    certificates = payload.get("certificates")
    if certificates is not None:
        if not isinstance(certificates, list):
            errors.append("certificates must be a list when present")
        elif len(certificates) != EXPECTED_TERMINAL_ASSIGNMENTS:
            errors.append(
                "certificates: expected "
                f"{EXPECTED_TERMINAL_ASSIGNMENTS}, got {len(certificates)}"
            )
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
    parser.add_argument("--check", action="store_true", help="compare regenerated payload with artifact")
    parser.add_argument("--assert-expected", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument("--summary-json", action="store_true", help="print JSON without certificates")
    args = parser.parse_args()
    if args.n != EXPECTED_N:
        parser.error("this checker is calibrated and expected-count checked for n=9 only")

    payload = build_result(args.n)
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
        print("n=9 Kalmanson self-edge frontier replay")
        print(f"terminal assignments: {payload['terminal_assignments_after_filters']}")
        print(f"killed by Kalmanson self-edge: {payload['terminal_assignments_killed_by_kalmanson_self_edge']}")
        print(f"unkilled: {payload['unkilled_terminal_assignments']}")
        print(f"certificate sha256: {payload['certificate_sha256']}")
        if args.write:
            print(f"wrote {args.artifact}")
        if args.assert_expected:
            print("OK: n=9 Kalmanson frontier replay counts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
