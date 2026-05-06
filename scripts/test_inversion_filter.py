"""Test the inversion-based filter on n=8 and n=9 surviving patterns.

This script:
1.  Loads the 15 reconstructed n=8 selected-witness survivors from
    ``data/incidence/n8_reconstructed_15_survivors.json``.
2.  Regenerates the 184 n=9 patterns that survive the pre-vertex-circle
    pair/crossing/count filters (the cross-check set from
    ``data/certificates/n9_vertex_circle_exhaustive.json``).
3.  Runs the inversion audit (F1-F6) from
    ``erdos97.inversion_filter`` on every pattern.
4.  Saves a JSON artifact at
    ``data/certificates/inversion_filter_test.json`` describing kills,
    survivors, and any novel obstructions vs. the existing
    vertex-circle filter.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from erdos97.inversion_filter import inversion_audit  # noqa: E402
from erdos97.n9_vertex_circle_exhaustive import (  # noqa: E402
    MASK_BITS,
    N as N9,
    OPTIONS as N9_OPTIONS,
    PAIRS as N9_PAIRS,
    ROW_PAIR_INDICES as N9_ROW_PAIR_INDICES,
    rows_compatible as n9_rows_compatible,
    vertex_circle_status as n9_vertex_circle_status,
    valid_options_for_center as n9_valid_options,
)


def _rows_from_indicator(indicator_rows):
    n = len(indicator_rows)
    out = []
    for i, row in enumerate(indicator_rows):
        ws = sorted(idx for idx, val in enumerate(row) if val)
        out.append(ws)
    return out


def load_n8_survivors() -> list[dict]:
    """Load 15 n=8 reconstructed survivors as dicts with rows-as-lists."""
    path = REPO_ROOT / "data" / "incidence" / "n8_reconstructed_15_survivors.json"
    raw = json.loads(path.read_text())
    out = []
    for entry in raw:
        rid = entry["id"]
        rows = _rows_from_indicator(entry["rows"])
        out.append({"id": rid, "rows": rows})
    return out


def collect_n9_pre_vertex_circle_survivors() -> list[list[list[int]]]:
    """Re-run the n=9 search WITHOUT vertex-circle pruning to capture the 184 full assignments."""
    all_full: list[dict[int, int]] = []

    def search(assign, column_counts, witness_pair_counts):
        if len(assign) == N9:
            all_full.append(dict(assign))
            return
        best_center = None
        best_options = None
        for center in range(N9):
            if center in assign:
                continue
            opts = n9_valid_options(center, assign, column_counts, witness_pair_counts)
            if best_options is None or len(opts) < len(best_options):
                best_center = center
                best_options = opts
                if not opts:
                    break
        if not best_options:
            return
        center = best_center
        assert center is not None
        for m in best_options:
            assign[center] = m
            for target in MASK_BITS[m]:
                column_counts[target] += 1
            for pidx in N9_ROW_PAIR_INDICES[m]:
                witness_pair_counts[pidx] += 1
            search(assign, column_counts, witness_pair_counts)
            for pidx in N9_ROW_PAIR_INDICES[m]:
                witness_pair_counts[pidx] -= 1
            for target in MASK_BITS[m]:
                column_counts[target] -= 1
            del assign[center]

    for row0 in N9_OPTIONS[0]:
        assign = {0: row0}
        column_counts = [0] * N9
        witness_pair_counts = [0] * len(N9_PAIRS)
        for target in MASK_BITS[row0]:
            column_counts[target] += 1
        for pidx in N9_ROW_PAIR_INDICES[row0]:
            witness_pair_counts[pidx] += 1
        search(assign, column_counts, witness_pair_counts)

    # Convert each assignment to a row list.  Each MASK_BITS[m] gives the four
    # witness indices for row "center".
    out: list[list[list[int]]] = []
    for assign in all_full:
        rows = []
        for center in range(N9):
            mask = assign[center]
            ws = sorted(MASK_BITS[mask])
            rows.append(ws)
        out.append(rows)
    return out


def split_by_vertex_circle(
    n9_assignments: list[list[list[int]]],
) -> tuple[list[list[list[int]]], list[list[list[int]]]]:
    """Split n=9 cross-check survivors by their vertex-circle status."""
    main_kills: list[list[list[int]]] = []
    main_survivors: list[list[list[int]]] = []
    for rows in n9_assignments:
        # Build the assignment dict expected by vertex_circle_status.
        assign = {}
        for center, witnesses in enumerate(rows):
            mask = 0
            for w in witnesses:
                mask |= 1 << w
            assign[center] = mask
        status = n9_vertex_circle_status(assign)
        if status == "ok":
            main_survivors.append(rows)
        else:
            main_kills.append(rows)
    return main_kills, main_survivors


def run_inversion_audit_batch(name: str, patterns: list[list[list[int]]]) -> dict:
    """Run inversion audit over a batch and summarise."""
    kill_count = 0
    survivor_count = 0
    f1_hits = 0
    f2_hits = 0
    f3_hits = 0
    f4_hits = 0
    f5_hits = 0
    f6_hits = 0
    per_pattern = []
    for idx, rows in enumerate(patterns):
        audit = inversion_audit(rows)
        f1n = len(audit["f1_chord_three_circles"])
        f2n = len(audit["f2_line_circle"])
        f3n = len(audit["f3_three_rows_share_triple"])
        f4n = len(audit["f4_inverted_line_coincidence"])
        f5n = len(audit["f5_pencil_overload_three"])
        f6n = len(audit["f6_pentagon_excess"])
        f1_hits += int(f1n > 0)
        f2_hits += int(f2n > 0)
        f3_hits += int(f3n > 0)
        f4_hits += int(f4n > 0)
        f5_hits += int(f5n > 0)
        f6_hits += int(f6n > 0)
        if audit["obstructed"]:
            kill_count += 1
        else:
            survivor_count += 1
        per_pattern.append(
            {
                "index": idx,
                "rows": rows,
                "obstructed": audit["obstructed"],
                "f1_count": f1n,
                "f2_count": f2n,
                "f3_count": f3n,
                "f4_count": f4n,
                "f5_count": f5n,
                "f6_count": f6n,
            }
        )
    return {
        "name": name,
        "patterns_total": len(patterns),
        "kills_by_inversion_filter": kill_count,
        "survivors_after_inversion_filter": survivor_count,
        "hit_counts_per_audit": {
            "f1_chord_three_circles": f1_hits,
            "f2_line_circle": f2_hits,
            "f3_three_rows_share_triple": f3_hits,
            "f4_inverted_line_coincidence": f4_hits,
            "f5_pencil_overload_three": f5_hits,
            "f6_pentagon_excess": f6_hits,
        },
        "per_pattern": per_pattern,
    }


def main() -> dict:
    n8_entries = load_n8_survivors()
    n8_patterns = [entry["rows"] for entry in n8_entries]
    n8_summary = run_inversion_audit_batch("n8_reconstructed_15_survivors", n8_patterns)

    n9_assignments = collect_n9_pre_vertex_circle_survivors()
    main_kills, main_survivors = split_by_vertex_circle(n9_assignments)
    n9_full_summary = run_inversion_audit_batch(
        "n9_pre_vertex_circle_184", n9_assignments
    )
    n9_main_kills_summary = run_inversion_audit_batch(
        "n9_vertex_circle_kills", main_kills
    )
    n9_main_survivors_summary = run_inversion_audit_batch(
        "n9_vertex_circle_survivors", main_survivors
    )

    novel_kills_n9 = sum(
        1
        for entry in n9_main_survivors_summary["per_pattern"]
        if entry["obstructed"]
    )

    payload = {
        "type": "erdos97_inversion_filter_test_v1",
        "trust": "MACHINE_CHECKED_FILTER_AUDIT",
        "summary": {
            "n8_total": len(n8_patterns),
            "n8_kills": n8_summary["kills_by_inversion_filter"],
            "n8_survivors": n8_summary["survivors_after_inversion_filter"],
            "n9_pre_vertex_circle_total": len(n9_assignments),
            "n9_pre_vertex_circle_kills_inversion": n9_full_summary[
                "kills_by_inversion_filter"
            ],
            "n9_vertex_circle_kills_total": len(main_kills),
            "n9_vertex_circle_survivors_total": len(main_survivors),
            "n9_vertex_circle_survivors_killed_by_inversion": novel_kills_n9,
        },
        "n8_test": n8_summary,
        "n9_pre_vertex_circle_test": n9_full_summary,
        "n9_vertex_circle_kills_test": n9_main_kills_summary,
        "n9_vertex_circle_survivors_test": n9_main_survivors_summary,
        "interpretation": [
            "F1, F2, F3 are pair-cap consistency audits implied by the existing necessary"
            " filters; nonzero counts here would indicate a bug upstream.",
            "F4 (inverted-line coincidence) and F6 (pentagon excess) are also implied"
            " by the pair-cap and would indicate redundancy if present.",
            "F5 reports rows where a pair {i,j} appears in three or more selected rows.",
            "If 'n9_vertex_circle_survivors_killed_by_inversion' > 0 then the inversion"
            " filter strictly extends the existing necessary checks; if = 0 it is"
            " redundant relative to the existing pair/crossing/count filters.",
        ],
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This artifact records a deterministic combinatorial audit only.",
        ],
    }
    return payload


if __name__ == "__main__":
    payload = main()
    output_path = REPO_ROOT / "data" / "certificates" / "inversion_filter_test.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {output_path}")
    s = payload["summary"]
    print(json.dumps(s, indent=2))
