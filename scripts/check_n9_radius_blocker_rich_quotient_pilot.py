#!/usr/bin/env python3
"""Check full rich-class vertex-circle replay on the n=9 size-five pilot.

This is a finite bridge diagnostic only. It proves no general theorem about
Erdos Problem #97 and supplies no counterexample.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Mapping, Sequence

from erdos97.radius_blocker_packets import TRUST
from erdos97.vertex_circle_quotient_replay import (
    RichClassRow,
    replay_vertex_circle_rich_quotient,
    result_to_json,
)

ROOT = Path(__file__).resolve().parents[1]

SCHEMA = "erdos97.n9_radius_blocker_rich_quotient_pilot.v1"
STATUS = "N9_RADIUS_BLOCKER_RICH_QUOTIENT_PILOT_ONLY"
DEFAULT_SOURCE = (
    ROOT / "data" / "certificates" / "n9_radius_blocker_rich_projection_pilot.json"
)
DEFAULT_OUT = (
    ROOT / "data" / "certificates" / "n9_radius_blocker_rich_quotient_pilot.json"
)
EXPECTED_SUMMARY = {
    "n": 9,
    "rich_class_count": 9,
    "max_rich_class_size": 5,
    "vertex_circle_status": "self_edge",
    "strict_edge_count": 225,
    "self_edge_conflict_count": 193,
    "cycle_edge_count": 0,
    "first_self_edge_row": 0,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_projection_payload(path: Path) -> Mapping[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise AssertionError("projection pilot artifact is not an object")
    return payload


def rich_rows_from_payload(payload: Mapping[str, object]) -> list[RichClassRow]:
    raw_classes = payload.get("projected_rich_classes")
    if not isinstance(raw_classes, list):
        raise AssertionError("projection pilot has no rich classes")
    rows: list[RichClassRow] = []
    for center, center_classes in enumerate(raw_classes):
        if not isinstance(center_classes, list) or len(center_classes) != 1:
            raise AssertionError(f"center {center} does not have one rich class")
        rich_class = center_classes[0]
        if not isinstance(rich_class, list):
            raise AssertionError(f"center {center} rich class is not a list")
        rows.append(
            RichClassRow(
                center=center,
                witnesses=tuple(int(label) for label in rich_class),
            )
        )
    return rows


def order_from_payload(payload: Mapping[str, object]) -> list[int]:
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("projection pilot has no summary")
    order = summary.get("order")
    if not isinstance(order, list):
        raise AssertionError("projection pilot summary has no order")
    return [int(label) for label in order]


def build_payload(source: Path = DEFAULT_SOURCE) -> dict[str, object]:
    """Build the deterministic full rich-class quotient pilot payload."""

    projection = load_projection_payload(source)
    rich_rows = rich_rows_from_payload(projection)
    order = order_from_payload(projection)
    n = len(order)
    replay = replay_vertex_circle_rich_quotient(n, order, rich_rows)
    class_sizes = [len(row.witnesses) for row in rich_rows]
    self_edge_rows = Counter(edge.row for edge in replay.self_edge_conflicts)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Full rich-class vertex-circle quotient replay for the bounded "
            "n=9 synthetic size-five radius-blocker pilot. It checks this "
            "one finite rich-class family without choosing exact four-subsets, "
            "but it is not a proof of n=9, not a proof of the adaptive "
            "blocker bridge, and not a counterexample."
        ),
        "summary": {
            "n": n,
            "order": order,
            "rich_class_count": len(rich_rows),
            "rich_class_sizes": class_sizes,
            "max_rich_class_size": max(class_sizes),
            "vertex_circle_status": replay.status,
            "strict_edge_count": replay.strict_edge_count,
            "self_edge_conflict_count": len(replay.self_edge_conflicts),
            "cycle_edge_count": len(replay.cycle_edges),
            "first_self_edge_row": (
                replay.self_edge_conflicts[0].row
                if replay.self_edge_conflicts
                else None
            ),
        },
        "source_projection_pilot": {
            "path": source.relative_to(ROOT).as_posix(),
            "schema": projection.get("schema"),
            "status": projection.get("status"),
            "trust": projection.get("trust"),
            "sha256": sha256_file(source),
            "summary": projection.get("summary"),
        },
        "rich_rows": [
            {
                "center": row.center,
                "witnesses": list(row.witnesses),
            }
            for row in rich_rows
        ],
        "self_edge_rows": {
            str(row): int(self_edge_rows[row]) for row in sorted(self_edge_rows)
        },
        "replay": result_to_json(replay),
        "interpretation_warnings": [
            "This checks one synthetic size-five rich-class family only.",
            "It is full quotient replay for that family, not a classification of n=9.",
            "It does not prove the adaptive radius-blocker bridge.",
            "No general proof and no counterexample are claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_n9_radius_blocker_rich_quotient_pilot.py",
            "command": (
                "python scripts/check_n9_radius_blocker_rich_quotient_pilot.py "
                "--write --assert-expected"
            ),
            "sources": [
                "data/certificates/n9_radius_blocker_rich_projection_pilot.json",
                "src/erdos97/vertex_circle_quotient_replay.py",
            ],
        },
    }


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    """Assert the stable full rich-class quotient pilot counts."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"unexpected status: {payload.get('status')!r}")
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("summary is missing")
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary[{key!r}] is {summary.get(key)!r}, expected {expected!r}"
            )


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = json.loads(path.read_text(encoding="utf-8"))
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=9 radius-blocker full rich-class quotient pilot")
    print(f"claim scope: {payload['claim_scope']}")
    print(f"rich classes: {summary['rich_class_count']}")
    print(f"status: {summary['vertex_circle_status']}")
    print(f"strict edges: {summary['strict_edge_count']}")
    print(f"self-edge conflicts: {summary['self_edge_conflict_count']}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true", help="write the artifact")
    parser.add_argument("--check", action="store_true", help="compare artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print full JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload(args.source)
    if args.assert_expected:
        assert_expected_payload(payload)
    if args.check:
        compare_artifact(payload, args.out)
    if args.write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_summary(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
