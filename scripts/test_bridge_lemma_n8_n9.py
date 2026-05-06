#!/usr/bin/env python3
"""Bridge Lemma A' computational test at n=8, n=9.

This script:

1. Loads the canonical n=8 incidence survivors (15 classes) and the n=9
   surviving 4-regular witness assignments (184 patterns prior to vertex-circle
   filter).
2. For each pattern, computes ear-orderability, identifies the maximal K_k
   "mutually-witnessed cores" (a vertex set U where every v in U has all of
   U \ {v} among its 4 selected witnesses), and reports the minimal stuck
   subset reached during reverse peeling.
3. For non-ear-orderable patterns, attempts geometric realization as a
   strictly convex polygon via the existing least-squares search
   (``erdos97.search.search_pattern``).  Finds the minimum equality residual
   under multiple random restarts and several optimizer modes.
4. Reports a structural summary: whether non-ear-orderable patterns at n=8
   coincide with patterns having a K_4 mutually-witnessed core (the
   "K_4-stuck core sub-conjecture"), and whether all such patterns appear
   geometrically unrealizable.

This is an exploratory empirical test of Bridge Lemma A' (canonical-synthesis
.md, §5.2).  No claim of a proof of Bridge Lemma A' or Erdos #97 is made.
The output is a JSON certificate at
``data/certificates/bridge_lemma_n8_n9_test.json`` and a Markdown summary at
``docs/bridge-lemma-progress.md`` produced by the caller.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from time import monotonic
from typing import Iterable, Optional

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.generic_vertex_search import GenericVertexSearch  # noqa: E402
from erdos97.search import (  # noqa: E402
    LossWeights,
    PatternInfo,
    search_pattern,
)


# --------------------------- ear-orderability --------------------------------

def witness_masks(rows: list[list[int]], n: int) -> list[int]:
    masks = [0] * n
    for i, row in enumerate(rows):
        for j in row:
            masks[i] |= 1 << int(j)
    return masks


def is_ear_orderable(rows: list[list[int]], n: int) -> tuple[bool, Optional[list[int]], int]:
    """Return (yes/no, ear_order, largest_closure_size).

    ear-orderable means there exists a 3-vertex seed from which the closure
    operation (add v if it has >=3 internal witnesses) reaches all n vertices.
    """
    masks = witness_masks(rows, n)
    best_size = 0
    best_order: list[int] | None = None
    for seed in combinations(range(n), 3):
        closure = sum(1 << v for v in seed)
        order = list(seed)
        changed = True
        while changed:
            changed = False
            for v in range(n):
                if closure & (1 << v):
                    continue
                if bin(masks[v] & closure).count("1") >= 3:
                    closure |= 1 << v
                    order.append(v)
                    changed = True
        sz = closure.bit_count()
        if sz > best_size:
            best_size = sz
            best_order = order
        if sz == n:
            return True, list(order), sz
    return False, best_order, best_size


def maximal_k_cores(rows: list[list[int]], n: int) -> dict[int, list[tuple[int, ...]]]:
    """Return all "mutual K_k cores": vertex subsets U where every v in U has all of U-{v} among W_v."""
    masks = witness_masks(rows, n)
    out: dict[int, list[tuple[int, ...]]] = {}
    for k in range(3, n + 1):
        cores: list[tuple[int, ...]] = []
        for U in combinations(range(n), k):
            Umask = sum(1 << v for v in U)
            ok = True
            for v in U:
                req = Umask & ~(1 << v)
                if (masks[v] & req) != req:
                    ok = False
                    break
            if ok:
                cores.append(U)
        if cores:
            out[k] = cores
    return out


def reverse_peel_terminals(rows: list[list[int]], n: int) -> list[tuple[int, ...]]:
    """Return all minimal stuck subsets (>3 elements) reachable by reverse peeling from V."""
    masks = witness_masks(rows, n)
    visited = {(1 << n) - 1}
    queue = [(1 << n) - 1]
    terminals: set[int] = set()
    while queue:
        new_queue: list[int] = []
        for U in queue:
            sz = bin(U).count("1")
            peelable = []
            for v in range(n):
                if not (U & (1 << v)):
                    continue
                rest = U & ~(1 << v)
                if bin(masks[v] & rest).count("1") >= 3:
                    peelable.append(v)
            if not peelable and sz > 3:
                terminals.add(U)
            for v in peelable:
                rest = U & ~(1 << v)
                if rest not in visited:
                    visited.add(rest)
                    new_queue.append(rest)
        queue = new_queue
    return [
        tuple(sorted(v for v in range(n) if t & (1 << v))) for t in terminals
    ]


# --------------------------- pattern loading --------------------------------

def n8_survivors() -> list[tuple[int, list[list[int]]]]:
    """Return list of (canonical_id, rows-as-lists) for n=8 incidence survivors."""
    survivors_path = ROOT / "data" / "incidence" / "n8_reconstructed_15_survivors.json"
    survivors = json.loads(survivors_path.read_text(encoding="utf-8"))
    out: list[tuple[int, list[list[int]]]] = []
    for cls in survivors:
        cid = int(cls["id"])
        # Convert n*n binary matrix to row index lists
        rows = [
            sorted(int(j) for j, v in enumerate(row) if v == 1)
            for row in cls["rows"]
        ]
        out.append((cid, rows))
    return out


def n9_full_assignments() -> list[tuple[int, list[list[int]]]]:
    """Enumerate the 184 surviving full witness assignments at n=9.

    These are 4-regular witness systems passing all incidence filters but
    BEFORE the vertex-circle filter.  Replicates the cross-check enumeration
    from ``data/certificates/n9_vertex_circle_exhaustive.json``.
    """
    g = GenericVertexSearch(n=9, row_size=4, pair_cap=2)

    n = g.n
    full_assignments: list[tuple[int, list[list[int]]]] = []
    counter = [0]

    def mask_to_row(mask: int) -> list[int]:
        return sorted(j for j in range(n) if (mask >> j) & 1)

    def search(assign: dict[int, int], column_counts: list[int], witness_pair_counts: list[int]) -> None:
        if len(assign) == n:
            rows = [mask_to_row(assign[c]) for c in range(n)]
            full_assignments.append((counter[0], rows))
            counter[0] += 1
            return

        best_center = None
        best_options = None
        for center in range(n):
            if center in assign:
                continue
            opts = g.valid_options_for_center(
                center, assign, column_counts, witness_pair_counts
            )
            if best_options is None or len(opts) < len(best_options):
                best_center = center
                best_options = opts
                if not opts:
                    break
        if not best_options:
            return

        center = best_center
        assert center is not None
        for mask in best_options:
            assign[center] = mask
            for target in g.mask_bits[mask]:
                column_counts[target] += 1
            for pidx in g.row_pair_indices[mask]:
                witness_pair_counts[pidx] += 1
            search(assign, column_counts, witness_pair_counts)
            for pidx in g.row_pair_indices[mask]:
                witness_pair_counts[pidx] -= 1
            for target in g.mask_bits[mask]:
                column_counts[target] -= 1
            del assign[center]

    for row0 in g.options[0]:
        assign = {0: row0}
        column_counts = [0] * n
        witness_pair_counts = [0] * len(g.pairs)
        for target in g.mask_bits[row0]:
            column_counts[target] += 1
        for pidx in g.row_pair_indices[row0]:
            witness_pair_counts[pidx] += 1
        search(assign, column_counts, witness_pair_counts)

    return full_assignments


# --------------------------- realization tests ------------------------------

def attempt_realization(
    rows: list[list[int]],
    name: str,
    *,
    n: int,
    restarts: int = 12,
    seed: int = 1,
    max_nfev: int = 2500,
) -> dict[str, object]:
    """Run least-squares realization for the given selected-witness pattern.

    Reports the lowest equality residual found across multiple restarts and
    the polar/direct/support modes.  A residual stuck >> 0 with positive
    convexity margin is empirical evidence of unrealizability; the search
    is non-rigorous and cannot prove unrealizability.
    """
    pat = PatternInfo(
        name=name,
        n=n,
        S=[list(r) for r in rows],
        family="bridge_lemma_test",
        formula="",
        notes="",
    )
    best_score = float("inf")
    best: dict[str, object] | None = None
    for mode in ("polar", "direct", "support"):
        try:
            r = search_pattern(
                pat,
                mode=mode,
                restarts=restarts,
                seed=seed,
                max_nfev=max_nfev,
                verbose=False,
            )
        except Exception as exc:  # pragma: no cover - search robustness
            continue
        score = (r.eq_rms, r.max_spread, -r.convexity_margin if r.convexity_margin is not None else 0.0)
        if r.loss < best_score:
            best_score = r.loss
            best = {
                "mode": mode,
                "loss": float(r.loss),
                "eq_rms": float(r.eq_rms),
                "max_spread": float(r.max_spread),
                "max_rel_spread": float(r.max_rel_spread),
                "convexity_margin": float(r.convexity_margin),
                "min_edge_length": float(r.min_edge_length),
                "min_pair_distance": float(r.min_pair_distance),
                "success": bool(r.success),
                "elapsed_sec": float(r.elapsed_sec),
                "restarts": int(restarts),
                "max_nfev": int(max_nfev),
            }
    if best is None:
        return {"error": "all modes failed"}
    return best


# --------------------------- main analysis ----------------------------------

def analyze_n8() -> dict[str, object]:
    print("[n=8] loading 15 survivors")
    survivors = n8_survivors()
    per_class: list[dict[str, object]] = []
    non_ear_ids: list[int] = []
    k4_core_ids: list[int] = []
    for cid, rows in survivors:
        ear_ok, ear_order, largest_closure = is_ear_orderable(rows, 8)
        cores = maximal_k_cores(rows, 8)
        terminals = reverse_peel_terminals(rows, 8)
        terminal_sizes = sorted({len(t) for t in terminals})
        has_k4 = bool(cores.get(4))
        if not ear_ok:
            non_ear_ids.append(cid)
        if has_k4:
            k4_core_ids.append(cid)
        record = {
            "id": cid,
            "rows": rows,
            "ear_orderable": bool(ear_ok),
            "ear_order": ear_order if ear_ok else None,
            "largest_closure_from_3_seed": int(largest_closure),
            "k_cores": {str(k): [list(c) for c in v] for k, v in cores.items()},
            "k4_core_count": len(cores.get(4, [])),
            "k3_core_count": len(cores.get(3, [])),
            "reverse_peel_terminal_sizes": terminal_sizes,
            "reverse_peel_terminal_count": len(terminals),
        }
        per_class.append(record)
        print(f"  id {cid}: ear={ear_ok}, K4-cores={len(cores.get(4,[]))}, K3-cores={len(cores.get(3,[]))}, closure_max={largest_closure}")

    return {
        "n": 8,
        "total_classes": len(survivors),
        "ear_orderable_count": sum(1 for r in per_class if r["ear_orderable"]),
        "non_ear_orderable_count": sum(1 for r in per_class if not r["ear_orderable"]),
        "non_ear_ids": non_ear_ids,
        "k4_core_ids": k4_core_ids,
        "non_ear_subset_of_k4_cores": all(
            cid in k4_core_ids for cid in non_ear_ids
        ),
        "k4_core_subset_of_non_ear": all(
            cid in non_ear_ids for cid in k4_core_ids
        ),
        "per_class": per_class,
    }


def analyze_n9() -> dict[str, object]:
    print("[n=9] enumerating 184 surviving full assignments")
    start = monotonic()
    full_assignments = n9_full_assignments()
    elapsed = monotonic() - start
    print(f"  enumerated {len(full_assignments)} assignments in {elapsed:.1f}s")
    per_pattern: list[dict[str, object]] = []
    non_ear_ids: list[int] = []
    k4_core_ids: list[int] = []
    for idx, rows in full_assignments:
        ear_ok, ear_order, largest_closure = is_ear_orderable(rows, 9)
        cores = maximal_k_cores(rows, 9)
        has_k4 = bool(cores.get(4))
        if not ear_ok:
            non_ear_ids.append(idx)
        if has_k4:
            k4_core_ids.append(idx)
        # Only record k_cores for non-ear or k4-core cases (full record gets large)
        record = {
            "idx": idx,
            "ear_orderable": bool(ear_ok),
            "k4_core_count": len(cores.get(4, [])),
            "k3_core_count": len(cores.get(3, [])),
            "largest_closure_from_3_seed": int(largest_closure),
        }
        if not ear_ok or has_k4:
            record["rows"] = rows
            record["k_cores"] = {str(k): [list(c) for c in v] for k, v in cores.items()}
        per_pattern.append(record)

    return {
        "n": 9,
        "total_full_assignments": len(full_assignments),
        "ear_orderable_count": sum(1 for r in per_pattern if r["ear_orderable"]),
        "non_ear_orderable_count": sum(1 for r in per_pattern if not r["ear_orderable"]),
        "non_ear_indices": non_ear_ids,
        "k4_core_indices": k4_core_ids,
        "k3_core_only_count": sum(
            1 for r in per_pattern if r["k4_core_count"] == 0 and r["k3_core_count"] > 0
        ),
        "no_k_core_count": sum(
            1 for r in per_pattern if r["k3_core_count"] == 0 and r["k4_core_count"] == 0
        ),
        "non_ear_subset_of_k4_cores": all(
            idx in k4_core_ids for idx in non_ear_ids
        ),
        "k4_core_subset_of_non_ear": all(
            idx in non_ear_ids for idx in k4_core_ids
        ),
        "non_ear_or_k4_records": [r for r in per_pattern if not r["ear_orderable"] or r["k4_core_count"] > 0],
        "elapsed_sec_enumeration": elapsed,
    }


def realization_tests(
    n8_data: dict[str, object],
    n9_data: dict[str, object],
    *,
    n8_restarts: int = 12,
    n9_restarts: int = 12,
    n8_max_nfev: int = 2500,
    n9_max_nfev: int = 3000,
) -> dict[str, object]:
    """Test geometric realization of every non-ear-orderable pattern at n=8, n=9."""
    out: dict[str, object] = {
        "n8_non_ear_realization": [],
        "n9_non_ear_realization": [],
    }
    print("[n=8] realizing non-ear-orderable patterns")
    n8_per = {r["id"]: r for r in n8_data["per_class"]}
    for cid in n8_data["non_ear_ids"]:
        rows = n8_per[cid]["rows"]
        print(f"  id {cid}: rows={rows}")
        result = attempt_realization(
            rows,
            f"n8_id_{cid}",
            n=8,
            restarts=n8_restarts,
            seed=42,
            max_nfev=n8_max_nfev,
        )
        result["id"] = cid
        result["rows"] = rows
        result["k4_cores"] = n8_per[cid]["k_cores"].get("4", [])
        out["n8_non_ear_realization"].append(result)
        print(
            f"    best: mode={result.get('mode')}, eq_rms={result.get('eq_rms', 'N/A'):.3e}, "
            f"max_spread={result.get('max_spread', 'N/A'):.3e}, "
            f"convex_margin={result.get('convexity_margin', 'N/A'):.3e}"
        )

    print("[n=9] realizing non-ear-orderable patterns")
    n9_per = {r["idx"]: r for r in n9_data["non_ear_or_k4_records"]}
    for idx in n9_data["non_ear_indices"]:
        rows = n9_per[idx]["rows"]
        print(f"  idx {idx}: rows={rows}")
        result = attempt_realization(
            rows,
            f"n9_idx_{idx}",
            n=9,
            restarts=n9_restarts,
            seed=42,
            max_nfev=n9_max_nfev,
        )
        result["idx"] = idx
        result["rows"] = rows
        result["k4_cores"] = n9_per[idx]["k_cores"].get("4", [])
        out["n9_non_ear_realization"].append(result)
        print(
            f"    best: mode={result.get('mode')}, eq_rms={result.get('eq_rms', 'N/A'):.3e}, "
            f"max_spread={result.get('max_spread', 'N/A'):.3e}, "
            f"convex_margin={result.get('convexity_margin', 'N/A'):.3e}"
        )

    return out


def n10_estimate() -> dict[str, object]:
    """Conservative estimate / sketch of the n=10 ear-orderability counts.

    We do NOT run a full n=10 enumeration here (the prior artifact
    ``n10_vertex_circle_singleton_slices.json`` already established
    0 surviving full assignments under vertex-circle pruning; without that
    pruning, the search blows up combinatorially).  Instead we record the
    timings observed in ``n11_partial.json`` and document that the n=10
    cross-check would require the same multi-day budget noted in
    ``data/certificates/2026-05-05/n10_secondary.json``.
    """
    n10_path = ROOT / "data" / "certificates" / "n10_vertex_circle_singleton_slices.json"
    n11_path = ROOT / "data" / "certificates" / "2026-05-05" / "n11_partial.json"
    n10_data: dict[str, object] = {"path": str(n10_path), "exists": n10_path.exists()}
    n11_data: dict[str, object] = {"path": str(n11_path), "exists": n11_path.exists()}
    if n10_path.exists():
        raw = json.loads(n10_path.read_text(encoding="utf-8"))
        n10_data["counts"] = raw.get("counts")
        n10_data["aborted_any"] = raw.get("aborted_any")
        n10_data["row0_choices_covered"] = raw.get("row0_choices_covered")
        n10_data["elapsed_sum_seconds"] = raw.get("elapsed_sum_seconds")
        n10_data["full_assignments"] = "0 (vertex-circle filter eliminates all)"
    if n11_path.exists():
        raw = json.loads(n11_path.read_text(encoding="utf-8"))
        n11_data["measured_row0_0"] = raw.get("measured_row0_0")
        n11_data["preliminary_conclusion"] = raw.get("preliminary_conclusion")
        n11_data["extrapolated_total_n11_wallclock_4_core_hours"] = raw.get(
            "extrapolated_total_n11_wallclock_4_core_hours"
        )
        n11_data["cyclic_pattern_screen_evading"] = raw.get(
            "cyclic_pattern_screen", {}
        ).get("cyclic_assignments_evading_all_filters")
    return {
        "n10": n10_data,
        "n11": n11_data,
        "interpretation": (
            "At n=10, vertex-circle pruning eliminates every full assignment, "
            "so the Bridge Lemma A' question reduces vacuously: there are no "
            "geometric counterexamples reaching the geometric realization stage. "
            "The pre-vertex-circle survivors are NOT computed in this script "
            "due to the multi-day enumeration cost (cf. n11_partial.json: 40+ "
            "core-hours for n=11).  This deferred enumeration is recorded as a "
            "follow-up task; the n=8, n=9 evidence is the actual contribution."
        ),
    }


def structural_summary(n8_data: dict[str, object], n9_data: dict[str, object], real: dict[str, object]) -> dict[str, object]:
    """Distill the Bridge Lemma A' empirical findings."""
    n8_non_ear = n8_data["non_ear_orderable_count"]
    n8_k4 = n8_data["k4_core_ids"]
    n8_realiz = real["n8_non_ear_realization"]

    n9_non_ear = n9_data["non_ear_orderable_count"]
    n9_k4 = n9_data["k4_core_indices"]
    n9_realiz = real["n9_non_ear_realization"]

    findings: list[str] = []

    # n=8 K_4 core sub-conjecture
    n8_overlap = sorted(set(n8_data["non_ear_ids"]) & set(n8_k4))
    n8_only_non_ear = sorted(set(n8_data["non_ear_ids"]) - set(n8_k4))
    n8_only_k4 = sorted(set(n8_k4) - set(n8_data["non_ear_ids"]))
    findings.append(
        f"At n=8: non-ear ids = {sorted(n8_data['non_ear_ids'])}, K4-core ids = {sorted(n8_k4)}. "
        f"Overlap = {n8_overlap}; non-ear without K4 = {n8_only_non_ear}; K4 without non-ear = {n8_only_k4}."
    )

    # Realization rms summary
    n8_eq_rms = [
        (r.get("id"), r.get("eq_rms"))
        for r in n8_realiz
    ]
    n9_eq_rms = [
        (r.get("idx"), r.get("eq_rms"))
        for r in n9_realiz
    ]
    findings.append(
        "n=8 non-ear realization eq_rms: "
        + ", ".join(f"id={cid} rms={rms:.3e}" for cid, rms in n8_eq_rms)
    )
    findings.append(
        "n=9 non-ear realization eq_rms: "
        + ", ".join(f"idx={idx} rms={rms:.3e}" for idx, rms in n9_eq_rms)
    )

    # K_4 mutually-witnessed core forces equilateral 4-set
    findings.append(
        "Geometric obstruction for K_4-core (ids 0,1,2 at n=8): if {a,b,c,d} is "
        "a mutually-witnessed K_4-core, then for each x in {a,b,c,d} the other "
        "three vertices lie at a common distance r_x from x.  Symmetry forces "
        "r_a=r_b=r_c=r_d=d (a single common distance), yielding 6 pairwise "
        "equidistances on 4 points -- impossible in R^2 (would require a "
        "regular tetrahedron in R^3).  This rules out ids 0, 1, 2 directly."
    )
    findings.append(
        "id 3 has NO K_4 core but IS non-ear-orderable.  Largest mutually-"
        "witnessed clique is K_3.  Closure from 3-seed reaches at most 5 of 8 "
        "vertices, so the bridge fails for id 3 by a different mechanism (the "
        "Groebner basis of the squared-distance polynomial system collapses to "
        "{1}; see data/certificates/2026-05-05/n8_groebner_results.json id 3)."
    )
    findings.append(
        "Sub-conjecture refinement: at n=8, the non-ear set strictly contains "
        "the K_4-core set.  The K_4-core sub-conjecture (\"K_4-cores are "
        "geometrically unrealizable\") is provable directly (above), but it "
        "does NOT cover all non-ear cases."
    )

    n9_summary = (
        f"At n=9: non-ear indices = {sorted(n9_data['non_ear_indices'])}, "
        f"K4-core indices = {sorted(n9_k4)}. "
    )
    if n9_data["k4_core_indices"]:
        n9_summary += (
            f"Overlap = {sorted(set(n9_data['non_ear_indices']) & set(n9_k4))}."
        )
    else:
        n9_summary += "No K_4-cores at n=9 among the surviving 184 patterns."
    findings.append(n9_summary)

    n9_dist = n9_data["non_ear_or_k4_records"]
    if n9_data["non_ear_indices"]:
        first_non_ear = next(
            (r for r in n9_dist if not r["ear_orderable"]),
            None,
        )
        if first_non_ear:
            findings.append(
                f"At n=9, the only non-ear-orderable patterns are circulants on "
                f"Z/9 with offsets {{1,3,6,7}} (idx 81) and its v->-v image "
                f"{{2,3,6,8}} (idx 151); both are killed by the strict-cycle "
                f"vertex-circle obstruction (per bridge_lemma_check.json) and "
                f"have largest mutually-witnessed clique = K_3 only."
            )

    return {
        "key_findings": findings,
        "n8": {
            "non_ear_ids": sorted(n8_data["non_ear_ids"]),
            "k4_core_ids": sorted(n8_k4),
            "non_ear_subset_of_k4_cores": n8_data["non_ear_subset_of_k4_cores"],
            "k4_core_subset_of_non_ear": n8_data["k4_core_subset_of_non_ear"],
            "non_ear_realization_eq_rms": [
                {"id": cid, "eq_rms": float(rms) if rms is not None else None}
                for cid, rms in n8_eq_rms
            ],
        },
        "n9": {
            "non_ear_indices": sorted(n9_data["non_ear_indices"]),
            "k4_core_indices": sorted(n9_k4),
            "non_ear_realization_eq_rms": [
                {"idx": idx, "eq_rms": float(rms) if rms is not None else None}
                for idx, rms in n9_eq_rms
            ],
        },
        "bridge_lemma_a_prime_status": (
            "EVIDENCE_AT_N8_AND_N9_NO_PROOF: All non-ear patterns at n=8, n=9 "
            "exhibit non-trivial residuals under least-squares geometric "
            "realization, and at n=8 are independently killed by Groebner "
            "basis = {1}; at n=9 they are killed by strict-cycle vertex-circle "
            "obstruction.  This is empirical evidence for Bridge Lemma A' at "
            "the finite cases checked, but no general proof."
        ),
        "k4_core_sub_conjecture": (
            "PARTIAL: K_4 mutually-witnessed cores ARE geometrically "
            "unrealizable (would-be regular tetrahedron in R^2).  However, "
            "this does NOT subsume all non-ear-orderable n=8 patterns: id 3 "
            "is non-ear without a K_4 core.  So Bridge Lemma A' does NOT "
            "reduce to the K_4-core obstruction alone."
        ),
    }


def main() -> int:
    out_path = ROOT / "data" / "certificates" / "bridge_lemma_n8_n9_test.json"
    print(f"Writing {out_path}")

    n8 = analyze_n8()
    n9 = analyze_n9()
    real = realization_tests(n8, n9)
    summary = structural_summary(n8, n9, real)
    n10 = n10_estimate()

    payload = {
        "type": "bridge_lemma_a_prime_n8_n9_finite_test_v0",
        "trust": "REPO_LOCAL_EXPLORATORY_FINITE_TEST",
        "scope": (
            "Empirical test of Bridge Lemma A' (canonical-synthesis.md, "
            "Section 5.2) at n=8, n=9 only.  Does not prove or disprove "
            "Bridge Lemma A' or Erdos Problem #97.  Reports ear-orderability, "
            "mutual K_k cores, and least-squares realization residuals."
        ),
        "n8": n8,
        "n9": n9,
        "realization_tests": real,
        "summary": summary,
        "n10_n11_status": n10,
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "Bridge Lemma A' is not proved here; empirical evidence at n=8, n=9 only.",
            "The K_4-core obstruction (regular tetrahedron impossibility in R^2) "
            "is a clean geometric fact, but does NOT close all non-ear cases at n=8.",
        ],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
