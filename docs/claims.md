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

### Literature-backed shortcut: Dumitrescu isosceles count for n <= 8

Status: `LITERATURE_BACKED_PROOF_NOTE` / `REVIEW_PENDING`.

The proof note `docs/dumitrescu-isosceles-n8-shortcut.md` records a shorter
external-bound route to the same small-case wall. In the apex-counted
isosceles convention, Dumitrescu's convex-position bound gives

```text
Z(P) <= (11 n^2 - 18 n) / 12.
```

If a strictly convex `n`-gon were 4-bad, every vertex would contribute at
least `binom(4,2) = 6` equal-leg pairs, so `Z(P) >= 6n`. Combining the two
inequalities forces `n >= 90/11 > 8`.

This is a compact human-readable shortcut, not an update to the repository
source-of-truth status. The checked selected-witness artifacts remain the
repo-local `n <= 8` source until this literature-backed note receives
independent review.

### Edge-sensitive rich-support counting bound

Status: `LEMMA`.

Let `R_i` be any same-radius support chosen at center `i`; unlike selected
witness rows, `R_i` may have size larger than four. Then

```text
sum_i binom(|R_i|, 2) <= n(n - 2).
```

The proof is the pair-sharing cap with hull-edge pairs counted separately. For
a fixed unordered witness pair `{a,b}`, every center whose support contains
both `a` and `b` lies on the perpendicular bisector of segment `ab`. If `{a,b}`
is a non-edge, strict convexity permits at most two polygon vertices on that
line. If `{a,b}` is a hull edge, the perpendicular bisector already meets the
polygon boundary at the edge midpoint and can contain at most one further
boundary vertex, hence at most one center. Double-counting witness pairs inside
supports gives the displayed inequality.

Thus, if every center has a rich distance class of size at least `k`, then the
edge-sensitive pair count gives `n >= binom(k, 2) + 2`. The support-saturation
obstruction rules out the equality wall for `k >= 4`, improving this to
`n >= binom(k, 2) + 3`. In particular, every-vertex size-five richness is
impossible for `n <= 12`. Choosing a maximum rich class at each center of a
hypothetical 4-bad nonagon also shows that at most two centers can have
`E(i) >= 5`, so at least seven centers must be exact-four. The same relaxation
forces at least five exact-four centers for `n=10` and at least three for
`n=11`.

The profile-deficiency refinement in the same checker rules out the three raw
nonagon profiles still allowed by the global pair budget, namely `5 4^8`,
`5^2 4^7`, and `6 4^8`, by comparing pair-capacity slack with the label
deficiency residues forced by row sizes. The companion localized counting cap
gives an even shorter per-label route to the same nonagon conclusion. For each
fixed witness label `x`,

```text
sum_{i: x in R_i} (|R_i| - 1) <= 2n - 4.
```

For `n=9`, every support occurrence contributes at least `3` to its label's
localized budget, so each label occurs in at most four chosen supports. The
4-bad baseline already needs `36` support occurrences, hence every chosen
support is exact-four and every label has selected indegree four.

These are support-level counting lemmas only. The saturation obstruction only
rules out the equality wall, and the profile-deficiency and localized routes
both reduce hypothetical nonagons to the all-exact-four support frontier. They
do not prove the review-pending exact-four vertex-circle checker, `n=9`,
`n=10`, `n=11`, or Erdos Problem #97. See
`docs/rich-support-counting-lemma.md`, `docs/support-saturation-obstruction.md`,
`docs/localized-rich-support-counting.md`, and the checkers
`scripts/check_rich_support_counting_bound.py`,
`scripts/check_support_saturation_obstruction.py`, and
`scripts/check_localized_rich_support_counting.py`.

The all-five-rich `n=12` equality wall also has an independent determinant
obstruction in `docs/n12-rich-support-determinant-obstruction.md`: saturated
pair capacities force a `12 x 12` incidence Gram matrix with nonsquare
determinant `2,592,000 = 720^2 * 5`, contradicting
`det(A^T A) = det(A)^2`. This is a support-level cross-check of the equality
wall already closed by support saturation. It does not prove the full `n=12`
case, any mixed exact-four/size-five catalogue, or Erdos Problem #97. Check it
with `scripts/check_n12_rich_support_determinant.py`.

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

The sparse-frontier Kalmanson escape audit in
`docs/sparse-frontier-kalmanson-escape-audit.md` separately confirms that the
stored C25 and C29 fixed orders still escape the direct two-inequality
Kalmanson inverse-pair filter when all `2*binom(n,4)` strict Kalmanson rows are
replayed. This is a fixed-order filter diagnostic only; it does not weaken the
C29 fixed-order Farkas certificate above, and it does not supply an all-order
C25 or C29 obstruction.

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

### Fixed-order Kalmanson/Farkas obstruction for reversed-block clean rows

Status: `EXACT_OBSTRUCTION` for 16 fixed selected-witness extensions in their
recorded fixed cyclic orders only.

The reversed-second-block shuffle negative-control artifact
`data/certificates/block6_reversed_block_shuffle_vertex_circle_escape.json`
records 16 fixed assignment/order pairs that remain clean under the
vertex-circle quotient gate. The checked follow-up
`data/certificates/block6_reversed_block_clean_kalmanson.json` gives an exact
Kalmanson quotient-cone certificate for each of those 16 pairs. Across the
packet, the certificates use `394` strict Kalmanson rows with total weight
`16850`, and every combined coefficient vector is exactly zero after
selected-distance quotienting.

This closes only the 16 stored fixed selected-row assignments in the stored
cyclic orders. It is not all-order closure for the oriented-block family, not a
fragile-bridge proof, not a proof of Erdos #97, and not a counterexample.
Check it with
`python scripts/check_block6_reversed_block_clean_kalmanson.py --check --assert-expected --json`.
The companion crosswalk
`data/certificates/block6_reversed_block_two_stage_closure.json` only checks
that this 16-row packet lines up with the reversed-block vertex-circle packet,
giving the bounded-family count `446 + 16 = 462`.

The first-block-forward two-orientation crosswalk
`data/certificates/block6_forward_block_two_orientation_closure.json` only
joins this reversed-block count to the forward-second-block vertex-circle
sweep, giving `462 + 462 = 924` closed normalized shuffle orders under the
extra convention that the first block remains in forward orientation. It is
not a claim about first-block-reversed orientations, arbitrary cyclic orders,
all selected-row systems, the fragile bridge, Erdos #97, or a counterexample.

The oriented-block reversal crosswalk
`data/certificates/block6_oriented_block_reversal_closure.json` only transfers
those counts across the exact cyclic-order reversal map
`[0] + reversed(order[1:])`. It verifies `462` reversal pairs from
`forward-forward` to `reversed-reversed` and `462` reversal pairs from
`forward-reversed` to `reversed-forward`, giving `1848` closed oriented-block
shuffle orders. It is not a claim about arbitrary cyclic orders, all
selected-row systems, the fragile bridge, Erdos #97, or a counterexample.

## Lemmas

### Circle-intersection cap

In any selected-witness counterexample, for distinct centers `a,b`,

```text
|S_a cap S_b| <= 2.
```

Otherwise two distinct Euclidean circles would share at least three points.[^small]

### Same-distance K4 obstruction

After exact same-distance quotienting, one ordinary distance class cannot
contain all six edges of a `K_4` on four distinct vertices. Four planar points
cannot be pairwise equidistant at one positive distance: three would form an
equilateral triangle, and the only planar point equidistant from all three is
the circumcenter, whose distance to the vertices is smaller than the side
length.

This is a fixed-pattern or quotient-class obstruction only. It becomes
available after selected-distance equalities, reciprocal selected-edge
components, or another exact mechanism has proved that all six ordinary pairs
belong to one distance class.

### Same-distance K4-e stretch obstruction

If an exact ordinary distance class contains exactly five of the six edges on
four distinct vertices, then the missing edge has length `sqrt(3)` times the
common class length. The proof is the two-equilateral-triangles picture: the
five equal edges force two equilateral triangles sharing the edge opposite the
missing pair, and distinct planar vertices put the two missing-edge endpoints
on opposite sides of that shared edge.

The checker `scripts/check_k4e_kalmanson_stretch_audit.py` uses this relation
only after exact selected-distance quotienting, and only inside fixed patterns
and fixed cyclic orders. It represents coefficients in `Q(sqrt(3))` exactly
and then tests whether a substituted Kalmanson inequality has positive
left-minus-right coefficient for all positive quotient class lengths.

The current replay kills the displayed `n=10` quotient-level survivor and one
`n=9` diagnostic pattern. This is a filter improvement and a fixed-pattern
audit only; it is not an `n=10` exclusion and does not change the global
problem status.

### n=9 no-reciprocal regular-tournament obstruction

Status: `EXACT_N9_NO_RECIPROCAL_SUBCASE_AUDIT`.

For `n=9`, a selected-witness system with no reciprocal selected pair must
select every unordered pair in exactly one direction: there are `9 * 4 = 36`
directed selections and `binom(9,2) = 36` unordered pairs. Hence this subcase is
exactly the labelled regular tournament subcase, with each row selecting four
out-neighbors.

The checker `scripts/check_n9_regular_tournament_kalmanson.py` enumerates all
`3,230,080` labelled regular tournaments on cyclic labels `0,1,...,8`. For each
tournament, it substitutes the selected row-radius variables into the strict
Kalmanson inequalities for the fixed cyclic order and records every one-term
cancellation as a strict implication `rho_a < rho_b`. Every enumerated
tournament has a strongly connected implication graph, so in particular every
one has a strict implication cycle and is impossible in a strict convex
realization.

This proves only that an `n=9` selected-witness candidate must contain at least
one reciprocal selected pair. It is not an `n=9` proof, not a promotion of the
review-pending exhaustive `n=9` vertex-circle checker, and not a global status
update. See `docs/n9-regular-tournament-kalmanson-audit.md`.

### n=9 one-reciprocal Kalmanson obstruction

Status: `EXACT_N9_ONE_RECIPROCAL_SUBCASE_AUDIT`.

For `n=9`, if a selected-witness system has exactly one reciprocal selected
unordered pair, then the selected-edge count also forces exactly one unordered
pair to be absent. Every other unordered pair is selected in exactly one
direction.

The checker `scripts/check_n9_one_reciprocal_kalmanson.py` enumerates the `76`
cyclic-dihedral status representatives covering all `1,260` labelled choices
of the reciprocal pair and absent pair. For each status it searches every
degree-4 orientation of the remaining pairs. Selected-distance quotienting
substitutes row-radius variables, the reciprocal pair identifies two row
radii, and the absent pair remains an ordinary distance class. One-term
cancellations in strict Kalmanson inequalities produce strict implications
between quotient classes; every branch develops a strict implication cycle.

Combined with the no-reciprocal regular-tournament audit, this proves only that
an `n=9` selected-witness candidate must contain at least two reciprocal
selected unordered pairs, and hence at least two absent unordered pairs. It is
not an `n=9` proof, not a promotion of the review-pending exhaustive `n=9`
vertex-circle checker, and not a global status update. See
`docs/n9-one-reciprocal-kalmanson-audit.md`.

### Diameter-lens local lemmas

The proof note `docs/diameter-lens-local-lemmas.md` records four local facts
for a global diameter pair `{A,B}`:

```text
diameter-circle pinching,
mutual selected-diameter overlap <= 1,
double-boundary seven-vertex lower bound,
|R(theta)-L(phi)| <= D iff theta*phi >= 0.
```

It also records the seven-point lens-cap negative control showing that the
double-boundary same-side and seven-vertex lemmas are sharp but do not by
themselves contradict strict convexity. Any endpoint-reduction proof must use
the other 4-bad witness rows or another exact certificate.

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

### n=9 all-five-rich support obstruction

Status: `REVIEW_PENDING_DIAGNOSTIC` / generator-independent finite support
catalogue.

In a strict convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, suppose
each center has some rich distance class containing at least five witnesses.
Choosing any five witnesses from each such class gives one size-five support
at each center. The checked support catalogue enumerates all `56^9` such
choices and applies only the two-circle row-pair cap and radical-axis crossing
rule for two-overlaps.

The checker finds no complete assignment satisfying those necessary filters:
the deterministic backtracking search visits `136` assignment nodes, reaches
maximum depth `2`, and has `0` complete assignments. Check it with
`python scripts/check_n9_all_five_rich_support_obstruction.py --check --assert-expected --json`.

Repo-locally, this rules out the all-centers-size-at-least-five subcase for
`n=9`. It does not enumerate mixed exact-four/size-five rich catalogues, does
not prove `n=9`, does not prove the adaptive radius-blocker bridge, does not
prove Erdos Problem #97, and does not provide a counterexample. See
`docs/n9-all-five-rich-support-obstruction.md`.

### n=9 mixed rich-support reduction

Status: `REVIEW_PENDING_DIAGNOSTIC` / generator-independent finite support
catalogue.

In a strict convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, enumerate
all four- and five-witness supports at every center. The checked support
catalogue applies the two-circle row-pair cap, the radical-axis crossing rule
for two-overlaps, and the witness-pair capacity bound that any unordered pair
of witnesses can occur together in rich classes at at most two centers.

The checker searches the full `126^9` mixed support assignment space by exact
backtracking. It visits `108,018` assignment nodes and leaves `184` complete
assignments, all of which use exactly four witnesses at every center. There
are `0` complete assignments containing a size-five support. Check it with
`python scripts/check_n9_mixed_rich_support_reduction.py --check --assert-expected --json`.

The localized rich-support count now gives the proof-facing version of this
nonagon support reduction. The finite mixed catalogue remains useful
provenance and confirms that the row-pair/crossing/witness-pair abstraction
lands on the same `184` all-exact-four assignments. It does not independently
prove the review-pending exact-four vertex-circle exhaustive checker, does not
prove `n=9`, does not prove Erdos Problem #97, and does not provide a
counterexample. See `docs/n9-mixed-rich-support-reduction.md`.

The companion crosswalk
`python scripts/check_n9_mixed_rich_frontier_crosswalk.py --check --assert-expected --json`
checks that the `184` terminal mixed-support assignments are exactly the
stored `184` exact-four pre-vertex-circle frontier assignments as a labelled
set. The mixed and frontier sequences differ at six positions, but the sorted
row-set digest matches and the stored frontier statuses are `158` self-edges
and `26` strict cycles. This remains support-to-frontier bookkeeping only; it
does not prove the exact-four checker, `n=9`, Erdos Problem #97, or a
counterexample. See `docs/n9-mixed-rich-frontier-crosswalk.md`.

### n=10 mixed rich-support capacity diagnostic

Status: `REVIEW_PENDING_DIAGNOSTIC` / generator-independent finite support
catalogue.

For a cyclically labelled decagon, the checker in
`scripts/check_n10_mixed_rich_support_capacity.py` applies only three
necessary support filters: the row-pair cap, the two-overlap crossing rule,
and witness-pair capacity. It searches all dihedral center-set representatives
with `q=3,...,7` size-five supports and finds `0` complete assignments. A
direct stored `q=2` witness survives the same filters, so this is sharp for
that abstraction.

Repo-locally, any `n=10` four/five support assignment surviving those filters
has at most `2` size-five supports, hence at least `8` exact-four-only
centers. This checker alone does not close the `q=0`, `q=1`, or `q=2` cases,
does not prove `n=10`, does not prove Erdos Problem #97, and does not provide
a counterexample. See `docs/n10-mixed-rich-support-capacity.md`.

### n=10 q=2 rich vertex-circle closure diagnostic

Status: `REVIEW_PENDING_DIAGNOSTIC` / finite support-plus-quotient
catalogue.

The checker in `scripts/check_n10_q2_rich_vertex_circle.py` exhausts the
dihedral representatives with exactly two size-five supports under the same
row-pair cap, two-overlap crossing, and witness-pair capacity filters, then
adds the rich vertex-circle quotient gate on partial assignments. It finds no
clean complete `q=2` assignment.

Combined with the earlier `q=3,...,7` support-capacity closure, this says any
`n=10` four/five support assignment surviving these support-plus-quotient
filters has at most `1` size-five support, hence at least `9` exact-four-only
centers. This combined consequence depends on both artifacts; this checker
itself closes exactly the `q=2` layer. It does not close `q=0` or `q=1`, does
not prove `n=10`, does not prove Erdos Problem #97, and does not provide a
counterexample. See `docs/n10-q2-rich-vertex-circle.md`.

### n=10 q=1 rich vertex-circle closure diagnostic

Status: `REVIEW_PENDING_DIAGNOSTIC` / finite support-plus-quotient
catalogue.

The checker in `scripts/check_n10_q1_rich_vertex_circle.py` exhausts the
unique dihedral representative with exactly one size-five support under the
same row-pair cap, two-overlap crossing, and witness-pair capacity filters,
then adds the rich vertex-circle quotient gate on partial assignments. It
finds no clean complete `q=1` assignment.

Combined with the earlier `q=2` rich vertex-circle closure and the `q=3,...,7`
support-capacity closure, this says any `n=10` four/five support assignment
surviving these support-plus-quotient filters must be all-exact-four at this
abstraction level. This combined consequence depends on all three artifacts;
this checker itself closes exactly the `q=1` layer. It does not close `q=0`,
does not prove `n=10`, does not prove Erdos Problem #97, and does not provide
a counterexample. See `docs/n10-q1-rich-vertex-circle.md`.

### n=10 row0 turn plus vertex-circle crosswalk

Status: `FINITE_BOOKKEEPING_NOT_A_PROOF`.

The checker in `scripts/check_n10_turn_row0_combined_closure.py` joins the
bounded `n=10` row0-index-0 turn pilot with the four stored row0-local
vertex-circle self-edge escape templates. It verifies that stored weak-turn
Farkas certificates close `156` of the `160` assignments, that the remaining
weak-turn SAT assignments are exactly `[74,103,156,157]`, and that those four
assignments are exactly the stored vertex-circle escape records.

This is a closure crosswalk for one bounded row0 slice only. It does not prove
`n=10`, does not complete the `n=10` singleton-slice search, does not promote
the row0 pilot to a completeness result, and does not provide a counterexample.
See `docs/n10-turn-row0-combined-closure.md`.

### n=9 Kalmanson self-edge replay

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`.

The checked artifact `data/certificates/n9_kalmanson_selfedge.json` stores one
strict Kalmanson self-edge certificate for each of the 184 labelled
selected-witness systems that survive the exact `n=9` pair/crossing/count
filters. For each stored assignment, the verifier quotients ordinary
distance-pair variables by selected-distance equalities and checks that one
strict Kalmanson inequality has the same quotient multiset on both sides. The
stable certificate-list digest is
`8e5344265e774ce352d64e16e0480eaff4ad6051a69051a304a3f9145db0e3c5`.

Check the certificate replay with
`python scripts/check_n9_kalmanson_selfedge.py --verify-certificate data/certificates/n9_kalmanson_selfedge.json --assert-expected --json`.
This is a compact audit aid for the review-pending `n=9` frontier only. It does
not independently complete review of the brancher filters, does not promote
`n=9` to source-of-truth theorem status, does not prove Erdos Problem #97, and
does not provide a counterexample. See `docs/n9-kalmanson-selfedge.md`.

### n=9 compact independent brancher audit

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`.

The checker in `scripts/check_n9_vertex_circle_compact_brancher.py`
regenerates the `n=9` selected-witness frontier without importing the project
n=9 brancher modules and without reading the stored 184-assignment frontier
artifact. It uses the row shape, row-pair cap, two-overlap crossing rule, and
witness-pair capacity rule, then directly replays the selected-distance
quotient and nested vertex-circle strict inequalities.

It visits `100817` search nodes, regenerates `184` terminal frontier
assignments with sorted row-set digest
`dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55`, and
classifies all of them as vertex-circle quotient obstructed: `158`
self-edges and `26` strict cycles, with `0` clean assignments. This is
independent audit evidence only. It does not complete independent review of
the exhaustive checker, does not promote `n=9` to a theorem, does not prove
Erdos Problem #97, and does not provide a counterexample. See
`docs/n9-vertex-circle-compact-brancher.md`.

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

The activation-requirement packet in
`docs/bootstrap-t12-activation-requirements.md` separates the stored T12/F16
relation requirements from row forcing. It records five equality-connector
pair requirements and two strict-edge endpoint-set requirements across the six
missing row centers, with source `151` row `7` as the main closure-exposure
negative control: the row is exposed through `[0,1,4]` but still misses
endpoint `6` for the strict edge.

The bridge-target map in `docs/bootstrap-t12-bridge-target-map.md` joins the
row-pressure, support, and activation-requirement packets into six explicit
next-lemma targets. It is a proof-mining map only: the hard strict endpoint
rows `151:7` and `151:8`, and the open connector-pair row `151:5`, remain
unproved bridge obligations rather than forced geometric rows.

The hard strict-endpoint packet in
`docs/bootstrap-t12-hard-strict-endpoints.md` isolates the two hard strict
rows. Row `151:7` is closure-exposed but its exposed deletion closure supplies
only `[0,1]` of the strict endpoint set `[0,1,6]`; row `151:8` has singleton
supports that split the strict endpoint set `[1,5,7]`. This is diagnostic
bookkeeping only, not a lemma that strict endpoint sets are forced.

The open connector-pair packet in
`docs/bootstrap-t12-open-connector-pair.md` isolates the remaining open
connector row. Row `151:5` needs equality-connector pair `[7,8]`, but the
deletion closure for core vertex `2` and the two singleton supports each supply
only one connector endpoint. This is diagnostic bookkeeping only, not a lemma
that connector pairs or missing rows are forced.

The relation-sufficient row packet in
`docs/bootstrap-t12-relation-sufficient-rows.md` isolates rows `81:3`, `81:8`,
and `151:6`. Their connector requirements are already bootstrap-core
sufficient or support-sufficient, but this is still diagnostic bookkeeping
only, not a lemma that those rows or rich classes are forced.

The focused `81:3` closure-target packet in
`docs/bootstrap-t12-81-3-closure-target.md` records the smallest current
positive bridge target. Row `81:3` is the unique relation-sufficient row whose
full fixed selected row lies in a deletion closure, and it supplies the final
T12 equality connector `[1,3]=[0,3]` if the row is genuinely available. The
packet keeps that conditional: it is not a lemma that closure membership
forces a rich class or equality connector.

The follow-up `81:3` rich-triple connector contract in
`docs/bootstrap-t12-81-3-rich-triple-contract.md` weakens the target from full
row forcing to a pair-level local conditional. If a genuine rich class at
center `3` contains witnesses `0` and `1`, then the connector equality
`[1,3]=[0,3]` follows immediately. The packet does not prove such a rich class
exists. Its value is to isolate the exact escape: every rich class at center
`3` must avoid the pair `[0,1]`, and any connector-avoiding activation through
the fixed witness set must use label `6` before center `3` activates.

The order-resolved `81:3` fixed-row escape audit in
`docs/bootstrap-t12-81-3-order-escape.md` shows that the existing fixed
singleton-rich packet does not itself supply that escape. From seed `[0,1,4]`,
center `3` is the only initial fixed-row activation and fires through
`[0,1,4]`; label `6` enters only afterward through trigger `[0,3,4]`, which
already uses center `3`. It also records a same-center disjointness guard:
if the source-`81` center-`6` fixed row `[0,3,4,7]` is preserved as a genuine
class, then no additional center-`6` class can contain the seed triple
`[0,1,4]`. This is still a fixed-row-preservation diagnostic only, not a
theorem about all genuine rich-class catalogues.

The relaxed `81:3` escape-candidate scan in
`docs/bootstrap-t12-81-3-escape-candidates.md` drops preservation of the
center-`3` and center-`6` rows while preserving the other seven source-`81`
rows. It enumerates all `40` one-class replacement candidates for pre-`3`
label-`6` supply followed by connector-avoiding center-`3` activation, and all
fail basic row-pair, witness-pair, or crossing filters. This is still a
fixed-row-neighborhood diagnostic only, not a theorem about all genuine
rich-class catalogues.

The one-row-drop follow-up in
`docs/bootstrap-t12-81-3-escape-one-row-drop.md` allows any one of those seven
preserved rows to move as an arbitrary 4-set while also replacing centers `3`
and `6` as above. It checks `19600` candidates and again finds no survivor
under the basic row-pair, witness-pair, and crossing filters. This remains a
finite proof-mining diagnostic only, not a proof of row forcing, `n=9`, the
bootstrap bridge, or Erdos Problem #97.

The two-row-drop follow-up in
`docs/bootstrap-t12-81-3-escape-two-row-drop.md` allows any pair of those seven
preserved rows to move as arbitrary 4-sets while also replacing centers `3`
and `6` as above. It checks `4116000` candidates and again finds no survivor
under the same basic filters. This remains a finite proof-mining diagnostic
only, not a proof of row forcing, `n=9`, the bootstrap bridge, or Erdos
Problem #97.

The full-neighborhood CSP in
`docs/bootstrap-t12-81-3-escape-full-neighborhood.md` allows all seven of those
rows to move simultaneously while keeping the same one-class replacement
spaces at centers `3` and `6`. It proves by exact backtracking that the
implicit `329417200000000`-assignment space has no complete assignment
satisfying the same basic filters. This remains a finite proof-mining
diagnostic only, not a proof of row forcing, `n=9`, the bootstrap bridge, or
Erdos Problem #97.

The auxiliary-rich-class CSP in
`docs/bootstrap-t12-81-3-escape-auxiliary-csp.md` treats the center-`6` supply
class and center-`3` connector class as auxiliary rich classes rather than
necessarily selected rows. The selected rows at centers `3` and `6` may equal
those auxiliary classes or be disjoint from them. Exact backtracking proves no
complete assignment satisfies the same basic filters plus same-center
disjointness. This remains a finite proof-mining diagnostic only, not a proof
of row forcing, `n=9`, the bootstrap bridge, or Erdos Problem #97.

The trigger-family uniqueness audit in
`docs/bootstrap-t12-81-3-trigger-uniqueness.md` checks the specified auxiliary
trigger families used by that CSP. Since any two classes in the center-`6`
supply family intersect, and any two classes in the center-`3`
connector-avoiding family intersect, same-center distance-class disjointness
allows at most one class from each specified family in a genuine rich-class
catalogue. This narrows the auxiliary-CSP catalogue gap only; it does not prove
trigger-class existence, row forcing, `n=9`, the bootstrap bridge, or Erdos
Problem #97.

The rich-support auxiliary CSP in
`docs/bootstrap-t12-81-3-escape-rich-support-csp.md` extends that audit by
allowing the center-`6` supply object and center-`3` connector-avoiding object
to be rich supports of size larger than four. It checks all 930 support pairs
from 31 supply supports and 30 connector-avoiding supports, with selected rows
at those centers allowed to be 4-subsets of the support or disjoint 4-sets.
Exact backtracking leaves no complete assignment satisfying the same basic
filters. This remains a finite proof-mining diagnostic only, not a proof of
support existence, row forcing, `n=9`, the bootstrap bridge, or Erdos Problem
#97.

The first-supply-chain prefix CSP in
`docs/bootstrap-t12-81-3-first-supply-chains.md` lets any non-seed, non-`3`
center activate first after seed `[0,1,4]` before checking center-`6` label-`6`
supply. Exact backtracking leaves exactly three basic-filter prefix survivors,
all with first activation at center `8`, and no immediate center-`6` label-`6`
supply extension. The second-supply-chain prefix crosswalk in
`docs/bootstrap-t12-81-3-second-supply-chains.md` then allows one additional
activation from closure `[0,1,4,8]`; it leaves one center-`8` then center-`2`
prefix, with support `[1,3,4,8]`, and no immediate center-`6` label-`6`
supply extension for that prefix. The second-step-chain continuation in
`docs/bootstrap-t12-81-3-second-step-chains.md` then allows distinct
intermediate centers from `{2,5,7}` after those center-`8` prefixes before one
center-`6` supply support. It finds no surviving chain under the same basic
filters. These are bounded proof-mining diagnostics only; they do not prove
support existence, row forcing, `n=9`, the bootstrap bridge, or Erdos
Problem #97. The companion post-`8` supply-chain accounting packet in
`docs/bootstrap-t12-81-3-post8-supply-chains.md` records the raw denominator
for the same bounded model: `3,918,164,268` support catalogues reduce to `58`
initially compatible catalogues and zero selected-row completions. It has the
same diagnostic-only claim boundary.
The ordered chain-closure CSP in
`docs/bootstrap-t12-81-3-chain-closure-csp.md` then follows every eligible
sequential activation from closure `[0,1,4]`, with center `3` held back and
each new support containing at least three currently closed labels. It checks
`5916` candidate extensions, leaves four non-supply prefixes, and finds no
surviving prefix whose next activated center is `6`. This closes only the
audited sequential support-chain model; it does not prove support existence,
row forcing, genuine rich-class order, `n=9`, the bootstrap bridge, or Erdos
Problem #97.

The source-`81` row-`8` singleton-support audit in
`docs/bootstrap-t12-81-8-singleton-support-audit.md` checks a neighboring
relation-sufficient row target. It enumerates the nine center-`8` rows that
contain bootstrap-core witnesses `[0,2]` and one singleton support from
`[5,6]`. Only the original row `[0,2,5,6]` survives in the fixed source-`81`
neighborhood; in the one-row-drop relaxation, the only survivors also keep the
dropped row equal to its original source-`81` row. This remains a finite
proof-mining diagnostic only, not a proof of singleton support existence, row
forcing, `n=9`, the bootstrap bridge, or Erdos Problem #97.

The source-`81` row-`8` two-row-drop follow-up in
`docs/bootstrap-t12-81-8-singleton-support-two-row-drop.md` allows any two
non-target source-`81` rows to move. It checks `1,234,800` candidates and
leaves `28` survivors, all of which keep row `8` and both dropped rows equal
to their original source-`81` choices. This remains a finite proof-mining
diagnostic only, not a proof of singleton support existence, row forcing,
`n=9`, the bootstrap bridge, or Erdos Problem #97.

The source-`81` row-`8` full-neighborhood vertex-circle packet in
`docs/bootstrap-t12-81-8-full-neighborhood-vertex-circle.md` fixes row `8` to
the same nine activation rows but lets every other center choose any selected
4-set. Basic filters leave `34` complete assignments, including `27` with a
non-original row `8`; vertex-circle quotient replay kills all `34` by
self-edge or strict-cycle obstructions. This remains a finite proof-mining
diagnostic only, not a proof of singleton support existence, row forcing,
`n=9`, the bootstrap bridge, or Erdos Problem #97.

The source-`151` row-`6` outside-pair audit in
`docs/bootstrap-t12-151-6-outside-pair-audit.md` checks the remaining
relation-sufficient row target. It enumerates the thirteen center-`6` rows
that contain bootstrap-core witness `[0]` and one outside support pair from
`[3,5]`, `[3,8]`, or `[5,8]`. Only the original row `[0,3,5,8]` survives in
the fixed source-`151` neighborhood; in the one-row-drop relaxation, the only
survivors also keep the dropped row equal to its original source-`151` row.
This remains a finite proof-mining diagnostic only, not a proof of outside-pair
support existence, row forcing, `n=9`, the bootstrap bridge, or Erdos Problem
#97.

The source-`151` singleton-support audit in
`docs/bootstrap-t12-151-singleton-support-audit.md` covers rows `151:5` and
`151:8`. In both fixed source-`151` neighborhoods, only the original target row
survives among the nine singleton-support activation rows; in the one-row-drop
relaxations, the only survivors also keep the dropped row equal to its
original source-`151` row. This remains a finite proof-mining diagnostic only,
not a proof of singleton support existence, row forcing, `n=9`, the bootstrap
bridge, or Erdos Problem #97.

The source-`151` two-row-drop extension in
`docs/bootstrap-t12-151-singleton-two-row-drop.md` lets any unordered pair of
non-target rows move arbitrarily while the target row stays in its
bootstrap-core-plus-singleton activation family. It checks `2,469,600`
candidates across rows `151:5` and `151:8`, leaves `56` survivors, and every
survivor keeps the target row and both dropped rows equal to their source-`151`
rows. This is still finite incidence/crossing bookkeeping only, not singleton
support existence, row forcing, `n=9`, or a bridge proof.

The source-`151` full-neighborhood vertex-circle replay in
`docs/bootstrap-t12-151-singleton-full-neighborhood-vertex-circle.md` lets all
other centers move to arbitrary selected `4`-sets, then applies the exact
vertex-circle quotient replay to the basic-filter survivors. Basic filters
leave `50` complete assignments, including `36` with non-original target rows;
all `50` are killed by vertex-circle self-edge or strict-cycle obstructions.
This remains a review-pending diagnostic only, not singleton support
existence, row forcing, `n=9`, the bootstrap bridge, or Erdos Problem #97.

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

### Vertex-circle T02 shared-endpoint self-edge local lemma candidates

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

In a strictly convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, each of
the following four selected-row cores is locally impossible:

```text
T02/F01:
center 0: {1,2,3,8}
center 1: {0,2,4,7}
center 8: {0,1,4,5}

T02/F04:
center 0: {1,2,4,6}
center 1: {0,2,3,5}
center 2: {1,3,4,8}

T02/F08:
center 0: {1,2,4,8}
center 1: {0,2,3,5}
center 8: {0,1,3,7}

T02/F14:
center 0: {1,2,6,8}
center 1: {0,2,3,7}
center 8: {0,1,5,7}
```

For `F01`, `F08`, and `F14`, the selected-distance equalities force

```text
[1,8] = [0,8] = [0,1] = [1,2].
```

The relevant row-`0` witness order puts the outer chord `[1,8]` around the
inner chord `[1,2]`, so vertex-circle monotonicity gives `[1,8] > [1,2]`.
For `F04`, the selected-distance equalities force

```text
[0,2] = [0,1] = [1,2] = [2,3],
```

while the row-`1` witness order gives `[0,2] > [2,3]`. Thus each T02 core
creates a reflexive strict edge in the selected-distance quotient, and no
strictly convex realization can satisfy that exact local core in the displayed
cyclic order.

The packet label `T02` and family labels `F01`, `F04`, `F08`, and `F14` are
navigation only; the hypotheses are the displayed cyclic order and selected
rows. This is not an `n=9` completeness proof, not a promotion of the
review-pending exhaustive checker, and not a proof of Erdos Problem #97. Check
the focused packet and its small input-data replay with
`python scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py --check --assert-expected --json`
and
`python scripts/check_n9_t02_self_edge_minireplay.py --check --assert-expected --json`.

### Vertex-circle T03 multi-family self-edge local lemma candidates

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

In a strictly convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, each of
the following two selected-row cores is locally impossible:

```text
T03/F05:
center 1: {2,5,7,8}
center 2: {1,3,4,8}
center 3: {0,2,4,7}
center 6: {1,3,5,7}

T03/F15:
center 0: {1,3,4,8}
center 1: {0,2,4,5}
center 2: {1,3,5,6}
center 3: {2,4,6,7}
```

For `F05`, the selected-distance equalities force

```text
[3,7] = [2,3] = [1,2] = [1,7].
```

The row-`6` witness order `[7,1,3,5]` puts the outer chord `[3,7]` around the
inner chord `[1,7]`, so vertex-circle monotonicity gives `[3,7] > [1,7]`.
For `F15`, the selected-distance equalities force

```text
[1,4] = [1,2] = [2,3] = [3,4],
```

while the row-`0` witness order `[1,3,4,8]` gives `[1,4] > [3,4]`. Thus each
T03 core creates a reflexive strict edge in the selected-distance quotient,
and no strictly convex realization can satisfy that exact local core in the
displayed cyclic order.

The checked packet covers 20 frontier assignments across `F05` and `F15`, but
that assignment count is packet-catalog evidence only. The packet label `T03`
and family labels `F05` and `F15` are navigation only; the hypotheses are the
displayed cyclic order and selected rows. This is not an `n=9` completeness
proof, not a promotion of the review-pending exhaustive checker, and not a
proof of Erdos Problem #97. Check the focused packet and its small input-data
replay with
`python scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py --check --assert-expected --json`
and
`python scripts/check_n9_t03_self_edge_minireplay.py --check --assert-expected --json`.

### Vertex-circle T04/F13 selected-path self-edge local lemma candidate

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

In a strictly convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, suppose the
following four selected rows are present:

```text
center 0: {1,2,5,7}
center 1: {2,3,6,8}
center 3: {1,4,5,8}
center 5: {1,3,6,7}
```

The selected-distance equalities force

```text
[1,5] = [3,5] = [1,3] = [1,2].
```

Meanwhile row `0` has witness order `[1,2,5,7]` around vertex `0`, so the
outer chord `[1,5]` strictly contains the inner chord `[1,2]`. The
vertex-circle chord monotonicity lemma gives

```text
[1,5] > [1,2].
```

Thus the selected-distance quotient has a reflexive strict edge, and no
strictly convex realization can satisfy these exact local hypotheses. The
checked packet covers two frontier assignments in family `F13`, but that count
is packet-catalog evidence only. The packet label `T04/F13` is navigation
only; the hypotheses are the displayed cyclic order and selected rows. This is
not an `n=9` completeness proof, not a promotion of the review-pending
exhaustive checker, and not a proof of Erdos Problem #97. Check the focused
packet and its small input-data replay with
`python scripts/check_n9_vertex_circle_t04_self_edge_lemma_packet.py --check --assert-expected --json`
and
`python scripts/check_n9_t04_self_edge_minireplay.py --check --assert-expected --json`.

### Vertex-circle T05/F10 selected-path self-edge local lemma candidate

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

In a strictly convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, suppose the
following four selected rows are present:

```text
center 0: {1,2,4,8}
center 2: {1,3,4,7}
center 7: {2,5,6,8}
center 8: {0,1,6,7}
```

The selected-distance equalities force

```text
[1,8] = [7,8] = [2,7] = [1,2].
```

Meanwhile row `0` has witness order `[1,2,4,8]` around vertex `0`, so the
outer chord `[1,8]` strictly contains the inner chord `[1,2]`. The
vertex-circle chord monotonicity lemma gives

```text
[1,8] > [1,2].
```

Thus the selected-distance quotient has a reflexive strict edge, and no
strictly convex realization can satisfy these exact local hypotheses. The
checked packet covers 18 frontier assignments in family `F10`, but that count
is packet-catalog evidence only. The packet label `T05/F10` is navigation
only; the hypotheses are the displayed cyclic order and selected rows. This is
not an `n=9` completeness proof, not a promotion of the review-pending
exhaustive checker, and not a proof of Erdos Problem #97. Check the focused
packet and its small input-data replay with
`python scripts/check_n9_vertex_circle_t05_self_edge_lemma_packet.py --check --assert-expected --json`
and
`python scripts/check_n9_t05_self_edge_minireplay.py --check --assert-expected --json`.

### Vertex-circle T06/F11 selected-path self-edge local lemma candidate

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

In a strictly convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, suppose the
following five selected rows are present:

```text
center 1: {0,3,5,8}
center 5: {0,3,4,7}
center 6: {2,5,7,8}
center 7: {0,1,5,6}
center 8: {2,3,6,7}
```

The selected-distance equalities force

```text
[3,8] = [6,8] = [6,7] = [5,7] = [3,5].
```

Meanwhile row `1` has witness order `[3,5,8,0]` around vertex `1`, so the
outer chord `[3,8]` strictly contains the inner chord `[3,5]`. The
vertex-circle chord monotonicity lemma gives

```text
[3,8] > [3,5].
```

Thus the selected-distance quotient has a reflexive strict edge, and no
strictly convex realization can satisfy these exact local hypotheses. The
checked packet covers 18 frontier assignments in family `F11`, but that count
is packet-catalog evidence only. The packet label `T06/F11` is navigation
only; the hypotheses are the displayed cyclic order and selected rows. This is
not an `n=9` completeness proof, not a promotion of the review-pending
exhaustive checker, and not a proof of Erdos Problem #97. Check the focused
packet and its small input-data replay with
`python scripts/check_n9_vertex_circle_t06_self_edge_lemma_packet.py --check --assert-expected --json`
and
`python scripts/check_n9_t06_self_edge_minireplay.py --check --assert-expected --json`.

### Vertex-circle T07/F06 selected-path self-edge local lemma candidate

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

In a strictly convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, suppose the
following five selected rows are present:

```text
center 0: {1,2,4,7}
center 2: {0,1,4,6}
center 4: {1,3,5,7}
center 5: {3,4,6,8}
center 6: {0,2,5,7}
```

The selected-distance equalities force

```text
[1,4] = [4,5] = [5,6] = [2,6] = [1,2].
```

Meanwhile row `0` has witness order `[1,2,4,7]` around vertex `0`, so the
outer chord `[1,4]` strictly contains the inner chord `[1,2]`. The
vertex-circle chord monotonicity lemma gives

```text
[1,4] > [1,2].
```

Thus the selected-distance quotient has a reflexive strict edge, and no
strictly convex realization can satisfy these exact local hypotheses. The
checked packet covers 18 frontier assignments in family `F06`, but that count
is packet-catalog evidence only. The packet label `T07/F06` is navigation
only; the hypotheses are the displayed cyclic order and selected rows. This is
not an `n=9` completeness proof, not a promotion of the review-pending
exhaustive checker, and not a proof of Erdos Problem #97. Check the focused
packet and its small input-data replay with
`python scripts/check_n9_vertex_circle_t07_self_edge_lemma_packet.py --check --assert-expected --json`
and
`python scripts/check_n9_t07_self_edge_minireplay.py --check --assert-expected --json`.

### Vertex-circle T08/F02 selected-path self-edge local lemma candidate

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

In a strictly convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, suppose the
following six selected rows are present:

```text
center 0: {1,2,3,8}
center 1: {0,3,4,7}
center 2: {1,3,5,6}
center 5: {2,4,6,7}
center 6: {1,5,7,8}
center 7: {0,1,4,6}
```

The selected-distance equalities force

```text
[1,3] = [1,7] = [6,7] = [5,6] = [2,5] = [1,2].
```

Meanwhile row `0` has witness order `[1,2,3,8]` around vertex `0`, so the
outer chord `[1,3]` strictly contains the inner chord `[1,2]`. The
vertex-circle chord monotonicity lemma gives

```text
[1,3] > [1,2].
```

Thus the selected-distance quotient has a reflexive strict edge, and no
strictly convex realization can satisfy these exact local hypotheses. The
checked packet covers 18 frontier assignments in family `F02`, but that count
is packet-catalog evidence only. The packet label `T08/F02` is navigation
only; the hypotheses are the displayed cyclic order and selected rows. This is
not an `n=9` completeness proof, not a promotion of the review-pending
exhaustive checker, and not a proof of Erdos Problem #97. Check the focused
packet and its small input-data replay with
`python scripts/check_n9_vertex_circle_t08_self_edge_lemma_packet.py --check --assert-expected --json`
and
`python scripts/check_n9_t08_self_edge_minireplay.py --check --assert-expected --json`.

### Vertex-circle T09/F03 selected-path self-edge local lemma candidate

Status: `REVIEW_PENDING_LOCAL_LEMMA_CANDIDATE`.

In a strictly convex nonagon with cyclic order `0,1,2,3,4,5,6,7,8`, suppose the
following six selected rows are present:

```text
center 0: {1,2,3,8}
center 1: {0,3,5,7}
center 2: {1,3,4,6}
center 3: {2,4,5,8}
center 4: {0,3,6,8}
center 8: {0,1,4,7}
```

The selected-distance equalities force

```text
[1,3] = [0,1] = [0,8] = [4,8] = [3,4] = [2,3] = [1,2].
```

Meanwhile row `0` has witness order `[1,2,3,8]` around vertex `0`, so the
outer chord `[1,3]` strictly contains the inner chord `[1,2]`. The
vertex-circle chord monotonicity lemma gives

```text
[1,3] > [1,2].
```

Thus the selected-distance quotient has a reflexive strict edge, and no
strictly convex realization can satisfy these exact local hypotheses. The
checked packet covers 18 frontier assignments in family `F03`, but that count
is packet-catalog evidence only. The packet label `T09/F03` is navigation
only; the hypotheses are the displayed cyclic order and selected rows. This is
not an `n=9` completeness proof, not a promotion of the review-pending
exhaustive checker, and not a proof of Erdos Problem #97. Check the focused
packet and its small input-data replay with
`python scripts/check_n9_vertex_circle_t09_self_edge_lemma_packet.py --check --assert-expected --json`
and
`python scripts/check_n9_t09_self_edge_minireplay.py --check --assert-expected --json`.

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
Check the focused packet and its small input-data replay with
`python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py --check --assert-expected --json`
and
`python scripts/check_n9_t10_strict_cycle_minireplay.py --check --assert-expected --json`.

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

### Closest-pair radius barrier

Status: `LEMMA` / structural necessary condition.

Let `delta` be the global minimum distance between two distinct vertices of a
strictly convex polygon. If `p` is an endpoint of a pair at distance `delta`,
then at most three other vertices lie at distance `delta` from `p`.

Indeed, four such vertices would lie on the circle of radius `delta` centered
at `p`. Their angular span around the hull vertex `p` is strictly less than
`pi`. Since `delta` is the global closest-pair distance, every consecutive
angular gap among those four circle points must be at least `pi/3`; otherwise
the corresponding chord would have length less than `delta`. Three such gaps
force span at least `pi`, a contradiction. See
`docs/closest-pair-radius-barrier.md`.

Thus in any counterexample, every endpoint of a globally closest pair must use
a four-rich distance class at radius strictly larger than the closest-pair
distance. This is a structural constraint only, not a proof of Erdos #97.

### Threefold pair-lift obstruction

Status: `LEMMA` / `FAILED_SEARCH_MECHANISM`.

No finite nondegenerate union of full 3-fold rotational orbits can be 4-bad by
the mechanism where each point uses its two same-orbit mates and an
equidistant pair from one other full 3-fold orbit. If

```text
O_p = {p, omega*p, omega^2*p},  omega = exp(2*pi*i/3),
```

then the same-orbit witness radius from `p = r*exp(i*theta)` is
`sqrt(3)*r`. For a distinct orbit `O_q` to provide two more witnesses at that
same radius, its phase must be opposite to `theta` modulo `2*pi/3` and its
radius must be `2*r`; the same-phase positive solution only gives the original
orbit back. Thus every orbit would need an outgoing partner with doubled
radius, impossible in a finite directed cycle. See
`docs/threefold-pair-lift-obstruction.md`.

This is a narrow mechanism obstruction, not a general exclusion of 3-fold
symmetric configurations and not a proof of Erdos #97.

### Cyclic polygon subcase

If all vertices lie on one circle, then no vertex has more than two other
vertices at any one distance. A second circle centered at the vertex intersects
the common circumcircle in at most two points.[^syn]

### Ellipse model case

Status: `LEMMA` / `FAILED_SEARCH_FAMILY`.

No finite point set on a Euclidean ellipse can be a counterexample to Erdos
Problem #97. The circle case is the cyclic polygon subcase above. For a
noncircular ellipse, after Euclidean normalization write

```text
p(t) = (a*cos(t), b*sin(t)),  lambda = a^2/b^2 > 1.
```

For any center parameter `tau`, four equal-distance witness parameters satisfy

```text
(1/4) * sum_k cos(t_k) = (lambda/(lambda - 1))*cos(tau).
```

Choosing a parameter with maximal positive cosine, or otherwise with minimal
negative cosine, contradicts the same identity. See
`docs/ellipse-model-case.md`.

This is a restricted exact obstruction only. It does not imply that arbitrary
strictly convex polygons reduce to elliptical configurations.

### Parabola model case

Status: `LEMMA` / `FAILED_SEARCH_FAMILY`.

No finite point set on a nondegenerate affine parabola can be a counterexample
to Erdos Problem #97. More precisely, for

```text
gamma(t) = p0 + u*t + v*t^2
```

with `u,v` linearly independent, and for any finite set of distinct parameters
`T`, each endpoint parameter gives a good vertex. If `M = max T`, then a
positive-radius equation centered at `gamma(M)` is a quartic polynomial in the
parameter. Since it is negative at `M` and tends to `+infinity` as
`t -> +infinity`, it has a root outside the parameter interval. Four available
witness parameters below `M` would then give five distinct real roots of a
quartic, impossible. See `docs/parabola-model-case.md`.

This is a restricted exact obstruction only. It does not imply that arbitrary
strictly convex polygons reduce to parabolic configurations.

### Hyperbola branch model case

Status: `LEMMA` / `FAILED_SEARCH_FAMILY`.

No finite point set on one branch of a nondegenerate Euclidean hyperbola can be
a counterexample to Erdos Problem #97. After Euclidean normalization write

```text
p(s) = (a*cosh(s), b*sinh(s)),  a,b > 0.
```

For any center parameter `sigma`, four equal-distance witness parameters
satisfy

```text
(1/4) * sum_k cosh(s_k) =
  (a^2/(a^2 + b^2))*cosh(sigma).
```

Choosing a sampled parameter minimizing `cosh(sigma)` contradicts the identity,
since all witnesses on the same branch have `cosh(s_k) >= cosh(sigma)` while
the multiplier is strictly less than `1`. See
`docs/hyperbola-branch-model-case.md`.

This is a restricted exact obstruction only. It does not cover point sets using
both branches of a hyperbola, and it does not imply that arbitrary strictly
convex polygons reduce to hyperbolic configurations.

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
