"""A3 bridge-ear-orderability: focused study of the 6 non-ear frontier objects.

Lane A3. This script is a COMBINATORIAL diagnostic over fixed selected-witness
patterns. It does NOT certify Euclidean realizability, does NOT prove Bridge
Lemma A', does NOT prove Erdos Problem #97, and does NOT claim a counterexample.

It treats the stored selected rows as INPUT (one selected 4-set per center,
i.e. the *singleton rich class* interpretation). The objects studied are the 6
non-ear-orderable frontier objects recorded in
data/certificates/bridge_lemma_frontier.json:
    n=8 survivor classes 0,1,2,3 and n=9 assignments 81,151.

We use the repo definitions:
  - rich-triple closure cl(.) and bootstrap rank rho(P) from
    docs/bootstrap-core-bridge.md / src/erdos97/bootstrap_cores.py;
  - ear-orderable  <=>  rho(P) <= 3 (closure-rank lemma).

Outputs, per object:
  (1) re-confirmation of non-ear (rho > 3) over the singleton-rich family;
  (2) the full set of minimal stuck sets (radius-blockers in the fixed-row
      sense) and the inclusion-minimal generating cores;
  (3) tests of three candidate *extra* hypotheses that one might hope force
      ear-orderability, reported honestly as forcing / not-forcing on these
      fixed objects:
        (H1) minimality-style "use any rich class, not the stored one" cannot
             be tested on a fixed singleton family (the stored row is the only
             class); we instead test the *circulant orbit* alternative: does
             allowing ALL rotations of the row as alternative rich classes at a
             center change rho?  (probes the noncanonical-selection gap);
        (H2) rich-class enlargement: if a center is allowed a SECOND disjoint
             rich class (size>=4) drawn from the remaining vertices, does some
             completion drop rho to <=3?  (probes whether richer geometry helps);
        (H3) convex-order / cyclic-arc restriction: restrict generators to
             cyclic *intervals* (arcs) of length<=3 -- does an interval seed
             still generate?  (probes whether convex order alone forces ears).

Reproduce:
    python scripts/exploration/a3_ear_orderability_frontier.py
"""

from __future__ import annotations

import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

import networkx as nx  # noqa: E402  (available per environment)

from erdos97.bootstrap_cores import (  # noqa: E402
    closure,
    is_inclusion_minimal_generator,
)
from erdos97.stuck_sets import (  # noqa: E402
    find_minimal_stuck_sets,
    forward_ear_order,
)

FRONTIER = os.path.join(ROOT, "data", "certificates", "bridge_lemma_frontier.json")


def load_targets():
    with open(FRONTIER) as fh:
        data = json.load(fh)
    out = []
    for t in data["proof_mining_targets"]:
        out.append(
            {
                "id": t["target_id"],
                "n": t["n"],
                "rows": [list(r) for r in t["selected_rows"]],
                "offsets": t.get("circulant_offsets"),
                "stored_closure": t["ear_order"]["largest_closure"],
                "stored_seed": t["ear_order"]["largest_closure_seed"],
            }
        )
    return out


def singleton_rich(rows):
    """One rich class per center = the stored selected row."""
    return [[list(r)] for r in rows]


def overgenerous_closure_generates(seed, classes_by_center, n):
    """Rich-triple closure that does NOT enforce disjoint classes per center.

    This is an explicit RELAXATION used only for the H1/H2 over-generous upper
    bounds: a center is added once any of its (possibly overlapping) candidate
    classes has >=3 vertices already in the closure. Because real geometry forces
    distinct distance classes at a center to be disjoint, this relaxation can
    only ADD generating power, never remove it. So if even this relaxed closure
    cannot generate from any small seed, the genuine geometric closure cannot
    either: a robust 'no'.
    """
    masks_by_center = []
    for classes in classes_by_center:
        masks = []
        for row in classes:
            m = 0
            for v in row:
                m |= 1 << int(v)
            masks.append(m)
        masks_by_center.append(masks)
    cl = 0
    for v in seed:
        cl |= 1 << int(v)
    changed = True
    while changed:
        changed = False
        for c in range(n):
            if cl & (1 << c):
                continue
            for m in masks_by_center[c]:
                if (m & cl).bit_count() >= 3:
                    cl |= 1 << c
                    changed = True
                    break
    return cl.bit_count() == n


def is_circulant(rows, n):
    """Return offset-set if rows are a circulant pattern S_i = i + offsets, else None."""
    base = sorted((w - 0) % n for w in rows[0])
    for i in range(n):
        want = sorted((o + i) % n for o in base)
        if sorted(rows[i]) != want:
            return None
    return base


def rho_singleton(rows):
    """Bootstrap rank rho over the singleton-rich family (exhaustive up to size 4)."""
    rc = singleton_rich(rows)
    n = len(rows)
    for size in range(1, min(4, n) + 1):
        for seed in itertools.combinations(range(n), size):
            if closure(seed, rc).generates_all:
                return size, list(seed)
    return None, None  # rho > 4 (well above the <=3 threshold)


def all_minimal_stuck(rows):
    res = find_minimal_stuck_sets(rows, max_examples=10_000)
    return res


def inclusion_minimal_generators(rows, max_size=6):
    """List inclusion-minimal generating cores up to max_size (singleton rich)."""
    rc = singleton_rich(rows)
    n = len(rows)
    cores = []
    for size in range(4, min(max_size, n) + 1):
        for core in itertools.combinations(range(n), size):
            if closure(core, rc).generates_all and is_inclusion_minimal_generator(core, rc):
                cores.append(list(core))
    return cores


# ---- candidate extra hypotheses -------------------------------------------------

def h1_circulant_orbit(rows, n):
    """H1: allow ALL n rotations of the base row as alternative rich classes at
    every center (only meaningful for circulant patterns). Does rho drop to <=3?

    This is deliberately *over-generous*: it does NOT respect that distinct rich
    classes at a center must be disjoint, so it is an UPPER bound on richness.
    A 'no' here is therefore strong evidence the obstruction survives richness.
    """
    base = is_circulant(rows, n)
    if base is None:
        return {"applicable": False}
    rc = []
    for c in range(n):
        classes = []
        for shift in range(n):
            row = sorted((o + shift) % n for o in base)
            if c in row:
                continue
            classes.append(row)
        # dedupe
        uniq = []
        seen = set()
        for r in classes:
            key = tuple(r)
            if key not in seen:
                seen.add(key)
                uniq.append(r)
        rc.append(uniq)
    # exhaustive rho with this (non-disjoint) over-rich family
    for size in range(1, 4):
        for seed in itertools.combinations(range(n), size):
            if overgenerous_closure_generates(seed, rc, n):
                return {"applicable": True, "rho_leq_3": True, "seed": list(seed)}
    return {"applicable": True, "rho_leq_3": False}


def h2_second_disjoint_class(rows):
    """H2: allow each center one ADDITIONAL disjoint rich class of size 4 drawn
    from the remaining vertices. Does there EXIST a choice of second classes that
    drops rho to <=3?  We search greedily/exhaustively over per-center options
    but report only existence of a drop, capped for runtime.

    Returns dict with 'exists_drop' and an example if found.
    """
    n = len(rows)
    base = [set(r) for r in rows]
    # candidate second classes per center: 4-subsets of V\{center} disjoint from base[c]
    options = []
    for c in range(n):
        avail = [v for v in range(n) if v != c and v not in base[c]]
        opts = [list(r) for r in itertools.combinations(avail, 4)]
        options.append(opts)
    # If any center has < 1 option, it just contributes only the base class.
    # Full product is enormous; instead test a necessary relaxation:
    # the UNION of base + ALL candidate second classes (over-generous, non-disjoint),
    # which upper-bounds achievable richness from a single extra disjoint class.
    rc = []
    for c in range(n):
        classes = [list(rows[c])] + options[c]
        rc.append(classes)
    for size in range(1, 4):
        for seed in itertools.combinations(range(n), size):
            if overgenerous_closure_generates(seed, rc, n):
                return {"exists_drop_upper_bound": True, "seed": list(seed),
                        "note": "over-generous (all candidate 2nd classes at once)"}
    return {"exists_drop_upper_bound": False,
            "note": "even allowing every disjoint 4-subset as an extra class, rho>3"}


def h3_convex_interval_seeds(rows, n):
    """H3: restrict generating seeds to cyclic INTERVALS (arcs) of length<=3.
    Does any cyclic interval generate (singleton rich)? Records the best arc.
    Convex order is the cyclic order 0..n-1 here (selected rows are in that frame).
    """
    rc = singleton_rich(rows)
    best = (-1, None)
    found = None
    for length in range(1, 4):
        for start in range(n):
            arc = [(start + k) % n for k in range(length)]
            res = closure(arc, rc)
            if len(res.closure) > best[0]:
                best = (len(res.closure), arc)
            if res.generates_all:
                found = arc
                break
        if found:
            break
    return {"interval_seed_generates": found is not None,
            "generating_arc": found,
            "best_arc": best[1], "best_arc_closure_size": best[0]}


def stuck_set_graph_signature(rows, stuck_vertices):
    """Internal-witness directed graph on a stuck set; report indegree/outdegree."""
    sub = set(stuck_vertices)
    G = nx.DiGraph()
    G.add_nodes_from(sorted(sub))
    for c in sorted(sub):
        for w in rows[c]:
            if w in sub:
                G.add_edge(c, w)  # center c selects internal witness w
    outdeg = {v: G.out_degree(v) for v in G.nodes}  # internal selected witnesses
    indeg = {v: G.in_degree(v) for v in G.nodes}
    return {
        "size": len(sub),
        "internal_outdeg": outdeg,
        "internal_indeg": indeg,
        "max_internal_outdeg": max(outdeg.values()) if outdeg else 0,
        "is_strongly_connected": nx.is_strongly_connected(G) if len(sub) > 1 else True,
    }


def analyze(target):
    n = target["n"]
    rows = target["rows"]
    rep = {"id": target["id"], "n": n, "circulant_offsets": target["offsets"]}

    # confirm non-ear two ways
    fe = forward_ear_order(rows)
    rep["forward_ear_exists"] = fe.exists
    rep["forward_ear_largest_closure"] = sorted(fe.largest_closure)
    rep["forward_ear_largest_closure_size"] = fe.largest_closure_size
    rho, rseed = rho_singleton(rows)
    rep["rho_singleton"] = rho if rho is not None else ">4"
    rep["rho_seed"] = rseed
    rep["non_ear_confirmed"] = (not fe.exists) and (rho is None or rho > 3)

    # circulant check
    base = is_circulant(rows, n)
    rep["is_circulant"] = base is not None
    rep["circulant_base_offsets"] = base

    # minimal stuck sets
    ms = all_minimal_stuck(rows)
    rep["minimal_stuck_size"] = ms.minimal_size
    rep["minimal_stuck_count"] = ms.total_at_minimal_size
    rep["minimal_stuck_examples"] = [s.vertices for s in ms.examples[:6]]
    if ms.examples:
        rep["stuck_graph_signature"] = stuck_set_graph_signature(rows, ms.examples[0].vertices)

    internal_full = {c: sum(1 for w in rows[c] if 0 <= w < n) for c in range(n)}
    rep["every_center_internal_in_full"] = internal_full  # = 4 always (sanity)

    # inclusion-minimal generators (these are the radius-blocker complements' duals)
    cores = inclusion_minimal_generators(rows, max_size=min(6, n))
    rep["inclusion_minimal_generators_upto6"] = cores[:12]
    rep["inclusion_minimal_generator_min_size"] = (
        min((len(c) for c in cores), default=None)
    )

    # candidate extra hypotheses
    rep["H1_circulant_orbit"] = h1_circulant_orbit(rows, n)
    rep["H2_second_disjoint_class"] = h2_second_disjoint_class(rows)
    rep["H3_convex_interval_seed"] = h3_convex_interval_seeds(rows, n)

    return rep


def main():
    targets = load_targets()
    results = [analyze(t) for t in targets]
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    main()
