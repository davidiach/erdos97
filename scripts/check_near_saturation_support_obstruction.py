#!/usr/bin/env python3
"""Check the near-saturation rich-support obstruction bookkeeping.

This standalone checker records the arithmetic and case bookkeeping for the
review-pending lemma draft in docs/near-saturation-support-obstruction.md:

    For every strictly convex n-gon with n >= 8 and any choice of one
    same-radius support R_i at each center,

        sum_i binom(|R_i|, 2) <= n(n-2) - 2.

Equivalently, pair-capacity slack 0 and slack 1 are both impossible.  The
proof extends the support-saturation turn-cover argument from uniform sizes
at the exact equality wall to arbitrary mixed size profiles and one missing
capacity unit.

The checker verifies only the discrete bookkeeping used by the proof note
(distinct short diagonals, chain connectivity, vertex-cover sizes, turn-unit
arithmetic, profile enumeration, and consistency with the raw-budget and
uniform-saturation lemmas).  It is not a realization search, it does not
verify Euclidean geometry, and it does not prove n=9, n=10, n=11, or Erdos
Problem #97.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from math import comb
from pathlib import Path
from typing import Any

SCHEMA = "erdos97.near_saturation_support_obstruction.v1"
STATUS = "REVIEW_PENDING_NEAR_SATURATION_OBSTRUCTION"
TRUST = "LEMMA_DRAFT_REVIEW_PENDING"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = REPO_ROOT / "data" / "certificates" / (
    "near_saturation_support_obstruction.json"
)

BRUTE_FORCE_MAX_VERTICES = 14


def raw_pair_budget(n: int) -> int:
    """Edge-sensitive pair budget n(n-2) from the counting lemma."""

    if n < 0:
        raise ValueError("n must be nonnegative")
    return n * (n - 2)


def sharpened_pair_budget(n: int) -> int:
    """Near-saturation budget n(n-2) - 2, claimed for n >= 8."""

    if n < 8:
        raise ValueError("the near-saturation budget is claimed only for n >= 8")
    return raw_pair_budget(n) - 2


def short_diagonal_pairs(n: int) -> tuple[set[frozenset[int]], set[frozenset[int]]]:
    """Return the gap-2 and gap-3 diagonal pair sets of the n-cycle."""

    if n < 8:
        raise ValueError("short-diagonal bookkeeping is used only for n >= 8")
    gap2 = {frozenset({i, (i + 2) % n}) for i in range(n)}
    gap3 = {frozenset({i, (i + 3) % n}) for i in range(n)}
    return gap2, gap3


def short_diagonals_distinct(n: int) -> bool:
    """Check that the n gap-2 and n gap-3 pairs are 2n distinct diagonals."""

    gap2, gap3 = short_diagonal_pairs(n)
    if len(gap2) != n or len(gap3) != n:
        return False
    if gap2 & gap3:
        return False
    hull = {frozenset({i, (i + 1) % n}) for i in range(n)}
    return not ((gap2 | gap3) & hull)


def cycle_minus_edges_connected(n: int, removed: tuple[int, ...]) -> bool:
    """Check connectivity of the n-cycle after removing the listed edges.

    Edge j joins vertices j and j+1 mod n.
    """

    if n < 3:
        raise ValueError("cycle size must be at least 3")
    removed_set = set(removed)
    adjacency: dict[int, set[int]] = {v: set() for v in range(n)}
    for j in range(n):
        if j in removed_set:
            continue
        adjacency[j].add((j + 1) % n)
        adjacency[(j + 1) % n].add(j)
    seen = {0}
    stack = [0]
    while stack:
        v = stack.pop()
        for w in adjacency[v]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    return len(seen) == n


def side_chain_connected_after_one_removal(n: int) -> bool:
    """Check Step 2: the side-equality chain survives any one missing edge."""

    return all(cycle_minus_edges_connected(n, (j,)) for j in range(n))


def min_vertex_cover_cycle(n: int) -> int:
    """Minimum vertex-cover size of the n-cycle: ceil(n/2)."""

    if n < 3:
        raise ValueError("cycle size must be at least 3")
    return (n + 1) // 2


def min_vertex_cover_path_edges(edge_count: int) -> int:
    """Minimum vertex-cover size of a path with the given edge count."""

    if edge_count < 0:
        raise ValueError("edge count must be nonnegative")
    return (edge_count + 1) // 2


def brute_force_min_cover(n: int, edges: list[tuple[int, int]]) -> int:
    """Exact minimum vertex cover by subset search (small n only)."""

    if n > BRUTE_FORCE_MAX_VERTICES:
        raise ValueError("brute-force cover search is limited to small n")
    for size in range(n + 1):
        for subset in combinations(range(n), size):
            chosen = set(subset)
            if all(a in chosen or b in chosen for a, b in edges):
                return size
    raise AssertionError("unreachable: the full vertex set covers everything")


def cover_formulas_verified(max_n: int = 12) -> bool:
    """Brute-force check of the two cover formulas used in Step 4."""

    for n in range(3, max_n + 1):
        cycle_edges = [(j, (j + 1) % n) for j in range(n)]
        if brute_force_min_cover(n, cycle_edges) != min_vertex_cover_cycle(n):
            return False
        for removed in range(n):
            path_edges = [edge for j, edge in enumerate(cycle_edges) if j != removed]
            if brute_force_min_cover(n, path_edges) != min_vertex_cover_path_edges(
                n - 1
            ):
                return False
    return True


def slack_one_case_row(n: int) -> dict[str, Any]:
    """Case bookkeeping for one n: the three d <= 1 sub-cases of the proof.

    Turn units are counted in multiples of pi/3; each forced exterior turn
    2*pi/3 contributes 2 units and the total turn 2*pi is 6 units.
    """

    if n < 8:
        raise ValueError("the lemma is claimed only for n >= 8")
    cases = {
        "all_capacities_saturated": {
            "side_chain_connected": True,
            "cover_lower_bound": min_vertex_cover_cycle(n),
        },
        "one_gap2_unit_missing": {
            "side_chain_connected": side_chain_connected_after_one_removal(n),
            "cover_lower_bound": min_vertex_cover_cycle(n),
        },
        "one_gap3_unit_missing": {
            "side_chain_connected": True,
            "cover_lower_bound": min_vertex_cover_path_edges(n - 1),
        },
    }
    rows: dict[str, Any] = {}
    all_contradict = True
    for name, data in cases.items():
        turn_units = 2 * int(data["cover_lower_bound"])
        contradiction = bool(data["side_chain_connected"]) and turn_units > 6
        all_contradict = all_contradict and contradiction
        rows[name] = {
            "side_chain_connected": data["side_chain_connected"],
            "forced_turn_set_cover_lower_bound": data["cover_lower_bound"],
            "forced_turn_units_pi_over_3": turn_units,
            "total_turn_units_pi_over_3": 6,
            "turn_contradiction": contradiction,
        }
    return {
        "n": n,
        "raw_pair_budget": raw_pair_budget(n),
        "sharpened_pair_budget": sharpened_pair_budget(n),
        "short_diagonals_distinct": short_diagonals_distinct(n),
        "cases": rows,
        "slack_le_1_contradiction_in_every_case": (
            all_contradict and short_diagonals_distinct(n)
        ),
    }


def four_bad_q_bound(n: int) -> int | None:
    """Sharpened bound on centers with support size >= 5 in a 4-bad n-gon.

    Returns None when the sharpened budget already excludes 4-bad supports.
    """

    budget = sharpened_pair_budget(n)
    if 6 * n > budget:
        return None
    return min(n, (budget - 6 * n) // 4)


def raw_four_bad_q_bound(n: int) -> int | None:
    """Raw-budget bound on centers with support size >= 5, for comparison."""

    budget = raw_pair_budget(n)
    if 6 * n > budget:
        return None
    return min(n, (budget - 6 * n) // 4)


def enumerate_profiles(n: int) -> tuple[list[dict[str, Any]], list[tuple[int, ...]]]:
    """Split raw-feasible 4-bad support-size profiles by the sharpened budget.

    Profiles are nondecreasing size tuples with 4 <= size < n and raw pair
    cost at most n(n-2).  A profile is newly excluded when its raw slack is
    0 or 1.
    """

    raw_budget = raw_pair_budget(n)
    sharpened = sharpened_pair_budget(n)
    newly_excluded: list[dict[str, Any]] = []
    surviving: list[tuple[int, ...]] = []

    def visit(start_size: int, remaining: int, used: int, profile: list[int]) -> None:
        if remaining == 0:
            if used > sharpened:
                newly_excluded.append(
                    {
                        "profile": list(profile),
                        "pair_cost": used,
                        "raw_slack": raw_budget - used,
                    }
                )
            else:
                surviving.append(tuple(profile))
            return
        for size in range(start_size, n):
            new_used = used + comb(size, 2)
            if new_used + (remaining - 1) * comb(size, 2) > raw_budget:
                break
            profile.append(size)
            visit(size, remaining - 1, new_used, profile)
            profile.pop()

    visit(4, n, 0, [])
    return newly_excluded, surviving


def profile_row(n: int) -> dict[str, Any]:
    """Profile-level consequence row for one n."""

    newly_excluded, surviving = enumerate_profiles(n)
    surviving_q = [sum(1 for size in profile if size >= 5) for profile in surviving]
    max_surviving_q = max(surviving_q) if surviving_q else None
    return {
        "n": n,
        "raw_pair_budget": raw_pair_budget(n),
        "sharpened_pair_budget": sharpened_pair_budget(n),
        "raw_feasible_profile_count": len(newly_excluded) + len(surviving),
        "newly_excluded_profile_count": len(newly_excluded),
        "newly_excluded_profiles": newly_excluded,
        "surviving_profile_count": len(surviving),
        "max_q_among_surviving_profiles": max_surviving_q,
        "raw_budget_q_bound": raw_four_bad_q_bound(n),
        "sharpened_q_bound": four_bad_q_bound(n),
        "min_exact_four_centers_sharpened": (
            None if four_bad_q_bound(n) is None else n - int(four_bad_q_bound(n))
        ),
    }


def uniform_threshold_consistency(min_k: int = 4, max_k: int = 8) -> dict[str, Any]:
    """Check that the sharpened budget recovers n >= binom(k,2) + 3."""

    rows: list[dict[str, Any]] = []
    all_match = True
    for k in range(min_k, max_k + 1):
        expected = comb(k, 2) + 3
        found = None
        n = 8
        while found is None:
            if n * comb(k, 2) <= sharpened_pair_budget(n):
                found = n
            n += 1
        match = found == expected
        all_match = all_match and match
        rows.append(
            {
                "k": k,
                "min_n_allowed_by_sharpened_budget": found,
                "support_saturation_threshold": expected,
                "match": match,
            }
        )
    return {"rows": rows, "all_match": all_match}


def slack_two_failure_records() -> dict[str, Any]:
    """Record exactly why the method stops at slack 1.

    These are records about the proof method; they claim nothing about the
    realizability of slack-2 support systems.
    """

    n = 8
    # Failure 1: two missing gap-2 units can disconnect the side chain.
    disconnect_removed = (0, 4)
    chain_disconnected = not cycle_minus_edges_connected(n, disconnect_removed)

    # Failure 2: two missing gap-3 units can leave a cover of size 3 at n=8,
    # and 3 forced turns of 2*pi/3 only reach the total turn 2*pi.
    cycle_edges = [(j, (j + 1) % n) for j in range(n)]
    min_cover_after_two = min(
        brute_force_min_cover(
            n, [edge for j, edge in enumerate(cycle_edges) if j not in removed]
        )
        for removed in combinations(range(n), 2)
    )
    turn_units = 2 * min_cover_after_two
    return {
        "claim_scope": (
            "method-boundary records only; no claim about slack-2 realizability"
        ),
        "equilateral_step_failure": {
            "n": n,
            "removed_side_chain_edges": list(disconnect_removed),
            "side_chain_disconnected": chain_disconnected,
        },
        "turn_count_failure": {
            "n": n,
            "min_cover_after_two_missing_gap3_units": min_cover_after_two,
            "forced_turn_units_pi_over_3": turn_units,
            "total_turn_units_pi_over_3": 6,
            "turn_contradiction": turn_units > 6,
        },
    }


def build_summary(min_n: int = 8, max_n: int = 16) -> dict[str, Any]:
    """Build the stable JSON summary for the lemma-draft bookkeeping."""

    if min_n < 8:
        raise ValueError("min_n must be at least 8")
    if max_n < min_n:
        raise ValueError("max_n must be at least min_n")
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Review-pending near-saturation strengthening of the "
            "edge-sensitive rich-support pair budget: for strictly convex "
            "n-gons with n >= 8, sum_i binom(|R_i|,2) <= n(n-2) - 2. "
            "Discrete bookkeeping checks only; not a realization search, "
            "not a proof of n=9, n=10, or n=11, not a proof of Erdos "
            "Problem #97, and not a counterexample."
        ),
        "lemma_draft": (
            "For any same-radius supports R_i in a strictly convex n-gon "
            "with n >= 8, sum_i binom(|R_i|, 2) <= n(n-2) - 2; equivalently "
            "pair-capacity slack 0 and 1 are impossible."
        ),
        "proof_accounting": {
            "capacities": (
                "hull-edge witness pairs have capacity 1, diagonal witness "
                "pairs capacity 2 with at most one using center per side"
            ),
            "step_1_2": (
                "each saturated gap-2 diagonal forces one side equality; a "
                "cycle minus at most one edge stays connected, so all sides "
                "are equal"
            ),
            "step_3": (
                "each saturated gap-3 diagonal forces an exterior turn "
                "2*pi/3 at one of the two short-side vertices"
            ),
            "step_4_5": (
                "the forced-turn set covers the n-cycle minus at most one "
                "edge, so it has at least 4 members and the total exterior "
                "turn would be at least 8*pi/3 > 2*pi"
            ),
        },
        "cover_formulas_brute_force_verified_to_n_12": cover_formulas_verified(),
        "case_rows": [slack_one_case_row(n) for n in range(min_n, max_n + 1)],
        "uniform_threshold_consistency": uniform_threshold_consistency(),
        "four_bad_profile_rows": [profile_row(n) for n in range(9, 14)],
        "slack_two_failure_records": slack_two_failure_records(),
    }


def check_expected(summary: dict[str, Any]) -> None:
    """Assert the expected bookkeeping for the default range."""

    if not summary["cover_formulas_brute_force_verified_to_n_12"]:
        raise AssertionError("vertex-cover formulas failed brute-force verification")

    for row in summary["case_rows"]:
        if not row["slack_le_1_contradiction_in_every_case"]:
            raise AssertionError(f"n={row['n']}: missing slack<=1 contradiction")
        if row["sharpened_pair_budget"] != row["raw_pair_budget"] - 2:
            raise AssertionError(f"n={row['n']}: budget arithmetic mismatch")

    consistency = summary["uniform_threshold_consistency"]
    if not consistency["all_match"]:
        raise AssertionError(
            "sharpened budget does not recover the uniform saturation thresholds"
        )

    profile_rows = {row["n"]: row for row in summary["four_bad_profile_rows"]}
    expected_counts = {
        # n: (newly excluded, surviving, max surviving q, sharpened q bound,
        #     raw q bound, min exact-four centers)
        9: (2, 2, 1, 1, 2, 8),
        10: (2, 10, 4, 4, 5, 6),
        11: (4, 33, 7, 7, 8, 4),
        12: (14, 95, 11, 11, 12, 1),
        13: (30, 263, 13, 13, 13, 0),
    }
    for n, (
        newly,
        surviving,
        max_q,
        q_bound,
        raw_q,
        min_exact_four,
    ) in expected_counts.items():
        row = profile_rows[n]
        got = (
            row["newly_excluded_profile_count"],
            row["surviving_profile_count"],
            row["max_q_among_surviving_profiles"],
            row["sharpened_q_bound"],
            row["raw_budget_q_bound"],
            row["min_exact_four_centers_sharpened"],
        )
        want = (newly, surviving, max_q, q_bound, raw_q, min_exact_four)
        if got != want:
            raise AssertionError(f"n={n}: got {got}, expected {want}")
        if row["max_q_among_surviving_profiles"] > row["sharpened_q_bound"]:
            raise AssertionError(f"n={n}: profile enumeration exceeds the q bound")

    expected_boundary_profiles = {
        9: [
            ([4, 4, 4, 4, 4, 4, 4, 4, 6], 63, 0),
            ([4, 4, 4, 4, 4, 4, 4, 5, 5], 62, 1),
        ],
        10: [
            ([4, 4, 4, 4, 4, 4, 4, 4, 5, 7], 79, 1),
            ([4, 4, 4, 4, 4, 5, 5, 5, 5, 5], 80, 0),
        ],
        11: [
            ([4, 4, 4, 4, 4, 4, 4, 4, 6, 6, 7], 99, 0),
            ([4, 4, 4, 4, 4, 4, 4, 5, 5, 6, 7], 98, 1),
            ([4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 6], 99, 0),
            ([4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5], 98, 1),
        ],
    }
    for n, expected_profiles in expected_boundary_profiles.items():
        got_profiles = [
            (entry["profile"], entry["pair_cost"], entry["raw_slack"])
            for entry in profile_rows[n]["newly_excluded_profiles"]
        ]
        want_profiles = [
            (profile, cost, slack) for profile, cost, slack in expected_profiles
        ]
        if got_profiles != want_profiles:
            raise AssertionError(
                f"n={n}: newly excluded profiles {got_profiles} != {want_profiles}"
            )

    failures = summary["slack_two_failure_records"]
    if not failures["equilateral_step_failure"]["side_chain_disconnected"]:
        raise AssertionError("expected the slack-2 side-chain disconnection record")
    turn_failure = failures["turn_count_failure"]
    if turn_failure["min_cover_after_two_missing_gap3_units"] != 3:
        raise AssertionError("expected a size-3 cover after two missing gap-3 units")
    if turn_failure["turn_contradiction"]:
        raise AssertionError("the slack-2 turn record must not be a contradiction")


def artifact_payload(summary: dict[str, Any]) -> dict[str, Any]:
    """Wrap the summary with an embedded provenance block."""

    payload = dict(summary)
    payload["provenance"] = {
        "command": (
            "python scripts/check_near_saturation_support_obstruction.py "
            "--write-artifact"
        ),
        "generator": "scripts/check_near_saturation_support_obstruction.py",
        "notes": (
            "Deterministic bookkeeping summary for the review-pending "
            "near-saturation rich-support obstruction; regenerated, never "
            "hand-edited."
        ),
    }
    return payload


def check_artifact(path: Path, summary: dict[str, Any]) -> None:
    """Check the stored artifact against a freshly built summary."""

    stored = json.loads(path.read_text())
    expected = artifact_payload(summary)
    if stored != expected:
        stored_keys = set(stored) if isinstance(stored, dict) else None
        raise AssertionError(
            "stored artifact does not match the regenerated summary "
            f"(stored top-level keys: {sorted(stored_keys) if stored_keys else stored_keys})"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-n", type=int, default=8)
    parser.add_argument("--max-n", type=int, default=16)
    parser.add_argument(
        "--check",
        action="store_true",
        help="assert the expected default bookkeeping",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument(
        "--write-artifact",
        action="store_true",
        help="write the summary artifact with embedded provenance",
    )
    parser.add_argument(
        "--check-artifact",
        action="store_true",
        help="check the stored artifact against a fresh regeneration",
    )
    parser.add_argument(
        "--artifact",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help="artifact path for --write-artifact / --check-artifact",
    )
    args = parser.parse_args()

    summary = build_summary(args.min_n, args.max_n)
    if args.check or args.check_artifact or args.write_artifact:
        if (args.min_n, args.max_n) != (8, 16):
            raise SystemExit(
                "--check/--write-artifact/--check-artifact are only defined "
                "for the default n range"
            )
        check_expected(summary)
    if args.write_artifact:
        args.artifact.parent.mkdir(parents=True, exist_ok=True)
        args.artifact.write_text(
            json.dumps(artifact_payload(summary), indent=2, sort_keys=True) + "\n"
        )
        print(f"wrote {args.artifact}")
    if args.check_artifact:
        check_artifact(args.artifact, summary)

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif not args.write_artifact:
        print(f"schema: {summary['schema']}")
        print(f"trust: {summary['trust']}")
        for row in summary["four_bad_profile_rows"]:
            print(
                f"n={row['n']}: sharpened q bound={row['sharpened_q_bound']} "
                f"(raw {row['raw_budget_q_bound']}), newly excluded "
                f"profiles={row['newly_excluded_profile_count']}, min "
                f"exact-four centers={row['min_exact_four_centers_sharpened']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
