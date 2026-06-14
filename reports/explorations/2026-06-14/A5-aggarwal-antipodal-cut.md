# A5 — Aggarwal antipodal-cut forbidden-cycle transfer (the deferred checker)

Trust label: `LITERATURE_ANCHOR` + `DESIGN_NOTE` + `EXACT_FIXED_CLASS_FILTER`
(the prototype) and `SHARP_NO_GO_FOR_NEW_KILLS` (the frontier result).

Scope guardrail: this note does NOT prove Erdos Problem #97, does NOT claim a
counterexample, and does NOT certify Euclidean realizability of any
configuration. The exact combinatorial quotient classes below are built with
the repository's existing exact selected-distance union-find
(`erdos97.vertex_circle_quotient_replay`), not floating point. The two small
geometry probes are numerical and labelled as such; no near-equality is treated
as a fact. The official / global status of #97 remains open. The deliverable is
(a) a precise statement of which Aggarwal hypotheses are needed, (b) the exact
obstruction that blocks transferring them to the variable-radius selected
matrix, and (c) a stdlib/numpy/networkx prototype filter run on the n=9 frontier
with the result that it newly obstructs **zero** assignments.

Reproduction:

```bash
python scripts/exploration/a5_aggarwal_antipodal_cut.py
python scripts/exploration/a5_aggarwal_antipodal_cut.py --assume-intersection-free
ruff check scripts/exploration/a5_aggarwal_antipodal_cut.py
```

Inputs (treated as data, not truth):

- `data/certificates/n9_vertex_circle_frontier_motif_classification.json`
  (the 184 regenerated n=9 pre-vertex-circle frontier assignments, cyclic
  order `0..8`, each row `[center, w1, w2, w3, w4]`, with the existing-filter
  `status` field `self_edge` / `strict_cycle`).
- `data/certificates/n9_vertex_circle_exhaustive.json` (search metadata only;
  it stores the 70 row-0 choices and the `184 = 158 + 26` accounting, not the
  184 assignments themselves — those live in the motif-classification file).

Literature access caveat: arXiv (`1009.2216`), ScienceDirect, Semantic Scholar
and ResearchGate all returned HTTP 403 during this session, so the precise
verbatim definitions of "distance-like matrix" and "intersection-free edge"
could not be re-pulled from the primary source. The statements below use the
repository's own careful transcription in
`docs/research-directions-2026-05-19.md` Section 1 and
`docs/literature-risk.md` (Aggarwal entry), cross-checked against web-search
summaries that confirm: antipodal cut = two parallel supporting lines splitting
the polygon into two chains; the distance matrix is the cross-chain matrix; the
0-1 cut matrix is its skeleton; and the forbidden object is a cycle of
unit-distance edges with an intersection-free edge. The internal-consistency of
the property used here (cross-chain Kalmanson/Monge) is verified numerically
below, so the analysis does not depend on the blocked primary text.

---

## (a) Which Aggarwal hypotheses the forbidden-cycle result requires

Aggarwal, "On Unit Distances in a Convex Polygon", arXiv:1009.2216, Discrete
Mathematics 338 (2015), 88-92. The cut-matrix forbidden-cycle ingredient needs
all four of the following:

1. **Antipodal cut → two contiguous chains.** Two parallel supporting lines of
   the convex polygon split its boundary into two arcs (chains) `A` and `B`.
   Crucially, `A` and `B` are each *contiguous* in the boundary cyclic order
   and they do **not** interleave. (Web-search-confirmed: "an antipodal cut
   partitions a polygon into two subpolygons using two parallel supporting
   lines".)

2. **A single fixed ordinary-distance class `Q`.** The matrix is the
   *unit-distance* matrix of cross-chain pairs: `M[a,b]=1` iff `|p_a-p_b|`
   equals the one common value (the unit). Every cycle entry is in that one
   class.

3. **Distance-likeness = cross-chain Monge / Kalmanson monotonicity.** The real
   cross-chain distance matrix `D[a,b]=|p_a-p_b|`, with `A` and `B` listed in
   boundary order, satisfies a Monge-type / inverse-Monge total-monotonicity.
   For ordinary (unsquared) distances of a convex polygon this is exactly the
   Kalmanson inequality restricted to cross-chain quadruples. (Web-search:
   "A 0-1 cut matrix is the skeleton of a distance matrix"; the proof that the
   cycle is forbidden uses the monotone structure of the distance matrix.)

4. **An intersection-free edge in the cycle.** The forbidden object is a cycle
   in the 0-1 matrix — rows `r_1=1,r_2,...,r_l`, columns `c_1=1,c_2,...,c_l`,
   `r_i != r_{i+1}`, `c_i != c_{i+1}`, with `(r_i,c_i)` and `(r_i,c_{i+1})`
   both `1` cyclically — that additionally has an **intersection-free edge**:
   one of the cycle's unit segments `p_{r_i} p_{c_i}` crosses no other segment
   of the cycle. The "one-only containment" convention is permissive: extra `1`
   entries are harmless; only the required cycle entries must lie in `Q`.

The forbidden conclusion: no distance-like (cross-chain-Monge) matrix can host
such a cycle with an intersection-free edge. This is hypotheses (1)+(2)+(3)+(4)
acting together; dropping any one breaks the result.

Internal verification of (3) (numerical, `numpy`/`scipy`): on regular n-gons
and random convex-hull n-gons in boundary order, both Kalmanson inequalities
`d(i,j)+d(k,l) <= d(i,k)+d(j,l)` and `d(j,k)+d(i,l) <= d(i,k)+d(j,l)` (boundary
order `i<j<k<l`) hold with **zero** violations on unsquared distances, while the
**squared**-distance analogue is violated (e.g. 53/126 quadruples on one random
9-gon). This reproduces the repository's existing finding
`docs/canonical-synthesis.md` Section 6.9 ("Monge property on squared distances
is FALSE"). So the distance-likeness Aggarwal needs lives on *ordinary*
distances, not squared distances.

---

## (b) Exact obstruction to transferring (3)+(2) to the variable-radius matrix

The **unsafe transfer** flagged in `docs/research-directions-2026-05-19.md`
Section 1 is confirmed and made precise here. Two independent obstructions:

**O1 — the combined selected matrix is not one distance class (kills naive use
of hypothesis 2).** The selected-witness matrix `M[i,j]=1 iff j in S_i` mixes
`n` per-center radii. Its `1` entries do not lie in one ordinary-distance class,
so it is neither a unit-distance matrix nor a single-class cut matrix. Hence
hypotheses (2) and (3) fail simultaneously for the *combined* matrix: there is
no single class, and there is no cross-chain Monge structure on a multi-radius
0-1 matrix. This is the documented "do not combine all selected center-witness
edges into one matrix" warning, now stated as: **the only safe `Q` is a forced
single ordinary-distance class**, obtained from selected-row equalities by the
exact quotient (reciprocal + transitive merges). The prototype therefore tests
**only** quotient classes, never a raw per-center row.

This obstruction is real but **not vacuous on the frontier**: every one of the
184 n=9 frontier assignments has many reciprocal selected edges (histogram of
reciprocal-edge counts over 184: `{5:54, 6:18, 8:36, 9:22, 10:18, 11:36}`), so
the selected-distance quotient *does* force nontrivial single ordinary-distance
classes (largest forced class up to 13 pairs). There is genuine single-class
material to feed Aggarwal. So the route is not dead at step (2); it is killed at
step (4).

**O2 — the intersection-free edge (hypothesis 4) cannot be supplied from
abstract combinatorial cut data (kills the only genuinely-new content).** This
is the sharp obstruction. Decompose the cycle by length `l`:

- **`l = 2` (a 2x2 all-ones submatrix, the canonical cycle seed).** On a
  *contiguous separated* cut, a 2x2 all-ones in `Q` means four cross distances
  `D(r1,c1)=D(r1,c2)=D(r2,c1)=D(r2,c2)` are equal. With `A=(r1,r2)` and
  `B=(c2,c1)` as separated arcs, the four points are a clean convex quadruple
  and the equality is exactly a Kalmanson **equality** (`side+side = diag+diag`).
  Strict convexity gives **strict** Kalmanson (verified: min slack over 20000
  random strict-convex 4-gons `= 4.97e-6 > 0`; the sign is the crossing-diagonal
  fact, exact). So the `l=2` Aggarwal cycle on an antipodal cut is **already
  killed by the strict-Kalmanson certificate stack the repository owns** — it
  needs no intersection-free edge and contributes nothing beyond Kalmanson.
  (Negative control that the cut hypothesis is essential: the same-distance
  cross `K_{2,2}` *is* realizable in strict convex position as a rhombus
  `a1,b1,a2,b2`, but there `{a1,a2}` is **not** a contiguous arc — A and B
  interleave — so it is not an antipodal-cut configuration and is correctly not
  forbidden.)

- **`l = 3` (a bipartite hexagon, the first genuinely-Aggarwal pattern).** A
  same-distance cross 6-cycle `r1-c1-r2-c2-r3-c3-r1` (all six cross edges in one
  class). This is where Aggarwal's intersection-free edge would do real work
  beyond Kalmanson. Two findings:

  (i) Numerical realizability probe (`numpy`/`scipy`, separated-arc
  parametrization with strictly monotone polar angles so `A` precedes `B`): out
  of residual-zero solutions (best residual `5.5e-10`), **zero** are strictly
  convex with `A` before `B`; every same-distance 6-cycle realization forces the
  arcs to interleave. This is *consistent with* the 6-cycle on a genuine
  antipodal cut being geometrically forbidden, but it is only numerical evidence
  and is NOT a proof.

  (ii) Exact propagation observation: applying Kalmanson to the 6-cycle's own
  cyclic quadruples forces additional equalities. For the A001 hexagon (rows
  `{0,1,2}`, cols `{3,7,8}`, edges `(0,3)(0,8)(1,8)(1,7)(2,7)(2,3)`), Kalmanson
  on `(0,1,7,8)` gives `d(0,7) >= R` and Kalmanson on `(0,2,3,7)` gives
  `d(0,7) <= R`, hence `d(0,7) = R` — the same-distance class **propagates**.
  This cascade is exactly what the existing same-distance-clique, `K4-e`
  stretch, vertex-circle, and Kalmanson/Farkas filters already exploit. So the
  `l=3` content is also reachable by the existing exact stack, and does not
  require Aggarwal's intersection-free machinery to be ported.

**Net of (b): the Aggarwal antipodal-cut route, restricted to the safe single
quotient-class scope, transfers only its `l=2` content, which is identical to
the repository's strict-Kalmanson certificate; its genuinely-new `l>=3`
intersection-free-edge content requires a geometric edge-crossing certificate
that the abstract selected-incidence + cyclic-order data cannot supply, and
where it could matter, plain Kalmanson propagation already bites.** The
prototype below treats the intersection-free edge as a separate gate that
defaults to *uncertified*, so it never overclaims an obstruction.

This route also respects the hard convexity constraint: the only kill it would
ever emit comes from **strict** Kalmanson equality-vs-strict-inequality
(hypothesis 1, contiguous separated arcs + strict convexity). It does not fire
on the P24 metric-linear nonconvex control, because that construction's
alternating turn signs mean it has no antipodal cut into two contiguous chains,
and its rows are not one forced ordinary-distance class — so no single-class
cross cut matrix is built. (The prototype operates only on supplied incidence +
cyclic order; the P24 control is not a convex cyclic order and supplies no
antipodal cut, so the checker produces no obstruction for it. The repository's
dedicated control `scripts/verify_p24_metric_linear_nonconvex.py` remains the
authoritative non-convex negative control and is unaffected.)

---

## (c) Prototype checker and frontier run

Code: `scripts/exploration/a5_aggarwal_antipodal_cut.py` (stdlib + `numpy`
imports only via the shared module; cycle search uses `networkx.cycle_basis`;
quotient classes via the repo's exact union-find). `ruff check` passes.

Pipeline (matches the deferred spec's four parts):

1. **Antipodal-cut enumerator.** For the fixed cyclic order `0..8`, enumerate
   every split into two nonempty contiguous arcs (the superset of geometric
   antipodal cuts; the parallel-supporting-line refinement is a strictly
   smaller set, noted as a known over-approximation).
2. **Exact quotient classes.** Reuse the selected-distance union-find. A class
   `Q` is a set of unordered pairs *proved* equal-length by selected-row
   equalities. Only classes of size `>= 2` are tested (singletons cannot host a
   cycle). Raw per-center rows are never used as `Q` (obstruction O1).
3. **Cut matrix + cycle search.** Build the bipartite 1-graph of `M_Q` on
   cross-chain pairs and take `cycle_basis`; a basis cycle of vertex-length
   `2l` is an Aggarwal cycle of length `l`. `l=2` are 2x2 all-ones, `l=3` are
   hexagons.
4. **Output schema.** `EXACT_FIXED_CLASS_CUT_OBSTRUCTION` candidates with cut,
   class, rows/cols, and cycle entries; promotion to an obstruction requires the
   intersection-free-edge gate (default uncertified, so default zero
   obstructions). An explicitly-labelled `--assume-intersection-free` debug mode
   gives the unsafe upper bound.

### Result on the 184 frontier assignments

| quantity | value |
|---|---|
| assignments checked | 184 |
| total candidate Aggarwal cycles (single class, cross-chain) | 9342 |
| cycle-length histogram (`l -> count`) | `{2: 7795, 3: 1547}` |
| assignments with >= 1 candidate cycle | 158 |
| **certified obstructions (safe mode)** | **0** |
| **assignments newly obstructed (safe mode)** | **0** |
| assignments obstructed under unsafe `--assume-intersection-free` | 158 |
| assignments already killed by existing vertex-circle filter | 184 (158 self-edge + 26 strict-cycle) |

Clean structural split (verified):

- The **158** assignments that host Aggarwal candidate cycles are **exactly**
  the `self_edge` assignments. (A vertex-circle self-edge is a degenerate
  same-class cross pattern, so it is unsurprising these coincide.)
- The **26** assignments with **zero** Aggarwal candidate cycles are **exactly**
  the `strict_cycle` assignments. The Aggarwal antipodal-cut route therefore
  **structurally cannot reach** the 26 strict-cycle assignments; only the
  vertex-circle strict-cycle filter does.

**Newly obstructed vs already killed: 0 newly obstructed.** Every assignment the
Aggarwal route could even in principle touch (the 158 self-edge ones) is already
killed by the existing vertex-circle filter, and for those the safe checker
emits no certified obstruction anyway (no intersection-free edge). The 26
strict-cycle assignments are out of Aggarwal's reach entirely.

---

## What was NOT established (honesty ledger)

- **No proof** that the same-distance cross 6-cycle on a genuine antipodal cut
  is impossible. The `l=3` evidence is numerical (zero strict-convex
  separated-arc realizations found) plus a Kalmanson-propagation observation on
  one example; it is not a general theorem. A real proof would either (i) port
  Aggarwal's intersection-free-edge argument with an exact cross-segment
  geometry certificate, or (ii) show the Kalmanson propagation always closes.
- **No verbatim primary-source definitions.** arXiv/ScienceDirect were 403 this
  session; the hypothesis statements rest on the repository's transcription plus
  web-search corroboration and an internal numerical check of the cross-chain
  Kalmanson property. The exact wording of "intersection-free edge" and
  "distance-like" should be re-pinned against the PDF before any paper-style
  use.
- **The cut enumerator is an over-approximation.** It enumerates all contiguous
  bipartitions, a superset of true antipodal (parallel-supporting-line) cuts. A
  tighter geometric antipodal test would only *reduce* the candidate count, so
  it cannot create a missed obstruction; but the candidate counts above are
  upper bounds on the geometric-cut candidate counts.
- **No new bridge** from arbitrary variable-radius counterexamples. As the
  source note already says, this is a fixed quotient-class filter, not a bridge.

---

## Why this negative is still useful

1. It **closes the deferred A5 task** with a precise statement of the exact
   obstruction to transfer (O1 multi-radius, O2 intersection-free-edge), so the
   route will not be re-opened naively.
2. It establishes that the Aggarwal `l=2` content is **provably identical** to
   the existing strict-Kalmanson certificate (same equality-vs-strict
   contradiction), preventing duplicate certificate work.
3. It produces a **clean partition diagnostic** of the 184 frontier: Aggarwal
   candidates ⇔ self-edge (158), no candidates ⇔ strict-cycle (26). This
   sharpens the picture of which frontier kills are "same-distance-cycle"
   shaped versus "nested-chord strict-cycle" shaped.
4. It contributes a reusable, ruff-clean exact single-quotient-class cut filter
   that could become productive at larger `n` where a forced class is large
   enough to host an `l>=3` cycle that Kalmanson does *not* already propagate to
   a contradiction — at which point porting the intersection-free-edge geometry
   would be the next concrete step.

---

## Verify

```bash
# Safe mode: 0 newly obstructed; histogram {2:7795, 3:1547}; 158 host candidates.
python scripts/exploration/a5_aggarwal_antipodal_cut.py

# Unsafe upper bound: 158 assignments (= exactly the self_edge ones).
python scripts/exploration/a5_aggarwal_antipodal_cut.py --assume-intersection-free

# Lint.
ruff check scripts/exploration/a5_aggarwal_antipodal_cut.py
```
