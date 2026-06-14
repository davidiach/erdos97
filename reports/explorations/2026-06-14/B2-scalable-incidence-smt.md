# B2: Scalable SAT/SMT incidence search to push the finite frontier (n>=10)

Lane: B2 (Erdos Problem #97). Date: 2026-06-14.

Trust label of every result below:
`MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`, and only for the
**necessary-incidence** layer. Nothing here is a geometric proof for any `n`,
nothing promotes `n=9`/`n=10`, nothing proves Erdos Problem #97, and nothing
claims a counterexample. The official/global status remains falsifiable/open.

## Objective and scope

Build a more scalable abstract-incidence search than the repo's `n=9`
minimum-remaining-options (MRO) exhaustive enumerator and `n=10` singleton-slice
draft, enforcing the documented NECESSARY incidence filters with aggressive
dihedral symmetry-breaking, and push the finite frontier toward `n=10/11/12`.

Variables are the selected 4-sets `S_i` (one per center). Constraints are
exactly the necessary filters every strictly convex 4-bad `n`-gon must satisfy:

1. two-circle cap: `|S_a ∩ S_b| <= 2` (two circles meet in <= 2 points);
2. radical-axis crossing: if `S_a ∩ S_b = {u,v}` exactly, chords `{a,b}` and
   `{u,v}` must cross in the cyclic order and neither is an edge (so adjacent
   centers share <= 1 witness);
3. witness-pair cap: each unordered witness pair occurs in <= 2 rows;
4. selected-indegree cap: each label has indegree `<= floor(2(n-1)/3)`;
5. vertex-circle quotient: selected-distance equalities quotient ordinary
   pair-distances; nested-chord strict inequalities around each center orient
   strict edges between classes; a self-edge or directed strict cycle is
   unrealizable.

These are the same filters as `docs/n9-vertex-circle-exhaustive.md` /
`docs/n10-vertex-circle-singleton-slices.md` and the lemmas in `docs/claims.md`
(circle-intersection cap, radical-axis crossing/bisection, sharpened incidence
counting, strict quotient-graph obstruction). Strict convexity enters only
through filters 2 and 5 (perpendicular-bisector crossing and nested-chord strict
inequalities). The search introduces NO point coordinates; it is purely
combinatorial. Adjacent lane B1 owns exact-geometry z3 at `n=9`; this lane owns
only scaling the abstract search to `n>=10`.

## Code

- `scripts/exploration/b2_scalable_incidence_search.py` — incremental
  backtracking search. Bitset rows; precomputed pairwise-compatibility tables,
  witness-pair / selected-equality membership, and nested-chord strict edges;
  MRO center selection; incremental union-find with a rollback trail; a per-
  `search()`-call cached base strict-graph reused across all candidate options;
  and a from-scratch full-quotient **terminal soundness guard** re-confirming
  every complete assignment (so the incremental per-candidate convention cannot
  leak a false survivor). Two symmetry modes:
  - `--symmetry none`: every lexicographic row0 is a separate start (no
    quotient) — used as a correctness oracle;
  - `--symmetry refl0`: row0 restricted to representatives canonical under the
    single dihedral reflection `r(k) = (-k) mod n` that fixes center 0 — a sound
    symmetry break (every labelled survivor has a dihedral image whose center-0
    row is refl0-canonical), giving dihedral-orbit-reduced survivor counts.
- `scripts/exploration/b2_realizability_spotcheck.py` — optional z3 strict-convex
  realizability spot-check (strict turns + equal selected squared distances) for
  any surviving incidence system at `n>=10`. Reuses B1's geometric encoding lane;
  included only to triage a small survivor immediately.

Both files pass `ruff check` (All checks passed).

## Correctness validation (the load-bearing part)

The search is validated against the repo's `n=9` results on a fully independent
code path (it imports no project search modules):

- `--n 9 --symmetry none` gives **70 row0 options and 0 incidence survivors**,
  matching `data/certificates/n9_vertex_circle_exhaustive.json` (the full `n=9`
  frontier is killed by the vertex-circle filter). Reproduce:
  `python scripts/exploration/b2_scalable_incidence_search.py --n 9 --symmetry none --assert-n9`.
- With the vertex-circle quotient disabled, the search reproduces **exactly the
  184 pre-vertex-circle frontier** and the exact stored sorted-row-set digest
  `dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55`
  (the digest in `docs/n9-vertex-circle-exhaustive.md` and the compact-brancher
  artifact). This certifies that filters 1–4 and the search are correct, and
  that the incremental quotient logic agrees with the repo on which 184 systems
  are vertex-circle-obstructed.
- `--n 9 --symmetry refl0` gives **38 row0 options** (matching the archive's
  "38 canonical row0 classes" in the late-archive cross-check) and **0
  survivors**, agreeing with the `none` mode.

The z3 realizability spot-check was smoke-tested on `n=9` pre-vertex-circle
frontier rows (incidence-valid but vertex-circle-obstructed): one returned
`unsat` (no strict-convex realization in the natural order, consistent with the
combinatorial obstruction) in ~2.3s; the other two returned `unknown` at a 15s
timeout (z3 QF_NRA is not always decisive — reported honestly). This confirms the
helper is wired correctly end-to-end; it does not re-do B1's `n=9` study.

## Results table

| n  | symmetry | row0 options | nodes explored | survivors | runtime | complete? |
|----|----------|-------------:|---------------:|----------:|--------:|-----------|
| 9  | none     | 70           | 22,591         | 0         | ~4.6 s  | yes (oracle) |
| 9  | none, VC off | 70       | (184 terminal) | 184 (=frontier, digest match) | ~5 s | yes |
| 9  | refl0    | 38           | 13,187         | 0         | ~3.3 s  | yes |
| 10 | refl0    | 66           | ~295k–397k in budget | 0 so far | aborted at 110–195 s | **no** |
| 11 | refl0    | 110          | (not started)  | n/a       | n/a     | no (constructs only) |
| 12 | refl0    | 170          | (not started)  | n/a       | n/a     | no (constructs only) |

`n=10`, `refl0`: in 195 s the search explored 397,312 nodes (210,111 self-edge +
442,604 strict-cycle prunes), 0 survivors so far, and did not finish. Per-slice
profiling (one fixed row0 per run, 2 s budget each) completed **0 of 66** slices
— every single row0 subtree is itself larger than 2 s. So the `n=10` cost is in
deep per-slice subtrees, not the slice count.

## Scaling bottleneck (what stops n=10)

Steady-state throughput is ~2,000–2,700 nodes/s in pure Python. The dominant
per-node costs are:

1. **MRO option regeneration.** `choose_center` calls `valid_options` for every
   unassigned center at every node; each `valid_options` scans up to ~210
   candidate rows and, per row, the pairwise-compatibility set lookups against
   all placed rows plus indegree/witness-pair caps. Deep in the `n=10` tree this
   is the largest single cost.
2. **Vertex-circle quotient evaluation.** Even with the cached base strict-graph
   (built once per `search()` call and reused across candidates) and the cheap
   self-edge short-circuit, each candidate still runs an incremental cycle DFS
   over class roots. Caching the base graph cut the constant factor by only
   ~30% because cost (1) co-dominates.

At ~2k nodes/s, the stored `n=10` singleton artifact's 4.1M-node fixed-order
search corresponds to ~30+ min — consistent with the repo calling it
"artifact-tier, not fast-tier." `n=11/12` are strictly larger in both branching
(110/170 refl0 row0 vs 66; 210/330 rows/center) and depth, so they are further
out of reach by the same mechanism.

The bottleneck is **Python-interpreter per-node overhead in MRO option
regeneration**, not a missing pruning rule (the prunes are already aggressive:
the `refl0` `n=10` budgeted run shows ~650k prunes vs ~400k explored nodes).

## What I did NOT establish

- I did **not** complete the `n=10` necessary-incidence frontier; `n=10` remains
  open in this lane. I reached a partial frontier (~0.4M nodes, 0 survivors,
  0/66 `refl0` slices completed) within the compute budget.
- I did **not** start `n=11`/`n=12` searches (only confirmed they construct and
  are strictly harder).
- I did **not** find any surviving `n=10` incidence system, so the z3
  realizability spot-check had nothing live to triage; it was only smoke-tested
  on `n=9` frontier rows.
- No result is a geometric proof. Absence of survivors is a necessary-incidence
  non-existence statement conditional on implementation correctness and on these
  filters being the complete necessary set; it does not by itself exclude a
  strictly convex 4-bad `n`-gon.
- `refl0` survivor counts (when nonzero) would be dihedral-orbit-reduced, not all
  labelled survivors.

## Honest assessment / next steps

To actually finish `n=10` one needs to remove the Python per-node overhead, not
add filters. Concrete options: (a) port the inner loop (MRO + compatibility +
quotient) to a compiled kernel or a bitset-SAT/CP-SAT encoding (e.g. OR-Tools
CP-SAT or a custom C/Cython backtracker) — the incidence filters are exactly the
clause families a CP/SAT solver handles natively, and a static variable order
with the same `refl0` symmetry break would likely close `n=10` in minutes;
(b) precompute, per center pair, compatibility as integer bitsets so
`valid_options` becomes a few bitwise-AND/popcount operations instead of Python
set scans; (c) static (non-MRO) center order to avoid recomputing every center's
option list at every node. The mathematics (filters + symmetry break) is in
place and validated against `n=9`; the remaining work is purely an engineering
speedup of the same search.

## Reproduction

```bash
# n=9 correctness oracle (70 row0, 0 survivors)
python scripts/exploration/b2_scalable_incidence_search.py --n 9 --symmetry none --assert-n9

# n=9 dihedral-symmetry-broken (38 row0, 0 survivors)
python scripts/exploration/b2_scalable_incidence_search.py --n 9 --symmetry refl0

# n=10 attempt with a time budget (reports partial, aborted frontier)
python scripts/exploration/b2_scalable_incidence_search.py --n 10 --symmetry refl0 --time-budget 180 --no-survivors

# 184 pre-vertex-circle frontier digest check (Python REPL):
#   s=ScalableIncidenceSearch(9,symmetry='none'); set all s.row_strict[k]=[]; s.run()
#   -> survivors=184, digest dc28b32...f213d55

# optional z3 realizability spot-check on a survivors JSON (none exist at n=10):
python scripts/exploration/b2_realizability_spotcheck.py --rows-json <survivors.json> --timeout-ms 10000
```
