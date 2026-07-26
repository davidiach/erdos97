#!/usr/bin/env python3
"""Generate or check the exact equilateral-nonagon chord obstruction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from erdos97.json_io import load_json, write_json
from erdos97.n9_equilateral_chord_obstruction import (
    assert_expected_payload,
    payload,
    validate_payload,
)
from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_equilateral_chord_obstruction.json"
)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _load_object(path: Path) -> dict[str, Any]:
    data = load_json(path)
    if not isinstance(data, dict):
        raise ValueError(f"expected object payload in {display_path(path, ROOT)}")
    return data


def summary_json_payload(data: dict[str, Any]) -> dict[str, Any]:
    """Return a compact reviewer-facing payload without the class records."""

    compact = dict(data)
    compact.pop("classes", None)
    return compact


def _print_summary(data: dict[str, Any], elapsed: float) -> None:
    counts = data["counts"]
    print("exact equilateral-nonagon chord obstruction")
    print(f"n: {data['n']}")
    print(f"degree-admissible chord graphs: {counts['degree_admissible_graphs']}")
    print(f"ledger-admissible chord graphs: {counts['ledger_admissible_graphs']}")
    print(f"dihedral classes: {counts['dihedral_classes']}")
    print(f"refuted classes: {counts['refuted_classes']}")
    print(f"strict certificates: {counts['strict_certificates']}")
    print(f"surviving graphs: {counts['surviving_graphs']}")
    print(f"elapsed_seconds: {elapsed:.6f}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print JSON without the per-class certificate records",
    )
    parser.add_argument(
        "--write", action="store_true", help="write stable JSON artifact"
    )
    parser.add_argument("--check", action="store_true", help="check a stored artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    artifact_path = _resolve(args.artifact)
    out_path = _resolve(args.out)
    if args.write and args.check and artifact_path != out_path:
        raise SystemExit("--write --check requires --artifact and --out to match")

    start = perf_counter()
    data = _load_object(artifact_path) if args.check else payload()
    errors = validate_payload(data)
    if errors:
        raise SystemExit("; ".join(errors[:5]))
    if args.assert_expected:
        assert_expected_payload(data)
    if args.write:
        write_json(data, out_path)
    elapsed = perf_counter() - start

    if args.summary_json:
        print(json.dumps(summary_json_payload(data), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        _print_summary(data, elapsed)
        if args.assert_expected:
            print("OK: equilateral-nonagon chord obstruction matches expected data")
        if args.check:
            print(f"checked {display_path(artifact_path, ROOT)}")
        if args.write:
            print(f"wrote {display_path(out_path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
