# Claims ledger

This file is proof-facing. Numerical near-misses live in `data/runs/` and in the
candidate/failed-route docs, not as proofs of equality.

## Theorems

### No selected-witness counterexample for n <= 8

For `n=5`, every selected witness set is `V \ {i}`. Two distinct rows
therefore share three vertices, contradicting the two-circle cap below.[^small]

For `n=6`, write `S_i = V \ {i, f(i)}`. Then `S_i` and `S_{f(i)}` share at
least three vertices, again contradicting the two-circle cap.[^small]

For `n=7`, the incidence count saturates. Every selected indegree is 4, every
pair of rows intersects in exactly two points, and the common-witness map is a
permutation of the 21 unordered chords. Perpendicularity along the cycles of
that permutation forces all cycles to be even, impossible for 21 objects.[^small]

The current repository also keeps the finite Fano enumeration as a reproducible
check of the `n=7` equality case: `scripts/enumerate_n7_fano.py` enumerates 30
labelled Fano planes and 720 pointed complement families, then quotients them
to 54 cyclic-dihedral classes. Every class has common-witness chord-cycle type
`7+7+7`, so every class contains odd perpendicularity cycles. See
`docs/n7-fano-enumeration.md`.

For `n=8`, the column-pair cap below forces every witness indegree to equal 4.
The checked incidence enumerator then exhausts all selected-witness systems
under the necessary incidence and forced-perpendicularity filters, obtaining 15
canonical survivor classes. The exact obstruction checker kills all 15 by
cyclic-order noncrossing, perpendicular-bisector algebra, equal-distance
algebra, duplicate vertices, collinearity, or strict-convexity failure. See
`docs/n8-incidence-enumeration.md` and `docs/n8-exact-survivors.md`.

## Lemmas

### Circle-intersection cap

In any selected-witness counterexample, for distinct centers `a,b`,

```text
|S_a cap S_b| <= 2.
```

Otherwise two distinct Euclidean circles would share at least three points.[^small]

### Radical-axis perpendicularity

If `S_i cap S_j = {a,b}`, then `p_i p_j` is perpendicular to `p_a p_b`.
Both centers lie on the perpendicular bisector of the common chord.[^small]

### Incidence counting lower bound

Let `d_j = #{i : j in S_i}`. Then `sum_j d_j = 4n`, and the cap gives

```text
sum_j binom(d_j,2) <= 2 binom(n,2).
```

Convexity of `binom(d,2)` with average indegree 4 gives
`sum_j binom(d_j,2) >= 6n`, so any selected-witness counterexample has
`n >= 7`.[^repo]

### Pair and triple sharing

For an unordered pair `{a,b}`, at most two polygon vertices `x` satisfy
`|x-a| = |x-b|`: the locus is one perpendicular-bisector line, and a line
meets a strictly convex polygon boundary in at most two vertices.[^digest]

Any noncollinear triple of vertices can appear together in at most one selected
witness set, because three noncollinear points have a unique circumcenter.[^digest]

### n=8 witness indegree regularity

For `n=8`, the pair-sharing cap forces every witness indegree to equal 4. If a
fixed vertex `v` occurs in `d` selected witness rows, those occurrences contain
`3d` pairs `{v,a}`. There are 7 possible partners `a`, and each pair can occur
in at most two rows, so `3d <= 14` and `d <= 4`. Since the total indegree is
`4n = 32`, all 8 indegrees are exactly 4.

### Vertex cone and chord order

At a vertex of a strictly convex polygon, all other vertices lie in the open
cone between the two incident edges. Boundary order therefore agrees with
angular order around that vertex.[^digest]

For witnesses on a circle centered at that vertex, chord length is
`2r sin(theta/2)` and is monotone while the angular separation is below `pi`.
This supports endpoint and short-base reductions, but those reductions still
need their global bridge claims.[^digest]

### Cyclic polygon subcase

If all vertices lie on one circle, then no vertex has more than two other
vertices at any one distance. A second circle centered at the vertex intersects
the common circumcircle in at most two points.[^syn]

### Paraboloid lift

Lifting `p=(x,y)` to `(x,y,x^2+y^2)`, four vertices are equidistant from
`p_i` exactly when their lifts are coplanar in a plane parallel to the tangent
plane at the lift of `p_i`.[^syn]

### Algebraic witness equations

The equation

```text
|p_i-p_a|^2 = |p_i-p_b|^2
```

is affine-linear in the center coordinates `p_i` and quadratic overall. If
`a,b,c` are noncollinear and `p_i` is equidistant from them, then `p_i` is the
circumcenter of triangle `abc`; the fourth witness condition says the fourth
point lies on the same circle.[^alg]

### Jacobian kernels

For the selected squared-distance constraint map, translations and rotation are
always in the Jacobian kernel.[^paper]

At an exact solution, homogeneity adds the scaling direction:
`R_W(p) p = 2F_W(p) = 0`. Thus a nondegenerate solution has
`rank R_W(p) <= 2n - 4`. Generic rank `2n-3` at non-solutions is a diagnostic,
not a proof of nonexistence.[^rank]

### Semicircle correction

A witness set from a hull vertex may lie inside a semicircle of its witness
circle. The center of the circle therefore need not lie inside the convex hull
of the witnesses.[^alg]

## Conjectures / Conditional Programs

### Ear-orderable bridge

If every realizable `k=4` counterexample admitted an ear-orderable selected
witness pattern, the rank/scaling contradiction would rule it out. The bridge
or key-peeling lemma is open.[^rank]

### Endpoint descent

The Lemma 12 endpoint-descent route would work if at least one endpoint of a
minimal bad circle satisfied the required outside-of-`A` endpoint-control
claim. That auxiliary claim is open.[^syn]

### Critical centered 4-ties

A corrected global-counting program would prove the problem if every bad
vertex forced a low-rank, 3-critical centered 4-tie and strictly convex
`n`-gons had fewer than `n` such ties. Both ingredients are conjectural.[^alg]

### Noncrossing chord selection

A canonical short-base chord rule might assign distinct noncrossing chords to
bad vertices, but the needed injectivity statement is not proved.[^syn]

### Three-cap bridge

The two-point smallest-enclosing-circle case is controlled by known cap
arguments. The three-support case remains open and would need a bridge lemma
forcing enough witnesses into opposite caps.[^syn]

[^small]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/02_SMALL_CASES_N5_N6_N7.md`.
[^repo]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/16_repo_handoff_and_claim_taxonomy.md`.
[^digest]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/01_USEFUL_FINDINGS_DIGEST.md`.
[^syn]: Source file: `erd archive/outputs/erdos97_synthesis.md`.
[^alg]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/04_algebraic_and_semicircle_corrections.md`.
[^paper]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/source_notes/05_rank_scaling_and_verifier_review.md`.
[^rank]: Source file: `erd archive/outputs/useful_research_findings.zip::useful_research_findings/generated_summaries/03_RANK_AND_BRIDGE_STATUS.md`.
