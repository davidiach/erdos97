#!/usr/bin/env python3
"""Validate the n=9 selected-baseline escape-budget overlay artifact."""

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

from erdos97.n9_selected_baseline_escape_budget import (  # noqa: E402
    selected_baseline_escape_budget_overlay,
)

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_selected_baseline_escape_budget_overlay.json"
)
EXPECTED_TOP_LEVEL_KEYS = {
    "accepted_frontier_overlay",
    "base_apex_slack",
    "budget_overlay",
    "claim_scope",
    "interpretation",
    "n",
    "provenance",
    "schema",
    "selected_baseline",
    "source_artifacts",
    "status",
    "trust",
    "witness_size",
}
EXPECTED_CLAIM_SCOPE = (
    "Focused n=9 selected-baseline escape-budget overlay bookkeeping; "
    "not a proof of n=9, not a counterexample, not a geometric "
    "realizability test, and not a global status update."
)
EXPECTED_PROVENANCE = {
    "generator": "scripts/analyze_n9_selected_baseline_escape_budget_overlay.py",
    "command": (
        "python scripts/analyze_n9_selected_baseline_escape_budget_overlay.py "
        "--assert-expected --out "
        "data/certificates/n9_selected_baseline_escape_budget_overlay.json"
    ),
}


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def validate_payload(payload: Any) -> list[str]:
    """Return validation errors for a loaded overlay artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    top_level_keys = set(payload)
    if top_level_keys != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(top_level_keys)!r}"
        )

    expected_meta = {
        "schema": "erdos97.n9_selected_baseline_escape_budget_overlay.v2",
        "status": "EXPLORATORY_LEDGER_ONLY",
        "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
        "n": 9,
        "witness_size": 4,
        "base_apex_slack": 9,
    }
    for key, expected in expected_meta.items():
        expect_equal(errors, key, payload.get(key), expected)

    claim_scope = payload.get("claim_scope")
    expect_equal(errors, "claim_scope", claim_scope, EXPECTED_CLAIM_SCOPE)
    if isinstance(claim_scope, str):
        lowered = claim_scope.lower()
        for phrase in (
            "not a proof",
            "not a counterexample",
            "not a geometric realizability test",
            "not a global status update",
        ):
            if phrase not in lowered:
                errors.append(f"claim_scope must include {phrase!r}")

    provenance = payload.get("provenance")
    expect_equal(errors, "provenance", provenance, EXPECTED_PROVENANCE)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list) or not all(
        isinstance(item, str) for item in interpretation
    ):
        errors.append("interpretation must be a list of strings")
    elif "No proof of the n=9 case is claimed." not in interpretation:
        errors.append("interpretation must preserve the no-proof statement")

    try:
        expected_payload = selected_baseline_escape_budget_overlay()
    except (AssertionError, ValueError) as exc:
        errors.append(f"recomputed overlay failed: {exc}")
    else:
        expect_equal(errors, "overlay payload", payload, expected_payload)
    return errors


def display_path(path: Path) -> str:
    """Return a stable repo-relative path when possible."""

    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    selected = object_payload.get("selected_baseline", {})
    budget = object_payload.get("budget_overlay", {})
    strict_rows = []
    conservative_rows = []
    if isinstance(budget, dict):
        strict = budget.get("strict_positive_threshold", {})
        conservative = budget.get("sum_exceeds_threshold", {})
        if isinstance(strict, dict):
            strict_rows = strict.get("budget_rows", [])
        if isinstance(conservative, dict):
            conservative_rows = conservative.get("budget_rows", [])
    return {
        "ok": not errors,
        "artifact": display_path(path),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "assignment_count": (
            selected.get("assignment_count") if isinstance(selected, dict) else None
        ),
        "strict_selected_baseline_forced_assignment_count": (
            selected.get("strict_positive_forced_assignment_count")
            if isinstance(selected, dict)
            else None
        ),
        "conservative_selected_baseline_forced_assignment_count": (
            selected.get("sum_exceeds_forced_assignment_count")
            if isinstance(selected, dict)
            else None
        ),
        "strict_budget9_universally_forced_assignment_count": (
            strict_rows[9]["universally_forced_assignment_count"]
            if isinstance(strict_rows, list) and len(strict_rows) > 9
            else None
        ),
        "conservative_budget9_universally_forced_assignment_count": (
            conservative_rows[9]["universally_forced_assignment_count"]
            if isinstance(conservative_rows, list) and len(conservative_rows) > 9
            else None
        ),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="fail if validation fails")
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 selected-baseline escape-budget overlay artifact")
        print(f"artifact: {summary['artifact']}")
        print(f"assignments: {summary['assignment_count']}")
        print(
            "selected-baseline forced assignments: "
            f"strict={summary['strict_selected_baseline_forced_assignment_count']}, "
            f"conservative={summary['conservative_selected_baseline_forced_assignment_count']}"
        )
        if args.check:
            print("OK: selected-baseline overlay checks passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
