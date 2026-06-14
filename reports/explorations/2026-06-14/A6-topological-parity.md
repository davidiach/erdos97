# A6 — Topological / Degree / Parity Obstruction

Date: 2026-06-14
Lane: A6 (topological / degree / parity invariants only; inversion/Möbius is A7's lane and is not touched here)
Author: research subagent

## Trust labels used in this report

- `LEMMA` — exact, finite, proved within the repo's existing lemma stack (here: L2, L6).
- `EXACT_FINITE_COMPUTATION` — a deterministic, exact (integer/set) computation over a stored finite input set; conclusions hold for *that input set only*.
- `NO_GO` / `LIMITATION` — an explicit statement of what the invariant does **not** establish.
- No claim in this report is a proof of Erdős #97 or a counterexample. The global problem remains FALSIFIABLE/OPEN.

## TL;DR

I picked candidate (ii): **a parity invariant of the selected-witness incidence
digraph forced by convex cyclic order**, and made the n=7 perpendicularity-cycle
argument into an **n-independent invariant**:

> **The perpendicularity graph `G_⊥` of any selected-witness system must be
> bipartite** (no odd cycle), and within each connected component the
> 2-colouring induces **forced-parallel chord classes**; two forced-parallel
> chords may not share a vertex (else 3 collinear vertices). Call these the
> **parity layer** (bipartiteness, = `H¹(G_⊥; ℤ/2)` vanishing) and the
> **coordination layer** (parallel-endpoint, = the ℝP¹ refinement).

Concrete computation on frontier objects (exact, reproducible):

| family | systems | killed by parity (non-bipartite) | additionally killed by parallel-endpoint | survive both |
|---|---|---|---|---|
| n=7 Fano dihedral classes | 54 | **54** | 0 | **0** |
| n=8 15 survivor classes | 15 | 0 | 0 | **15** |
| n=9 184 frontier assignments | 184 | 22 | **162** | **0** |

**Headline finding (`EXACT_FINITE_COMPUTATION`):** the entire stored **n=9
pre-vertex-circle frontier of 184 selected-witness assignments is eliminated by
the parity + parallel-endpoint filter alone — purely combinatorially, with no
vertex-circle / metric-quotient reasoning.** This is *not* a new global theorem,
but it is a strict, useful re-derivation: the repo's n=9 frontier search dropped
the parallel-endpoint filter that was active at n=8 (see "Provenance gap"), and
reinstating it closes the frontier at the incidence/parity level instead of the
heavier vertex-circle level.

**Honest no-go (`LIMITATION`):** the same invariant leaves **all 15 n=8 survivor
classes alive** (they die only to exact metric/orthocenter algebra). So
parity+parallel is **necessary but not sufficient**; it cannot, by itself, settle
even n=8, let alone the general problem. Topology underdetermines the metric
exactly here.

## 1. The invariant, precisely

### 1.1 Setup and the two geometric inputs (both already proved: L2, L6)

For a selected-witness system, center `i` has 4-set `W_i`. Define the
**perpendicularity graph** `G_⊥` on unordered vertex-chords:

- vertices: all chords `{a,b}` that occur either as a center-chord or as a
  common-witness chord;
- for every pair of centers `i≠j` with `|W_i ∩ W_j| = 2`, say
  `W_i ∩ W_j = {a,b}`, put an undirected **perp-edge** between chord `{i,j}` and
  chord `{a,b}`.

The single geometric fact powering every edge is

- **L6 (radical-axis perpendicularity):** if `W_i ∩ W_j = {a,b}` then
  `p_i p_j ⟂ p_a p_b`, because both centers lie on the perpendicular bisector of
  segment `ab`.

### 1.2 Parity layer = ℤ/2 slope cohomology

Assign each chord `e` its slope class `θ(e) ∈ ℝP¹ = ℝ/πℤ`. Perpendicularity is
the **fixed-point-free involution** `θ ↦ θ + π/2` on ℝP¹. Along any perp-path the
slope alternates by `+π/2`; around a **closed walk of odd length** the slope must
return to itself after an odd number of quarter-turns, i.e. `θ = θ + π/2` in
ℝ/πℤ — impossible for a **nonzero** chord.

- **Zero chords are excluded by L2** (no two polygon vertices coincide under
  strict convexity), so `θ(e)` is always well-defined. **This is where strict
  convexity enters the parity layer.**

So the necessary realizability condition is exactly:

> `G_⊥` is **bipartite** ⇔ the all-ones ℤ/2 edge-cochain has zero class in
> `H¹(G_⊥; ℤ/2)` ⇔ the 2-colouring (slope-class) system is solvable.

This is the n-independent form of the n=7 argument. At n=7 the common-witness
map `φ(e) = W_i ∩ W_j` is a **permutation of all 21 chords** (Jensen-saturation,
special to n=7), so `G_⊥` is the disjoint union of `φ`'s functional cycles and
"21 = odd" forces an odd cycle. For `n ≥ 8`, `φ` is not a permutation and the
direct bipartiteness test is the correct generalization.

### 1.3 Coordination layer = ℝP¹ refinement (parallel-endpoint)

Within one connected component of `G_⊥`, two chords at **even** perp-distance have
**equal** slope class, i.e. they are **parallel**. If two such forced-parallel
chords **share an endpoint** `v`, the two segments through `v` are collinear, so
3 polygon vertices are collinear — forbidden by **L2 (strict convexity)**.

This is exactly the "no same-color forced-parallel chord class sharing an
endpoint" filter that the repo already implements **for n=8** in
`src/erdos97/n8_incidence.py::passes_forced_perpendicularity_filters`. I
re-derived it as the coordination layer sitting on top of the parity layer.

### 1.4 Why this is genuinely a strict-convexity obstruction (mandatory check)

Both layers use strict convexity in a way a non-convex configuration can
violate:

1. L6's perpendicular bisector meets a strictly convex polygon in ≤ 2 vertices,
   pinning the chord-to-chord perpendicularity (the structure the parity walk
   rides on).
2. L2 (distinct vertices, no 3 collinear) is used twice: to make slopes nonzero
   (parity layer) and to forbid parallel-endpoint coincidence (coordination
   layer).

Negative control consistency: the repo's non-convex 24-point metric-linear
control (`failed-ideas.md` #16) and the concave alternating decagon
(`canonical-synthesis.md` §7.6) are *not* in scope here because the invariant is
asserted only as a *necessary* condition under strict convexity; it makes no
claim about non-convex realizability and so cannot be falsified by them.

## 2. Computation and reproduction

Script (standalone, dependency-free, exact set arithmetic):
`scripts/exploration/a6_topological_parity.py`.

```bash
python scripts/exploration/a6_topological_parity.py
```

Inputs (all STORED = INPUT, read-only):
- `data/incidence/n7_fano_dihedral_representatives.json` (54 classes)
- `data/incidence/n8_reconstructed_15_survivors.json` (15 classes)
- `data/certificates/n9_vertex_circle_frontier_motif_classification.json` (184 assignments)

The script additionally runs a **repo-faithful cross-check** that rebuilds the
parity test using the repository's own
`erdos97.incidence_filters.forced_perpendicular_graph` and
`odd_forced_perpendicular_cycle`, plus the n=8 parallel-endpoint logic. It
reproduces the table exactly (22 + 162 = 184 on the n=9 frontier), certifying
the standalone graph build has no bug.

```text
repo_cross_check: { n9_nonbipartite_repo_oddcycle: 22,
                    n9_parallel_endpoint_kill: 162,
                    n9_survive_both: 0, n9_total: 184 }
```

`tests/test_n8_incidence.py` still passes (the report adds no source changes; the
only new file is the exploration script).

## 3. Findings, with scope

### 3.1 `EXACT_FINITE_COMPUTATION` — n=7 sanity
All 54 Fano dihedral classes are non-bipartite. The invariant reproduces the
canonical perpendicularity-cycle argument exactly (each class has `G_⊥` =
permutation cycles of type 7+7+7, all odd).

### 3.2 `EXACT_FINITE_COMPUTATION` — n=9 frontier fully closed combinatorially
All 184 stored pre-vertex-circle assignments are eliminated: 22 by the parity
layer (odd cycle) and the remaining **162 by the coordination layer
(parallel-endpoint)**. The coordination layer is the load-bearing piece for 162
of 184 — the repo's own `odd_forced_perpendicular_cycle` alone catches only the
22.

Worked instance (assignment `A001`, repo template `T02`): centers 1 and 4 of
`A001` make `{1,3} ⟂ {0,2}` and `{1,4} ⟂ {0,2}`, so chords `{1,3}` and `{1,4}`
are forced parallel and share vertex `1` → vertices `1,3,4` collinear →
contradiction. No metric coordinates needed.

### 3.3 Provenance gap this exposes (actionable)
`src/erdos97/n9_incidence_frontier.py` defines two filter lists:
`BRANCH_PREFILTER_STATUSES` (used for search pruning) **omits**
`odd_forced_perpendicular_cycle`, and there is **no** parallel-endpoint filter
anywhere in the n=9 pipeline (`incidence_filters.py` has
`forced_perpendicular_graph` and `odd_forced_perpendicular_cycle` but **not** the
parallel-endpoint refinement that `n8_incidence.py` carries). Consequently the
184 "frontier" assignments were never tested against parity-as-a-hard-filter or
against parallel-endpoint before the vertex-circle stage. Reinstating both at the
incidence level would close the stored n=9 frontier set without any
vertex-circle/quotient machinery. This is a *consolidation/strengthening of an
existing route*, not an independent proof of n=9 (the vertex-circle route already
classifies all 184 as obstructed; see §4).

### 3.4 `LIMITATION` / `NO_GO` — the invariant does not settle n=8 (or the problem)
All **15 n=8 survivor classes pass both** the parity layer and the
parallel-endpoint layer. They are killed only by exact metric/orthocenter
algebra (`docs/n8-exact-survivors.md`). Therefore:

- parity + parallel-endpoint is **necessary but not sufficient**;
- it **cannot** be promoted to a general-`n` proof, because it provably fails to
  exclude realizable-looking n=8 incidence patterns;
- "topology underdetermines the metric" is concrete here: the ℝP¹ slope data
  (parity + parallel classes) is fully consistent for all 15 n=8 survivors, yet
  the actual squared-distance equalities are not.

## 4. Why the other A6 candidates do not (yet) give more

- **(i) Turning-number / winding coupling.** The convex polygon has signed
  turning number `+1`. I looked for a way to couple this to the parity layer
  (e.g. a "selected-witness map" whose degree is forced by `+1`). Obstacle: the
  perpendicularity graph lives on *chords*, and its ℤ/2 class is a property of
  the **abstract incidence pattern**, independent of the `+1` turning of the
  boundary cycle. The `+1` enters only through the *cyclic-order* (crossing /
  Kalmanson / vertex-circle) filters, which are a **different** invariant already
  owned by other lanes. I found no clean homomorphism from the boundary winding
  to the slope cohomology that adds information beyond §1. Recorded as a
  `NO_GO` for the direct coupling: the parity invariant is order-free, the
  turning number is order-bound; they do not multiply.
- **(iii) Degree-of-map / continuity on the moduli of convex `n`-gons.** A
  continuity/jump argument would need a *connected* family of all-centers-4-
  equidistant convex polygons to even define a degree; none is known to exist
  (the problem is whether any single such polygon exists). So there is no space
  on which to run a degree argument. `NO_GO` until a positive-dimensional family
  is exhibited.
- **(iv) Euler-characteristic / mod-2 incidence count.** The ℤ/2 incidence count
  is exactly the bipartiteness obstruction already captured in §1.2 (the cycle
  space of `G_⊥` over `𝔽₂`); the parallel-endpoint refinement is the additional
  𝔽₂-linear constraint from collinearity. I did not find an independent
  Euler-characteristic count beyond these two.

## 5. What I did NOT establish

- No proof of Erdős #97 and no counterexample.
- No new general-`n` theorem. The parity+parallel invariant is **necessary
  only**; it fails to exclude the 15 n=8 survivors, so it has a proven ceiling.
- I did **not** prove that every realizable counterexample's frontier must enter
  a non-bipartite-or-parallel-endpoint pattern; the n=9 result is for the
  **stored 184 frontier set only** (which itself is a review-pending diagnostic
  artifact, not a source-of-truth completeness claim).
- I did **not** re-run the full n=9 branch search with the reinstated filters; I
  only evaluated the invariant on the stored frontier output. Re-running the
  search with parallel-endpoint as a hard prefilter is the natural follow-up
  (would let the search terminate earlier and might shrink the frontier before
  vertex-circle), but it is left as a recommendation.
- I did not touch inversion/Möbius geometry (A7's lane).

## 6. Recommended follow-ups (for maintainers)

1. Add a `parallel_endpoint_violation` filter to
   `src/erdos97/incidence_filters.py` (lift the n=8 logic to general `n`) and
   include both it and `odd_forced_perpendicular_cycle` in
   `n9_incidence_frontier.BRANCH_PREFILTER_STATUSES`. Expected effect: the 184
   stored frontier assignments become incidence-infeasible, giving a lighter
   (combinatorial) route to the same n=9 frontier conclusion that currently
   needs the vertex-circle quotient stage.
2. Decide the soundness/scope question for the parallel-endpoint filter formally
   (it is sound; the proof is the 2-line L6+L2 argument in §1.3) and, if desired,
   record it as a `LEMMA` in `docs/claims.md` next to the radical-axis crossing
   lemma.
3. Do **not** advertise parity+parallel as a proof route past the incidence
   layer: the n=8 survivors are the standing counterexample to its sufficiency.

## Appendix — files

- New: `scripts/exploration/a6_topological_parity.py` (exploration only).
- Read (inputs): `data/incidence/n7_fano_dihedral_representatives.json`,
  `data/incidence/n8_reconstructed_15_survivors.json`,
  `data/certificates/n9_vertex_circle_frontier_motif_classification.json`.
- Repo functions reused for cross-check:
  `src/erdos97/incidence_filters.py::forced_perpendicular_graph`,
  `::odd_forced_perpendicular_cycle`;
  `src/erdos97/n8_incidence.py::passes_forced_perpendicularity_filters`.
