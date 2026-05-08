#!/usr/bin/env python3
"""Generate the n=9 selected-baseline D=3 escape-class crosswalk."""

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

from erdos97.n9_selected_baseline_d3_escape_class_crosswalk import (  # noqa: E402
    assert_expected_crosswalk_counts,
    selected_baseline_d3_escape_class_crosswalk_report,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_OUT = (
    ROOT / "data" / "certificates" / "n9_selected_baseline_d3_escape_class_crosswalk.json"
)


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def load_json(path: Path) -> object:
    """Load a JSON file."""

    return json.loads(path.read_text(encoding="utf-8"))


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print generated JSON")
    parser.add_argument("--out", type=Path, help="write generated JSON to this path")
    parser.add_argument(
        "--check-artifact",
        type=Path,
        help="compare generated JSON with an existing artifact",
    )
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = selected_baseline_d3_escape_class_crosswalk_report()
    if args.assert_expected:
        assert_expected_crosswalk_counts(payload)

    if args.check_artifact is not None:
        artifact = (
            args.check_artifact
            if args.check_artifact.is_absolute()
            else ROOT / args.check_artifact
        )
        checked = load_json(artifact)
        if checked != payload:
            print(
                f"FAILED: generated payload differs from {display_path(artifact, ROOT)}",
                file=sys.stderr,
            )
            return 1

    if args.out is not None:
        out = args.out if args.out.is_absolute() else ROOT / args.out
        write_json(payload, out)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif args.check_artifact is not None:
        print("OK: selected-baseline D=3 escape-class crosswalk artifact is current")
    elif args.out is not None:
        print(f"wrote {display_path(out, ROOT)}")
    else:
        print("n=9 selected-baseline D=3 escape-class crosswalk")
        print(f"assignments: {payload['assignment_count']}")
        print(f"budget-3 choices: {payload['total_budget3_slot_choice_count']}")
        print(f"escaping landings: {payload['escaping_budget3_slot_choice_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
