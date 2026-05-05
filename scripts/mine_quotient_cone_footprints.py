#!/usr/bin/env python3
"""Mine compact equality-footprints from checked quotient-cone certificates.

This first-pass miner intentionally starts from existing fixed-order
certificates. It extracts the selected-distance quotient support that a
certificate actually uses, which is the reusable object needed before trying
larger all-order searches.
"""

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

from erdos97.quotient_cone import footprint_summary  # noqa: E402


C29_CERTIFICATE = (
    ROOT / "data" / "certificates" / "c29_sidon_fixed_order_kalmanson_165_unsat.json"
)


def _display_path(path: Path) -> str:
    if not path.is_absolute():
        return path.as_posix()
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "certificates",
        nargs="*",
        type=Path,
        help="certificate JSON paths; defaults to the recorded C29 fixed-order certificate",
    )
    parser.add_argument("--out", type=Path, help="write JSON footprint payload")
    parser.add_argument("--assert-c29", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    paths = args.certificates or [C29_CERTIFICATE]
    footprints = []
    for path in paths:
        cert = json.loads(path.read_text(encoding="utf-8"))
        item = footprint_summary(cert)
        item["path"] = _display_path(path)
        footprints.append(item)

    if args.assert_c29:
        by_pattern = {str(item["pattern"]): item for item in footprints}
        c29 = by_pattern.get("C29_sidon_1_3_7_15")
        if c29 is None:
            raise AssertionError("C29_sidon_1_3_7_15 footprint missing")
        if c29["strict_rows"] != 165:
            raise AssertionError("unexpected C29 strict-row count")
        if c29["distance_classes"] != 319:
            raise AssertionError("unexpected C29 distance-class count")
        if c29["zero_sum_verified"] is not True:
            raise AssertionError("C29 footprint did not replay as zero-sum certificate")

    payload: object
    payload = footprints[0] if len(footprints) == 1 else {
        "type": "quotient_cone_footprint_collection_v1",
        "footprints": footprints,
    }

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "pattern  n  rows  classes  touched-classes  touched-centers  "
            "zero-sum  source-counts"
        )
        for item in footprints:
            print(
                f"{item['pattern']}  {item['n']}  {item['strict_rows']}  "
                f"{item['distance_classes']}  "
                f"{item['touched_distance_class_count']}  "
                f"{item['touched_selected_center_count']}  "
                f"{item['zero_sum_verified']}  {item['source_counts']}"
            )
        if args.assert_c29:
            print("OK: C29 quotient-cone footprint expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
