#!/usr/bin/env python3
"""Scan n=9 vertex-circle packets for reusable local lemma instances."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_vertex_circle_local_lemmas import (  # noqa: E402
    assert_expected_local_lemma_scan,
    local_lemma_scan_payload,
)

DEFAULT_SELF_EDGE_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_self_edge_template_packet.json"
)
DEFAULT_STRICT_CYCLE_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_strict_cycle_template_packet.json"
)


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def scan_payload(
    *,
    self_edge_packet_path: Path = DEFAULT_SELF_EDGE_PACKET,
    strict_cycle_packet_path: Path = DEFAULT_STRICT_CYCLE_PACKET,
) -> dict[str, Any]:
    """Load source artifacts and return the local-lemma scan payload."""

    return local_lemma_scan_payload(
        load_artifact(self_edge_packet_path),
        load_artifact(strict_cycle_packet_path),
    )


def summary_lines(payload: dict[str, Any]) -> list[str]:
    """Return human-readable scan summary lines."""

    coverage = payload["coverage_summary"]
    lines = [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"source families: {coverage['source_family_count']}",
        f"source assignments: {coverage['source_assignment_count']}",
        f"covered families: {coverage['covered_family_count']}",
        f"covered assignments: {coverage['covered_assignment_count']}",
        f"uncovered families: {coverage['uncovered_family_count']}",
        f"uncovered assignments: {coverage['uncovered_assignment_count']}",
        f"uncovered family ids: {','.join(coverage['uncovered_family_ids'])}",
    ]
    for lemma in payload["lemmas"]:
        lines.append(
            f"{lemma['lemma_id']}: "
            f"{lemma['instance_count']} instances, "
            f"{lemma['covered_assignment_count']} assignments, "
            f"families {','.join(lemma['family_ids'])}"
        )
    special = payload["direct_two_row_nested_spoke_special_case"]
    lines.append(
        f"{special['lemma_id']}: {special['instance_count']} exact direct instances"
    )
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-edge-packet",
        type=Path,
        default=DEFAULT_SELF_EDGE_PACKET,
        help="Path to n9 self-edge template packet JSON.",
    )
    parser.add_argument(
        "--strict-cycle-packet",
        type=Path,
        default=DEFAULT_STRICT_CYCLE_PACKET,
        help="Path to n9 strict-cycle template packet JSON.",
    )
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="Assert the currently expected local-lemma scan counts.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args(argv)

    payload = scan_payload(
        self_edge_packet_path=args.self_edge_packet,
        strict_cycle_packet_path=args.strict_cycle_packet,
    )
    if args.assert_expected:
        assert_expected_local_lemma_scan(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("\n".join(summary_lines(payload)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
