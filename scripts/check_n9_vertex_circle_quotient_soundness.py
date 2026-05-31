#!/usr/bin/env python3
"""Replay the n=9 vertex-circle selected-distance quotient audit."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97 import n9_vertex_circle_exhaustive as n9  # noqa: E402
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    SelectedRow,
    parse_selected_rows,
    replay_vertex_circle_quotient,
)

DEFAULT_LOCAL_CORE_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_local_core_packet.json"
)
DEFAULT_FRONTIER_CLASSIFICATION = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)

SCHEMA = "erdos97.n9_vertex_circle_quotient_soundness.v1"
STATUS = "REVIEW_PENDING_QUOTIENT_SOUNDNESS_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Selected-distance quotient status audit for the review-pending n=9 "
    "vertex-circle checker. It compares the repo-native checker, the reusable "
    "quotient replay helper, and a direct local quotient/status replay on "
    "stored local-core rows and the 184 stored pre-vertex-circle frontier "
    "assignments. It does not prove row coverage, brancher coverage, "
    "strict-edge geometry, n=9, a counterexample, or any official/global "
    "status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_quotient_soundness.py",
    "command": (
        "python scripts/check_n9_vertex_circle_quotient_soundness.py "
        "--check --assert-expected --json"
    ),
}
SUMMARY_JSON_KEYS = (
    "schema",
    "status",
    "trust",
    "claim_scope",
    "n",
    "row_size",
    "source_artifacts",
    "validation_status",
    "validation_errors",
    "interpretation",
    "provenance",
)
QUOTIENT_SECTION_SUMMARY_KEYS = (
    "label",
    "row_set_count",
    "selected_row_total",
    "spoke_pairs_checked",
    "status_counts",
    "strict_edge_count_histogram",
    "replay_self_edge_conflict_records",
    "replay_cycle_edge_records",
    "direct_self_edge_records",
    "direct_strict_cycle_row_sets",
    "row_equality_component_violations",
    "status_mismatches",
)

EXPECTED_LOCAL_CORE = {
    "row_set_count": 16,
    "selected_row_total": 67,
    "spoke_pairs_checked": 268,
    "status_counts": {"self_edge": 13, "strict_cycle": 3},
    "strict_edge_count_histogram": {27: 5, 36: 6, 45: 2, 54: 3},
    "replay_self_edge_conflict_records": 43,
    "replay_cycle_edge_records": 8,
}
EXPECTED_FRONTIER_FULL = {
    "row_set_count": 184,
    "selected_row_total": 1_656,
    "spoke_pairs_checked": 6_624,
    "status_counts": {"self_edge": 158, "strict_cycle": 26},
    "strict_edge_count_histogram": {81: 184},
    "replay_self_edge_conflict_records": 2_988,
    "replay_cycle_edge_records": 56,
}
EXPECTED_FRONTIER_CORE = {
    "row_set_count": 184,
    "selected_row_total": 802,
    "spoke_pairs_checked": 3_208,
    "status_counts": {"self_edge": 158, "strict_cycle": 26},
    "strict_edge_count_histogram": {27: 46, 36: 64, 45: 36, 54: 38},
    "replay_self_edge_conflict_records": 670,
    "replay_cycle_edge_records": 59,
}

Pair = tuple[int, int]


@dataclass(frozen=True)
class DirectQuotientResult:
    """Small direct replay result for one selected-row set."""

    selected_row_count: int
    strict_edge_count: int
    status: str
    self_edge_count: int
    has_strict_cycle: bool
    row_equality_component_violations: int


class UnionFind:
    """Deterministic union-find over unordered pair labels."""

    def __init__(self, items: Sequence[Pair]) -> None:
        self.parent = {item: item for item in items}

    def find(self, item: Pair) -> Pair:
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, a: Pair, b: Pair) -> None:
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return
        if root_b < root_a:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a


def load_json(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def direct_quotient_result(
    n: int,
    order: Sequence[int],
    rows: Sequence[SelectedRow],
) -> DirectQuotientResult:
    """Replay quotient equalities and strict edges without using helper status code."""

    order_tuple = tuple(int(label) for label in order)
    positions = {label: index for index, label in enumerate(order_tuple)}
    uf = UnionFind(_all_pairs(n))
    for row in rows:
        spokes = [_pair(row.center, witness) for witness in row.witnesses]
        base = spokes[0]
        for spoke in spokes[1:]:
            uf.union(base, spoke)

    row_violations = 0
    for row in rows:
        roots = {uf.find(_pair(row.center, witness)) for witness in row.witnesses}
        if len(roots) != 1:
            row_violations += 1

    edge_roots: list[tuple[Pair, Pair]] = []
    for row in rows:
        witnesses = tuple(
            sorted(
                row.witnesses,
                key=lambda witness: (positions[witness] - positions[row.center]) % n,
            )
        )
        for outer_start in range(4):
            for outer_end in range(outer_start + 1, 4):
                for inner_start in range(4):
                    for inner_end in range(inner_start + 1, 4):
                        if (outer_start, outer_end) == (inner_start, inner_end):
                            continue
                        if not _properly_contains(
                            outer_start,
                            outer_end,
                            inner_start,
                            inner_end,
                        ):
                            continue
                        outer = _pair(witnesses[outer_start], witnesses[outer_end])
                        inner = _pair(witnesses[inner_start], witnesses[inner_end])
                        edge_roots.append((uf.find(outer), uf.find(inner)))

    self_edge_count = sum(outer == inner for outer, inner in edge_roots)
    has_cycle = False if self_edge_count else _has_directed_cycle(edge_roots)
    if self_edge_count:
        status = "self_edge"
    elif has_cycle:
        status = "strict_cycle"
    else:
        status = "ok"
    return DirectQuotientResult(
        selected_row_count=len(rows),
        strict_edge_count=len(edge_roots),
        status=status,
        self_edge_count=self_edge_count,
        has_strict_cycle=has_cycle,
        row_equality_component_violations=row_violations,
    )


def quotient_soundness_payload(
    *,
    local_core_path: Path = DEFAULT_LOCAL_CORE_PACKET,
    frontier_path: Path = DEFAULT_FRONTIER_CLASSIFICATION,
) -> dict[str, Any]:
    """Return a replay audit for n=9 selected-distance quotient soundness."""

    local_core = load_json(local_core_path)
    frontier = load_json(frontier_path)
    errors: list[str] = []

    local_core_summary = _audit_named_row_sets(
        [
            {
                "row_set_id": str(certificate["family_id"]),
                "recorded_status": str(certificate["status"]),
                "rows": certificate["compact_selected_rows"],
            }
            for certificate in local_core["certificates"]
        ],
        label="local core packet",
    )
    frontier_full_summary = _audit_named_row_sets(
        [
            {
                "row_set_id": str(assignment["assignment_id"]),
                "recorded_status": str(assignment["status"]),
                "rows": assignment["selected_rows"],
            }
            for assignment in frontier["assignments"]
        ],
        label="frontier full assignments",
    )
    frontier_core_summary = _audit_named_row_sets(
        [
            {
                "row_set_id": str(assignment["assignment_id"]),
                "recorded_status": str(assignment["status"]),
                "rows": assignment["core_selected_rows"],
            }
            for assignment in frontier["assignments"]
        ],
        label="frontier transformed cores",
    )

    _check_section(errors, "local_core_packet", local_core_summary, EXPECTED_LOCAL_CORE)
    _check_section(
        errors,
        "frontier_full_assignments",
        frontier_full_summary,
        EXPECTED_FRONTIER_FULL,
    )
    _check_section(
        errors,
        "frontier_core_assignments",
        frontier_core_summary,
        EXPECTED_FRONTIER_CORE,
    )

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "local_core_packet": local_core_summary,
        "frontier_full_assignments": frontier_full_summary,
        "frontier_core_assignments": frontier_core_summary,
        "source_artifacts": [
            _source_metadata(local_core_path, local_core),
            _source_metadata(frontier_path, frontier),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says stored n=9 local-core rows and stored "
            "pre-vertex-circle frontier rows get the same quotient-obstruction "
            "status from the exhaustive checker, the reusable replay helper, "
            "and a small direct quotient/status replay. This is quotient "
            "implementation agreement only."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_quotient_soundness(payload: Mapping[str, Any]) -> None:
    """Assert the expected quotient-soundness replay audit result."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
    if payload.get("claim_scope") != CLAIM_SCOPE:
        raise AssertionError(f"claim_scope mismatch: {payload.get('claim_scope')!r}")
    claim_scope = CLAIM_SCOPE
    for required in (
        "does not prove row coverage",
        "brancher coverage",
        "strict-edge geometry",
        "n=9",
        "counterexample",
        "official/global status update",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")
    _assert_section("local_core_packet", payload, EXPECTED_LOCAL_CORE)
    _assert_section("frontier_full_assignments", payload, EXPECTED_FRONTIER_FULL)
    _assert_section("frontier_core_assignments", payload, EXPECTED_FRONTIER_CORE)


def _audit_named_row_sets(
    row_sets: Sequence[Mapping[str, Any]],
    *,
    label: str,
) -> dict[str, Any]:
    replay_status_counts: Counter[str] = Counter()
    checker_status_counts: Counter[str] = Counter()
    direct_status_counts: Counter[str] = Counter()
    recorded_status_counts: Counter[str] = Counter()
    strict_edge_histogram: Counter[int] = Counter()
    selected_row_total = 0
    spoke_pairs_checked = 0
    replay_self_edge_conflicts = 0
    replay_cycle_edges = 0
    direct_self_edges = 0
    direct_strict_cycle_count = 0
    row_equality_component_violations = 0
    status_mismatches = 0
    example_mismatches: list[dict[str, Any]] = []

    for row_set in row_sets:
        row_set_id = str(row_set["row_set_id"])
        recorded_status = str(row_set["recorded_status"])
        rows = parse_selected_rows(row_set["rows"])
        replay = replay_vertex_circle_quotient(n9.N, n9.ORDER, rows)
        direct = direct_quotient_result(n9.N, n9.ORDER, rows)
        checker_status = n9.vertex_circle_status(_assignment_from_rows(rows))

        selected_row_total += len(rows)
        spoke_pairs_checked += len(rows) * n9.ROW_SIZE
        replay_status_counts[replay.status] += 1
        checker_status_counts[checker_status] += 1
        direct_status_counts[direct.status] += 1
        recorded_status_counts[recorded_status] += 1
        strict_edge_histogram[replay.strict_edge_count] += 1
        replay_self_edge_conflicts += len(replay.self_edge_conflicts)
        replay_cycle_edges += len(replay.cycle_edges)
        direct_self_edges += direct.self_edge_count
        if direct.has_strict_cycle:
            direct_strict_cycle_count += 1
        row_equality_component_violations += direct.row_equality_component_violations

        statuses = {
            "recorded": recorded_status,
            "checker": checker_status,
            "replay": replay.status,
            "direct": direct.status,
        }
        if len(set(statuses.values())) != 1:
            status_mismatches += 1
            if len(example_mismatches) < 5:
                example_mismatches.append({"row_set_id": row_set_id, "statuses": statuses})

    return {
        "label": label,
        "row_set_count": len(row_sets),
        "selected_row_total": selected_row_total,
        "spoke_pairs_checked": spoke_pairs_checked,
        "status_counts": dict(sorted(replay_status_counts.items())),
        "recorded_status_counts": dict(sorted(recorded_status_counts.items())),
        "checker_status_counts": dict(sorted(checker_status_counts.items())),
        "replay_status_counts": dict(sorted(replay_status_counts.items())),
        "direct_status_counts": dict(sorted(direct_status_counts.items())),
        "strict_edge_count_histogram": dict(sorted(strict_edge_histogram.items())),
        "replay_self_edge_conflict_records": replay_self_edge_conflicts,
        "replay_cycle_edge_records": replay_cycle_edges,
        "direct_self_edge_records": direct_self_edges,
        "direct_strict_cycle_row_sets": direct_strict_cycle_count,
        "row_equality_component_violations": row_equality_component_violations,
        "status_mismatches": status_mismatches,
        "example_mismatches": example_mismatches,
    }


def _check_section(
    errors: list[str],
    name: str,
    section: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> None:
    if section.get("status_mismatches") != 0:
        errors.append(f"{name} status mismatches: {section.get('example_mismatches')!r}")
    if section.get("row_equality_component_violations") != 0:
        errors.append(
            f"{name} row equality component violations: "
            f"{section.get('row_equality_component_violations')!r}"
        )
    for key, value in expected.items():
        if section.get(key) != value:
            errors.append(f"{name} {key} mismatch: {section.get(key)!r} != {value!r}")
    for key in (
        "recorded_status_counts",
        "checker_status_counts",
        "replay_status_counts",
        "direct_status_counts",
    ):
        if section.get(key) != expected["status_counts"]:
            errors.append(
                f"{name} {key} mismatch: "
                f"{section.get(key)!r} != {expected['status_counts']!r}"
            )


def _assert_section(
    name: str,
    payload: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> None:
    section = payload.get(name)
    if not isinstance(section, Mapping):
        raise AssertionError(f"{name} section missing")
    errors: list[str] = []
    _check_section(errors, name, section, expected)
    if errors:
        raise AssertionError("; ".join(errors))


def _assignment_from_rows(rows: Sequence[SelectedRow]) -> dict[int, int]:
    return {
        row.center: n9.mask([int(witness) for witness in row.witnesses])
        for row in rows
    }


def _source_metadata(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
    }


def _all_pairs(n: int) -> list[Pair]:
    return [(u, v) for u in range(n) for v in range(u + 1, n)]


def _pair(a: int, b: int) -> Pair:
    if a == b:
        raise ValueError(f"loop pair is not allowed: ({a}, {b})")
    return (a, b) if a < b else (b, a)


def _properly_contains(
    outer_start: int,
    outer_end: int,
    inner_start: int,
    inner_end: int,
) -> bool:
    return (
        outer_start <= inner_start
        and inner_end <= outer_end
        and (outer_start < inner_start or inner_end < outer_end)
    )


def _has_directed_cycle(edges: Sequence[tuple[Pair, Pair]]) -> bool:
    graph: dict[Pair, list[Pair]] = defaultdict(list)
    for outer, inner in edges:
        if outer != inner:
            graph[outer].append(inner)
    for source in graph:
        graph[source].sort()

    color: dict[Pair, int] = {}

    def visit(node: Pair) -> bool:
        color[node] = 1
        for target in graph.get(node, []):
            target_color = color.get(target, 0)
            if target_color == 1:
                return True
            if target_color == 0 and visit(target):
                return True
        color[node] = 2
        return False

    return any(color.get(node, 0) == 0 and visit(node) for node in sorted(graph))


def summary_json_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing JSON view without mismatch examples."""

    summary = {key: payload[key] for key in SUMMARY_JSON_KEYS if key in payload}
    for section_key in (
        "local_core_packet",
        "frontier_full_assignments",
        "frontier_core_assignments",
    ):
        section = payload.get(section_key)
        if isinstance(section, Mapping):
            summary[f"{section_key}_summary"] = {
                key: section[key]
                for key in QUOTIENT_SECTION_SUMMARY_KEYS
                if key in section
            }
    return summary


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        "local-core row sets: "
        f"{payload['local_core_packet']['row_set_count']}",
        "frontier full row sets: "
        f"{payload['frontier_full_assignments']['row_set_count']}",
        "frontier core row sets: "
        f"{payload['frontier_core_assignments']['row_set_count']}",
    ]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-core-packet", type=Path, default=DEFAULT_LOCAL_CORE_PACKET)
    parser.add_argument(
        "--frontier-classification",
        type=Path,
        default=DEFAULT_FRONTIER_CLASSIFICATION,
    )
    parser.add_argument("--check", action="store_true", help="validate the audit")
    parser.add_argument("--assert-expected", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="emit JSON payload")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="emit compact reviewer-facing JSON without mismatch examples",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    local_core_path = (
        args.local_core_packet
        if args.local_core_packet.is_absolute()
        else ROOT / args.local_core_packet
    )
    frontier_path = (
        args.frontier_classification
        if args.frontier_classification.is_absolute()
        else ROOT / args.frontier_classification
    )
    payload = quotient_soundness_payload(
        local_core_path=local_core_path,
        frontier_path=frontier_path,
    )

    if args.assert_expected:
        assert_expected_quotient_soundness(payload)

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle quotient soundness audit")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=9 quotient soundness audit checks passed")
    else:
        print("FAILED: n=9 quotient soundness audit", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
