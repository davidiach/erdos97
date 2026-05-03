# Claims ledger

This file is proof-facing. Numerical near-misses live in `data/runs/` and in the
candidate/failed-route docs, not as proofs of equality.

## Proof-facing claims

This ledger records local proof-facing claims and their current trust posture.
It is not a paper-style theorem list. In particular, the `n <= 8`
selected-witness result is a repo-local machine-checked finite-case artifact
pending independent review, and the global Erdos #97 problem remains
falsifiable/open.

### No selected-witness counterexample for n <= 8

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT` in the repo-local sense;
independent review is required before paper-style or public theorem-style
claims.

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

The crossing/bisection lemma below gives a shorter independent exclusion of
`n <= 7`. The repo still keeps the Fano enumeration because it is structurally
useful and reproducible.

For `n=8`, the sharpened count saturates: all witness indegrees equal 4,
adjacent row-pairs meet in exactly one selected witness, and nonadjacent
row-pairs meet in exactly two. The checked incidence enumerator then exhausts
all selected-witness systems under the necessary incidence and
forced-perpendicularity filters, obtaining 15 canonical survivor classes. The
exact obstruction checker kills all 15 by cyclic-order noncrossing,
perpendicular-bisector algebra, equal-distance algebra, duplicate vertices,
collinearity, or strict-convexity failure. These are machine-checked
repo-local artifacts, not standalone public proof certificates. See
`docs/n8-incidence-enumeration.md` and `docs/n8-exact-survivors.md`.

### Proof-note draft: geometric no-go for n <= 8

A separate proof-note draft in `docs/n8-geometric-proof.md` gives a compact
human-readable obstruction for bad convex polygons with `n <= 8`. It uses a
base-apex lemma to count isosceles triangles and then analyzes the equality
case for octagons. Independent review is still requested before promoting this
note beyond the repository's local proof-facing ledger.

### Altman diagonal-order sums

For a strict convex `n`-gon in cyclic order, the sums `U_k` of chord lengths of
cyclic order `k` satisfy

```text
U_1 < U_2 < ... < U_floor(n/2).
```

Therefore a natural-order cyclic-offset selected pattern that forces
`U_a = U_b` for distinct chord orders `a,b` is impossible. This is a
natural-order obstruction only; it does not apply to arbitrary cyclic
relabelings of the same incidence pattern. See
`docs/altman-diagonal-sums.md`.

### Fixed-order Kalmanson/Farkas obstruction for C19_skew

Status: `EXACT_OBSTRUCTION` for one fixed selected-witness pattern and one
fixed cyclic order only.

For the `C19_skew` selected-witness pattern with offsets `[-8,-3,5,9]` and
cyclic order

```text
[18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1]
```

the checked certificate
`data/certificates/round2/c19_kalmanson_known_order_two_unsat.json` gives a
positive integer combination of 2 strict Kalmanson distance inequalities whose
total coefficient vector is exactly zero after quotienting by the
selected-distance equalities. Summing the strict inequalities gives `0 > 0`.
The earlier 94-inequality certificate remains checked as provenance at
`data/certificates/round2/c19_kalmanson_known_order_unsat.json`.

This is not a proof that abstract `C19_skew` is impossible across all cyclic
orders, and it is not a proof of Erdos #97. See
`docs/round2/kalmanson_distance_filter.md` and
`scripts/check_kalmanson_certificate.py`.

The related `C17_skew` Ptolemy-log artifact in
`data/certificates/round2/c17_skew_ptolemy_log_certificate.json` is retained as
a method note and verifier regression. It does not move the live wall, because
`C17_skew` was already exactly killed by earlier fixed-pattern filters.

### All-order Kalmanson/Farkas obstruction for C13_sidon_1_2_4_10

Status: `EXACT_OBSTRUCTION` for one fixed selected-witness pattern across all
cyclic orders.

For the `C13_sidon_1_2_4_10` selected-witness pattern with offsets
`[1,2,4,10]`, the checked exhaustive order-search artifact
`data/certificates/c13_sidon_all_orders_kalmanson_two_search.json` verifies
that every cyclic order contains a two-inequality Kalmanson inverse-pair
certificate. The search fixes label `0` first using circulant translation
symmetry, visits `1496677` surviving-prefix nodes, prunes `6192576` branches by
completed two-certificates, and finds no survivor order.

This kills the fixed abstract C13 Sidon selected-witness pattern across all
cyclic orders. It is not a proof of Erdos #97. See
`docs/kalmanson-two-order-search.md` and
`scripts/check_kalmanson_two_order_search.py`.

### Fixed-order Kalmanson/Farkas pilot for C13_sidon_1_2_4_10

Status: superseded fixed-order certificate, retained as provenance.

For the `C13_sidon_1_2_4_10` selected-witness pattern with offsets
`[1,2,4,10]` and cyclic order

```text
[5,0,10,8,9,7,4,6,2,11,12,3,1]
```

the checked certificate
`data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json` gives a
positive integer combination of 2 strict Kalmanson distance inequalities whose
total coefficient vector is exactly zero after quotienting by the
selected-distance equalities. Summing the strict inequalities gives `0 > 0`.
The earlier 34-inequality certificate remains checked as provenance at
`data/certificates/c13_sidon_order_survivor_kalmanson_unsat.json`.

See `docs/kalmanson-c13-pilot.md`, `docs/round2/kalmanson_distance_filter.md`,
and `scripts/check_kalmanson_certificate.py`.

## Lemmas

### Circle-intersection cap

In any selected-witness counterexample, for distinct centers `a,b`,

```text
|S_a cap S_b| <= 2.
```

Otherwise two distinct Euclidean circles would share at least three points.[^small]

### Radical-axis crossing / bisection

If

```text
S_x cap S_y = {a,b}
```

for distinct centers `x,y`, then the line `p_x p_y` is the perpendicular
bisector of segment `p_a p_b`; the segment `p_x p_y` contains the midpoint of
segment `p_a p_b`; chords `{x,y}` and `{a,b}` cross in the cyclic order; and
neither chord is a polygon edge.

Both centers are equidistant from `p_a` and `p_b`, so they lie on the
perpendicular bisector of `p_a p_b`. Let `m = (p_a + p_b)/2`. The point `m`
lies on segment `ab`, hence in `conv(P)`, and also on the line `xy`.

If `xy` were a polygon edge, its line would support the strictly convex polygon,
but `a` and `b` lie on opposite sides of their perpendicular bisector. Thus
`xy` is a diagonal. A line through two nonadjacent vertices of a strictly convex
polygon meets the polygon in exactly the chord segment between them, so
`m in [p_x,p_y]`. Since `m` is also in the relative interior of `[p_a,p_b]`,
the two chords cross at `m`. A crossed chord cannot be a boundary edge, so
`ab` is not an edge either.

Consequently, adjacent centers satisfy

```text
|S_x cap S_y| <= 1,
```

and any proposed cyclic order must make every source chord with two common
witnesses cross its common-witness chord. See
`docs/mutual-rhombus-filter.md` for the fixed-pattern filters built from this
lemma.

### Sharpened incidence counting lower bound

Let `d_j = #{i : j in S_i}`. Then `sum_j d_j = 4n`, and convexity of
`binom(d,2)` with average indegree 4 gives

```text
sum_j binom(d_j,2) >= 6n.
```

Also

```text
sum_j binom(d_j,2) = sum_{i<j} |S_i cap S_j|.
```

The two-circle cap gives intersection size at most `2` for every row-pair. The
crossing/bisection lemma improves the `n` adjacent row-pairs to size at most
`1`. Hence

```text
sum_{i<j} |S_i cap S_j|
  <= n + 2*(binom(n,2) - n)
  = n(n-2).
```

Thus `6n <= n(n-2)`, so any selected-witness counterexample has `n >= 8`.
This gives a shorter exact proof excluding `n <= 7`; it does not replace the
separate `n=8` exact pipeline.[^repo]

### n=8 crossing-permutation compression

If a selected-witness counterexample had `n=8`, equality would hold throughout
the sharpened incidence count. Therefore:

```text
d_v = 4 for every label v,
|S_i cap S_j| = 1 for adjacent row-pairs {i,j},
|S_i cap S_j| = 2 for nonadjacent row-pairs {i,j}.
```

The map

```text
phi({i,j}) = S_i cap S_j
```

is consequently defined on all 20 diagonals of the octagon and on no boundary
edges. The crossing/bisection lemma says every source diagonal crosses its
image. The pair-sharing cap makes `phi` injective on these diagonals: a witness
pair `{a,b}` can occur together in at most two selected rows, hence can be the
common-witness pair of at most one row-pair. Since there are 20 source
diagonals and 20 target diagonals, `phi` is a crossing permutation of the
octagon diagonals.

This is a compression of the hypothetical `n=8` case, not a replacement for the
checked `n=8` exact survivor pipeline.

### Mutual-rhombus midpoint obstruction

Define

```text
phi({x,y}) = S_x cap S_y
```

whenever the intersection has size exactly `2`. If `phi(e) = f` and
`phi(f) = e` for unordered chords `e={x,y}` and `f={a,b}`, then the two chords
are mutual perpendicular bisectors. Therefore they share a midpoint:

```text
p_x + p_y = p_a + p_b.
```

For each coordinate this is the exact integer linear equation

```text
X_x + X_y - X_a - X_b = 0.
```

If exact rational row reduction of all such midpoint equations forces
`X_u = X_v` for distinct labels `u,v`, then every realization has
`p_u = p_v`, impossible in a strictly convex polygon. This is a fixed
selected-witness pattern obstruction, not a proof against other possible
4-subset selections on the same hypothetical coordinate set.

### Pair and triple sharing

For an unordered pair `{a,b}`, at most two polygon vertices `x` satisfy
`|x-a| = |x-b|`: the locus is one perpendicular-bisector line, and a line
meets a strictly convex polygon boundary in at most two vertices.[^digest]

Any noncollinear triple of vertices can appear together in at most one selected
witness set, because three noncollinear points have a unique circumcenter.[^digest]

### Minimal-counterexample critical tie

In a counterexample with the minimum possible number of vertices, every deleted
vertex is essential to some remaining vertex's badness. More precisely, for
each vertex `x`, there is a vertex `y != x` such that `x` belongs to the unique
distance class of size exactly 4 at `y`.

Proof. Delete `x`. By minimality, the remaining polygon is not a counterexample,
so some remaining vertex `y` has `E(y) <= 3` after deletion. In the original
polygon, any distance class at `y` of size at least 4 must have contained `x`;
otherwise it would still have size at least 4 after deletion. Since `x` lies at
only one distance from `y`, there is at most one such class. Its size cannot
exceed 4, because a class of size at least 5 containing `x` would still have
size at least 4 after deletion. Thus `x` lies in a unique critical 4-tie at
`y`.

This is structural information about minimal counterexamples; by itself it is
not a contradiction.

### n=8 witness indegree regularity

For `n=8`, the pair-sharing cap forces every witness indegree to equal 4. If a
fixed vertex `v` occurs in `d` selected witness rows, those occurrences contain
`3d` pairs `{v,a}`. There are 7 possible partners `a`, and each pair can occur
in at most two rows, so `3d <= 14` and `d <= 4`. Since the total indegree is
`4n = 32`, all 8 indegrees are exactly 4.

### Vertex cone and chord order

At a vertex of a strictly convex polygon, all other vertices lie in the closed
cone spanned by the two incident edges. Only the two adjacent vertices lie on
the boundary rays, and all non-adjacent vertices lie in the open cone. Boundary
order therefore agrees with angular order around that vertex.[^digest]

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
