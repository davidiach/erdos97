"""Test the dual paraboloid filter on n=8, n=9, and exploratory n=10/n=11.

Outputs an aggregate JSON to data/certificates/paraboloid_lift_test.json with
columns:

    n, source, id, dpf_basis_size, dpf_is_trivial, dpf_elapsed_sec,
    dpf_column_only_basis_size, dpf_column_only_elapsed_sec,
    column_determinant_count, indegrees.

The "column-only" variant uses only the column-determinant Plucker relations
and DROPS the row equidistance equations. If column-only Groebner returns {1},
that is a strictly stronger statement than full Groebner returning {1}: it
says the column-incidence subsystem alone is unrealizable, even before using
the bilinear row equations.

The "full DPF" variant includes both. It is mathematically equivalent (up to
elimination of the auxiliary c_i) to the existing row-Groebner pipeline.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

# Allow running as a script without installing the package.
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.paraboloid_lift_filters import (  # noqa: E402
    column_determinant_indegree,
    column_determinant_rank_summary,
    incidence_matrix_rank_diagnostics,
    run_column_pucker_only_groebner,
    run_row_groebner_with_column_pucker_enrichment,
)


def load_n8_survivors() -> list[dict]:
    path = ROOT / "data" / "incidence" / "n8_reconstructed_15_survivors.json"
    with path.open() as f:
        data = json.load(f)
    return [
        {"n": 8, "source": "n8_reconstructed_15", "id": entry["id"], "rows": entry["rows"]}
        for entry in data
    ]


def load_n9_groebner_families() -> list[dict]:
    """Load only the F07/F08/F09/F12/F13 families (non-trivial-GB-at-n9 cases)."""
    path = ROOT / "data" / "certificates" / "2026-05-05" / "n9_groebner_results.json"
    with path.open() as f:
        data = json.load(f)
    return [
        {
            "n": 9,
            "source": "n9_groebner_2026-05-05",
            "id": entry["family_id"],
            "rows": entry["rows"],
            "row_groebner_size": entry.get("gb_size"),
            "row_groebner_trivial": entry.get("is_trivial"),
        }
        for entry in data
    ]


def explore_n10_seed_patterns() -> list[dict]:
    """Build a SMALL set of n=10 cyclic-shift candidate patterns to probe.

    These are *exploratory* candidates: they pass the basic incidence/L4
    filters but were not separately verified to be vertex-circle survivors.
    The goal is to see whether the DPF lands on something the existing
    finite-case toolkit has not yet processed.

    We use the cyclic shift family row(c) = (c + S) mod n for various S.
    Patterns where any S already encodes self-incidence are skipped.
    """
    n = 10
    out = []
    seeds = [
        [1, 2, 3, 4],
        [1, 2, 3, 5],
        [1, 2, 4, 7],
        [1, 3, 4, 7],
        [1, 3, 5, 7],
        [1, 2, 5, 8],
        [1, 3, 6, 8],
    ]
    for seed in seeds:
        rows = []
        ok = True
        for c in range(n):
            row = sorted([(c + s) % n for s in seed])
            if c in row:
                ok = False
                break
            rows.append(row)
        if not ok:
            continue
        # L5 / pair_cap=2 quick check.
        from collections import Counter
        pair_counts = Counter()
        for r in rows:
            for a, b in [(r[i], r[j]) for i in range(4) for j in range(i + 1, 4)]:
                pair_counts[(min(a, b), max(a, b))] += 1
        if pair_counts and max(pair_counts.values()) > 2:
            continue
        out.append({
            "n": n,
            "source": "n10_cyclic_seed",
            "id": "S=" + "_".join(str(s) for s in seed),
            "rows": rows,
            "seed_offsets": seed,
        })
    return out


def explore_n11_seed_patterns() -> list[dict]:
    n = 11
    out = []
    seeds = [
        [1, 2, 3, 4],
        [1, 2, 4, 8],
        [1, 3, 4, 9],
        [1, 3, 5, 9],
        [2, 3, 5, 8],
    ]
    for seed in seeds:
        rows = []
        ok = True
        for c in range(n):
            row = sorted([(c + s) % n for s in seed])
            if c in row:
                ok = False
                break
            rows.append(row)
        if not ok:
            continue
        from collections import Counter
        pair_counts = Counter()
        for r in rows:
            for a, b in [(r[i], r[j]) for i in range(4) for j in range(i + 1, 4)]:
                pair_counts[(min(a, b), max(a, b))] += 1
        if pair_counts and max(pair_counts.values()) > 2:
            continue
        out.append({
            "n": n,
            "source": "n11_cyclic_seed",
            "id": "S=" + "_".join(str(s) for s in seed),
            "rows": rows,
            "seed_offsets": seed,
        })
    return out


def run_one(entry: dict, time_budget_sec: float = 90.0,
            run_col_only: bool = True,
            run_enriched: bool = True) -> dict:
    n = entry["n"]
    rows = entry["rows"]
    print(
        f"[{entry['source']}/{entry['id']} n={n}] starting", flush=True,
    )
    t0 = time.time()
    indegrees = column_determinant_indegree(rows, n)
    summary = column_determinant_rank_summary(rows, n)
    rank_info = incidence_matrix_rank_diagnostics(rows, n)
    out: dict = {
        "n": n,
        "source": entry["source"],
        "id": entry["id"],
        "rows": rows,
        "indegrees": indegrees,
        "column_det_count": summary["total_nonzero_column_dets"],
        "column_det_per_j": summary["per_vertex_j"],
        "incidence_rank": rank_info,
    }
    if run_enriched:
        info_full = run_row_groebner_with_column_pucker_enrichment(
            rows, n, use_column_pucker=True,
        )
        out["row_plus_pucker_gb"] = info_full
        print(
            f"  row+pucker GB: size={info_full.get('basis_size')} "
            f"trivial={info_full.get('is_trivial_one')} "
            f"t={info_full.get('elapsed_sec', -1):.2f}s",
            flush=True,
        )
    if run_col_only:
        info_col_only = run_column_pucker_only_groebner(rows, n)
        out["column_pucker_only_gb"] = info_col_only
        print(
            f"  col-only GB: size={info_col_only.get('basis_size')} "
            f"trivial={info_col_only.get('is_trivial_one')} "
            f"t={info_col_only.get('elapsed_sec', -1):.2f}s",
            flush=True,
        )
    out["wallclock_sec"] = time.time() - t0
    if "row_groebner_size" in entry:
        out["row_groebner_size"] = entry["row_groebner_size"]
        out["row_groebner_trivial"] = entry["row_groebner_trivial"]
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("n8", "n9", "n10", "n11", "all"),
        default="all",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Optional max number of patterns to process.",
    )
    parser.add_argument(
        "--time-budget", type=float, default=90.0,
        help="Soft per-pattern wall budget (s).",
    )
    parser.add_argument(
        "--out",
        default=str(ROOT / "data" / "certificates" / "paraboloid_lift_test.json"),
    )
    parser.add_argument(
        "--skip-col-only", action="store_true",
        help="Skip the slower column-only Plucker Groebner run.",
    )
    parser.add_argument(
        "--skip-enriched", action="store_true",
        help="Skip the row+Plucker enriched Groebner run.",
    )
    args = parser.parse_args(argv)

    entries: list[dict] = []
    if args.mode in ("n8", "all"):
        entries.extend(load_n8_survivors())
    if args.mode in ("n9", "all"):
        entries.extend(load_n9_groebner_families())
    if args.mode in ("n10", "all"):
        entries.extend(explore_n10_seed_patterns())
    if args.mode in ("n11", "all"):
        entries.extend(explore_n11_seed_patterns())

    if args.limit is not None:
        entries = entries[: args.limit]

    print(f"running {len(entries)} pattern(s)...", flush=True)

    results = []
    for entry in entries:
        result = run_one(
            entry, time_budget_sec=args.time_budget,
            run_col_only=not args.skip_col_only,
            run_enriched=not args.skip_enriched,
        )
        results.append(result)

    out = {
        "type": "dual_paraboloid_filter_test_v0",
        "trust": "EXPLORATORY_DRAFT_REVIEW_PENDING",
        "purpose": (
            "Compare full dual paraboloid filter vs column-only Plucker "
            "subsystem on registered finite-case incidence patterns. The "
            "full DPF is mathematically equivalent to the existing row "
            "Groebner system after eliminating auxiliary c_i; the column-"
            "only run is a weaker subsystem and reports only those "
            "patterns whose Plucker column determinants alone form an "
            "infeasible polynomial system."
        ),
        "results": results,
        "summary": {
            "total": len(results),
            "row_plus_pucker_trivial": sum(
                1 for r in results
                if r.get("row_plus_pucker_gb", {}).get("is_trivial_one") is True
            ),
            "column_only_trivial": sum(
                1 for r in results
                if r.get("column_pucker_only_gb", {}).get("is_trivial_one") is True
            ),
            "column_only_basis_sizes": [
                r.get("column_pucker_only_gb", {}).get("basis_size")
                for r in results
                if r.get("column_pucker_only_gb")
            ],
        },
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(out, f, indent=2, sort_keys=False, default=str)
    print(f"wrote {out_path}", flush=True)
    print("summary:", out["summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
