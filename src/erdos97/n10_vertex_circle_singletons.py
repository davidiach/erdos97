"""Review-pending n=10 singleton-slice artifact helpers."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from erdos97.generic_vertex_search import GenericVertexSearch

N = 10
ROW_SIZE = 4
EXPECTED_ROW0_CHOICES = 126
EXPECTED_TOTAL_NODES = 4_142_738
EXPECTED_TOTAL_FULL = 0
EXPECTED_COUNTS = {
    "partial_self_edge": 4_467_592,
    "partial_strict_cycle": 5_318_250,
}
TRUST = "MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING"


@dataclass(frozen=True)
class SingletonRow:
    row0_index: int
    row0_start: int
    row0_end: int
    nodes: int
    full: int
    aborted: bool
    counts: dict[str, int]
    elapsed_seconds: float | None = None

    def to_json(self) -> dict[str, object]:
        row: dict[str, object] = {
            "row0_index": self.row0_index,
            "row0_range": [self.row0_start, self.row0_end],
            "nodes": self.nodes,
            "full": self.full,
            "aborted": self.aborted,
            "counts": dict(sorted(self.counts.items())),
        }
        if self.elapsed_seconds is not None:
            row["elapsed_seconds"] = self.elapsed_seconds
        return row


def load_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    """Load archive JSONL singleton rows."""
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"line {line_number} is not a JSON object")
        rows.append(payload)
    return rows


def rows_from_archive_jsonl(path: Path) -> list[SingletonRow]:
    """Convert archive rows to explicit singleton records."""
    rows: list[SingletonRow] = []
    for row0_index, payload in enumerate(load_jsonl_rows(path)):
        if int(payload.get("N", -1)) != N:
            raise ValueError(f"row {row0_index} has wrong N: {payload.get('N')!r}")
        if int(payload.get("M", -1)) != EXPECTED_ROW0_CHOICES:
            raise ValueError(f"row {row0_index} has wrong M: {payload.get('M')!r}")
        counts = payload.get("counts", {})
        if not isinstance(counts, dict):
            raise ValueError(f"row {row0_index} counts is not an object")
        rows.append(
            SingletonRow(
                row0_index=row0_index,
                row0_start=row0_index,
                row0_end=row0_index + 1,
                nodes=int(payload["nodes"]),
                full=int(payload["full"]),
                aborted=bool(payload["aborted"]),
                counts={str(key): int(value) for key, value in counts.items()},
                elapsed_seconds=float(payload["elapsed"]) if "elapsed" in payload else None,
            )
        )
    return rows


def artifact_payload(rows: Sequence[SingletonRow]) -> dict[str, object]:
    """Build the stable n=10 singleton-slice artifact payload."""
    total_counts: Counter[str] = Counter()
    for row in rows:
        total_counts.update(row.counts)
    elapsed_values = [
        row.elapsed_seconds
        for row in rows
        if row.elapsed_seconds is not None
    ]
    return {
        "type": "n10_vertex_circle_singleton_slices_v1",
        "trust": TRUST,
        "scope": (
            "Review-pending finite-case draft for n=10 selected-witness "
            "assignments in the natural cyclic order; does not update the "
            "official/global falsifiable-open status."
        ),
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "The repo source-of-truth strongest local result remains n <= 8.",
            "This n=10 artifact needs independent checker review before any public theorem-style use.",
        ],
        "n": N,
        "row_size": ROW_SIZE,
        "row0_choice_count_expected": EXPECTED_ROW0_CHOICES,
        "row0_choices_covered": len(rows),
        "row0_ranges": [[row.row0_start, row.row0_end] for row in rows],
        "aborted_any": any(row.aborted for row in rows),
        "total_nodes": sum(row.nodes for row in rows),
        "total_full": sum(row.full for row in rows),
        "counts": dict(sorted(total_counts.items())),
        "elapsed_sum_seconds": sum(elapsed_values) if elapsed_values else None,
        "rows": [row.to_json() for row in rows],
    }


def load_artifact(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("n=10 singleton artifact must be a JSON object")
    return payload


def assert_expected_payload(payload: dict[str, Any]) -> None:
    """Assert the n=10 singleton artifact has the expected draft counts."""
    if payload.get("type") != "n10_vertex_circle_singleton_slices_v1":
        raise AssertionError(f"unexpected type: {payload.get('type')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"unexpected trust: {payload.get('trust')!r}")
    if payload.get("n") != N:
        raise AssertionError(f"unexpected n: {payload.get('n')!r}")
    if payload.get("row_size") != ROW_SIZE:
        raise AssertionError(f"unexpected row_size: {payload.get('row_size')!r}")
    if payload.get("row0_choice_count_expected") != EXPECTED_ROW0_CHOICES:
        raise AssertionError("unexpected expected row0 choice count")
    if payload.get("row0_choices_covered") != EXPECTED_ROW0_CHOICES:
        raise AssertionError("n=10 singleton artifact does not cover all row0 choices")
    if payload.get("aborted_any") is not False:
        raise AssertionError("n=10 singleton artifact has aborted slices")
    if payload.get("total_nodes") != EXPECTED_TOTAL_NODES:
        raise AssertionError(f"unexpected total_nodes: {payload.get('total_nodes')!r}")
    if payload.get("total_full") != EXPECTED_TOTAL_FULL:
        raise AssertionError(f"unexpected total_full: {payload.get('total_full')!r}")
    if payload.get("counts") != EXPECTED_COUNTS:
        raise AssertionError(f"unexpected counts: {payload.get('counts')!r}")

    rows = payload.get("rows")
    if not isinstance(rows, list) or len(rows) != EXPECTED_ROW0_CHOICES:
        raise AssertionError("rows must contain 126 singleton records")
    expected_ranges = [[idx, idx + 1] for idx in range(EXPECTED_ROW0_CHOICES)]
    if payload.get("row0_ranges") != expected_ranges:
        raise AssertionError("row0_ranges are not the 126 singleton slices")

    node_sum = 0
    full_sum = 0
    row_counts: Counter[str] = Counter()
    for idx, row in enumerate(rows):
        if not isinstance(row, dict):
            raise AssertionError(f"row {idx} is not an object")
        if row.get("row0_index") != idx:
            raise AssertionError(f"row {idx} has wrong row0_index")
        if row.get("row0_range") != [idx, idx + 1]:
            raise AssertionError(f"row {idx} has wrong row0_range")
        if row.get("aborted") is not False:
            raise AssertionError(f"row {idx} aborted")
        if row.get("full") != 0:
            raise AssertionError(f"row {idx} has full assignments")
        node_sum += int(row["nodes"])
        full_sum += int(row["full"])
        counts = row.get("counts")
        if not isinstance(counts, dict):
            raise AssertionError(f"row {idx} counts is not an object")
        row_counts.update({str(key): int(value) for key, value in counts.items()})
    if node_sum != EXPECTED_TOTAL_NODES:
        raise AssertionError(f"row node sum mismatch: {node_sum}")
    if full_sum != EXPECTED_TOTAL_FULL:
        raise AssertionError(f"row full sum mismatch: {full_sum}")
    if dict(sorted(row_counts.items())) != EXPECTED_COUNTS:
        raise AssertionError(f"row count sum mismatch: {row_counts}")


def assert_generic_spot_check(payload: dict[str, Any], row0_index: int = 0) -> None:
    """Rerun one singleton slice with the repo-native generic checker."""
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise AssertionError("payload rows missing")
    expected = rows[row0_index]
    if not isinstance(expected, dict):
        raise AssertionError("expected row is not an object")
    search = GenericVertexSearch(N)
    result = search.exhaustive_search(
        row0_start=row0_index,
        row0_end=row0_index + 1,
        use_vertex_circle=True,
    )
    if result.nodes_visited != expected["nodes"]:
        raise AssertionError(
            f"row0 {row0_index} nodes mismatch: {result.nodes_visited} != {expected['nodes']}"
        )
    if result.full_assignments != expected["full"]:
        raise AssertionError(
            f"row0 {row0_index} full mismatch: {result.full_assignments} != {expected['full']}"
        )
    if result.aborted != expected["aborted"]:
        raise AssertionError(
            f"row0 {row0_index} aborted mismatch: {result.aborted} != {expected['aborted']}"
        )
    if result.counts != expected["counts"]:
        raise AssertionError(
            f"row0 {row0_index} counts mismatch: {result.counts} != {expected['counts']}"
        )
