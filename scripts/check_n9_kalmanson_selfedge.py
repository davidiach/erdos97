#!/usr/bin/env python3
"""Run or replay the review-pending n=9 Kalmanson self-edge checker."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter

from erdos97.n9_kalmanson_selfedge import (
    assert_expected_summary,
    run,
    summary_payload,
    verify_certificate_payload,
)
from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_kalmanson_selfedge.json"


def load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=9)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print stable JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print stable JSON without certificate arrays",
    )
    parser.add_argument("--summary-only", action="store_true", help="omit certificate arrays")
    parser.add_argument("--write", action="store_true", help="write the full artifact")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="path used by --write")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument(
        "--verify-certificate",
        default=None,
        help="replay a stored certificate JSON without rerunning the brancher",
    )
    args = parser.parse_args()
    if args.n != 9 and not args.verify_certificate:
        parser.error("this n9 artifact checker only supports --n 9")

    start = perf_counter()
    if args.verify_certificate:
        payload = load_json(Path(args.verify_certificate))
        result = verify_certificate_payload(payload)
        result["mode"] = "verify_certificate"
    else:
        payload = run(args.n)
        result = summary_payload(payload) if args.summary_only else dict(payload)
        result["mode"] = "enumerate"

    if args.assert_expected:
        assert_expected_summary(result)

    if args.write:
        if args.verify_certificate:
            parser.error("--write cannot be combined with --verify-certificate")
        write_json(Path(args.out), payload)

    elapsed = perf_counter() - start
    if args.summary_json:
        print(json.dumps(summary_payload(result), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("review-pending n=9 Kalmanson self-edge checker")
        print(f"mode: {result['mode']}")
        print(f"n: {result['n']}")
        print(f"row options per center: {result['row_options_per_center']}")
        print(f"nodes visited: {result['nodes_visited']}")
        print(f"terminal assignments: {result['terminal_assignments']}")
        print(f"killed by Kalmanson self-edge: {result['killed_by_kalmanson_self_edge']}")
        print(f"unkilled: {result['unkilled']}")
        print(f"certificate sha256: {result['certificate_sha256']}")
        print(f"elapsed_seconds: {elapsed:.6f}")
        if "verified_certificates" in result:
            print(f"verified certificates: {result['verified_certificates']}")
        if args.write:
            print(f"wrote {display_path(args.out, ROOT)}")
        if args.assert_expected:
            print("OK: n=9 Kalmanson self-edge counts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
