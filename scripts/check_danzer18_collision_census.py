#!/usr/bin/env python3
"""Collision-point rank census for the doubled-Danzer 18-gon C3 slice.

At the collision point (both nonagon copies at the base values) every one of
the 15^6 = 11,390,625 witness assignments is solved, and the question is
first-order: how much does the 18x12 assignment Jacobian drop below its
generic rank 9 (the trivial kernel - rotation, scaling, diagonal base-family
flex - is 3-dimensional), and does the nontrivial kernel have anti-diagonal
(copy-splitting) components on all three orbits?

Default mode verifies the landmark values quickly (uniform assignments, the
four recorded rank-6 assignments, the 19 externally supplied survivors, and
an mpmath dps=40 rank spot-check).  --full reruns the complete census and the
split-support classification of all excess-corank assignments; with
--write-artifact it stores the certificate JSON.

Numerical linear-algebra census only: it proves no branch existence and is
not a counterexample claim for Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from erdos97.danzer18_doubling import (
    EXPECTED_CENSUS_COUNTS,
    EXPECTED_RANK6,
    EXTERNAL_SURVIVORS,
    assignment_rank_and_kernel,
    kernel_split_norms,
    mp_assignment_jacobian,
    mp_base,
    mp_collision_x,
    projected_blocks,
    split_direction_matrix,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "danzer18_collision_rank_census.json"
)
SCHEMA = "erdos97.danzer18_collision_rank_census.v1"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
RANK_TOL = 1e-8
SPLIT_TOL = 1e-6
GENERATOR_COMMAND = (
    "python scripts/check_danzer18_collision_census.py --full --write-artifact"
)

# Fixed mpmath spot-check sample (assignment tuple, expected projected rank).
MP_SPOT_SAMPLE = (
    ((5, 5, 5, 5, 5, 5), 9),
    ((1, 2, 3, 4, 5, 6), 9),
    ((0, 0, 0, 0, 0, 0), 6),
    ((0, 0, 0, 0, 5, 5), 6),
    ((0, 0, 5, 5, 0, 0), 6),
    ((5, 5, 0, 0, 0, 0), 6),
    ((1, 2, 1, 2, 1, 2), 8),
    ((3, 4, 3, 4, 3, 4), 8),
    ((1, 3, 11, 1, 5, 5), 8),
    ((10, 0, 5, 5, 0, 0), 7),
    ((5, 5, 0, 0, 12, 1), 7),
    ((13, 1, 4, 3, 0, 0), 8),
)


def landmark_checks() -> dict:
    pblocks, b = projected_blocks()
    psplit = split_direction_matrix()

    uniform_ranks = {}
    for k in (0, 5):
        assign = (k,) * 6
        rank, _ = assignment_rank_and_kernel(assign, pblocks, b, RANK_TOL)
        uniform_ranks[str(assign)] = rank

    rank6_ok = all(
        assignment_rank_and_kernel(a, pblocks, b, RANK_TOL)[0] == 6
        for a in EXPECTED_RANK6
    )

    survivors = []
    for assign in EXTERNAL_SURVIVORS:
        rank, kernel = assignment_rank_and_kernel(assign, pblocks, b, RANK_TOL)
        norms = kernel_split_norms(kernel, psplit)
        survivors.append(
            {
                "assignment": list(assign),
                "rank": rank,
                "kernel_dim": int(kernel.shape[0]),
                "kernel_split_norms": [float(v) for v in norms],
                "split_support": [bool(v > SPLIT_TOL) for v in norms],
            }
        )
    n_all_three = sum(1 for s in survivors if all(s["split_support"]))

    return {
        "rank_5x6": uniform_ranks["(5, 5, 5, 5, 5, 5)"],
        "rank_0x6": uniform_ranks["(0, 0, 0, 0, 0, 0)"],
        "expected_rank6_all_rank6": rank6_ok,
        "external_survivors": survivors,
        "external_survivors_with_all_three_splits": n_all_three,
    }


def mp_spot_check(dps: int = 40) -> dict:
    from mpmath import mp, mpf, svd_r

    x4, _ = mp_base(dps)
    xc = mp_collision_x(x4)
    rows = []
    all_ok = True
    for assign, expected in MP_SPOT_SAMPLE:
        j = mp_assignment_jacobian(xc, assign)
        sv = sorted((abs(v) for v in svd_r(j, compute_uv=False)), reverse=True)
        rank = sum(1 for v in sv if v > sv[0] * mpf(RANK_TOL))
        ok = rank == expected
        all_ok = all_ok and ok
        rows.append(
            {
                "assignment": list(assign),
                "expected_rank": expected,
                "mp_rank": rank,
                "sv_at_rank_boundary": [mp.nstr(sv[rank - 1], 5),
                                        mp.nstr(sv[rank], 5)],
                "ok": ok,
            }
        )
    return {"dps": dps, "sample": rows, "all_ok": all_ok}


def full_census(chunk: int = 150_000) -> dict:
    pblocks, b = projected_blocks()
    psplit = split_direction_matrix()
    n_total = 15 ** 6
    powers = np.array([15 ** (5 - c) for c in range(6)], dtype=np.int64)
    counts = np.zeros(10, dtype=np.int64)
    low_idx = []
    low_rank = []
    for start in range(0, n_total, chunk):
        idx = np.arange(start, min(start + chunk, n_total), dtype=np.int64)
        digits = (idx[:, None] // powers[None, :]) % 15
        jac = pblocks[np.arange(6)[None, :], digits].reshape(len(idx), 18, 9)
        sv = np.linalg.svd(jac, compute_uv=False)
        ranks = (sv > RANK_TOL * sv[:, :1]).sum(axis=1)
        counts += np.bincount(ranks, minlength=10)
        low = ranks < 9
        if low.any():
            low_idx.append(idx[low])
            low_rank.append(ranks[low])
        if start % (chunk * 20) == 0:
            print(f"  census {start}/{n_total}", file=sys.stderr, flush=True)
    low_idx = np.concatenate(low_idx)
    low_rank = np.concatenate(low_rank)

    # split-support classification of all excess-corank assignments
    digits = (low_idx[:, None] // powers[None, :]) % 15
    support_sizes = np.zeros(len(low_idx), dtype=np.int64)
    all_three = []
    rank7_list = []
    for start in range(0, len(low_idx), 20_000):
        dc = digits[start:start + 20_000]
        jac = pblocks[np.arange(6)[None, :], dc].reshape(len(dc), 18, 9)
        _, sv, vt = np.linalg.svd(jac)
        ranks = (sv > RANK_TOL * sv[:, :1]).sum(axis=1)
        for i in range(len(dc)):
            kernel = vt[i, ranks[i]:, :] @ b.T
            norms = kernel_split_norms(kernel, psplit)
            nsup = int((norms > SPLIT_TOL).sum())
            support_sizes[start + i] = nsup
            if nsup == 3:
                all_three.append([int(v) for v in dc[i]])
            if ranks[i] == 7:
                rank7_list.append([int(v) for v in dc[i]])

    support_counts = {
        int(k): int(v)
        for k, v in zip(*np.unique(support_sizes, return_counts=True))
    }
    return {
        "rank_counts": {int(r): int(c) for r, c in enumerate(counts) if c},
        "rank_counts_match_expected": {
            int(r): int(c) for r, c in enumerate(counts) if c
        } == EXPECTED_CENSUS_COUNTS,
        "excess_total": int(len(low_idx)),
        "rank6_assignments": sorted(
            [int(v) for v in (i // powers) % 15]
            for i in low_idx[low_rank == 6]
        ),
        "rank7_count": int((low_rank == 7).sum()),
        "split_support_size_counts": support_counts,
        "all_three_split_assignments": sorted(all_three),
        "rank7_assignments": sorted(rank7_list),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true",
                        help="rerun the complete 15^6 census (about 6 min)")
    parser.add_argument("--write-artifact", action="store_true")
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--skip-mp-spot-check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true",
                        help="exit nonzero unless all landmark checks pass")
    args = parser.parse_args()

    result = {
        "schema": SCHEMA,
        "status": "NEGATIVE_FIRST_ORDER_CENSUS",
        "trust": TRUST,
        "provenance": {"command": GENERATOR_COMMAND},
        "claim_scope": (
            "First-order (Jacobian rank) census of the doubled-Danzer 18-gon "
            "C3 slice at the collision point of the 2026-07 base nonagon. "
            "Float64 SVD at relative tolerance 1e-8 with mpmath dps=40 rank "
            "spot-checks. Not a branch-existence proof and not a "
            "counterexample claim for Erdos Problem #97."
        ),
        "conventions": {
            "class_order": "(m=0,s=0),(m=0,s=1),(m=1,s=0),(m=1,s=1),(m=2,s=0),(m=2,s=1)",
            "subset_order": "lexicographic over pool indices, 0=(0123) .. 14=(2345)",
            "rank_tolerance_relative": RANK_TOL,
            "split_tolerance": SPLIT_TOL,
        },
        "landmarks": landmark_checks(),
    }
    if not args.skip_mp_spot_check:
        result["mp_spot_check"] = mp_spot_check()
    if args.full:
        result["census"] = full_census()

    ok = (
        result["landmarks"]["rank_5x6"] == 9
        and result["landmarks"]["rank_0x6"] == 6
        and result["landmarks"]["expected_rank6_all_rank6"]
        and result["landmarks"]["external_survivors_with_all_three_splits"] == 8
        and result.get("mp_spot_check", {}).get("all_ok", True)
    )
    if args.full:
        ok = ok and result["census"]["rank_counts_match_expected"]
        ok = ok and len(result["census"]["all_three_split_assignments"]) == 8
    result["all_checks_pass"] = ok

    if args.write_artifact:
        if not args.full:
            print("--write-artifact requires --full", file=sys.stderr)
            return 2
        args.artifact.parent.mkdir(parents=True, exist_ok=True)
        with args.artifact.open("w", encoding="utf-8", newline="\n") as fh:
            json.dump(result, fh, indent=1, sort_keys=False)
            fh.write("\n")
        print(f"wrote {args.artifact}", file=sys.stderr)

    if args.json:
        summary = dict(result)
        if "census" in summary:
            summary["census"] = {
                k: v
                for k, v in summary["census"].items()
                if k not in ("rank7_assignments",)
            }
        json.dump(summary, sys.stdout, indent=1)
        sys.stdout.write("\n")
    else:
        print("rank_5x6:", result["landmarks"]["rank_5x6"])
        print("rank_0x6:", result["landmarks"]["rank_0x6"])
        print("expected_rank6_all_rank6:",
              result["landmarks"]["expected_rank6_all_rank6"])
        print("external_survivors_with_all_three_splits:",
              result["landmarks"]["external_survivors_with_all_three_splits"])
        if "census" in result:
            print("rank_counts:", result["census"]["rank_counts"])
            print("split_support_size_counts:",
                  result["census"]["split_support_size_counts"])
        print("all_checks_pass:", ok)

    if args.check and not ok:
        print("FAIL: census landmark checks failed", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
