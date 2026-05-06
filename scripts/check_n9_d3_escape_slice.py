#!/usr/bin/env python3
"""Validate the n=9 D=3 coupled escape-slice artifact."""

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

from erdos97.n9_d3_escape_slice import d3_escape_slice_report  # noqa: E402

DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n9_base_apex_d3_escape_slice.json"
EXPECTED_TOP_LEVEL_KEYS = {
    "capacity_deficit",
    "claim_scope",
    "coupled_slice",
    "escape_slice",
    "interpretation",
    "n",
    "profile_slice",
    "provenance",
    "relevant_deficit_count",
    "schema",
    "source_artifacts",
    "status",
    "total_profile_excess",
    "trust",
    "witness_size",
}
EXPECTED_CLAIM_SCOPE = (
    "Focused n=9 base-apex D=3,r=3 coupled escape-slice bookkeeping; "
    "not a proof of n=9, not a counterexample, not a geometric "
    "realizability test, and not a global status update."
)
EXPECTED_PROVENANCE = {
    "generator": "scripts/analyze_n9_d3_escape_slice.py",
    "command": (
        "python scripts/analyze_n9_d3_escape_slice.py --assert-expected "
        "--out data/certificates/n9_base_apex_d3_escape_slice.json"
    ),
}


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def validate_payload(payload: Any, *, recompute: bool = True) -> list[str]:
    """Return validation errors for a loaded D=3 escape-slice artifact."""

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
        "schema": "erdos97.n9_base_apex_d3_escape_slice.v1",
        "status": "EXPLORATORY_LEDGER_ONLY",
        "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
        "n": 9,
        "witness_size": 4,
        "total_profile_excess": 6,
        "capacity_deficit": 3,
        "relevant_deficit_count": 3,
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

    if recompute:
        try:
            expected_payload = d3_escape_slice_report()
        except (AssertionError, ValueError) as exc:
            errors.append(f"recomputed D=3 slice failed: {exc}")
        else:
            expect_equal(errors, "D=3 escape-slice payload", payload, expected_payload)
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
    profile = object_payload.get("profile_slice", {})
    escape = object_payload.get("escape_slice", {})
    coupled = object_payload.get("coupled_slice", {})
    return {
        "ok": not errors,
        "artifact": display_path(path),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "labelled_profile_sequence_count": (
            profile.get("labelled_profile_sequence_count")
            if isinstance(profile, dict)
            else None
        ),
        "labelled_escape_placement_count": (
            escape.get("labelled_escape_placement_count")
            if isinstance(escape, dict)
            else None
        ),
        "common_dihedral_pair_class_count": (
            coupled.get("common_dihedral_pair_class_count")
            if isinstance(coupled, dict)
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
        print("n=9 D=3 escape-slice artifact")
        print(f"artifact: {summary['artifact']}")
        print(f"profile sequences: {summary['labelled_profile_sequence_count']}")
        print(f"escape placements: {summary['labelled_escape_placement_count']}")
        print(
            "common-dihedral classes: "
            f"{summary['common_dihedral_pair_class_count']}"
        )
        if args.check:
            print("OK: D=3 escape-slice checks passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
