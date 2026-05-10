#!/usr/bin/env python3
"""Check the wrong-fourth closure-activation negative control."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.closure_activation_negative_controls import (  # noqa: E402
    assert_wrong_fourth_expected,
    certificate_summary,
    validate_wrong_fourth_certificate,
    wrong_fourth_negative_control_certificate,
)


DEFAULT_CERTIFICATE = (
    ROOT / "data" / "certificates" / "closure_activation_wrong_fourth_negative_control.json"
)


def load_payload(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("certificate top level must be a JSON object")
    return payload


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--certificate",
        type=Path,
        default=DEFAULT_CERTIFICATE,
        help="certificate path to check or write",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="load and check --certificate instead of generating the built-in payload",
    )
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print JSON summary")
    parser.add_argument(
        "--write",
        action="store_true",
        help="write the built-in payload to --certificate",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    certificate = args.certificate
    if not certificate.is_absolute():
        certificate = ROOT / certificate

    try:
        payload = (
            load_payload(certificate)
            if args.check
            else wrong_fourth_negative_control_certificate()
        )
        errors = validate_wrong_fourth_certificate(payload)
        if args.assert_expected and not errors:
            assert_wrong_fourth_expected(payload)
    except (OSError, ValueError, AssertionError) as exc:
        errors = [str(exc)]
        payload = {}

    if args.write and not args.check and not errors:
        certificate.parent.mkdir(parents=True, exist_ok=True)
        certificate.write_text(
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

    summary = certificate_summary(payload)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("closure activation wrong-fourth negative control")
        print(f"n: {summary['n']}")
        print(f"closure: {summary['closure']}")
        print(f"exposed row: {summary['exposed_row']}")
        print(f"target row absent: {summary['target_row_absent']}")
        if args.assert_expected:
            print("OK: wrong-fourth negative-control expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
