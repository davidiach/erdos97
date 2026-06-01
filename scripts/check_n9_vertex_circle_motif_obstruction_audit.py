#!/usr/bin/env python3
"""Audit stored n=9 motif representative obstruction certificates."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
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

SCHEMA = "erdos97.n9_vertex_circle_motif_obstruction_audit.v1"
STATUS = "REVIEW_PENDING_MOTIF_OBSTRUCTION_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Stored-certificate audit for the 16 review-pending n=9 vertex-circle "
    "motif representatives. It treats the motif-family artifact as input, "
    "recomputes selected-distance quotient classes and vertex-circle strict "
    "interval inequalities with a small local implementation, and verifies "
    "the stored representative self-edge paths or strict-cycle edges. It "
    "does not prove frontier coverage, brancher soundness, incidence-filter "
    "soundness, dihedral orbit bookkeeping, n=9, a counterexample, or any "
    "official/global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_motif_obstruction_audit.py",
    "command": (
        "python scripts/check_n9_vertex_circle_motif_obstruction_audit.py "
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
    "source_artifact",
    "validation_status",
    "validation_errors",
    "interpretation",
    "provenance",
)
MOTIF_OBSTRUCTION_SUMMARY_KEYS = (
    "family_count",
    "computed_status_counts",
    "stored_status_counts",
    "strict_edge_count_by_status",
    "self_edge_count_by_status",
    "strict_cycle_length_counts",
    "stored_status_mismatches",
    "self_edge_conflict_mismatches",
    "equality_path_mismatches",
    "strict_cycle_edge_mismatches",
    "strict_cycle_chain_mismatches",
)

EXPECTED_FAMILY_COUNT = 16
EXPECTED_STATUS_COUNTS = {"self_edge": 13, "strict_cycle": 3}
EXPECTED_STRICT_EDGE_COUNT_BY_STATUS = {"self_edge": 1053, "strict_cycle": 243}
EXPECTED_SELF_EDGE_COUNT_BY_STATUS = {"self_edge": 276, "strict_cycle": 0}
EXPECTED_STRICT_CYCLE_LENGTH_COUNTS = {"2": 1, "3": 2}
EXPECTED_STORED_STATUS_MISMATCHES = 0
EXPECTED_SELF_EDGE_CONFLICT_MISMATCHES = 0
EXPECTED_EQUALITY_PATH_MISMATCHES = 0
EXPECTED_STRICT_CYCLE_EDGE_MISMATCHES = 0
EXPECTED_STRICT_CYCLE_CHAIN_MISMATCHES = 0

Pair = tuple[int, int]
Rows = tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class StrictEdge:
    """One strict vertex-circle interval inequality after quotienting."""

    row: int
    witness_order: tuple[int, ...]
    outer_interval: tuple[int, int]
    inner_interval: tuple[int, int]
    outer_pair: Pair
    inner_pair: Pair
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


def motif_obstruction_audit_payload(
    *,
    motif_path: Path = DEFAULT_MOTIF_FAMILIES,
) -> dict[str, Any]:
    """Return the n=9 motif representative obstruction audit payload."""

    motif = load_json(motif_path)
    errors: list[str] = []
    summary = _audit_motif_obstructions(motif, errors)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "row_size": ROW_SIZE,
        "motif_obstruction_audit": summary,
        "source_artifact": {
            "path": display_path(motif_path, ROOT),
            "type": motif.get("type"),
            "trust": motif.get("trust"),
        },
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says each stored n=9 motif-family representative "
            "has a locally verified representative obstruction record: a "
            "self-edge conflict plus selected-distance equality path, or a "
            "strict directed quotient cycle. This is stored-certificate "
            "bookkeeping only."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_motif_obstruction_audit(payload: Mapping[str, Any]) -> None:
    """Assert stable expected counts for the motif obstruction audit."""

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
        "incidence-filter soundness",
        "dihedral orbit bookkeeping",
        "n=9",
        "counterexample",
        "official/global status update",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")
    summary = payload.get("motif_obstruction_audit")
    if not isinstance(summary, Mapping):
        raise AssertionError("motif_obstruction_audit missing")
    expected = {
        "family_count": EXPECTED_FAMILY_COUNT,
        "computed_status_counts": EXPECTED_STATUS_COUNTS,
        "stored_status_counts": EXPECTED_STATUS_COUNTS,
        "strict_edge_count_by_status": EXPECTED_STRICT_EDGE_COUNT_BY_STATUS,
        "self_edge_count_by_status": EXPECTED_SELF_EDGE_COUNT_BY_STATUS,
        "strict_cycle_length_counts": EXPECTED_STRICT_CYCLE_LENGTH_COUNTS,
        "stored_status_mismatches": EXPECTED_STORED_STATUS_MISMATCHES,
        "self_edge_conflict_mismatches": EXPECTED_SELF_EDGE_CONFLICT_MISMATCHES,
        "equality_path_mismatches": EXPECTED_EQUALITY_PATH_MISMATCHES,
        "strict_cycle_edge_mismatches": EXPECTED_STRICT_CYCLE_EDGE_MISMATCHES,
        "strict_cycle_chain_mismatches": EXPECTED_STRICT_CYCLE_CHAIN_MISMATCHES,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(f"{key} mismatch: {summary.get(key)!r} != {value!r}")


def _audit_motif_obstructions(
    motif: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    families = _motif_family_rows(motif)
    status_counts: Counter[str] = Counter()
    stored_status_counts: Counter[str] = Counter()
    strict_edge_count_by_status: Counter[str] = Counter()
    self_edge_count_by_status: Counter[str] = Counter()
    cycle_length_counts: Counter[int] = Counter()
    stored_status_mismatches = 0
    self_edge_conflict_mismatches = 0
    equality_path_mismatches = 0
    strict_cycle_edge_mismatches = 0
    strict_cycle_chain_mismatches = 0
    example_errors: list[dict[str, str]] = []

    for expected_index, family in enumerate(families, start=1):
        family_id = str(family.get("family_id"))
        if family_id != f"F{expected_index:02d}":
            _record_error(errors, example_errors, family_id, "family_id mismatch")
        rows = _rows_from_indexed_rows(family.get("representative_selected_rows"))
        obstruction = _as_mapping(
            family.get("representative_obstruction"),
            f"{family_id} representative_obstruction",
        )
        stored_status = str(obstruction.get("status"))
        stored_status_counts[stored_status] += 1

        edge_audit = _edge_audit(rows)
        strict_edge_count_by_status[edge_audit["computed_status"]] += len(edge_audit["edges"])
        self_edge_count_by_status[edge_audit["computed_status"]] += len(edge_audit["self_edges"])
        computed_status = str(edge_audit["computed_status"])
        status_counts[computed_status] += 1
        if str(family.get("status")) != stored_status or stored_status != computed_status:
            stored_status_mismatches += 1
            _record_error(
                errors,
                example_errors,
                family_id,
                (
                    f"status mismatch family={family.get('status')!r} "
                    f"stored={stored_status!r} computed={computed_status!r}"
                ),
            )

        if computed_status == "self_edge":
            if not _stored_conflict_is_valid_self_edge(obstruction, edge_audit):
                self_edge_conflict_mismatches += 1
                _record_error(errors, example_errors, family_id, "bad stored self-edge conflict")
            if not _stored_self_edge_path_is_valid(rows, obstruction, edge_audit):
                equality_path_mismatches += 1
                _record_error(errors, example_errors, family_id, "bad self-edge equality path")
        elif computed_status == "strict_cycle":
            cycle_edges = obstruction.get("cycle_edges")
            if not _stored_cycle_edges_are_recomputed(cycle_edges, edge_audit):
                strict_cycle_edge_mismatches += 1
                _record_error(errors, example_errors, family_id, "bad strict-cycle edge")
            elif not _stored_cycle_edges_chain(cycle_edges):
                strict_cycle_chain_mismatches += 1
                _record_error(errors, example_errors, family_id, "strict-cycle edges do not chain")
            else:
                cycle_length_counts[len(cycle_edges)] += 1
        else:
            _record_error(errors, example_errors, family_id, f"unknown computed status {computed_status!r}")

    _check_equal(errors, "family_count", len(families), EXPECTED_FAMILY_COUNT)
    _check_equal(
        errors,
        "computed_status_counts",
        dict(sorted(status_counts.items())),
        EXPECTED_STATUS_COUNTS,
    )
    _check_equal(
        errors,
        "stored_status_counts",
        dict(sorted(stored_status_counts.items())),
        EXPECTED_STATUS_COUNTS,
    )
    _check_equal(
        errors,
        "stored_status_mismatches",
        stored_status_mismatches,
        EXPECTED_STORED_STATUS_MISMATCHES,
    )
    _check_equal(
        errors,
        "self_edge_conflict_mismatches",
        self_edge_conflict_mismatches,
        EXPECTED_SELF_EDGE_CONFLICT_MISMATCHES,
    )
    _check_equal(
        errors,
        "equality_path_mismatches",
        equality_path_mismatches,
        EXPECTED_EQUALITY_PATH_MISMATCHES,
    )
    _check_equal(
        errors,
        "strict_cycle_edge_mismatches",
        strict_cycle_edge_mismatches,
        EXPECTED_STRICT_CYCLE_EDGE_MISMATCHES,
    )
    _check_equal(
        errors,
        "strict_cycle_chain_mismatches",
        strict_cycle_chain_mismatches,
        EXPECTED_STRICT_CYCLE_CHAIN_MISMATCHES,
    )

    return {
        "family_count": len(families),
        "computed_status_counts": dict(sorted(status_counts.items())),
        "stored_status_counts": dict(sorted(stored_status_counts.items())),
        "strict_edge_count_by_status": dict(sorted(strict_edge_count_by_status.items())),
        "self_edge_count_by_status": dict(sorted(self_edge_count_by_status.items())),
        "strict_cycle_length_counts": {
            str(length): int(cycle_length_counts[length])
            for length in sorted(cycle_length_counts)
        },
        "stored_status_mismatches": stored_status_mismatches,
        "self_edge_conflict_mismatches": self_edge_conflict_mismatches,
        "equality_path_mismatches": equality_path_mismatches,
        "strict_cycle_edge_mismatches": strict_cycle_edge_mismatches,
        "strict_cycle_chain_mismatches": strict_cycle_chain_mismatches,
        "example_errors": example_errors,
    }


def _motif_family_rows(motif: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    families = motif.get("dihedral_incidence_families", {}).get("families")
    if not isinstance(families, list):
        raise ValueError("motif artifact must contain dihedral incidence families")
    return [_as_mapping(row, "family") for row in families]


def _as_mapping(row: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(row, Mapping):
        raise ValueError(f"{label} row must be an object")
    return row


def _rows_from_indexed_rows(raw_rows: Any) -> Rows:
    if not isinstance(raw_rows, list) or len(raw_rows) != N:
        raise ValueError("indexed selected rows must be a list of 9 rows")
    return tuple(_witness_tuple(center, row) for center, row in enumerate(raw_rows))


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


def _edge_audit(rows: Rows) -> dict[str, Any]:
    uf = _distance_union_find(rows)
    edges = _strict_edges(rows, uf)
    self_edges = [edge for edge in edges if edge.outer_class == edge.inner_class]
    computed_status = "self_edge" if self_edges else "strict_cycle"
    return {
        "edges": edges,
        "edge_keys": {_edge_key(edge) for edge in edges},
        "self_edges": self_edges,
        "self_edge_keys": {_edge_key(edge) for edge in self_edges},
        "computed_status": computed_status,
    }


def _distance_union_find(rows: Rows) -> UnionFind:
    uf = UnionFind(_all_pairs())
    for center, witnesses in enumerate(rows):
        base = pair(center, witnesses[0])
        for witness in witnesses[1:]:
            uf.union(base, pair(center, witness))
    return uf


def _strict_edges(rows: Rows, uf: UnionFind) -> list[StrictEdge]:
    edges: list[StrictEdge] = []
    for center, witnesses in enumerate(rows):
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
                                witness_order=witness_order,
                                outer_interval=(outer_start, outer_end),
                                inner_interval=(inner_start, inner_end),
                                outer_pair=outer_pair,
                                inner_pair=inner_pair,
                                outer_class=uf.find(outer_pair),
                                inner_class=uf.find(inner_pair),
                            )
                        )
    return edges


def _stored_conflict_is_valid_self_edge(
    obstruction: Mapping[str, Any],
    edge_audit: Mapping[str, Any],
) -> bool:
    conflict = obstruction.get("conflict")
    if not isinstance(conflict, Mapping):
        return False
    return _edge_key_from_json(conflict) in edge_audit["self_edge_keys"]


def _stored_self_edge_path_is_valid(
    rows: Rows,
    obstruction: Mapping[str, Any],
    edge_audit: Mapping[str, Any],
) -> bool:
    conflict = obstruction.get("conflict")
    raw_path = obstruction.get("distance_equality_path")
    if not isinstance(conflict, Mapping) or not isinstance(raw_path, list):
        return False
    if _edge_key_from_json(conflict) not in edge_audit["self_edge_keys"]:
        return False
    current = pair_from_json(conflict.get("outer_pair"))
    target = pair_from_json(conflict.get("inner_pair"))
    for step in raw_path:
        if not isinstance(step, Mapping):
            return False
        row = int(step.get("row", -1))
        if not 0 <= row < N:
            return False
        next_pair = pair_from_json(step.get("next_pair"))
        selected_pairs = _selected_pairs_for_row(rows, row)
        if current not in selected_pairs or next_pair not in selected_pairs:
            return False
        current = next_pair
    return current == target


def _stored_cycle_edges_are_recomputed(
    cycle_edges: Any,
    edge_audit: Mapping[str, Any],
) -> bool:
    if not isinstance(cycle_edges, list) or not cycle_edges:
        return False
    edge_keys = edge_audit["edge_keys"]
    for raw_edge in cycle_edges:
        if not isinstance(raw_edge, Mapping):
            return False
        try:
            key = _edge_key_from_json(raw_edge)
        except (TypeError, ValueError):
            return False
        if key not in edge_keys:
            return False
        if tuple(raw_edge["outer_class"]) == tuple(raw_edge["inner_class"]):
            return False
    return True


def _stored_cycle_edges_chain(cycle_edges: Any) -> bool:
    if not isinstance(cycle_edges, list) or not cycle_edges:
        return False
    try:
        classes = [(_json_pair(edge["outer_class"]), _json_pair(edge["inner_class"])) for edge in cycle_edges]
    except (KeyError, TypeError, ValueError):
        return False
    return all(
        classes[index][1] == classes[(index + 1) % len(classes)][0]
        for index in range(len(classes))
    )


def _selected_pairs_for_row(rows: Rows, center: int) -> set[Pair]:
    return {pair(center, witness) for witness in rows[center]}


def pair(left: int, right: int) -> Pair:
    """Return a normalized unordered pair."""

    if left == right:
        raise ValueError("loop pair")
    return (left, right) if left < right else (right, left)


def pair_from_json(raw_pair: Any) -> Pair:
    """Return a normalized pair from a JSON pair field."""

    if not isinstance(raw_pair, list | tuple) or len(raw_pair) != 2:
        raise ValueError(f"bad pair: {raw_pair!r}")
    return pair(int(raw_pair[0]), int(raw_pair[1]))


def _json_pair(raw_pair: Any) -> Pair:
    if not isinstance(raw_pair, list | tuple) or len(raw_pair) != 2:
        raise ValueError(f"bad pair: {raw_pair!r}")
    first = int(raw_pair[0])
    second = int(raw_pair[1])
    if first > second:
        first, second = second, first
    return (first, second)


def _json_tuple(raw_values: Any, length: int) -> tuple[int, ...]:
    if not isinstance(raw_values, list | tuple) or len(raw_values) != length:
        raise ValueError(f"bad tuple field: {raw_values!r}")
    return tuple(int(value) for value in raw_values)


def _edge_key(edge: StrictEdge) -> tuple[Any, ...]:
    return (
        edge.row,
        edge.witness_order,
        edge.outer_interval,
        edge.inner_interval,
        edge.outer_pair,
        edge.inner_pair,
        edge.outer_class,
        edge.inner_class,
    )


def _edge_key_from_json(raw_edge: Mapping[str, Any]) -> tuple[Any, ...]:
    return (
        int(raw_edge["row"]),
        _json_tuple(raw_edge["witness_order"], ROW_SIZE),
        _json_tuple(raw_edge["outer_interval"], 2),
        _json_tuple(raw_edge["inner_interval"], 2),
        pair_from_json(raw_edge["outer_pair"]),
        pair_from_json(raw_edge["inner_pair"]),
        _json_pair(raw_edge["outer_class"]),
        _json_pair(raw_edge["inner_class"]),
    )


def _all_pairs() -> list[Pair]:
    return [(left, right) for left in range(N) for right in range(left + 1, N)]


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


def summary_json_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing JSON view without example errors."""

    summary = {key: payload[key] for key in SUMMARY_JSON_KEYS if key in payload}
    audit = payload.get("motif_obstruction_audit")
    if isinstance(audit, Mapping):
        summary["motif_obstruction_audit_summary"] = {
            key: audit[key] for key in MOTIF_OBSTRUCTION_SUMMARY_KEYS if key in audit
        }
    return summary


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    summary = payload["motif_obstruction_audit"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"families checked: {summary['family_count']}",
        f"computed statuses: {summary['computed_status_counts']}",
        f"self-edge conflict mismatches: {summary['self_edge_conflict_mismatches']}",
        f"equality path mismatches: {summary['equality_path_mismatches']}",
        f"strict-cycle mismatches: {summary['strict_cycle_edge_mismatches']}",
    ]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--motif-families", type=Path, default=DEFAULT_MOTIF_FAMILIES)
    parser.add_argument("--check", action="store_true", help="validate the audit")
    parser.add_argument("--assert-expected", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="emit JSON payload")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="emit compact reviewer-facing JSON without example errors",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = motif_obstruction_audit_payload(
            motif_path=_resolve(args.motif_families),
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
        assert_expected_motif_obstruction_audit(payload)

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle motif obstruction audit")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=9 motif obstruction audit checks passed")
    else:
        print("FAILED: n=9 motif obstruction audit", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
