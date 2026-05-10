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

### All-order Kalmanson/Farkas obstruction for C19_skew

Status: `EXACT_OBSTRUCTION` for one fixed selected-witness pattern across all
cyclic orders.

For the `C19_skew` selected-witness pattern with offsets `[-8,-3,5,9]`, the
checked SMT refinement artifact
`data/certificates/c19_skew_all_orders_kalmanson_z3.json` verifies that every
cyclic order contains a two-inequality Kalmanson inverse-pair certificate. The
artifact stores 7,981 exact forbidden ordered-quadrilateral pairs. The verifier
checks that each stored pair is an inverse pair of strict Kalmanson row vectors
after selected-distance quotienting, then asks Z3 to replay the accumulated
cyclic-order constraints as UNSAT.

This kills the fixed abstract C19 selected-witness pattern across all cyclic
orders. It is not a proof of Erdos #97. See
`docs/kalmanson-two-order-search.md` and
`scripts/check_kalmanson_two_order_z3.py`.

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

### Fixed-order Kalmanson/Farkas obstruction for C29_sidon_1_3_7_15

Status: `EXACT_OBSTRUCTION` for one fixed selected-witness pattern and one
fixed cyclic order only.

For the `C29_sidon_1_3_7_15` selected-witness pattern with offsets
`[1,3,7,15]` and cyclic order

```text
[0,27,11,4,19,5,26,12,6,21,13,28,14,2,20,18,7,24,10,25,17,3,9,15,1,22,8,23,16]
```

the checked certificate
`data/certificates/c29_sidon_fixed_order_kalmanson_165_unsat.json` gives a
positive integer combination of 165 strict Kalmanson distance inequalities
whose total coefficient vector is exactly zero after quotienting by the
selected-distance equalities. Summing the strict inequalities gives `0 > 0`.

This retires the fixed C29 order recorded as a stress test in
`data/certificates/c25_c29_sparse_frontier_probe.json`. It is not an all-order
obstruction for the abstract C29 Sidon selected-witness pattern, and it is not
a proof of Erdos #97. Check it with
`python scripts/check_kalmanson_certificate.py data/certificates/c29_sidon_fixed_order_kalmanson_165_unsat.json --summary-json`.

### Fixed-order Kalmanson/Farkas obstruction for the endpoint-control survivor

Status: `EXACT_OBSTRUCTION` for one fixed selected-witness extension and one
fixed cyclic order only.

For the endpoint-control survivor recorded in
`docs/minimal-fragile-cover-bridge.md`, in the natural cyclic order on labels
`0,...,10`, the checked certificate in
`scripts/check_endpoint_control_survivor_kalmanson_certificate.py` gives a
positive integer combination of 22 strict Kalmanson distance inequalities
whose total coefficient vector is exactly zero after quotienting by the
selected-distance equalities. The weight sum is 89, and summing the strict
inequalities gives `0 > 0`.

This rejects only that fixed full selected-row extension and natural cyclic
order. It is not an all-extension endpoint-control proof, not a Euclidean
realizability theorem for the abstract fragile rows, and not a proof of
Erdos #97.

### Crossing-compatible Kalmanson/Farkas obstruction for the endpoint-control survivor

Status: `EXACT_OBSTRUCTION` for one fixed selected-witness extension across
its five crossing-compatible cyclic orders only.

For the same endpoint-control survivor, the crossing-only frontier checker in
`scripts/check_endpoint_control_survivor_spine_pocket_orders.py` proves that
the necessary two-overlap crossing constraints leave exactly five normalized
cyclic orders. The checker
`scripts/check_endpoint_control_survivor_spine_pocket_kalmanson.py` then
replays a positive integer Kalmanson quotient-cone certificate for each of the
five orders. The strict-row counts are `[23, 12, 16, 10, 12]`, the weight sums
are `[541, 51, 79, 27, 38]`, and each combined coefficient vector reduces
exactly to zero across `25` selected-distance quotient classes.

Check it with
`python scripts/check_endpoint_control_survivor_spine_pocket_kalmanson.py --assert-expected --json`.
This closes the fixed survivor at the crossing-compatible Kalmanson level. It
does not rule out other full selected-row extensions of the same fragile rows,
does not prove endpoint control, and is not a proof of Erdos #97.

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

### Minimal fragile-cover bridge

Every minimal counterexample admits a partial fragile-cover witness system:
some exact critical 4-tie rows cover all vertices, each vertex is assigned to
a fragile center whose exact 4-tie contains it, and every retained fragile row
is assigned at least one vertex.

This follows by applying the minimal-counterexample critical-tie lemma to each
deleted vertex and retaining one copy of each resulting exact 4-tie. The row
usage condition is equivalently a matching from retained fragile centers to
distinct vertices they cover. Since every vertex in a counterexample is bad,
the retained fragile rows can also be extended to a full selected-witness
incidence system by choosing one 4-neighbor row at every non-fragile center and
using the retained critical row at each fragile center. The rows also satisfy
the two-circle cap and the radical-axis crossing rule for
two-overlaps. This is a necessary bridge theorem only; the block-6 abstract
family checked by `scripts/check_fragile_hypergraph.py --blocks 2 --assert-ok`
shows that fragile-cover hypergraph constraints alone are too weak to prove
the problem. See `docs/minimal-fragile-cover-bridge.md`.

### Adaptive peeling / radius-blocker alternative

Status: `LEMMA` / bridge fork.

Given the full family of rich distance classes at each bad vertex, adaptive
reverse peeling has an exact alternative: either it reaches a three-vertex seed
and constructs an ear-orderable selected-witness system, or it stops at a
radius-blocker `U` in which every rich class at every center of `U` has at most
two witnesses inside `U`.

If a minimal counterexample avoids all ear-orderable selected-witness
reductions, then it must contain such a radius-blocker. Writing
`O = V \ U`, every rich class centered in `U` has at least two witnesses in
`O`, and the perpendicular-bisector pair-sharing lemma gives
`|U| <= |O|(|O|-1)`. Any fragile critical row centered inside `U` therefore
has at most two witnesses in `U` and at least two outside.

This is not a proof of Erdos Problem #97. It isolates the next bridge target:
rule out radius-blockers using strict convexity, fragile-cover geometry, and
the current exact obstruction stack, or construct an exact blocker escape
mechanism. See `docs/adaptive-radius-blocker-bridge.md`.

### Bootstrap-core closure rank and weighted capacity

Status: `LEMMA` / bridge fork.

Given the full family of rich distance classes at each bad vertex, define
`cl(A)` by adding a center once three current vertices lie in one of its rich
classes. Let `rho` be the minimum size of a set whose closure is all vertices.
Then a polygon admits an ear-orderable selected-witness system if and only if
`rho <= 3`, using the repo convention that the first three vertices form the
base of the ear order.

If `rho > 3` and `U` is an inclusion-minimal generator, then for every
`u in U`, with `A_u = cl(U \ {u})` and `O = V \ U`, one has `u notin A_u` and
`|C cap A_u| <= 2` for every rich class `C` at `u`. Thus the private halo
`D_u = O \ A_u` contains at least `|C|-2` witnesses from each such class.

Counting all private outside pairs gives the weighted cyclic capacity bound

```text
sum_{u in U} sum_{C in R(u)} binom(|C cap D_u|, 2)
  <= sum_{{a,b} subset O} kappa_U(a,b)
  = 2 binom(|O|, 2) - sum_R binom(|R|, 2),
```

where the last sum is over maximal consecutive outside-vertex runs in the
cyclic order. This strengthens the one-pair-per-center radius-blocker bound
but is still only a bridge target, not a proof of Erdos Problem #97. See
`docs/bootstrap-core-bridge.md`.

The companion crosswalk in `docs/bootstrap-core-crosswalk.md` applies this
bookkeeping to current singleton-rich fixed-row frontier motifs. It records
that the audited cases have rank greater than 3 but still pass weighted
capacity, so it is negative diagnostic information about the strength of the
ledger, not a new obstruction theorem.

The companion overlay in `docs/bootstrap-vertex-circle-overlay.md` joins the
two tight `n=9` non-ear-orderable crosswalk rows to the review-pending
vertex-circle strict-cycle chain. Both rows land on the `T12/F16` strict-cycle
template by selected-row signature, but their local strict-cycle row cores are
not bootstrap-core-only. This is proof-mining scaffolding, not a proof of
`n=9`, not a proof of the bridge, and not a global status update.

The follow-up ledger in `docs/bootstrap-t12-forcing-targets.md` records the
next T12 target more explicitly: both tight rows need T12/F16 row centers
outside the bootstrap core, and the direct private-pair contacts are absent for
source `81` and partial for source `151`. This remains an open target ledger,
not a theorem that the missing rows are forced.

The row-pressure refinement in `docs/bootstrap-t12-row-pressure.md` classifies
the six missing row centers into two deletion-closure-exposed rows, three
one-outside-label rows, and one outside-pair row. This is a diagnostic
decomposition of the open target, not a theorem that any of those rows are
forced by genuine geometry.

The closure-exposed packet in `docs/bootstrap-t12-closure-exposed.md` isolates
the two deletion-closure-exposed rows, `81:3` and `151:7`. Both are
activation-ready in the deletion closure for core vertex `2`, but only `81:3`
has its full selected row contained in that closure. This remains fixed-row
proof-mining bookkeeping; it is not a rich-class row-forcing theorem.

The one-outside-label packet in `docs/bootstrap-t12-one-outside.md` isolates
the three singleton-support rows, `81:8`, `151:5`, and `151:8`. Each row has
two bootstrap-core witnesses and a row center private in every deletion
closure; in each row, one singleton support is private in all deletion halos
and one is internal to the deletion closure for core vertex `2`. This is a
diagnostic decomposition only, not a theorem that singleton supports or row
centers are forced by Euclidean geometry.

The outside-pair packet in `docs/bootstrap-t12-outside-pair.md` isolates the
single pair-supported row, `151:6`. It has one bootstrap-core witness and
three outside-pair supports; all three supports are private in every deletion
halo, and two also hit the private-pair ledger. This is still a diagnostic
decomposition only, not a theorem that a private-pair ledger hit forces an
equality-connector row in genuine geometry.

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

### Two-edge vertex-circle quotient-cycle schema

Status: `LEMMA` for any fixed local row core satisfying the stated hypotheses.

Suppose two selected rows have four distinct witnesses each, in angular orders

```text
a,b,c,d
e,f,g,h
```

around their respective centers. Vertex-circle chord monotonicity gives

```text
D_ac > D_ab,
D_fh > D_gh.
```

If selected-distance equality paths identify the inner pair of each strict
edge with the outer pair of the other,

```text
D_ab = D_fh,
D_gh = D_ac,
```

then no strictly convex selected-witness realization can satisfy that local
core, because

```text
D_ac > D_ab = D_fh > D_gh = D_ac.
```

This is only a local obstruction schema. It does not say that arbitrary
counterexamples contain such a core, does not prove `n=9`, and does not prove
Erdos Problem #97. The focused `T10/F12` packet below is one checked instance
of this schema.

### Two-row nondegeneracy for two-edge quotient cycles

Status: `LEMMA` for the two-edge vertex-circle schema.

In the two-edge schema above, suppose the only selected-distance equalities
available are those from the two rows producing the two strict
vertex-circle inequalities. If the four strict-edge endpoint pairs are
pairwise distinct, and neither strict edge is already a quotient self-edge,
then the cross-wired equalities cannot both hold.

The reason is purely combinatorial. The two rows generate only two star
equivalence classes of pair distances, one for pairs from the first center to
its four witnesses and one for pairs from the second center to its four
witnesses, possibly merged along a common center-witness pair. For the two
cross-wires to hold nontrivially, both strict pairs of the first row must lie
in the second row's star, and both strict pairs of the second row must lie in
the first row's star. Then each strict edge is already a self-edge, contrary
to the nondegeneracy assumption.

Thus a genuine two-edge quotient cycle needs an additional connector row or a
longer selected-distance path, unless it has already collapsed to a simpler
self-edge obstruction. This is a local structural fact only; it does not force
such connector rows to exist in arbitrary counterexamples.

### Vertex-circle T01/F09 self-edge local lemma candidate

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

In a strictly convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, suppose the
following three selected rows are present:

```text
center 0: {1,2,4,8}
center 1: {0,3,5,8}
center 2: {0,1,4,6}
```

The selected-distance equalities force

```text
[1,8] = [0,1] = [0,2] = [1,2].
```

Meanwhile row `0` has witness order `[1,2,4,8]` around vertex `0`, so the
vertex-circle chord monotonicity lemma gives the strict inequality

```text
[1,8] > [1,2].
```

Thus the selected-distance quotient has a reflexive strict edge, and no
strictly convex realization can satisfy these exact local hypotheses. The
packet label `T01/F09` is navigation only; the hypotheses are the displayed
cyclic order and selected rows. This is not an `n=9` completeness proof, not a
promotion of the review-pending exhaustive checker, and not a proof of Erdos
Problem #97. Check the focused packet with
`python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py --check --assert-expected --json`.

### Vertex-circle T10/F12 strict-cycle local lemma candidate

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

In a strictly convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, suppose the
following four selected rows are present:

```text
center 0: {1,2,5,6}
center 3: {0,1,4,6}
center 6: {1,3,4,7}
center 8: {0,3,6,7}
```

Rows `3` and `6` force `[0,3] = [3,6] = [1,6]`, while row `0` forces
`[0,1] = [0,6]`. The row-`8` witness order `[0,3,6,7]` gives
`[0,6] > [0,3]`, and the row-`3` witness order `[4,6,0,1]` gives
`[1,6] > [0,1]`. After selected-distance quotienting, these become

```text
[0,6] > [1,6] > [0,6].
```

Thus the strict quotient graph has a directed two-edge cycle, and no strictly
convex realization can satisfy these exact local hypotheses. The packet label
`T10/F12` is navigation only; the hypotheses are the displayed cyclic order
and selected rows. This is not an `n=9` completeness proof, not a promotion of
the review-pending exhaustive checker, and not a proof of Erdos Problem #97.
Check the focused packet with
`python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py --check --assert-expected --json`.

### Vertex-circle T11/F07 strict-cycle local lemma candidate

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

In a strictly convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, suppose the
following four selected rows are present:

```text
center 0: {1,2,4,8}
center 1: {0,2,3,5}
center 5: {0,3,4,7}
center 6: {1,5,7,8}
```

The row-`1` witness order `[2,3,5,0]` gives `[0,2] > [0,3]` and
`[0,3] > [0,5]`; row `5` forces `[0,5] = [5,7]`. The row-`6` witness order
`[7,8,1,5]` gives `[5,7] > [1,5]`; rows `1` and `0` force
`[1,5] = [0,1] = [0,2]`. After selected-distance quotienting, these become

```text
[0,2] > [0,3] > [5,7] > [0,2].
```

Thus the strict quotient graph has a directed three-edge cycle, and no
strictly convex realization can satisfy these exact local hypotheses. The
packet label `T11/F07` is navigation only; the hypotheses are the displayed
cyclic order and selected rows. This is not an `n=9` completeness proof, not a
promotion of the review-pending exhaustive checker, and not a proof of Erdos
Problem #97. Check the focused packet with
`python scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py --check --assert-expected --json`.

### Vertex-circle T12/F16 strict-cycle local lemma candidate

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

In a strictly convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, suppose the
following six selected rows are present:

```text
center 0: {1,3,6,7}
center 1: {2,4,7,8}
center 2: {0,3,5,8}
center 3: {0,1,4,6}
center 4: {1,2,5,7}
center 8: {0,2,5,6}
```

The row-`2` witness order `[3,5,8,0]` gives `[0,3] > [0,8]`, and row `8`
forces `[0,8] = [2,8]`. The row-`1` witness order `[2,4,7,8]` gives
`[2,8] > [2,4]`, while rows `4` and `1` force
`[2,4] = [1,4] = [1,7]`. The row-`0` witness order `[1,3,6,7]` gives
`[1,7] > [1,3]`, and row `3` forces `[1,3] = [0,3]`. After
selected-distance quotienting, these become

```text
[0,3] > [2,8] > [1,7] > [0,3].
```

Thus the strict quotient graph has a directed three-edge cycle, and no
strictly convex realization can satisfy these exact local hypotheses. The
packet label `T12/F16` is navigation only; the hypotheses are the displayed
cyclic order and selected rows. This is not an `n=9` completeness proof, not a
promotion of the review-pending exhaustive checker, and not a proof of Erdos
Problem #97. Check the focused packet with
`python scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py --check --assert-expected --json`.

### Low-angle ascent for middle witnesses

Let `alpha_p` be the interior angle at a bad vertex `p`, and let
`q_1,q_2,q_3,q_4` be a selected equidistant witness row in angular order around
`p`. Write

```text
delta_1 = angle(q_1,p,q_2),
delta_2 = angle(q_2,p,q_3),
delta_3 = angle(q_3,p,q_4).
```

Because the witnesses lie on a circle centered at `p`, the inscribed-angle
theorem gives

```text
angle(q_1,q_2,q_3) = pi - (delta_1 + delta_2)/2,
angle(q_2,q_3,q_4) = pi - (delta_2 + delta_3)/2.
```

Convexity places the two chord rays used in each displayed angle inside the
corresponding polygon interior angle, so

```text
alpha_{q_2} >= pi - (delta_1 + delta_2)/2,
alpha_{q_3} >= pi - (delta_2 + delta_3)/2.
```

In particular, if `alpha_p < 2*pi/3`, then the two middle witnesses in any
selected 4-row have strictly larger interior angle than `p`. This is a local
angle-ascent lemma only; by itself it gives no global angle-sum contradiction
for large polygons.

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

[^small]: Public consolidation: `public-provenance.md#small-cases-n5-through-n8`.
[^repo]: Public consolidation: `public-provenance.md#repository-handoff-and-claim-taxonomy`.
[^digest]: Public consolidation: `public-provenance.md#literature-digest`.
[^syn]: Public consolidation: `public-provenance.md#canonical-synthesis`.
[^alg]: Public consolidation: `public-provenance.md#algebraic-and-semicircle-corrections`.
[^paper]: Public consolidation: `public-provenance.md#paper-style-verifier-review`.
[^rank]: Public consolidation: `public-provenance.md#rank-and-bridge-status`.
