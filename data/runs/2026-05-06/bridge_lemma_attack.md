# Bridge Lemma A' Attack: 2026-05-06

**Status.** No general proof of Erdős #97 produced. No proof of Bridge Lemma A'
produced. We give a finer combinatorial/geometric characterization of the
stuck-set obstruction and identify a new geometric handle on the 2 non-ear
n = 9 circulants. Trust labels follow `STATE.md`.

## 1. Analysis of the 2 non-ear n = 9 patterns (`MACHINE_CHECKED_FACT`)

Both are circulants on Z/9 with 4-element offset multiset:
- **idx = 81:** offsets `{+1, +3, −2, −3}`.
- **idx = 151:** offsets `{+2, +3, −1, −3}` (image of idx = 81 under `v ↦ −v`).

### 1.1 Common combinatorial substructure

For *both* circulants the following structural facts hold (script:
`data/runs/2026-05-06/equilateral_triangle_obstruction.py`):

- **3 all-mutual triangles**: `{0,3,6}`, `{1,4,7}`, `{2,5,8}` — exactly the
  cosets of the subgroup `⟨3⟩ ⊂ Z/9`. In each triangle every vertex is a
  selected witness of the other two. This is forced by the offset `±3 ∈ S`.
- **9 K₄-bicycle stuck cores** (size-4 stuck sets where every center has
  internal selected witness count exactly 2). These cores form a single
  cyclic-shift orbit; representative `S = {0, 1, 4, 7}`. Each core contains
  exactly one of the 3 all-mutual triangles plus one extra vertex.
- **126 stuck sets total**, 99 of size 4, 27 of size 5 (script:
  `circulant_structure.py`).

### 1.2 Vertex-circle (UF/strict-cycle) trace (`MACHINE_CHECKED_FACT`)

Both patterns are killed by `strict_cycle`, not `self_edge`. The chord-pair
union-find under selected-row equalities collapses the 36 unordered pairs
into:
- **3 size-9 chord-length classes** with diff-multiset `{1: 3, 2: 3, 3: 3}`
  each (i.e. each large class contains 3 chords of each unsigned cyclic
  offset 1, 2, 3).
- **9 singletons**, all of cyclic offset 4.

The 3 large classes form a directed 3-cycle in the strict-nested-chord graph
(a strict-monotone cycle), forcing the chord-length class to satisfy
`|c_A| < |c_B| < |c_C| < |c_A|` after the UF identification — geometrically
impossible. Trace: `vertex_circle_trace.py`.

### 1.3 Forced-equilateral observation (`EVIDENCE`)

Each all-mutual triangle (3 vertices each pair-wise selected by the others)
forces the three sides equal to a common selected radius `R`, hence the
triangle is **equilateral with side `R`** (proved via two-line argument: if
`b, c ∈ row[a]` then `r_a = ‖a−b‖ = ‖a−c‖`; if also `a, c ∈ row[b]` then
`r_b = ‖a−b‖ = ‖b−c‖`; combining over all 3 sides gives all three sides
equal). Hence both circulants force 3 disjoint equilateral triangles
`{0,3,6}, {1,4,7}, {2,5,8}` in the realized 9-gon.

Direct numerical search (`three_equilateral_obstruction.py`, gradient
descent, 100 trials) shows that 3 such equilateral triangles inscribed
in a strictly convex 9-gon **are realizable** (Star-of-David-like
configurations, residual `5e-13`). Hence the equilateral-triangle
obstruction *alone* does not rule out idx=81/151. The vertex-circle
strict-cycle obstruction is genuinely more restrictive.

## 2. Stuck-set characterization (`MACHINE_CHECKED_FACT`)

### 2.1 K₄-bicycle stuck cores
A "K₄-bicycle stuck core" is a size-4 stuck set `S` where every center has
exactly 2 internal selected witnesses (max possible for a stuck set). The
induced selected-edge graph in `S` is then 2-regular, i.e. a 4-cycle (or
two disjoint edges with multiplicity).

### 2.2 K₄-bicycle ↔ non-ear is **false** (`COUNTEREXAMPLE`)

Across the 184 + 15 known patterns:
- All 4 non-ear n=8 patterns (ids 0–3) have ≥ 0 K₄-bicycle cores: id=0 has 6, id=2 has 0.
- 11/11 ear-orderable n=8 patterns have ≥ 2 K₄-bicycle cores each.
- 156 / 184 of the n=9 patterns have at least one K₄-bicycle core but ARE ear-orderable.

So *existence* of K₄-bicycles is not equivalent to non-ear. What is special
to the 2 non-ear circulants is that **all 9 K₄-bicycle cores share the
same 3 forced equilateral triangles** (a coordinated "global" obstruction)
plus the **3-class collapse + 3-cycle** in the chord-length quotient.

### 2.3 Cross-boundary L5 budget (`MACHINE_CHECKED_FACT`)

For minimal stuck `S` (size 4), with each center having ≤ 2 internal
witnesses (so ≥ 2 outside witnesses), the cross-boundary count is:
  `LHS = sum_{v∈S} C(out_v, 2) ≤ 2 · C(|V\S|, 2) = RHS` (L5).
At n = 9 with |S| = 4, RHS = 2·C(5,2) = 20. Maximal LHS = 4·C(2,2)=... = 24,
attainable when every center has exactly 2 outside witnesses (LHS = 4 ones
counted, but for outside *pair* incidences). Empirically idx=81 cores show
LHS ∈ {6, 8, 10}, far below 20. So **L5 alone is loose by a factor ~2**
on K₄-bicycle stuck cores.

## 3. Attack on Bridge Lemma A'

### 3.1 What I tried and what works

- **Conjecture: non-ear ⟺ K₄-bicycle stuck core.** Direction `⇐` fails
  (n=9, 156 counterexamples). Direction `⇒` (non-ear ⇒ K₄-bicycle core)
  also fails: n=8 id=2 is non-ear with 0 K₄-bicycle cores. So neither
  direction gives a structural simplification.

- **Cross-boundary double count:** L5 budget gives only LHS ≤ 2·C(n−|S|,2),
  which is far from tight for K₄-bicycle cores. Adding the all-mutual-
  triangle equality structure does not produce extra inequalities since
  outside witnesses are unconstrained on equilateral triangles. (`PARTIAL_GAP`)

- **Cyclic-order forced equilateral triangles ⇒ obstruction:** False in
  general (`COUNTEREXAMPLE`). 3 equilateral triangles in cosets of `⟨3⟩`
  ARE realizable as Star-of-David-like 9-gons.

- **Chord-class collapse + strict-cycle obstruction:** This is exactly
  what the vertex-circle filter detects, and it kills both circulants.
  But this is a known filter; we have not yet abstracted it into a more
  general "every non-ear realizable pattern is killed by chord-class
  collapse" theorem.

### 3.2 Precise gap (`OPEN`)

Bridge Lemma A' attack reduces to:

> **Conjecture (Bridge Lemma A' refinement).** If a 4-regular witness pattern
> `W` has a K₄-bicycle stuck core whose induced 4-cycle `v₁ → v₂ → v₃ → v₄
> → v₁` of bidirectional edges has length ≥ 3, then `W` is geometrically
> unrealizable as a strictly-convex `k=4` counterexample.

A 4-cycle of bidirectional edges forces 4 selected radii equal, hence
4 equal-sided distances around `S`. Combined with concyclicity at each
center (4 selected witnesses on a row circle), the resulting system is
**probably** overdetermined for `n ≥ 9`. *We did not produce a closed
proof of this.* The vertex-circle filter handles 3-cycle collapses
already; whether the 4-cycle case is qualitatively easier or harder is
unresolved.

### 3.3 Honest assessment

We did **not** prove Bridge Lemma A'. We did:
- Identify the precise structural reason the 2 non-ear n=9 patterns are
  killed: a 3-class chord-length collapse forming a strict 3-cycle (the
  vertex-circle obstruction) is induced by 3 disjoint forced equilateral
  triangles together with offset-4 separator chords.
- Show that ear-orderability **is not** characterized by absence of K₄-bicycle
  stuck cores, ruling out one tempting purely combinatorial bridge.

## 4. New geometric obstruction targeting non-ear patterns (`EXACTIFICATION`)

**Observation (forced equilateral triangle).** For *any* witness pattern at
*any* `n`, an all-mutual triangle `{a, b, c}` (each pair-wise in the
other's selected row) forces the triangle to be equilateral with side
`r_a = r_b = r_c`. This is a **necessary** consequence of selected
witnesses (proof: 2 lines, §1.3 above).

**Filter F-EQTRI (proposed).** For a candidate selected-witness pattern, list
all all-mutual triangles. Each forces a triple (a, b, c) of polygon vertices
into an equilateral triangle with one specific selected-radius value. If
the union of these constraints on the 2n-3-dimensional polygon moduli space
is overdetermined or inconsistent (e.g. forced concentric equilateral
triangles violate strict convexity), the pattern is unrealizable.

**Open question:** Does F-EQTRI catch any pattern not already killed by
vertex-circle / perp-bisector / Gröbner? A short numerical experiment
(§1.3) shows F-EQTRI alone cannot kill the n=9 non-ear circulants. But
combined with the cyclic order, it might be strictly stronger on patterns
with multiple all-mutual triangles in interlocking cyclic positions; this
is not implemented.

## 5. Computational artifacts

- `data/runs/2026-05-06/bridge_lemma_attack.py` — pattern enumeration,
  ear-orderability and stuck-set classification across n=8, n=9.
- `data/runs/2026-05-06/circulant_structure.py` — K₄-bicycle and stuck-set
  size distribution for the 2 non-ear circulants.
- `data/runs/2026-05-06/vertex_circle_trace.py` — UF chord-class and
  strict-cycle trace.
- `data/runs/2026-05-06/connection_analysis.py` — mapping K₄-bicycle cores
  to UF chord classes.
- `data/runs/2026-05-06/equilateral_triangle_obstruction.py` — all-mutual
  triangle search, presence in ear-orderable patterns.
- `data/runs/2026-05-06/three_equilateral_obstruction.py` — numerical
  realizability check for 3 disjoint equilateral triangles in convex 9-gon
  (realizable, residual ≈ 1e-13).
- `data/runs/2026-05-06/bridge_attack_main.py` — falsification of
  "non-ear ⟺ K₄-bicycle" conjecture.
- `data/runs/2026-05-06/bridge_lemma_attack_data.json` — JSON output of
  pattern-level analysis.

## 6. Trust-level summary

- `MACHINE_CHECKED_FACT`: §1.1 substructure of 2 non-ear circulants;
  §1.2 vertex-circle UF trace; §2.1, §2.3 stuck-set numerics;
  §2.2 disprove of K₄-bicycle ⟺ non-ear conjecture.
- `EVIDENCE`: §1.3 forced-equilateral lemma (proof on paper, not formalized).
- `EXACTIFICATION`: §4 F-EQTRI filter (proposed but not implemented;
  alone insufficient to kill the n=9 circulants).
- `OPEN`: Bridge Lemma A' itself; the conjectural refinement in §3.2.
- `FAILED_APPROACH`: K₄-bicycle ↔ non-ear, 3-equilateral-only obstruction.

No general proof or counterexample to Erdős #97 is claimed. This memo is
review-pending and does not update the FALSIFIABLE/OPEN status.
