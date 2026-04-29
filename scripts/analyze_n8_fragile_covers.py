#!/usr/bin/env python3
"""Analyze fragile-cover compatibility for the n=8 incidence survivors."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.fragile_hypergraph import (  # noqa: E402
    covering_subsets,
    rows_from_zero_one_matrix,
)

EXPECTED_MIN_COVER_DISTRIBUTION = {"2": 6, "3": 9}


def analyze_survivors(path: Path) -> dict[str, object]:
    survivors = json.loads(path.read_text(encoding="utf-8"))
    classes = []
    min_cover_distribution: Counter[str] = Counter()
    all_cover = True

    for record in survivors:
        rows = rows_from_zero_one_matrix(record["rows"])
        stats = covering_subsets(8, rows)
        all_cover = all_cover and bool(stats["cover_exists"])
        min_cover_distribution[str(stats["min_cover_size"])] += 1
        classes.append(
            {
                "class_id": int(record["id"]),
                **stats,
            }
        )

    return {
        "type": "n8_fragile_cover_analysis",
        "n": 8,
        "source": str(path),
        "survivor_classes": len(survivors),
        "all_survivors_admit_incidence_fragile_cover": all_cover,
        "min_cover_size_distribution": dict(sorted(min_cover_distribution.items())),
        "interpretation": (
            "The fragile-cover lemma adds no incidence-only obstruction to the "
            "n=8 survivor classes when any selected row is allowed to be fragile. "
            "Actual fragility is metric data and is not certified here."
        ),
        "classes": classes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--survivors",
        type=Path,
        default=ROOT / "data" / "incidence" / "n8_reconstructed_15_survivors.json",
        help="n=8 reconstructed survivor JSON",
    )
    parser.add_argument("--json", action="store_true", help="print full JSON")
    parser.add_argument("--check", action="store_true", help="assert expected fingerprints")
    parser.add_argument("--write-artifact", type=Path, help="write JSON artifact")
    args = parser.parse_args()

    data = analyze_survivors(args.survivors)

    if args.check:
        assert data["survivor_classes"] == 15
        assert data["all_survivors_admit_incidence_fragile_cover"] is True
        assert data["min_cover_size_distribution"] == EXPECTED_MIN_COVER_DISTRIBUTION

    if args.write_artifact:
        args.write_artifact.parent.mkdir(parents=True, exist_ok=True)
        args.write_artifact.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print("survivor classes:", data["survivor_classes"])
        print(
            "all admit incidence fragile cover:",
            data["all_survivors_admit_incidence_fragile_cover"],
        )
        print("min cover size distribution:", data["min_cover_size_distribution"])
        if args.check:
            print("OK: n=8 fragile-cover fingerprints verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
