#!/usr/bin/env python3
"""Generate or check the bounded n=10 row0 turn-inequality pilot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n10_turn_row0_pilot import (  # noqa: E402
    assert_expected_payload,
    summary_payload,
    validate_payload,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n10_turn_row0_pilot.json"


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _load(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("expected object payload")
    return payload


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="validate stored artifact")
    parser.add_argument("--write", action="store_true", help="write generated artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    out = _resolve(args.out)
    if args.write and args.check and artifact != out:
        parser.error("--write --check requires --artifact and --out to match")

    start = perf_counter()
    payload = _load(artifact) if args.check else summary_payload()
    errors = validate_payload(payload)
    if errors:
        raise SystemExit("; ".join(errors[:5]))
    if args.assert_expected:
        assert_expected_payload(payload)
    elapsed = perf_counter() - start

    if args.write:
        _write(out, payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("bounded n=10 row0 turn-inequality pilot")
        print(f"full assignments: {payload['full_assignment_count']}")
        print(f"turn status counts: {payload['turn_status_counts']}")
        print(f"vertex-circle counts: {payload['vertex_circle_status_counts']}")
        print(f"elapsed_seconds: {elapsed:.6f}")
        if args.assert_expected:
            print("OK: bounded n=10 row0 pilot matches expected data")
        if args.check:
            print(f"checked {display_path(artifact, ROOT)}")
        if args.write:
            print(f"wrote {display_path(out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
