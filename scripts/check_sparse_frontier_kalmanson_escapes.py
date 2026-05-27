#!/usr/bin/env python3
"""Audit sparse-frontier fixed orders that escape two-inequality Kalmanson pairs.

This checker treats ``data/certificates/c25_c29_sparse_frontier_probe.json`` as
input data and independently recomputes the selected-distance quotient plus the
strict Kalmanson row vectors for the stored C25/C29 fixed cyclic orders.

Scope: fixed-order filter diagnostic only.  A zero-conflict result is a
counterexample to this lightweight inverse-pair filter, not a geometric
counterexample and not an all-order obstruction claim.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data" / "certificates" / "c25_c29_sparse_frontier_probe.json"
DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "sparse_frontier_kalmanson_escape_audit.json"
)

Pair = tuple[int, int]
Quad = tuple[int, int, int, int]
Vector = tuple[tuple[int, int], ...]
KINDS = ("K1_diag_gt_sides", "K2_diag_gt_other")

SCHEMA = "erdos97.sparse_frontier_kalmanson_escape_audit.v1"
STATUS = "SPARSE_FRONTIER_TWO_INEQUALITY_FILTER_ESCAPE_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "This checker verifies only fixed cyclic orders from the sparse-frontier "
    "probe artifact. It tests whether the direct two-inequality Kalmanson "
    "inverse-pair filter sees a contradiction after selected-distance "
    "quotienting. It is not an all-order obstruction, not a geometric "
    "realizability result, not a counterexample, and not a proof of Erdos "
    "Problem #97."
)
PROVENANCE = {
    "generator": "scripts/check_sparse_frontier_kalmanson_escapes.py",
    "command": (
        "python scripts/check_sparse_frontier_kalmanson_escapes.py "
        "--write --assert-expected"
    ),
    "source_artifact": "data/certificates/c25_c29_sparse_frontier_probe.json",
}

PATTERN_OFFSETS = {
    "C25_sidon_2_5_9_14": [2, 5, 9, 14],
    "C29_sidon_1_3_7_15": [1, 3, 7, 15],
}
EXPECTED = {
    "C25_sidon_2_5_9_14:kalmanson_z3_step7_survivor": {
        "n": 25,
        "distance_class_count": 225,
        "selected_distance_class_size_histogram": {"1": 200, "4": 25},
        "full_kalmanson_rows_seen": 25300,
        "inverse_pair_conflicts": 0,
        "stored_rows_seen": 25025,
        "stored_row_count_matches_full_replay": False,
    },
    "C29_sidon_1_3_7_15:z3_kalmanson_survivor": {
        "n": 29,
        "distance_class_count": 319,
        "selected_distance_class_size_histogram": {"1": 290, "4": 29},
        "full_kalmanson_rows_seen": 47502,
        "inverse_pair_conflicts": 0,
        "stored_rows_seen": 47259,
        "stored_row_count_matches_full_replay": False,
    },
}


class DSU:
    def __init__(self, items: Iterable[Pair]) -> None:
        self.parent = {item: item for item in items}

    def find(self, item: Pair) -> Pair:
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, a: Pair, b: Pair) -> None:
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a != root_b:
            self.parent[root_b] = root_a


def pair(a: int, b: int) -> Pair:
    if a == b:
        raise ValueError(f"degenerate pair ({a}, {b})")
    return (a, b) if a < b else (b, a)


def row_witnesses(n: int, offsets: Sequence[int], center: int) -> list[int]:
    witnesses = sorted((center + int(offset)) % n for offset in offsets)
    if center in witnesses or len(set(witnesses)) != 4:
        raise ValueError(f"bad witness row {center}: {witnesses}")
    return witnesses


def build_distance_classes(n: int, offsets: Sequence[int]) -> dict[Pair, int]:
    """Quotient unordered distance-pair variables by selected row equalities."""

    pairs = [pair(a, b) for a, b in itertools.combinations(range(n), 2)]
    dsu = DSU(pairs)
    for center in range(n):
        witnesses = row_witnesses(n, offsets, center)
        base = pair(center, witnesses[0])
        for witness in witnesses[1:]:
            dsu.union(base, pair(center, witness))

    roots: dict[Pair, int] = {}
    classes: dict[Pair, int] = {}
    for item in pairs:
        root = dsu.find(item)
        roots.setdefault(root, len(roots))
        classes[item] = roots[root]
    return classes


def inequality_terms(kind: str, quad: Sequence[int]) -> list[tuple[Pair, int]]:
    """Coefficient terms for one strict convex Kalmanson inequality."""

    if len(quad) != 4 or len(set(quad)) != 4:
        raise ValueError(f"bad Kalmanson quadrilateral: {quad!r}")
    a, b, c, d = (int(label) for label in quad)
    if kind == "K1_diag_gt_sides":
        return [
            (pair(a, c), +1),
            (pair(b, d), +1),
            (pair(a, b), -1),
            (pair(c, d), -1),
        ]
    if kind == "K2_diag_gt_other":
        return [
            (pair(a, c), +1),
            (pair(b, d), +1),
            (pair(a, d), -1),
            (pair(b, c), -1),
        ]
    raise ValueError(f"unknown Kalmanson kind: {kind!r}")


def sparse_vector(classes: Mapping[Pair, int], kind: str, quad: Sequence[int]) -> Vector:
    acc: Counter[int] = Counter()
    for unordered_pair, coefficient in inequality_terms(kind, quad):
        acc[classes[unordered_pair]] += coefficient
    return tuple(sorted((class_id, coefficient) for class_id, coefficient in acc.items() if coefficient))


def validate_order(n: int, order: Sequence[int]) -> None:
    if len(order) != n or sorted(order) != list(range(n)):
        raise ValueError(f"order is not a permutation of 0..{n - 1}: {order!r}")


def source_cases(source: Mapping[str, object]) -> list[Mapping[str, object]]:
    raw_cases = source.get("cases")
    if not isinstance(raw_cases, list):
        raise TypeError("source artifact must contain a cases list")
    selected = []
    for item in raw_cases:
        if not isinstance(item, Mapping):
            raise TypeError("source cases must be objects")
        pattern = str(item.get("pattern"))
        if pattern in PATTERN_OFFSETS:
            selected.append(item)
    return selected


@dataclass(frozen=True)
class CaseResult:
    case: str
    pattern: str
    n: int
    offsets: list[int]
    order: list[int]
    distance_class_count: int
    selected_distance_class_size_histogram: dict[str, int]
    ordered_quad_count: int
    full_kalmanson_rows_expected: int
    full_kalmanson_rows_seen: int
    inverse_pair_conflicts: int
    first_conflict: list[object]
    stored_direct_rows_seen: int | None
    stored_direct_inverse_pair_conflicts: int | None
    stored_direct_first_conflict: object
    stored_row_count_matches_full_replay: bool | None
    stored_conflict_count_matches_full_replay: bool | None
    status: str
    trust: str
    claim_scope: str


def check_case(case: Mapping[str, object]) -> CaseResult:
    pattern = str(case["pattern"])
    n = int(case["n"])
    offsets = PATTERN_OFFSETS[pattern]
    order = [int(label) for label in case["order"]]  # type: ignore[index]
    validate_order(n, order)

    classes = build_distance_classes(n, offsets)
    class_sizes = Counter(classes.values())
    class_histogram = Counter(class_sizes.values())

    seen: dict[Vector, tuple[str, Quad]] = {}
    conflicts: list[tuple[tuple[str, Quad], tuple[str, Quad]]] = []
    rows_seen = 0
    for quad_raw in itertools.combinations(order, 4):
        quad = tuple(int(label) for label in quad_raw)
        for kind in KINDS:
            rows_seen += 1
            vector = sparse_vector(classes, kind, quad)
            inverse = tuple((class_id, -coefficient) for class_id, coefficient in vector)
            if inverse in seen:
                conflicts.append((seen[inverse], (kind, quad)))
            seen.setdefault(vector, (kind, quad))

    stored_direct = case.get("direct_kalmanson_inverse_pair_check")
    stored_rows = None
    stored_conflicts = None
    stored_first_conflict: object = None
    if isinstance(stored_direct, Mapping):
        stored_rows_raw = stored_direct.get("rows_seen")
        stored_conflicts_raw = stored_direct.get("inverse_pair_conflicts")
        stored_rows = None if stored_rows_raw is None else int(stored_rows_raw)
        stored_conflicts = None if stored_conflicts_raw is None else int(stored_conflicts_raw)
        stored_first_conflict = stored_direct.get("first_conflict")

    full_expected = 2 * math.comb(n, 4)
    return CaseResult(
        case=str(case["case"]),
        pattern=pattern,
        n=n,
        offsets=list(offsets),
        order=order,
        distance_class_count=len(set(classes.values())),
        selected_distance_class_size_histogram={
            str(size): class_histogram[size] for size in sorted(class_histogram)
        },
        ordered_quad_count=math.comb(n, 4),
        full_kalmanson_rows_expected=full_expected,
        full_kalmanson_rows_seen=rows_seen,
        inverse_pair_conflicts=len(conflicts),
        first_conflict=[] if not conflicts else [list(conflicts[0][0]), list(conflicts[0][1])],
        stored_direct_rows_seen=stored_rows,
        stored_direct_inverse_pair_conflicts=stored_conflicts,
        stored_direct_first_conflict=stored_first_conflict,
        stored_row_count_matches_full_replay=(None if stored_rows is None else stored_rows == rows_seen),
        stored_conflict_count_matches_full_replay=(
            None if stored_conflicts is None else stored_conflicts == len(conflicts)
        ),
        status=(
            "FIXED_ORDER_ESCAPES_TWO_INEQUALITY_KALMANSON_INVERSE_PAIR_FILTER"
            if not conflicts
            else "FIXED_ORDER_HAS_TWO_INEQUALITY_KALMANSON_INVERSE_PAIR_OBSTRUCTION"
        ),
        trust=TRUST,
        claim_scope=CLAIM_SCOPE,
    )


def diagnostic_payload(*, source_artifact: Path = DEFAULT_SOURCE) -> dict[str, object]:
    source = json.loads(source_artifact.read_text(encoding="utf-8"))
    if not isinstance(source, Mapping):
        raise TypeError("source artifact must be a JSON object")
    if source.get("type") != "c25_c29_sparse_frontier_probe_v1":
        raise AssertionError("source sparse-frontier probe artifact type drifted")
    case_results = [asdict(check_case(case)) for case in source_cases(source)]
    if sorted(result["case"] for result in case_results) != sorted(EXPECTED):
        raise AssertionError("source sparse-frontier probe cases drifted")
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifact": (
            source_artifact.relative_to(ROOT).as_posix()
            if source_artifact.is_relative_to(ROOT)
            else str(source_artifact)
        ),
        "cases": case_results,
        "interpretation": (
            "The stored C25 and C29 sparse/Sidon fixed orders remain exact escapes "
            "from the direct two-inequality Kalmanson inverse-pair filter even "
            "when the audit checks all 2*binom(n,4) strict Kalmanson rows. The "
            "stored probe's rows_seen counters do not match the full-row replay, "
            "but the zero-conflict conclusion is confirmed. Thus this lightweight "
            "inverse-pair route alone cannot retire these sparse-frontier orders; "
            "stronger fixed-order certificates or additional geometric filters are needed."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected(payload: Mapping[str, object]) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("claim_scope") != CLAIM_SCOPE:
        raise AssertionError(f"claim_scope mismatch: {payload.get('claim_scope')!r}")
    claim_scope = CLAIM_SCOPE
    for required in (
        "not an all-order obstruction",
        "not a geometric realizability result",
        "not a counterexample",
        "not a proof of Erdos Problem #97",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")

    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise AssertionError("payload cases must be a list")
    expected = dict(EXPECTED)
    for observed in cases:
        if not isinstance(observed, Mapping):
            raise AssertionError("case result must be an object")
        name = str(observed["case"])
        spec = expected.pop(name)
        for key in (
            "n",
            "distance_class_count",
            "selected_distance_class_size_histogram",
            "full_kalmanson_rows_seen",
            "inverse_pair_conflicts",
            "stored_row_count_matches_full_replay",
        ):
            if observed.get(key) != spec[key]:
                raise AssertionError(
                    f"{name}: {key} changed: expected {spec[key]!r}, got {observed.get(key)!r}"
                )
        if observed.get("full_kalmanson_rows_expected") != observed.get("full_kalmanson_rows_seen"):
            raise AssertionError(f"{name}: did not enumerate all full Kalmanson rows")
        if observed.get("first_conflict") != []:
            raise AssertionError(f"{name}: unexpected first conflict {observed.get('first_conflict')!r}")
        if observed.get("stored_direct_rows_seen") != spec["stored_rows_seen"]:
            raise AssertionError(f"{name}: stored rows_seen changed")
        if observed.get("stored_conflict_count_matches_full_replay") is not True:
            raise AssertionError(f"{name}: stored conflict count no longer agrees")
    if expected:
        raise AssertionError(f"missing cases: {sorted(expected)}")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be an object")
    if provenance.get("generator") != PROVENANCE["generator"]:
        raise AssertionError("provenance generator drifted")
    if provenance.get("command") != PROVENANCE["command"]:
        raise AssertionError("provenance command drifted")


def write_artifact(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-artifact", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="compare stored artifact to regenerated payload")
    parser.add_argument("--write", action="store_true", help="write regenerated payload to artifact path")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    source_artifact = args.source_artifact if args.source_artifact.is_absolute() else ROOT / args.source_artifact
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact
    generated = diagnostic_payload(source_artifact=source_artifact)
    payload = generated
    if args.check:
        stored = json.loads(artifact.read_text(encoding="utf-8"))
        if stored != generated:
            raise AssertionError(f"{artifact} is stale relative to regenerated audit")
        payload = stored
    if args.assert_expected:
        assert_expected(payload)
    if args.write:
        write_artifact(artifact, generated)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Sparse-frontier Kalmanson escape audit")
        for case in payload["cases"]:  # type: ignore[index]
            print(
                f"{case['case']}: {case['status']} "
                f"full_rows={case['full_kalmanson_rows_seen']} "
                f"conflicts={case['inverse_pair_conflicts']} "
                f"stored_rows_match={case['stored_row_count_matches_full_replay']}"
            )
        if args.check:
            print("OK: stored sparse-frontier Kalmanson escape audit matches")
        if args.assert_expected:
            print("OK: sparse-frontier Kalmanson escape audit matches expected values")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
