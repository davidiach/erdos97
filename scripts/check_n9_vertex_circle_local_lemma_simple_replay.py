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
DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_local_lemma_simple_replay.json"
)


def load_artifact(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def replay_payload(
    *,
    self_edge_packet_path: Path = DEFAULT_SELF_EDGE_PACKET,
    strict_cycle_packet_path: Path = DEFAULT_STRICT_CYCLE_PACKET,
) -> dict[str, Any]:
    return simple_packet_replay_payload(
        load_artifact(self_edge_packet_path),
        load_artifact(strict_cycle_packet_path),
    )


def validate_artifact_payload(payload: Any, expected_payload: dict[str, Any]) -> list[str]:
    """Return validation errors for a stored simple-replay artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]
    errors: list[str] = []
    try:
        assert_expected_simple_packet_replay(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected simple-replay payload failed: {exc}")
    if payload != expected_payload:
        errors.append("simple-replay payload mismatch")
    return errors


def summary_payload(path: Path, payload: Any, errors: list[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    coverage = object_payload.get("coverage_summary", {})
    if not isinstance(coverage, dict):
        coverage = {}
    return {
        "ok": not errors,
        "artifact": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "validation_status": object_payload.get("validation_status"),
        "covered_family_count": coverage.get("covered_family_count"),
        "covered_assignment_count": coverage.get("covered_assignment_count"),
        "self_edge_family_count": coverage.get("self_edge_family_count"),
        "self_edge_assignment_count": coverage.get("self_edge_assignment_count"),
        "strict_cycle_family_count": coverage.get("strict_cycle_family_count"),
        "strict_cycle_assignment_count": coverage.get("strict_cycle_assignment_count"),
        "validation_errors": list(errors),
    }


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
    parser.add_argument("--artifact", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="Write generated artifact.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the stored artifact against freshly replayed packet data.",
    )
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="Assert the current expected packet-level replay counts.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON payload.")
    args = parser.parse_args(argv)

    out = _resolve(args.out)
    artifact = _resolve(args.artifact) if args.artifact is not None else DEFAULT_ARTIFACT
    if args.write and args.check:
        if args.artifact is not None and artifact != out:
            print(
                "--write --check requires matching --artifact/--out or omitted --artifact",
                file=sys.stderr,
            )
            return 2
        artifact = out

    payload = replay_payload(
        self_edge_packet_path=_resolve(args.self_edge_packet),
        strict_cycle_packet_path=_resolve(args.strict_cycle_packet),
    )
    if args.assert_expected:
        assert_expected_simple_packet_replay(payload)

    if args.write:
        write_json(payload, out)
        if not args.check:
            if args.json:
                print(json.dumps(summary_payload(out, payload, []), indent=2, sort_keys=True))
            else:
                print(f"wrote {out.relative_to(ROOT)}")
            return 0

    if args.check:
        try:
            stored_payload = load_artifact(artifact)
            errors = validate_artifact_payload(stored_payload, payload)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            stored_payload = {}
            errors = [str(exc)]

        if args.json:
            print(json.dumps(summary_payload(artifact, stored_payload, errors), indent=2, sort_keys=True))
        elif errors:
            print(f"FAILED: {artifact}", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
        else:
            for line in summary_lines(stored_payload):
                print(line)
            print("OK: simple packet replay artifact checks passed")
        return 1 if errors else 0

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for line in summary_lines(payload):
            print(line)
        for error in payload["validation_errors"]:
            print(f"error[{error['scope']}]: {error['error']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
