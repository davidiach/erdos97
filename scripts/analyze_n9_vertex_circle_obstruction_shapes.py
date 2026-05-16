#!/usr/bin/env python3
"""Mine obstruction shapes in the n=9 vertex-circle frontier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_vertex_circle_obstruction_shapes import (  # noqa: E402
    assert_expected_counts,
    obstruction_shape_summary,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_vertex_circle_obstruction_shapes.json"


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(payload: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    parser.add_argument("--write", action="store_true", help="write stable JSON artifact")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="path used by --write")
    parser.add_argument(
        "--artifact",
        default=str(DEFAULT_OUT),
        help="path loaded by --check",
    )
    parser.add_argument("--check", action="store_true", help="validate an existing artifact")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    generated = obstruction_shape_summary()
    errors: list[str] = []
    if args.check:
        artifact = Path(args.artifact)
        try:
            payload = _load_json(artifact)
        except (OSError, json.JSONDecodeError) as exc:
            payload = {}
            errors.append(f"could not load artifact: {exc}")
        else:
            if payload != generated:
                errors.append("artifact does not match regenerated obstruction-shape payload")
    else:
        artifact = Path(args.out)
        payload = generated

    if args.assert_expected and not errors:
        try:
            assert_expected_counts(payload)  # type: ignore[arg-type]
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"expected obstruction-shape counts failed: {exc}")
    if args.write:
        out = Path(args.out)
        _write_json(generated, out)
    if args.json:
        if errors:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "artifact": display_path(artifact, ROOT),
                        "validation_errors": errors,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact, ROOT)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        search = payload["pre_vertex_circle_search"]
        print("n=9 vertex-circle obstruction shape diagnostic")
        print(f"nodes visited: {search['nodes_visited']}")
        print(f"pre-vertex-circle full assignments: {search['full_assignments']}")
        print(f"status counts: {payload['obstruction_status_counts']}")
        print(
            "strict-cycle lengths: "
            f"{payload['strict_cycle_summary']['cycle_length_counts']}"
        )
        print(
            "self-edge equality path lengths: "
            f"{payload['self_edge_summary']['equality_path_length_counts']}"
        )
        if args.assert_expected:
            print("OK: obstruction shape counts verified")
        if args.check:
            print("OK: stored obstruction-shape artifact matches regenerated payload")
        if args.write:
            print(f"wrote {display_path(args.out, ROOT)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
