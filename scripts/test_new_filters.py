#!/usr/bin/env python3
"""Test the new exact filters on every built-in pattern.

Writes results to ``data/certificates/new_filters_test.json``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.new_filters import (  # noqa: E402
    report_to_json,
    run_new_filters,
)
from erdos97.search import built_in_patterns  # noqa: E402

OUT_PATH = ROOT / "data" / "certificates" / "new_filters_test.json"


def main() -> int:
    patterns = built_in_patterns()
    rows: list[dict[str, object]] = []
    summary: list[str] = []

    for name, pat in patterns.items():
        report = run_new_filters(pat.S, pattern=name, max_5tuple_candidates=400)
        row = report_to_json(report)
        row["pattern_n"] = int(pat.n)
        row["pattern_family"] = pat.family
        row["pattern_status"] = pat.status
        rows.append(row)

        labels: list[str] = []
        if report.kite_identity.obstructed:
            labels.append(
                f"kite_zero_dist={len(report.kite_identity.forced_zero_distances)}"
            )
        if report.few_distance_5.obstructed:
            labels.append(
                f"fd5={len(report.few_distance_5.obstructions)}"
            )
        if report.triple_shared.obstructed:
            labels.append("triple_shared")
        if report.kite_row_collapse.obstructed:
            labels.append("kite_row_collapse")
        if report.row_chord_order.obstructed:
            labels.append(
                f"row_chord_order={len(report.row_chord_order.obstructions)}"
            )

        kit = report.kite_identity
        rco = report.row_chord_order
        summary.append(
            f"{name:30s} n={pat.n:3d}  "
            f"kite_rank={kit.matrix_rank:4d}  "
            f"free={kit.free_parameters:4d}  "
            f"force_eq_classes={len(kit.forced_equal_distance_classes):3d}  "
            f"row_chord_violations={len(rco.obstructions):3d}  "
            f"triple_shared_v={len(report.triple_shared.triple_shared):3d}  "
            f"OBSTRUCTED={report.obstructed}  "
            + (" ".join(labels) if labels else "-")
        )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "type": "new_filters_test",
        "summary": "Run of new filters on built-in patterns",
        "filter_descriptions": {
            "kite_identity": (
                "linear system on squared distances using witness-row "
                "equalities and rhombus kite identity 4 X_{x,a} = X_{x,y} "
                "+ X_{a,b}; obstruction = forced zero squared distance"
            ),
            "few_distance_5": (
                "5-point subsets where all 10 squared distances are forced "
                "into a single class by kite identity + row equalities; "
                "obstruction = pairwise-equidistant 5-tuple impossible in R^2"
            ),
            "triple_shared_witness": (
                "labels v shared by >=3 mutual phi 2-cycles "
                "(informational; potential rank-2 contradiction in plane)"
            ),
            "kite_row_collapse": (
                "forced-equal-radius equivalence classes from mutual phi "
                "2-cycles (kite identity gives r_x = r_y)"
            ),
            "row_chord_order": (
                "row-internal chord-order violations: kite-identity forces "
                "two chords within one row equal but their angular gaps "
                "(in the supplied cyclic order) differ; L7 monotonicity "
                "forbids equal lengths"
            ),
        },
        "results": rows,
    }
    with OUT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    print("\n".join(summary))
    print(f"\nwrote {OUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
