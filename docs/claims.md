# Claims ledger

This file is proof-facing. Numerical near-misses live in `data/runs/` and in the
candidate/failed-route docs, not as proofs of equality.

## Proof-facing claims

This ledger records local proof-facing claims and their current trust posture.
It is not a claim about the global problem. The elementary geometric theorem
below settles the repo-local small cases `n <= 8`; selected-witness computation
independently corroborates that result. The global Erdos #97 problem remains
falsifiable/open.

### Theorem: no bad strictly convex polygon for n <= 8

Status: `REPO_LOCAL_THEOREM` (elementary geometric proof). The proof was
line-by-line rederived twice in the 2026-07-09 repository audit; independent
external/publication review remains encouraged and is not claimed.

Let `A` be the vertex set of a strictly convex polygon. If every vertex of
`A` has four other vertices at one common distance, then `|A| >= 9`.

The proof in `docs/n8-geometric-proof.md` counts apex-marked isosceles
triangles. Base-pair capacity gives `T(A) <= n(n-2)`, while badness gives
`T(A) >= 6n`. Equality for `n=8` forces an equilateral octagon and makes every
length-3 diagonal have an apex on its two-vertex boundary side. Hence every
adjacent pair of exterior turns contains a turn of size `2*pi/3`; at least
four such turns are required, contradicting their total `2*pi`.

This theorem says nothing about `n >= 9` and does not change the official
falsifiable/open status of Erdos Problem #97.

### Machine-checked corroboration for n <= 8

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

This is a compact literature-backed shortcut, not the basis for the repository
status. The elementary proof in `docs/n8-geometric-proof.md` is the primary
repo-local `n <= 8` theorem; the selected-witness artifacts remain independent
machine-checked corroboration.

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

### Selected-path self-edge obstruction

Status: `LEMMA`.

Let selected rows generate an equivalence relation on unordered vertex-pair
distances. If a local row core contains a selected-distance equality path from
an unordered pair `p` to an unordered pair `q`, and a valid vertex-circle
strict inequality `p > q`, then that local core is unrealizable. The equality
path gives `D(p) = D(q)`, while the strict inequality gives `D(p) > D(q)`.
Equivalently, the strict quotient graph has a reflexive strict edge.

This is an n-independent local contradiction criterion only. It does not show
that any hypothetical counterexample must contain such a core, does not
complete the review-pending `n=9` packet audit, and does not prove Erdos
Problem #97. See `docs/n9-vertex-circle-self-edge-criterion.md`.

### Directed strict-cycle obstruction

Status: `LEMMA`.

Let selected rows generate an equivalence relation on unordered vertex-pair
distances. If a local row core contains a cyclic list of valid vertex-circle
strict inequalities `p_i > q_i`, and selected-distance equality paths from
each `q_i` to the next `p_{i+1}`, then that local core is unrealizable. The
equalities turn the strict inequalities into

```text
D(p_0) > D(p_1) > ... > D(p_{k-1}) > D(p_0),
```

which is impossible for real distances. Equivalently, the strict quotient graph
has a directed strict cycle.

This is an n-independent local contradiction criterion only. It does not show
that any hypothetical counterexample must contain such a core, does not
complete the review-pending `n=9` packet audit, and does not prove Erdos
Problem #97. See `docs/n9-vertex-circle-strict-cycle-criterion.md`.

### Strict quotient-graph obstruction

Status: `LEMMA`.

For any local selected-row core with certified vertex-circle strict edges,
quotient unordered vertex-pair distances by the selected-row equalities. If
the resulting strict quotient graph has a loop or a directed cycle, then the
core is unrealizable. In any realization, every strict edge strictly decreases
the real distance value of its quotient class, so loops and directed cycles
would force a strict inequality chain returning to its starting value. The
same criterion applies to a supplied rich same-radius class by quotienting all
center-witness spoke distances in that class and using the strict nested-chord
inequalities from its full witness set.

This is the common abstraction behind the selected-path self-edge and directed
strict-cycle obstruction lemmas above. It is only a local obstruction
criterion: acyclicity of the strict quotient graph does not imply geometric
realizability, and the lemma does not prove that every hypothetical
counterexample contains a quotient-graph obstruction. See
`docs/n9-vertex-circle-quotient-soundness-audit.md`.

Corollary: a nonempty finite closed descent region is also impossible. That is,
if `H` is a finite nonempty set of selected-distance quotient classes and
every class in `H` has at least one strict quotient-graph edge to a class in
`H`, possibly itself, then following one such edge repeatedly forces a
directed cycle.
The helper `validate_closed_descent_region` checks this certificate shape for
supplied strict quotient graphs, including graphs built from exact-four
selected rows or rich same-radius rows. This corollary is a bridge target, not
a proof that minimal counterexamples have such a region.

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
`data/certificates/c25_c29_