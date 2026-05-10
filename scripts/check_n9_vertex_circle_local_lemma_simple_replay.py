#!/usr/bin/env python3
"""Check the n=9 vertex-circle local-lemma packets by simple JSON replay."""

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

from erdos97.n9_vertex_circle_local_lemma_simple_replay import (  # noqa: E402
    assert_expected_simple_packet_replay,
    simple_packet_replay_payload,
)

DEFAULT_SELF_EDGE_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_self_edge_template_packet.json"
)
DEFAULT_STRICT_CYCLE_PACKET = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_strict_cycle_template_packet.json"
)


def load_artifact(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def replay_payload(
    *,
    self_edge_packet_path: Path = DEFAULT_SELF_EDGE_PACKET,
    strict_cycle_packet_path: Path = DEFAULT_STRICT_CYCLE_PACKET,
) -> dict[str, Any]:
    return simple_packet_replay_payload(
        load_artifact(self_edge_packet_path),
        load_artifact(strict_cycle_packet_path),
    )


def summary_lines(payload: dict[str, Any]) -> list[str]:
    coverage = payload["coverage_summary"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        (
            "families: "
            f"{coverage['covered_family_count']}/"
            f"{coverage['expected_family_count']}"
        ),
        (
            "assignments: "
            f"{coverage['covered_assignment_count']}/"
            f"{coverage['expected_assignment_count']}"
        ),
        (
            "self-edge: "
            f"{coverage['self_edge_family_count']} families, "
            f"{coverage['self_edge_assignment_count']} assignments"
        ),
        (
            "strict-cycle: "
            f"{coverage['strict_cycle_family_count']} families, "
            f"{coverage['strict_cycle_assignment_count']} assignments"
        ),
    ]


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
        "--check",
        action="store_true",
        help="Exit nonzero when packet-level replay validation fails.",
    )
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="Assert the current expected packet-level replay counts.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON payload.")
    args = parser.parse_args(argv)

    payload = replay_payload(
        self_edge_packet_path=args.self_edge_packet,
        strict_cycle_packet_path=args.strict_cycle_packet,
    )
    if args.assert_expected:
        assert_expected_simple_packet_replay(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for line in summary_lines(payload):
            print(line)
        for error in payload["validation_errors"]:
            print(f"error[{error['scope']}]: {error['error']}")

    if args.check and payload["validation_status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
