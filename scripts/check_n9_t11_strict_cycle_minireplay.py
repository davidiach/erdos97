#!/usr/bin/env python3
"""Generate or check the minimal T11/F07 strict-cycle mini-replay artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_t11_strict_cycle_minireplay import (  # noqa: E402
    assert_expected_payload,
    minireplay_payload,
    validate_payload,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_SOURCE = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_t11_strict_cycle_lemma_packet.json"
)
DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_t11_strict_cycle_minireplay.json"
)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _load(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"expected object payload in {display_path(path, ROOT)}")
    return payload


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="validate stored artifact")
    parser.add_argument("--write", action="store_true", help="write generated artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = _resolve(args.source)
    artifact = _resolve(args.artifact)
    out = _resolve(args.out)
    if args.write and args.check and artifact != out:
        raise SystemExit("--write --check requires --artifact and --out to match")

    source_packet = _load(source)
    payload = _load(artifact) if args.check else minireplay_payload(source_packet)
    errors = validate_payload(payload, source_packet)
    if errors:
        raise SystemExit("; ".join(errors[:5]))
    if args.assert_expected:
        assert_expected_payload(payload)

    if args.write:
        _write(out, payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        replay = payload["replay"]
        assert isinstance(replay, dict)
        print("n=9 T11/F07 strict-cycle mini-replay")
        print(f"ok: {payload['ok']}")
        print(f"core rows: {replay['core_centers']}")
        print(f"cycle length: {replay['cycle_length']}")
        print(f"strict-cycle contradiction: {replay['strict_cycle_contradiction']}")
        if args.assert_expected:
            print("OK: T11/F07 mini-replay matches expected data")
        if args.check:
            print(f"checked {display_path(artifact, ROOT)}")
        if args.write:
            print(f"wrote {display_path(out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
