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

SCHEMA = "erdos97.near_saturation_support_obstruction.v2"
STATUS = "REVIEW_PENDING_NEAR_SATURATION_OBSTRUCTION"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
NOTE_STATUS_LABEL = "LEMMA_DRAFT / REVIEW_PENDING"

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = REPO_ROOT / "data" / "certificates" / (
    "near_saturation_support_obstruction.json"
)

BRUTE_FORCE_MAX_VERTICES = 14
# Total exterior turn 2*pi is 6 units of pi/3; each forced turn 2*pi/3 is 2.
TOTAL_TURN_UNITS_PI_OVER_3 = 6


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


def cycle_edges(n: int) -> list[tuple[int, int]]:
    """Edges of the n-cycle in the convention: edge j joins j and j+1 mod n."""

    if n < 3:
        raise ValueError("cycle size must be at least 3")
    return [(j, (j + 1) % n) for j in range(n)]


def cycle_minus_edges_connected(n: int, removed: tuple[int, ...]) -> bool:
    """Check connectivity of the n-cycle after removing the listed edges."""

    removed_set = set(removed)
    adjacency: dict[int, set[int]] = {v: set() for v in range(n)}
    for j, (a, b) in enumerate(cycle_edges(n)):
        if j in removed_set:
            continue
        adjacency[a].add(b)
        adjacency[b].add(a)
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


def min_cover_after_removals(n: int, removed: tuple[int, ...]) -> int:
    """Exact minimum vertex cover of the n-cycle minus the listed edges."""

    removed_set = set(removed)
    edges = [edge for j, edge in enumerate(cycle_edges(n)) if j not in removed_set]
    return brute_force_min_cover(n, edges)


def cover_formulas_verified(max_n: int = 12) -> bool:
    """Brute-force check of the two cover formulas used in Step 4."""

    for n in range(3, max_n + 1):
        if min_cover_after_removals(n, ()) != min_vertex_cover_cycle(n):
            return False
        for removed in range(n):
            if min_cover_after_removals(n, (removed,)) != min_vertex_cover_path_edges(
                n - 1
            ):
                return False
    return True


def forced_turn_units(cover_lower_bound: int) -> int:
    """Turn units (multiples of pi/3) forced by a turn set of the given size."""

    return 2 * cover_lower_bound


def nonstrict_turn_contradiction(cover_lower_bound: int) -> bool:
    """The proof's Step 5 test: |M| forced turns strictly exceed 2*pi."""

    return forced_turn_units(cover_lower_bound) > TOTAL_TURN_UNITS_PI_OVER_3


def slack_one_case_row(n: int) -> dict[str, Any]:
    """Case bookkeeping for one n: the three d <= 1 sub-cases of the proof.

    The three rows split by where the (at most one) missing capacity unit
    sits: on no short diagonal at all (this covers d = 0 and a d = 1 unit on
    a hull edge or a gap >= 4 diagonal), on one gap-2 diagonal, or on one
    gap-3 diagonal.
    """

    if n < 8:
        raise ValueError("the lemma is claimed only for n >= 8")
    cases = {
        "no_short_diagonal_unit_missing": {
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
        cover = int(data["cover_lower_bound"])
        contradiction = bool(data["side_chain_connected"]) and (
            nonstrict_turn_contradiction(cover)
        )
        all_contradict = all_contradict and contradiction
        rows[name] = {
            "side_chain_connected": data["side_chain_connected"],
            "forced_turn_set_cover_lower_bound": cover,
            "forced_turn_units_pi_over_3": forced_turn_units(cover),
            "total_turn_units_pi_over_3": TOTAL_TURN_UNITS_PI_OVER_3,
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


def four_bad_q_bound_for_budget(n: int, budget: int) -> int | None:
    """Bound on centers with support size >= 5 in a 4-bad n-gon.

    Returns None when the budget already excludes 4-bad supports (the
    exact-four baseline alone exceeds it, as the sharpened budget does at
    n = 8).
    """

    if 6 * n > budget:
        return None
    return min(n, (budget - 6 * n) // (comb(5, 2) - comb(4, 2)))


def four_bad_q_bound(n: int) -> int | None:
    """Sharpened-budget bound on centers with support size >= 5."""

    return four_bad_q_bound_for_budget(n, sharpened_pair_budget(n))


def raw_four_bad_q_bound(n: int) -> int | None:
    """Raw-budget bound on centers with support size >= 5, for comparison."""

    return four_bad_q_bound_for_budget(n, raw_pair_budget(n))


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
    sharpened_q = four_bad_q_bound(n)
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
        "sharpened_q_bound": sharpened_q,
        "min_exact_four_centers_sharpened": (
            None if sharpened_q is None else n - sharpened_q
        ),
    }


def uniform_threshold_consistency(min_k: int = 4, max_k: int = 8) -> dict[str, Any]:
    """Check that the sharpened budget recovers n >= binom(k,2) + 3.

    The scan starts at n = 8 because the raw budget already excludes
    every-center size >= 4 supports for n <= 7 (6n > n(n-2)); the sharpened
    budget is only claimed for n >= 8.
    """

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


def slack_two_boundary_records() -> dict[str, Any]:
    """Record the exact slack-2 boundary of the proof method.

    Two records, both about the proof method rather than realizability:

    1. The genuine failure mode: two DISTINCT gap-2 diagonals each short by
       one unit remove two side-chain edges, and a cycle minus two distinct
       edges is always disconnected, so the equilateral step fails and no
       turn contradiction follows from these steps.

    2. The corrected turn accounting: with the strict form of Step 5 (the
       forced-turn set M is a proper subset of the n turn indices, so
       |M| >= 3 already forces total turn > 2*pi for n >= 4), every other
       slack-2 distribution still contradicts, because the cover of the
       turn-index cycle loses at most two edges and stays at least
       ceil((n-2)/2) >= 3 for n >= 8.  The note's headline proof uses the
       non-strict test (|M| >= 4), which genuinely fails on some two-edge
       removals (minimum cover exactly 3), so the uniform theorem still
       stops at slack 1 because of record 1, not because of the turn count.
    """

    n = 8
    # Record 1: two missing gap-2 units always disconnect the side chain.
    disconnect_removed = (0, 4)
    exhibit_disconnected = not cycle_minus_edges_connected(n, disconnect_removed)
    always_disconnected = all(
        not cycle_minus_edges_connected(m, pair)
        for m in range(8, 13)
        for pair in combinations(range(m), 2)
    )

    # Record 2: cover bounds for at most two missing gap-3 units.
    two_removal_covers = [
        min_cover_after_removals(n, pair) for pair in combinations(range(n), 2)
    ]
    min_cover_two_removals = min(two_removal_covers)
    min_cover_le_two_removals = min(
        min_cover_after_removals(n, ()),
        min(min_cover_after_removals(n, (j,)) for j in range(n)),
        min_cover_two_removals,
    )
    general_bound_holds = all(
        min_cover_after_removals(m, removed) >= max(3, (m - 2 + 1) // 2)
        for m in range(8, 13)
        for count in (0, 1, 2)
        for removed in combinations(range(m), count)
    )
    return {
        "claim_scope": (
            "method-boundary records only; no claim about slack-2 realizability"
        ),
        "chain_disconnection_failure": {
            "n": n,
            "exhibit_removed_side_chain_edges": list(disconnect_removed),
            "exhibit_side_chain_disconnected": exhibit_disconnected,
            "cycle_minus_two_distinct_edges_always_disconnected_n8_to_12": (
                always_disconnected
            ),
        },
        "strict_turn_closure_of_other_distributions": {
            "n": n,
            "strict_turn_set_threshold": 3,
            "min_cover_over_all_two_edge_removals": min_cover_two_removals,
            "min_cover_over_all_le_two_edge_removals": min_cover_le_two_removals,
            "all_le_two_edge_removal_covers_meet_strict_threshold": (
                min_cover_le_two_removals >= 3
            ),
            "general_bound_ceil_n_minus_2_over_2_verified_n8_to_12": (
                general_bound_holds
            ),
            "nonstrict_test_fails_for_some_two_edge_removals": (
                not nonstrict_turn_contradiction(min_cover_two_removals)
            ),
        },
    }


def headline_counts(profile_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Compact headline block for provenance pinning and ledger crosswalks."""

    rows = {row["n"]: row for row in profile_rows}
    return {
        "n9_sharpened_q_bound": rows[9]["sharpened_q_bound"],
        "n10_sharpened_q_bound": rows[10]["sharpened_q_bound"],
        "n11_sharpened_q_bound": rows[11]["sharpened_q_bound"],
        "n12_sharpened_q_bound": rows[12]["sharpened_q_bound"],
        "n10_min_exact_four_centers": rows[10]["min_exact_four_centers_sharpened"],
        "n11_min_exact_four_centers": rows[11]["min_exact_four_centers_sharpened"],
        "n12_min_exact_four_centers": rows[12]["min_exact_four_centers_sharpened"],
        "newly_excluded_profile_counts": {
            str(n): rows[n]["newly_excluded_profile_count"] for n in range(9, 14)
        },
    }


def build_summary(min_n: int = 8, max_n: int = 16) -> dict[str, Any]:
    """Build the stable JSON summary for the lemma-draft bookkeeping."""

    if min_n < 8:
        raise ValueError("min_n must be at least 8")
    if max_n < min_n:
        raise ValueError("max_n must be at least min_n")
    profile_rows = [profile_row(n) for n in range(9, 14)]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "note_status_label": NOTE_STATUS_LABEL,
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
        "four_bad_profile_rows": profile_rows,
        "headline": headline_counts(profile_rows),
        "slack_two_boundary_records": slack_two_boundary_records(),
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
        max_q_value = row["max_q_among_surviving_profiles"]
        q_bound_value = row["sharpened_q_bound"]
        if max_q_value is None or q_bound_value is None:
            raise AssertionError(f"n={n}: unexpected empty profile or q bound")
        if max_q_value > q_bound_value:
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

    headline = summary["headline"]
    expected_headline = {
        "n9_sharpened_q_bound": 1,
        "n10_sharpened_q_bound": 4,
        "n11_sharpened_q_bound": 7,
        "n12_sharpened_q_bound": 11,
        "n10_min_exact_four_centers": 6,
        "n11_min_exact_four_centers": 4,
        "n12_min_exact_four_centers": 1,
        "newly_excluded_profile_counts": {
            "9": 2,
            "10": 2,
            "11": 4,
            "12": 14,
            "13": 30,
        },
    }
    if headline != expected_headline:
        raise AssertionError(f"unexpected headline block: {headline}")

    boundary = summary["slack_two_boundary_records"]
    chain = boundary["chain_disconnection_failure"]
    if not chain["exhibit_side_chain_disconnected"]:
        raise AssertionError("expected the slack-2 side-chain disconnection exhibit")
    if not chain["cycle_minus_two_distinct_edges_always_disconnected_n8_to_12"]:
        raise AssertionError("expected cycle-minus-two-edges disconnection to hold")
    strict = boundary["strict_turn_closure_of_other_distributions"]
    if strict["min_cover_over_all_two_edge_removals"] != 3:
        raise AssertionError("expected minimum two-edge-removal cover exactly 3")
    if not strict["all_le_two_edge_removal_covers_meet_strict_threshold"]:
        raise AssertionError("expected all <=2-edge-removal covers to be >= 3")
    if not strict["general_bound_ceil_n_minus_2_over_2_verified_n8_to_12"]:
        raise AssertionError("expected the general two-removal cover bound to hold")
    if not strict["nonstrict_test_fails_for_some_two_edge_removals"]:
        raise AssertionError(
            "expected the non-strict turn test to fail at the minimum cover"
        )


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

    try:
        stored_text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(
            f"stored artifact not found: {path}; regenerate it with "
            "python scripts/check_near_saturation_support_obstruction.py "
            "--write-artifact"
        ) from None
    try:
        stored = json.loads(stored_text)
    except json.JSONDecodeError as error:
        raise SystemExit(
            f"stored artifact is not valid JSON: {path} ({error}); regenerate "
            "it with python scripts/check_near_saturation_support_obstruction.py "
            "--write-artifact"
        ) from None
    expected = artifact_payload(summary)
    if stored != expected:
        stored_keys = sorted(stored) if isinstance(stored, dict) else None
        raise AssertionError(
            "stored artifact does not match the regenerated summary "
            f"(stored top-level keys: {stored_keys})"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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

    summary = build_summary()
    if args.check or args.check_artifact or args.write_artifact:
        check_expected(summary)
    if args.write_artifact:
        args.artifact.parent.mkdir(parents=True, exist_ok=True)
        args.artifact.write_text(
            json.dumps(artifact_payload(summary), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote {args.artifact}")
    if args.check_artifact:
        check_artifact(args.artifact, summary)

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif not args.write_artifact:
        print(f"schema: {summary['schema']}")
        print(f"trust: {summary['trust']} (note status: {NOTE_STATUS_LABEL})")
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
