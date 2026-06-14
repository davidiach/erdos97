# A3 — Bridge Lemma A′ (ear-orderability): statement, L7-gauge-repair gap, and the 6 non-ear frontier objects

Lane: **A3 (ear-orderability / rigidity bridge)**.
Date: 2026-06-14. Author: research subagent A3.
Trust label of this note: **`REVIEW_PENDING_DIAGNOSTIC`** (proof-mining; the one
new combinatorial observation in §3.3 is `LEMMA`-grade but does **not** by itself
prove Bridge Lemma A′ or Erdős #97).

## Non-claims (hard constraints)

- No proof of Erdős Problem #97. No counterexample. No claim that Bridge
  Lemma A′ is true or false.
- Bridge Lemma A′ remains **OPEN** (`OPEN_NOT_PROVED_OR_REFUTED`, per
  `data/certificates/bridge_lemma_frontier.json`).
- All stuck-set / closure / digraph computations here are **combinatorial over a
  fixed selected-witness pattern** (the singleton-rich interpretation: one stored
  4-set per center). They are **not** Euclidean-realizability certificates.
- Stored JSON (`bridge_lemma_frontier.json`) is treated as INPUT.
- I did NOT touch lane A4 material (endpoint-control / diameter caps).

---

## 1. Precise statement of Bridge Lemma A′ and the exact definitions used

### 1.1 Setting

Let `P` be a hypothetical strictly convex `k=4` counterexample: a strictly
convex `n`-gon with vertex set `V` in cyclic order, with `M(i) ≥ 4` at every
vertex `i` (every center has ≥4 other vertices on one circle around it). For a
center `y` and radius `r`, `D_y(r) = {z ≠ y : |p_y p_z| = r}`; the **rich row
family** at `y` is `R(y) = { D_y(r) : |D_y(r)| ≥ 4 }`. Distinct classes in
`R(y)` are **disjoint** (a vertex has one distance from `y`). A **selected row**
at `y` is any 4-subset of a class in `R(y)`.

### 1.2 Ear-orderability (two equivalent forms)

**(Form 1 — vertex ordering, §5.2 of `canonical-synthesis.md`.)** A selected
system `{W_i}` (one 4-set per center) is **ear-orderable** if there is an
ordering `(v_1,…,v_n)` with, for every `k ≥ 4`,
`|W_{v_k} ∩ {v_1,…,v_{k-1}}| ≥ 3`. The first three vertices are an unconstrained
base; the "≥3 earlier witnesses" rule is imposed from the 4th vertex onward.

**(Form 2 — bootstrap rank, `bootstrap-core-bridge.md`.)** For `A ⊆ V`, define
the **rich-triple closure** `cl(A)` as the least superset of `A` closed under:
*if `y ∈ V`, `C ∈ R(y)`, and `|C ∩ cl(A)| ≥ 3`, then `y ∈ cl(A)`.* The
**bootstrap rank** is `ρ(P) = min{ |A| : cl(A) = V }`.

**Closure-rank Lemma (proved, repo):** `P` admits an ear-orderable
selected-witness system **iff** `ρ(P) ≤ 3`. (Proof in `bootstrap-core-bridge.md`,
implemented in `src/erdos97/bootstrap_cores.py`; I re-confirmed the equivalence
numerically on all 6 frontier objects below — `forward_ear_exists` agrees with
`ρ ≤ 3` in every case.)

### 1.3 Bridge Lemma A′ (the open statement)

> **Bridge Lemma A′ (OPEN).** Every *realizable* strictly-convex `k=4`
> counterexample `P` admits **some** ear-orderable selected-witness system;
> equivalently `ρ(P) ≤ 3`; equivalently the Key Peeling property holds: for
> every `S ⊆ V` with `|S| ≥ 4` there is `v ∈ S` and `C ∈ R(v)` with
> `|C ∩ (S\{v})| ≥ 3`.

**Why A′ would finish #97 (and what it does NOT do alone).** Combined with two
*proved* facts it gives a contradiction, hence #97:

- **Ear-rank theorem (proved, mod L7-gauge repair; §2 below).** If `W` is
  ear-orderable and `p` is in general position, then `rank R_W(p) = 2n − 3`.
- **L10 (proved).** At any solution `F_W(p) = 0`, Euler homogeneity puts the
  scaling vector `p ∈ ker R_W(p)`; with the 3-dim translation+rotation kernel,
  `rank R_W(p) ≤ 2n − 4`.

A′ supplies an ear-orderable selection *at a hypothetical solution*; the two
ranks `2n−3` vs `≤ 2n−4` then collide. **A′ is necessary but not sufficient on
its own**: without A′, an unordered/stuck selection evades the ear-rank theorem,
and a non-generic solution evades the generic-rank computation (`§6.7`,
`failed-ideas.md #9`). A′ is the combinatorial half; the ear-rank theorem is the
algebraic half (still carrying the L7-gauge gap).

### 1.4 Strict convexity is essential and *is used*

The only proved leverage against "stuck sets" is geometric and uses strict
convexity at two points:

- **L5 / perpendicular-bisector bound (uses strict convexity, L4):** an outside
  pair `{a,b}` is shared by ≤2 centers, because the bisector line meets a
  strictly convex boundary in ≤2 vertices. This is the engine of the
  private-halo capacity ledger (`bootstrap-core-bridge.md`).
- **The negative control `p24` (`failed-ideas.md #16`)** is a non-convex
  24-point configuration satisfying every selected metric/rank/row-linearity
  condition. Therefore **any** route to A′ (or to its rank consequence) that
  does not invoke strict convexity, cyclic-order signs, or one-sidedness must
  fail on `p24`. The whole bridge program respects this.

---

## 2. The L7-gauge-repair gap (canonical-synthesis §5.2 / §6.5)

This is the precise localization requested. It is a gap in the **algebraic half**
(ear-rank theorem), *adjacent* to A′ but logically separate from it.

### 2.1 What the gap is

The original ear-elimination argument inducts along an ear order and, at each
step, wants to "fix the unique infinitesimal Euclidean motion `ṗ^rig` agreeing
with the velocity `ṗ` on three noncollinear vertices `v_1,v_2,v_3`"
(§6.5). **The flaw:** infinitesimal Euclidean motions have only 3 d.o.f.
(`t ∈ ℝ²`, `ω ∈ ℝ`), but prescribing the velocity on 3 vertices is 6 scalar
conditions. A matching rigid motion need not exist, so the inductive base for
`rank R_W = 2n − 3` is not actually established by that step.

### 2.2 The two repair routes (per §6.5) and which combinatorial step is missing

- **Route A — gauge fixing (L7-based).** Impose only **3** scalar gauge
  conditions (e.g. `ṗ'_{v_1} = 0` plus one rotation gauge at `v_2`), matching the
  3 d.o.f. The **missing step** is then a re-checked induction: each newly added
  ear vertex `v_k` contributes one equidistance row pair whose 2×2 block (in the
  two coordinates of `v_k`) must be shown nonsingular *given the gauge and the
  three earlier witnesses*. The nonsingularity uses **L7 (chord-length
  monotonicity on the `<π` witness span)** to guarantee the two bisector
  directions at `v_k` are independent. The repo states this "needs the induction
  re-checked" but the re-checked induction is **not written out**.

- **Route B — explicit minor (described as cleaner).** Construct a
  `(2n−3) × (2n−3)` minor of `R_W(p)` with provably nonzero determinant, indexed
  directly by the ear order (3 gauge columns removed; each non-base vertex
  contributes a 2×2 diagonal block from its incoming ear edge). **The missing
  combinatorial step is exactly:** *exhibit the row/column selection from the ear
  order that makes the matrix block-triangular with nonsingular 2×2 diagonal
  blocks, and prove each block nonsingular via the L7 angular-gap inequality.*

### 2.3 Status (verbatim from the reconciliation log, lines 1053, 1091)

> "The L7-based gauge-fixing repair … is described as 'the better repair' in
> source notes but a **fully written proof using Route B (explicit minor) is not
> in the archive.** The rank theorem is therefore **conditional on this repair
> being executed.**"

So the gauge gap is **a finite, writable linear-algebra task**, not a deep
obstruction. The cleanest closure is Route B: an explicit ear-indexed minor with
nonsingular 2×2 blocks, each justified by L7. This is the single most
self-contained sub-target in the entire ear program and is **independent of the
6 frontier objects** — it would upgrade the ear-rank theorem from "conditional"
to "unconditional", after which **only** Bridge Lemma A′ (the combinatorial half)
remains between the program and #97.

**Caveat I must flag:** even with Route B fully written, the rank theorem is
*generic* (`rank = 2n−3` at general-position `p`). It does not by itself preclude
a non-generic solution (`failed-ideas.md #9`); the contradiction needs L10 *and*
A′ supplying an ear order at the solution. The gauge repair closes one of the
*three* ingredients, not the whole route.

---

## 3. The 6 non-ear frontier objects: structure and what they reveal

Source: `data/certificates/bridge_lemma_frontier.json` (treated as INPUT). The 6
objects are the only non-ear members of the finite frontier: **n=8 survivor
classes 0,1,2,3** and **n=9 assignments 81,151**.

Reproduce my analysis:
```bash
python scripts/exploration/a3_ear_orderability_frontier.py
```
(Confirm the input artifact: `python scripts/check_bridge_lemma_frontier.py --check --assert-expected --json`, exit 0.)

### 3.1 Independent re-confirmation (all 6)

For every object I recomputed both ear-orderability forms from the stored rows:

| object | n | circulant? | forward-ear exists | ρ (singleton-rich) | max 3-seed closure | exact obstruction (stored) |
|---|---:|---|---|---:|---:|---|
| n8-class-0 | 8 | no | False | 4 | **5** | `pb_y2_span` |
| n8-class-1 | 8 | no | False | 4 | **5** | `pb_y2_span` |
| n8-class-2 | 8 | no | False | 4 | **5** | `pb_y2_span` |
| n8-class-3 | 8 | no | False | 4 | **5** | `class3_duplicate_vertex` |
| n9-asg-81 | 9 | **yes** `{1,3,6,7}` | False | 4 | **5** | `vertex_circle_strict_cycle` (review-pending) |
| n9-asg-151 | 9 | **yes** `{2,3,6,8}` | False | 4 | **5** | `vertex_circle_strict_cycle` (review-pending) |

All six are confirmed non-ear (`ρ = 4 > 3`), agreeing with the stored data.

### 3.2 The sharp quantitative obstruction: **closure always stalls at exactly 5**

The decisive structural fact (new, clean, `LEMMA`-grade for these fixed objects):
**for every one of the 6 objects, the rich-triple closure of any 3-vertex seed
has size ≤ 5, and the maximum 5 is attained.** Closure-size histograms over all
`C(n,3)` seeds:

- n8-class-0: `{3: 24, 4: 8, 5: 24}` — best seed `(0,1,6) → {0,1,2,3,6}`.
- n9-81: `{3: 48, 4: 18, 5: 18}` — best seed `(0,1,4) → {0,1,3,4,6}`.
- n9-151: `{3: 48, 4: 18, 5: 18}` — best seed `(0,1,6)`.

So at n=8, **3 vertices are always unreachable**; at n=9, **4 vertices are always
unreachable**. The obstruction is not a single "bad triple" — it is uniform: no
3-seed escapes the size-5 ceiling. Equivalently, *every* 4-subset is contained in
a stuck set (minimal stuck sets: 44, 44, 44, 46, 99, 99 respectively, all of
**size 4**).

### 3.3 These are 4-out-regular digraphs with internal-outdegree-≤2 stuck sets

Confirming the §5.2 "this isn't combinatorial" mechanism concretely. Each object
is a 4-out-regular digraph (`i → w` for each selected witness `w ∈ W_i`). A
size-4 stuck set has every internal vertex with **internal out-degree ≤ 2**
(never the 3 needed to peel). Example (n9-81, stuck set `{0,1,2,3}`):

```
center 0: internal {1,3} (2)  outside {6,7}
center 1: internal {2}   (1)  outside {4,7,8}
center 2: internal {0,3} (2)  outside {5,8}
center 3: internal {0,1} (2)  outside {4,6}
```

n=8 stuck sets are **not** strongly connected (a "sink" vertex with 0 internal
witnesses, e.g. center 7 in `{0,1,2,7}`); n=9 stuck sets **are** strongly
connected. This matches the obstruction split in §3.4: n=8 classes die to an
algebraic `pb_y2_span`/duplicate-vertex obstruction; n=9 die to a *cyclic*
strict-cycle obstruction (`n9-vertex-circle-strict-cycle-criterion.md`),
consistent with the strongly-connected internal cycle.

### 3.4 What the objects reveal about whether A′ can hold

**The objects are evidence *for*, not against, A′ — because every one of them is
geometrically dead.** Crucially, none of these 6 non-ear patterns is a known
realizable polygon; each is killed by an exact (or review-pending exact)
obstruction in the repo:

- n=8 classes 0,1,2 → `pb_y2_span` (y₂ in the rational PB-polynomial span);
  class 3 → Gröbner forces a duplicate vertex. (Exact.)
- n=9 81,151 → directed strict-cycle among real distances
  `D(p_0) > D(p_1) > … > D(p_0)` (review-pending exact).

This is the same pattern as the **n=7 evidence (§8.6)**: the 6 cyclic n=7 starter
sets that are non-ear all have least-squares residual ≥ 0.6 — i.e. they are *not*
realizable. So across n=7, n=8, n=9 the empirical statement is:

> **Every** non-ear selected pattern examined so far is non-realizable
> (residual-bounded-away or exactly obstructed).

That is exactly what A′ predicts (contrapositive: realizable ⟹ ear-orderable).
**Nothing in the 6 objects contradicts A′; they are corroborating dead ends.**
The objects do *not*, however, prove A′: they are a finite frontier, and the
review-pending n=9 obstruction is not independently re-reviewed here.

### 3.5 Which extra hypothesis would force ear-orderability? — three tests

I tested three candidate strengthenings. Results are **honest and mixed**, and
they sharply separate the two families.

**(H1) Richness via the circulant orbit (n=9 only).** Allow every center the
full rotational orbit of the base row as alternative rich classes (an
*over-generous* relaxation: it ignores that distinct classes must be disjoint, so
it only *adds* generating power). Result: for **n=9 81 and 151 this drops
ρ to ≤ 3** (seed `[0,1,4]`); for n=8 it is inapplicable (not circulant).

> **Interpretation / caveat (important).** The H1 "yes" for n=9 is **not**
> geometric evidence that A′ holds, because the extra orbit classes are
> *fictitious*: under the genuine *stored* (singleton) family the same seed
> `[0,1,4]` reaches only `{0,1,3,4,6}` (size 5). A realizable circulant
> counterexample is **not** guaranteed to have additional size-≥4 distance
> classes at each center. So H1 only shows *"if a center had a second rich class
> from the rotation orbit, ear-orderability would follow"* — it converts the
> bridge into the sub-question of §4.

**(H2) One extra disjoint rich class per center (over-generous union).** Allow
each center, additionally, *every* disjoint 4-subset of the remaining vertices as
a candidate class (again over-generous). Result: **n=9 81,151 → ρ ≤ 3**; **n=8
0,1,2,3 → ρ still > 3** even with this maximal relaxation. So the n=8 classes are
*robustly* non-ear: no enrichment of rich classes (short of the geometrically
impossible) rescues them — consistent with their hard algebraic death. The n=9
circulants are non-ear *only because* the stored singleton family is artificially
sparse.

**(H3) Convex-order / cyclic-arc seeds.** Restrict generating seeds to cyclic
*intervals* (arcs) of length ≤3 (the natural "convex-order" base). Result:
**no cyclic arc generates for any of the 6 objects.** Best arcs reach only size
3–5. So "use a convex-order base" is the **wrong** strengthening — it *weakens*
generation. Convex order alone does **not** force ear-orderability.

**Summary of the hypothesis tests.**

| hypothesis | n=8 classes 0–3 | n=9 81,151 | verdict |
|---|---|---|---|
| H1 orbit-richness (over-generous) | n/a | ρ→≤3 | helps n=9 *only via fictitious classes* |
| H2 extra disjoint class (over-generous) | ρ>3 (robust) | ρ→≤3 | n=8 robustly non-ear; n=9 sparse-only |
| H3 convex-arc seed | fails | fails | convex order alone does **not** force ears |

**The forcing hypothesis that survives:** *not* convex-order, *not* minimality
(untestable on fixed singleton rows — minimality is a global property and the
fragile-cover route, `minimal-fragile-cover-bridge.md`, is a separate proved
foothold). What the data points to is a **rich-class availability** hypothesis:

> **Candidate extra hypothesis (RICH).** In a realizable strictly-convex
> counterexample, the genuine rich families `R(y)` are rich enough that the
> rich-triple closure of *some* 3-seed reaches all of `V`.

The n=9 H1/H2 results say RICH would *suffice* there; the n=8 H2 result says RICH
is *false as stated* for the stored n=8 singleton families (their closure stalls
even with every disjoint class added), so for n=8 the death is genuinely
algebraic (`pb_y2_span`), not a richness deficit. This is the key dichotomy:
**n=8 non-ear = hard algebraic obstruction; n=9 non-ear = sparse-singleton
artifact that genuine richness would dissolve.**

---

## 4. The smallest decisive sub-question

The frontier sharply localizes A′ to one question, with a concrete shape:

> **Decisive sub-question (A′-RICH).** Does every *realizable* strictly-convex
> `k=4` counterexample have, at the centers of a stuck set, enough genuine
> size-≥4 distance classes (rich classes) that the rich-triple closure of some
> 3-seed reaches `V`? Equivalently: can a realizable counterexample have
> bootstrap rank `ρ > 3` under its **true** rich families `R(y)` (not the sparse
> singleton family)?

This is strictly sharper than "prove A′": it isolates the **noncanonical-selection
gap** that `adaptive-radius-blocker-bridge.md` already named. The adaptive fork
proves: *non-ear ⟹ the counterexample contains a radius-blocker `U`* (every
`y ∈ U`, every `C ∈ R(y)` has `|C ∩ U| ≤ 2`), with `|U| ≤ |O|(|O|−1)`. The
bootstrap refinement (`bootstrap-core-bridge.md`) adds the **weighted cyclic
private-pair capacity ledger** (uses strict convexity via L5):
`Σ_{u∈U} Σ_{C∈R(u)} C(|C∩D_u|, 2) ≤ 2·C(|O|,2) − Σ_i C(o_i,2)`.

**What the 6 objects say about closing it (per `bootstrap-core-crosswalk.md` and
`bootstrap-vertex-circle-overlay.md`):** the two tight n=9 cases have bootstrap
core `[0,1,2,4]` with private-pair capacity **margins 8 and 6** — the smallest in
the whole crosswalk — yet the ledger **does not kill them**. Both land on the
`T12/F16` strict-cycle template, but the strict-cycle local rows are **not
contained in the bootstrap core** (for 151 even the strict-edge rows are
outside). So:

> **Concrete next experiment (highest leverage).** Prove the implication
> `bootstrap core [0,1,2,4] + small private-halo margin ⟹ a T12-like six-row
> strict-cycle core is forced`. This is the missing link that would let the
> *already-proved* strict-cycle criterion fire from bootstrap structure, turning
> the radius-blocker into a contradiction for these two cases. The blocker is
> that the strict-cycle's connector/strict rows live *outside* the core, so a
> genuine **rich-class forcing** step (not fixed-row bookkeeping) is needed to
> make those rows available — exactly Contract A/C of
> `lemma-driven-bridge-targets.md`.

If instead one wants a clean *sub-case proof*: the **n=8 family is already
fully closed** by exact obstructions (`pb_y2_span`, duplicate-vertex), so the
honest statement is **"Bridge Lemma A′ holds for n ≤ 8 in the repo-local
machine-checked sense"** (every non-ear n=8 survivor is non-realizable), and the
*first open n* is n=9, gated entirely on independently reviewing the
strict-cycle vertex-circle checker.

---

## 5. What I did NOT establish

- I did **not** prove or refute Bridge Lemma A′, nor any new geometric/realizability
  fact. Everything in §3 is fixed-pattern combinatorics over stored INPUT.
- I did **not** independently re-review the **review-pending** n=9 vertex-circle
  strict-cycle checker; the n=9 objects' "killed" status is inherited, not
  re-derived. (This is the live blocker for n=9.)
- I did **not** write out the **Route B explicit minor** (the L7-gauge repair). I
  localized it precisely (§2) but executing it is a separate linear-algebra task.
- The H1/H2 "ρ→≤3 for n=9" results are **over-generous relaxations** (they ignore
  rich-class disjointness and assume fictitious extra classes). They are *not*
  evidence A′ holds; they convert A′ into the rich-class-availability
  sub-question §4. I flagged this caveat at each use.
- I did **not** touch lane A4 (endpoint-control, diameter caps).

---

## 6. Artifacts and reproduction

- Analysis script: `scripts/exploration/a3_ear_orderability_frontier.py`
  (combinatorial; uses `networkx`, `src/erdos97/bootstrap_cores.py`,
  `src/erdos97/stuck_sets.py`).
  ```bash
  python scripts/exploration/a3_ear_orderability_frontier.py
  ```
- Input artifact check (exit 0):
  ```bash
  python scripts/check_bridge_lemma_frontier.py --check --assert-expected --json
  ```
- Supporting docs read: `bridge-lemma-frontier.md`, `canonical-synthesis.md`
  (§5.2, §6.5, reconciliation log), `bootstrap-core-bridge.md`,
  `adaptive-radius-blocker-bridge.md`, `minimal-fragile-cover-bridge.md`,
  `n9-vertex-circle-strict-cycle-criterion.md`, `bootstrap-core-crosswalk.md`,
  `bootstrap-vertex-circle-overlay.md`, `lemma-driven-bridge-targets.md`,
  `failed-ideas.md` (#2,#3,#5,#9,#16).
