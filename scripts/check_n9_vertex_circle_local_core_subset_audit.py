#!/usr/bin/env python3
"""Audit n=9 local cores as obstructing subsets of motif representatives."""

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

from erdos97.path_display import display_path  # noqa: E402

N = 9
ROW_SIZE = 4
DEFAULT_MOTIF_FAMILIES = ROOT / "data" / "certificates" / "n9_vertex_circle_motif_families.json"
DEFAULT_LOCAL_CORE_PACKET = ROOT / "data" / "certificates" / "n9_vertex_circle_local_core_packet.json"

SCHEMA = "erdos97.n9_vertex_circle_local_core_subset_audit.v1"
STATUS = "REVIEW_PENDING_LOCAL_CORE_SUBSET_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Cross-artifact input audit for the review-pending n=9 vertex-circle "
    "motif representatives and compact local-core packet. It checks that "
    "each compact local core is literally a subset of its stored full motif "
    "representative and that the compact rows alone force the same quotient "
    "self-edge or strict-cycle obstruction under a small direct replay. It "
    "does not prove frontier coverage, brancher soundness, motif-orbit "
    "bookkeeping, n=9, a counterexample, or any official/global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_local_core_subset_audit.py",
    "command": (
        "python scripts/check_n9_vertex_circle_local_core_subset_audit.py "
        "--check --assert-expected --json"
    ),
}

EXPECTED_FAMILY_COUNT = 16
EXPECTED_ORBIT_SIZE_SUM = 184
EXPECTED_STATUS_COUNTS = {"self_edge": 13, "strict_cycle": 3}
EXPECTED_CORE_SIZE_COUNTS = {"3": 5, "4": 6, "5": 2, "6": 3}
EXPECTED_STATUS_CORE_SIZE_COUNTS = {
    "self_edge": {"3": 5, "4": 4, "5": 2, "6": 2},
    "strict_cycle": {"4": 2, "6": 1},
}
EXPECTED_STRICT_CYCLE_LENGTH_COUNTS = {"2": 1, "3": 2}

Pair = tuple[int, int]
SparseRows = dict[int, tuple[int, ...]]


@dataclass(frozen=True)
class StrictEdge:
    row: int
    outer_class: Pair
    inner_class: Pair


class UnionFind:
    """Deterministic union-find over unordered vertex pairs."""

    def __init__(self, items: Sequence[Pair]) -> None:
        self.parent = {item: item for item in items}

    def find(self, item: Pair) -> Pair:
        if item not in self.parent:
            self.parent[item] = item
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, first: Pair, second: Pair) -> None:
        root_first = self.find(first)
        root_second = self.find(second)
        if root_first == root_second:
            return
        if root_second < root_first:
            root_first, root_second = root_second, root_first
        self.parent[root_second] = root_first


def load_json(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def local_core_subset_audit_payload(
    *,
    motif_path: Path = DEFAULT_MOTIF_FAMILIES,
    local_core_path: Path = DEFAULT_LOCAL_CORE_PACKET,
) -> dict[str, Any]:
    """Return a cross-artifact audit for compact n=9 local cores."""

    motif = load_json(motif_path)
    local_core = load_json(local_core_path)
    errors: list[str] = []
    summary = _audit_local_core_subsets(motif, local_core, errors)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "row_size": ROW_SIZE,
        "local_core_subset_audit": summary,
        "source_artifacts": [
            {
                "path": display_path(motif_path, ROOT),
                "role": "full motif representatives",
                "type": motif.get("type"),
                "trust": motif.get("trust"),
            },
            {
                "path": display_path(local_core_path, ROOT),
                "role": "compact local-core packet",
                "schema": local_core.get("schema"),
                "status": local_core.get("status"),
                "trust": local_core.get("trust"),
            },
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says every stored compact n=9 local core is an "
            "actual subset of the corresponding full motif representative and "
            "already forces its recorded self-edge or strict-cycle obstruction. "
            "This is cross-artifact bookkeeping only."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_local_core_subset_audit(payload: Mapping[str, Any]) -> None:
    """Assert stable expected counts for the local-core subset audit."""

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
        "does not prove frontier coverage",
        "brancher soundness",
        "motif-orbit bookkeeping",
        "n=9",
        "counterexample",
        "official/global status update",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")
    summary = payload.get("local_core_subset_audit")
    if not isinstance(summary, Mapping):
        raise AssertionError("local_core_subset_audit missing")
    expected = {
        "family_count": EXPECTED_FAMILY_COUNT,
        "orbit_size_sum": EXPECTED_ORBIT_SIZE_SUM,
        "stored_status_counts": EXPECTED_STATUS_COUNTS,
        "computed_status_counts": EXPECTED_STATUS_COUNTS,
        "core_size_counts": EXPECTED_CORE_SIZE_COUNTS,
        "status_core_size_counts": EXPECTED_STATUS_CORE_SIZE_COUNTS,
        "strict_cycle_length_counts": EXPECTED_STRICT_CYCLE_LENGTH_COUNTS,
        "family_id_mismatches": 0,
        "orbit_size_mismatches": 0,
        "status_mismatches": 0,
        "core_size_mismatches": 0,
        "subset_mismatches": 0,
        "unobstructed_core_count": 0,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(f"{key} mismatch: {summary.get(key)!r} != {value!r}")


def _audit_local_core_subsets(
    motif: Mapping[str, Any],
    local_core: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    full_families = _family_map(motif)
    certificates = _local_core_certificates(local_core)
    family_id_mismatches = 0
    orbit_size_mismatches = 0
    status_mismatches = 0
    core_size_mismatches = 0
    subset_mismatches = 0
    unobstructed_core_count = 0
    orbit_size_sum = 0
    stored_status_counts: Counter[str] = Counter()
    computed_status_counts: Counter[str] = Counter()
    core_size_counts: Counter[int] = Counter()
    status_core_size_counts: Counter[tuple[str, int]] = Counter()
    strict_cycle_length_counts: Counter[int] = Counter()
    example_errors: list[dict[str, str]] = []

    for expected_index, certificate in enumerate(certificates, start=1):
        family_id = str(certificate.get("family_id"))
        expected_family_id = f"F{expected_index:02d}"
        if family_id != expected_family_id:
            family_id_mismatches += 1
            _record_error(errors, example_errors, family_id, "family_id order mismatch")
        full_family = full_families.get(family_id)
        if full_family is None:
            family_id_mismatches += 1
            _record_error(errors, example_errors, family_id, "missing full motif family")
            continue

        full_rows = _rows_from_indexed_rows(full_family.get("representative_selected_rows"))
        core_rows = _core_rows_from_certificate(certificate)
        orbit_size = int(certificate.get("orbit_size", -1))
        orbit_size_sum += max(orbit_size, 0)
        stored_status = str(certificate.get("status"))
        stored_status_counts[stored_status] += 1
        core_size = len(core_rows)
        core_size_counts[core_size] += 1
        status_core_size_counts[(stored_status, core_size)] += 1

        if orbit_size != int(full_family.get("orbit_size", -2)):
            orbit_size_mismatches += 1
            _record_error(errors, example_errors, family_id, "orbit_size mismatch")
        if int(certificate.get("core_size", -1)) != core_size:
            core_size_mismatches += 1
            _record_error(errors, example_errors, family_id, "core_size mismatch")
        if not _core_rows_are_subset(core_rows, full_rows):
            subset_mismatches += 1
            _record_error(errors, example_errors, family_id, "compact rows are not full-row subsets")

        computed_status, cycle_length = _core_obstruction_status(core_rows)
        computed_status_counts[computed_status] += 1
        if computed_status == "ok":
            unobstructed_core_count += 1
            _record_error(errors, example_errors, family_id, "compact core is unobstructed")
        if computed_status == "strict_cycle" and cycle_length is not None:
            strict_cycle_length_counts[cycle_length] += 1
        if stored_status != computed_status:
            status_mismatches += 1
            _record_error(
                errors,
                example_errors,
                family_id,
                f"status mismatch stored={stored_status!r} computed={computed_status!r}",
            )

    _check_equal(errors, "family_count", len(certificates), EXPECTED_FAMILY_COUNT)
    _check_equal(errors, "orbit_size_sum", orbit_size_sum, EXPECTED_ORBIT_SIZE_SUM)
    _check_equal(
        errors,
        "stored_status_counts",
        dict(sorted(stored_status_counts.items())),
        EXPECTED_STATUS_COUNTS,
    )
    _check_equal(
        errors,
        "computed_status_counts",
        dict(sorted(computed_status_counts.items())),
        EXPECTED_STATUS_COUNTS,
    )
    _check_equal(errors, "core_size_counts", _string_counter(core_size_counts), EXPECTED_CORE_SIZE_COUNTS)
    _check_equal(
        errors,
        "status_core_size_counts",
        _nested_status_size_counter(status_core_size_counts),
        EXPECTED_STATUS_CORE_SIZE_COUNTS,
    )
    _check_equal(
        errors,
        "strict_cycle_length_counts",
        _string_counter(strict_cycle_length_counts),
        EXPECTED_STRICT_CYCLE_LENGTH_COUNTS,
    )
    for label, actual in (
        ("family_id_mismatches", family_id_mismatches),
        ("orbit_size_mismatches", orbit_size_mismatches),
        ("status_mismatches", status_mismatches),
        ("core_size_mismatches", core_size_mismatches),
        ("subset_mismatches", subset_mismatches),
        ("unobstructed_core_count", unobstructed_core_count),
    ):
        _check_equal(errors, label, actual, 0)

    return {
        "family_count": len(certificates),
        "orbit_size_sum": orbit_size_sum,
        "stored_status_counts": dict(sorted(stored_status_counts.items())),
        "computed_status_counts": dict(sorted(computed_status_counts.items())),
        "core_size_counts": _string_counter(core_size_counts),
        "status_core_size_counts": _nested_status_size_counter(status_core_size_counts),
        "strict_cycle_length_counts": _string_counter(strict_cycle_length_counts),
        "family_id_mismatches": family_id_mismatches,
        "orbit_size_mismatches": orbit_size_mismatches,
        "status_mismatches": status_mismatches,
        "core_size_mismatches": core_size_mismatches,
        "subset_mismatches": subset_mismatches,
        "unobstructed_core_count": unobstructed_core_count,
        "example_errors": example_errors,
    }


def _family_map(motif: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    families = motif.get("dihedral_incidence_families", {}).get("families")
    if not isinstance(families, list):
        raise ValueError("motif artifact must contain dihedral incidence families")
    out: dict[str, Mapping[str, Any]] = {}
    for family in families:
        if not isinstance(family, Mapping):
            raise ValueError("motif family entries must be objects")
        out[str(family.get("family_id"))] = family
    return out


def _local_core_certificates(local_core: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    certificates = local_core.get("certificates")
    if not isinstance(certificates, list):
        raise ValueError("local-core packet must contain certificates")
    out = []
    for certificate in certificates:
        if not isinstance(certificate, Mapping):
            raise ValueError("local-core certificate entries must be objects")
        out.append(certificate)
    return out


def _rows_from_indexed_rows(raw_rows: Any) -> tuple[tuple[int, ...], ...]:
    if not isinstance(raw_rows, list) or len(raw_rows) != N:
        raise ValueError("indexed selected rows must be a list of 9 rows")
    return tuple(_witness_tuple(center, row) for center, row in enumerate(raw_rows))


def _core_rows_from_certificate(certificate: Mapping[str, Any]) -> SparseRows:
    raw_rows = certificate.get("compact_selected_rows")
    if not isinstance(raw_rows, list):
        raise ValueError("compact_selected_rows must be a list")
    rows: SparseRows = {}
    for raw_row in raw_rows:
        if not isinstance(raw_row, list) or len(raw_row) != ROW_SIZE + 1:
            raise ValueError(f"bad compact row: {raw_row!r}")
        center = int(raw_row[0])
        if center in rows:
            raise ValueError(f"duplicate compact row center: {center}")
        rows[center] = _witness_tuple(center, raw_row[1:])
    return rows


def _witness_tuple(center: int, raw_witnesses: Sequence[Any]) -> tuple[int, ...]:
    witnesses = tuple(sorted(int(witness) for witness in raw_witnesses))
    if len(witnesses) != ROW_SIZE:
        raise ValueError(f"row {center} must contain {ROW_SIZE} witnesses")
    if len(set(witnesses)) != ROW_SIZE:
        raise ValueError(f"row {center} has duplicate witnesses")
    if center in witnesses:
        raise ValueError(f"row {center} selects itself")
    if any(witness < 0 or witness >= N for witness in witnesses):
        raise ValueError(f"row {center} has witness outside 0..{N - 1}")
    return witnesses


def _core_rows_are_subset(core_rows: SparseRows, full_rows: Sequence[Sequence[int]]) -> bool:
    return all(tuple(full_rows[center]) == witnesses for center, witnesses in core_rows.items())


def _core_obstruction_status(core_rows: SparseRows) -> tuple[str, int | None]:
    uf = _distance_union_find(core_rows)
    edges = _strict_edges(core_rows, uf)
    if any(edge.outer_class == edge.inner_class for edge in edges):
        return "self_edge", None
    cycle = _find_strict_cycle(edges)
    if cycle:
        return "strict_cycle", len(cycle)
    return "ok", None


def _distance_union_find(rows: SparseRows) -> UnionFind:
    uf = UnionFind(_all_pairs())
    for center, witnesses in rows.items():
        base = pair(center, witnesses[0])
        for witness in witnesses[1:]:
            uf.union(base, pair(center, witness))
    return uf


def _strict_edges(rows: SparseRows, uf: UnionFind) -> list[StrictEdge]:
    edges: list[StrictEdge] = []
    for center in sorted(rows):
        witnesses = rows[center]
        witness_order = tuple(sorted(witnesses, key=lambda witness: (witness - center) % N))
        for outer_start in range(ROW_SIZE):
            for outer_end in range(outer_start + 1, ROW_SIZE):
                for inner_start in range(ROW_SIZE):
                    for inner_end in range(inner_start + 1, ROW_SIZE):
                        if (outer_start, outer_end) == (inner_start, inner_end):
                            continue
                        contains = (
                            outer_start <= inner_start
                            and inner_end <= outer_end
                            and (outer_start < inner_start or inner_end < outer_end)
                        )
                        if not contains:
                            continue
                        outer_pair = pair(witness_order[outer_start], witness_order[outer_end])
                        inner_pair = pair(witness_order[inner_start], witness_order[inner_end])
                        edges.append(
                            StrictEdge(
                                row=center,
                                outer_class=uf.find(outer_pair),
                                inner_class=uf.find(inner_pair),
                            )
                        )
    return edges


def _find_strict_cycle(edges: Sequence[StrictEdge]) -> list[StrictEdge]:
    graph: dict[Pair, list[StrictEdge]] = defaultdict(list)
    for edge in edges:
        if edge.outer_class != edge.inner_class:
            graph[edge.outer_class].append(edge)
    for source in graph:
        graph[source].sort(key=lambda edge: (edge.inner_class, edge.row))

    color: dict[Pair, int] = {}
    parent: dict[Pair, tuple[Pair, StrictEdge] | None] = {}

    def dfs(node: Pair) -> list[StrictEdge]:
        color[node] = 1
        for edge in graph.get(node, []):
            nxt = edge.inner_class
            nxt_color = color.get(nxt, 0)
            if nxt_color == 0:
                parent[nxt] = (node, edge)
                found = dfs(nxt)
                if found:
                    return found
            elif nxt_color == 1:
                path_edges: list[StrictEdge] = []
                cur = node
                while cur != nxt:
                    parent_item = parent[cur]
                    if parent_item is None:  # pragma: no cover - defensive
                        break
                    prev, parent_edge = parent_item
                    path_edges.append(parent_edge)
                    cur = prev
                return list(reversed(path_edges)) + [edge]
        color[node] = 2
        return []

    for node in sorted(graph):
        if color.get(node, 0) == 0:
            parent[node] = None
            found = dfs(node)
            if found:
                return found
    return []


def pair(left: int, right: int) -> Pair:
    if left == right:
        raise ValueError("loop pair")
    return (left, right) if left < right else (right, left)


def _all_pairs() -> list[Pair]:
    return [(left, right) for left in range(N) for right in range(left + 1, N)]


def _string_counter(counter: Counter[int]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _nested_status_size_counter(counter: Counter[tuple[str, int]]) -> dict[str, dict[str, int]]:
    nested: dict[str, Counter[int]] = defaultdict(Counter)
    for (status, size), count in counter.items():
        nested[status][size] = int(count)
    return {
        status: {str(size): int(nested[status][size]) for size in sorted(nested[status])}
        for status in sorted(nested)
    }


def _record_error(
    errors: list[str],
    examples: list[dict[str, str]],
    family_id: str,
    message: str,
) -> None:
    errors.append(f"{family_id}: {message}")
    if len(examples) < 10:
        examples.append({"family_id": family_id, "message": message})


def _check_equal(errors: list[str], name: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{name} mismatch: {actual!r} != {expected!r}")


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    summary = payload["local_core_subset_audit"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"families checked: {summary['family_count']}",
        f"computed statuses: {summary['computed_status_counts']}",
        f"subset mismatches: {summary['subset_mismatches']}",
        f"status mismatches: {summary['status_mismatches']}",
    ]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--motif-families", type=Path, default=DEFAULT_MOTIF_FAMILIES)
    parser.add_argument("--local-core-packet", type=Path, default=DEFAULT_LOCAL_CORE_PACKET)
    parser.add_argument("--check", action="store_true", help="validate the audit")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="emit JSON payload")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = local_core_subset_audit_payload(
            motif_path=_resolve(args.motif_families),
            local_core_path=_resolve(args.local_core_packet),
        )
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        payload = {
            "schema": SCHEMA,
            "status": STATUS,
            "trust": TRUST,
            "claim_scope": CLAIM_SCOPE,
            "validation_status": "failed",
            "validation_errors": [str(exc)],
            "provenance": dict(PROVENANCE),
        }

    if args.assert_expected:
        assert_expected_local_core_subset_audit(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle local-core subset audit")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=9 local-core subset audit checks passed")
    else:
        print("FAILED: n=9 local-core subset audit", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
