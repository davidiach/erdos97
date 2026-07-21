#!/usr/bin/env python3
"""Check the bootstrap/T12 full-row anti-activation negative control."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from erdos97.closure_activation_negative_controls import (
    assert_full_row_anti_activation_expected,
    full_row_anti_activation_control_certificate,
    full_row_anti_activation_summary,
    validate_full_row_anti_activation_certificate,
)

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "bootstrap_t12_anti_activation_negative_control.json"
)


def load_payload(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("artifact top level must be a JSON object")
    return payload


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help="artifact path to check or write",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="load and check --artifact instead of generating the built-in payload",
    )
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print JSON summary")
    parser.add_argument(
        "--write",
        action="store_true",
        help="write the built-in payload to --artifact",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact
    if not artifact.is_absolute():
        artifact = ROOT / artifact

    try:
        payload = (
            load_payload(artifact)
            if args.check
            else full_row_anti_activation_control_certificate()
        )
        errors = validate_full_row_anti_activation_certificate(payload)
        if args.assert_expected and not errors:
            assert_full_row_anti_activation_expected(payload)
    except (OSError, ValueError, AssertionError) as exc:
        errors = [str(exc)]
        payload = {}

    if args.write and not args.check and not errors:
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if errors:
        if args.json:
            print(json.dumps({"ok": False, "errors": errors}, indent=2))
        else:
            for error in errors:
                print(error, file=sys.stderr)
        return 1

    summary = full_row_anti_activation_summary(payload)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 full-row anti-activation negative control")
        print(f"closure: {summary['closure_result']}")
        print(f"anti-activation row: {summary['anti_activation_row']['row']}")
        if args.assert_expected:
            print("OK: full-row anti-activation expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
