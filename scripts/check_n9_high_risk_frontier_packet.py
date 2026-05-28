#!/usr/bin/env python3
"""Generate or check the n=9 high-risk frontier packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_high_risk_frontier_packet import (  # noqa: E402
    CLAIM_SCOPE,
    PROVENANCE,
    SCHEMA,
    STATUS,
    TRUST,
    assert_expected_payload,
    build_payload,
)

DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n9_high_risk_frontier_packet.json"
EXPECTED_TOP_LEVEL_KEYS = {
    "assignments",
    "claim_scope",
    "cyclic_order",
    "families",
    "interpretation",
    "n",
    "provenance",
    "row_size",
    "schema",
    "selection_rule",
    "source_frontier",
    "status",
    "summary",
    "trust",
}


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a high-risk frontier packet payload."""

    errors: list[str] = []
    _expect_equal(errors, "top-level keys", set(payload), EXPECTED_TOP_LEVEL_KEYS)
    _expect_equal(errors, "schema", payload.get("schema"), SCHEMA)
    _expect_equal(errors, "status", payload.get("status"), STATUS)
    _expect_equal(errors, "trust", payload.get("trust"), TRUST)
    _expect_equal(errors, "claim_scope", payload.get("claim_scope"), CLAIM_SCOPE)
    _expect_equal(errors, "provenance", payload.get("provenance", {}).get("generator"), PROVENANCE["generator"])
    _expect_equal(errors, "provenance command", payload.get("provenance", {}).get("command"), PROVENANCE["command"])
    try:
        assert_expected_payload(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))

    summary = payload.get("summary")
    assignments = payload.get("assignments")
    families = payload.get("families")
    if isinstance(summary, Mapping) and isinstance(assignments, list):
        _expect_equal(
            errors,
            "assignment count",
            len(assignments),
            summary.get("selected_assignment_count"),
        )
        trigger_counts = [
            int(record.get("simple_obstruction_a_trigger_count", -1))
            for record in assignments
            if isinstance(record, Mapping)
        ]
        if any(count != 0 for count in trigger_counts):
            errors.append("selected assignment has a simple obstruction-A trigger")
        if any(
            record.get("kill_reason")
            not in {"vertex_circle_self_edge", "vertex_circle_strict_cycle"}
            for record in assignments
            if isinstance(record, Mapping)
        ):
            errors.append("selected assignment has an unexpected kill reason")
        if any(
            not record.get("radius_blocker_replay", {}).get(
                "all_incidence_survivors_obstructed"
            )
            for record in assignments
            if isinstance(record, Mapping)
        ):
            errors.append("selected assignment has an unobstructed blocker replay")
    if isinstance(families, list):
        family_ids = [row.get("family_id") for row in families if isinstance(row, Mapping)]
        if family_ids != sorted(family_ids):
            errors.append("families are not sorted by family_id")

    if recompute:
        try:
            regenerated = build_payload()
        except Exception as exc:  # pragma: no cover - defensive CLI validation
            errors.append(f"could not regenerate payload: {exc}")
        else:
            if payload != regenerated:
                errors.append("payload does not match regenerated high-risk packet")
    return errors


def summary_payload(path: Path, payload: Mapping[str, Any], errors: list[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    summary = payload.get("summary", {})
    if not isinstance(summary, Mapping):
        summary = {}
    return {
        "ok": not errors,
        "path": str(path),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "selected_assignment_count": summary.get("selected_assignment_count"),
        "selected_family_count": summary.get("selected_family_count"),
        "selected_status_counts": summary.get("selected_status_counts"),
        "non_ear_zero_based_indices": summary.get("non_ear_zero_based_indices"),
        "post_vertex_circle_survivor_count": summary.get(
            "post_vertex_circle_survivor_count"
        ),
        "errors": errors,
    }


def print_human_summary(payload: Mapping[str, Any]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("n=9 high-risk frontier packet")
    print(f"claim scope: {CLAIM_SCOPE}")
    print(f"selected assignments: {summary['selected_assignment_count']}")
    print(f"selected families: {summary['selected_family_count']}")
    print(f"status counts: {summary['selected_status_counts']}")
    print(f"non-ear indices: {summary['non_ear_zero_based_indices']}")
    print(
        "post vertex-circle survivors: "
        f"{summary['post_vertex_circle_survivor_count']}"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write the checked artifact")
    parser.add_argument("--check", action="store_true", help="compare against the checked artifact")
    parser.add_argument("--assert-expected", action="store_true", help="assert stable packet counts")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a human summary")
    parser.add_argument(
        "--lightweight",
        action="store_true",
        help="validate an existing artifact without regenerating the packet",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload()
    if args.assert_expected:
        assert_expected_payload(payload)
    if args.write:
        write_json(payload, args.out)
    if args.check:
        checked = load_artifact(args.out)
        if checked != payload:
            raise AssertionError(f"checked artifact is stale: {args.out.relative_to(ROOT)}")
    if args.json:
        if args.check:
            errors = validate_payload(
                load_artifact(args.out),
                recompute=not args.lightweight,
            )
            print(json.dumps(summary_payload(args.out, payload, errors), indent=2, sort_keys=True))
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_human_summary(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
