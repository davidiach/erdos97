#!/usr/bin/env python3
"""Generate or check the compact n=9 vertex-circle local-core packet."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_vertex_circle_obstruction_shapes import (  # noqa: E402
    LOCAL_CORE_PACKET_CLAIM_SCOPE,
    LOCAL_CORE_PACKET_PROVENANCE,
    LOCAL_CORE_PACKET_SCHEMA,
    LOCAL_CORE_PACKET_STATUS,
    LOCAL_CORE_PACKET_TRUST,
    assert_expected_local_core_packet_counts,
    local_core_packet_summary,
)
from erdos97.path_display import display_path  # noqa: E402
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    replay_local_core_bundle,
)

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_local_core_packet.json"
)
EXPECTED_TOP_LEVEL_KEYS = {
    "certificates",
    "claim_scope",
    "core_size_counts",
    "cyclic_order",
    "family_count",
    "interpretation",
    "max_core_size",
    "n",
    "orbit_size_sum",
    "provenance",
    "row_size",
    "schema",
    "source_artifacts",
    "status",
    "status_core_size_counts",
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


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error when values differ."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _validate_replay(payload: dict[str, Any], errors: list[str]) -> None:
    try:
        replays = replay_local_core_bundle(payload)
    except (TypeError, ValueError) as exc:
        errors.append(f"local-core replay failed: {exc}")
        return
    if not replays:
        errors.append("local-core replay produced no certificates")
        return

    status_counts = Counter(replay.result.status for replay in replays)
    if status_counts != {"self_edge": 13, "strict_cycle": 3}:
        errors.append(f"unexpected replay status counts: {dict(status_counts)}")
    mismatches = [replay.family_id for replay in replays if not replay.status_matches_expected]
    if mismatches:
        errors.append(f"replay status mismatches: {mismatches}")
    if max(replay.result.selected_row_count for replay in replays) != 6:
        errors.append("unexpected replay max selected row count")


def validate_payload(payload: Any, *, recompute: bool = True) -> list[str]:
    """Return validation errors for a compact local-core packet."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    if set(payload) != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(payload)!r}"
        )

    expected_meta = {
        "schema": LOCAL_CORE_PACKET_SCHEMA,
        "status": LOCAL_CORE_PACKET_STATUS,
        "trust": LOCAL_CORE_PACKET_TRUST,
        "claim_scope": LOCAL_CORE_PACKET_CLAIM_SCOPE,
        "n": 9,
        "row_size": 4,
        "cyclic_order": list(range(9)),
        "family_count": 16,
        "orbit_size_sum": 184,
        "max_core_size": 6,
        "provenance": LOCAL_CORE_PACKET_PROVENANCE,
    }
    for key, expected in expected_meta.items():
        expect_equal(errors, key, payload.get(key), expected)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list) or not all(
        isinstance(item, str) for item in interpretation
    ):
        errors.append("interpretation must be a list of strings")
    elif "No proof of the n=9 case is claimed." not in interpretation:
        errors.append("interpretation must preserve the no-proof statement")

    try:
        assert_expected_local_core_packet_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected packet counts failed: {exc}")

    _validate_replay(payload, errors)

    if recompute:
        try:
            expected_payload = local_core_packet_summary()
        except (AssertionError, ValueError) as exc:
            errors.append(f"recomputed compact local-core packet failed: {exc}")
        else:
            expect_equal(errors, "compact local-core packet", payload, expected_payload)
    return errors


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    return {
        "ok": not errors,
        "artifact": display_path(path, ROOT),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "family_count": object_payload.get("family_count"),
        "orbit_size_sum": object_payload.get("orbit_size_sum"),
        "core_size_counts": object_payload.get("core_size_counts"),
        "status_core_size_counts": object_payload.get("status_core_size_counts"),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write generated packet")
    parser.add_argument("--check", action="store_true", help="validate an existing packet")
    parser.add_argument("--json", action="store_true", help="print stable JSON summary")
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact
    out = args.out if args.out.is_absolute() else ROOT / args.out

    if args.write:
        payload = local_core_packet_summary()
        if args.assert_expected:
            assert_expected_local_core_packet_counts(payload)
        write_json(payload, out)
        if not args.check:
            if args.json:
                print(json.dumps(summary_payload(out, payload, []), indent=2, sort_keys=True))
            else:
                print(f"wrote {display_path(out, ROOT)}")
            return 0

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(payload, recompute=args.check or args.assert_expected)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact, ROOT)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 vertex-circle compact local-core packet")
        print(f"artifact: {summary['artifact']}")
        print(f"families: {summary['family_count']}")
        print(f"orbit-size sum: {summary['orbit_size_sum']}")
        print(f"core size counts: {summary['core_size_counts']}")
        if args.check or args.assert_expected:
            print("OK: compact local-core packet checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
