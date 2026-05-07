#!/usr/bin/env python3
"""Validate the archived secondary n=10 singleton replay artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n10_secondary_singleton_replay import (  # noqa: E402
    CHECK_SCOPE,
    ROW0_CHOICES_COVERED,
    TOTAL_FULL,
    TOTAL_NODES,
    TRUST,
    TYPE,
    load_artifact,
    primary_prefix_match,
    validate_secondary_payload,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "2026-05-05" / "n10_secondary.json"
DEFAULT_PRIMARY_ARTIFACT = ROOT / "data" / "certificates" / "n10_vertex_circle_singleton_slices.json"


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def summary_payload(
    artifact: Path,
    primary_artifact: Path,
    payload: Any,
    primary_payload: Any,
    errors: Sequence[str],
) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    object_primary = primary_payload if isinstance(primary_payload, dict) else {}
    return {
        "ok": not errors,
        "artifact": display_path(artifact, ROOT),
        "primary_artifact": display_path(primary_artifact, ROOT),
        "type": object_payload.get("type"),
        "trust": object_payload.get("trust"),
        "row0_choices_covered": object_payload.get("row0_choices_covered"),
        "expected_row0_choices_covered": ROW0_CHOICES_COVERED,
        "total_nodes": object_payload.get("total_nodes"),
        "expected_total_nodes": TOTAL_NODES,
        "total_full": object_payload.get("total_full"),
        "expected_total_full": TOTAL_FULL,
        "total_counts": object_payload.get("total_counts"),
        "check_scope": CHECK_SCOPE,
        "primary_prefix_match": (
            primary_prefix_match(object_payload, object_primary)
            if isinstance(payload, dict) and isinstance(primary_payload, dict)
            else False
        ),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--primary-artifact", type=Path, default=DEFAULT_PRIMARY_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="validate the artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print stable JSON summary")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = _resolve(args.artifact)
    primary_artifact = _resolve(args.primary_artifact)
    try:
        payload = load_artifact(artifact)
        primary_payload = load_artifact(primary_artifact)
        errors = validate_secondary_payload(payload, primary_payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        primary_payload = {}
        errors = [str(exc)]

    summary = summary_payload(artifact, primary_artifact, payload, primary_payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact, ROOT)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=10 secondary singleton replay cross-check")
        print(f"artifact: {summary['artifact']}")
        print(f"primary artifact: {summary['primary_artifact']}")
        print(f"type: {TYPE}")
        print(f"trust: {TRUST}")
        print(f"row0 choices covered: {summary['row0_choices_covered']}")
        print(f"total nodes: {summary['total_nodes']}")
        print(f"total full assignments: {summary['total_full']}")
        print("OK: secondary replay matches expected first-five singleton prefix")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
