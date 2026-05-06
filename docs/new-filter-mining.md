# New filter mining

Status: `EXPLORATORY` — three new exact filters added to the lemma library.
None produced kills strictly novel beyond the existing obstruction battery
on registered fixed-pattern catalog entries, but they expose new structural
information and re-derive several known kills via independent paths.

This note records the work done in `src/erdos97/new_filters.py` and
`scripts/test_new_filters.py`.  The main goal was to extract clean
selected-witness-pattern obstructions from the prompt's seven attack
angles (Cayley-Menger, Ptolemy, inscribed-angle, Stewart, Möbius
inversion, paraboloid lift, integer-rank LP).  Inversion (test
`data/certificates/inversion_filter_test.json`) and paraboloid lift
(test `data/certificates/paraboloid_lift_test.json`) were already mined
and produced no kills.

## Summary of the filter ideas attempted

| Filter | Direction | Status | Adds new kills? |
|---|---|---|---|
| **Kite identity (squared distances)** | Integer-rank LP | Implemented | No new kills, but exposes useful forced-equal classes |
| **Row-chord-order** (built on top of kite) | Inscribed angle / L7 | Implemented | Kills C9, C12, C13, P24 in natural order (overlap with crossing-bisector) |
| **Few-distance 5-tuple** (built on top of kite) | Cayley-Menger 5-point degeneration | Implemented | No fired obstruction on any built-in pattern |
| **Triple-shared witness rank** | Inscribed angle / projective | Implemented (informational) | No fired obstruction |
| **Kite-row collapse** | L7 + radius equivalence | Implemented (informational) | No fired obstruction |

## Filter 1: kite identity in squared-distance space

**Statement.** For every mutual phi 2-cycle `e = {x,y}, f = {a,b}`
(``phi(e) = f`` and ``phi(f) = e``), the rhombus geometry `{p_x, p_y,
p_a, p_b}` has perpendicular diagonals crossing at their common
midpoint.  By the Pythagorean theorem on the four right triangles, the
"diagonal-corner" length squared equals one quarter of the sum of the
diagonal lengths squared:

```text
4 |p_x - p_a|^2 = |p_x - p_y|^2 + |p_a - p_b|^2.
```

The four diagonal-corner identities are linear consequences of this one
plus the row-equalities `|p_x - p_a|^2 = |p_x - p_b|^2 = |p_y - p_a|^2
= |p_y - p_b|^2`.

**Why the filter is novel.** The existing `mutual_midpoint_matrix`
encodes the *coordinate-level* midpoint coincidence ``p_x + p_y = p_a +
p_b``.  The kite identity above is its *squared-distance shadow*:
midpoint plus perpendicularity collapses to one linear equation in
unknown squared distances.  In squared-distance space, this is a
constraint that the row-equality system alone does not imply.

**Implementation.** `kite_identity_matrix(S)` builds the integer matrix
with one column per unordered chord ``(p,q)``, ``p<q``, encoding both
the row-equalities `X_{i,w_a} - X_{i,w_b} = 0` and the kite identity
`4 X_{x,a} - X_{x,y} - X_{a,b} = 0` per mutual phi 2-cycle.
`kite_identity_obstruction(S)` reports the matrix rank, the free
parameters, the forced-equal squared-distance classes, and any forced
zero squared distances (which would indicate vertex coincidence).

**Empirical results on the 14 built-in patterns.**

| Pattern | n | rank | free | classes |
|---|---|---|---|---|
| C9_pm_2_4   |  9 | 26 |  10 | 2 (sizes 18, 9)  |
| C12_pm_2_5  | 12 | 35 |  31 | 2 (sizes 24, 12) |
| C13_pm_3_5  | 13 | 38 |  40 | 2 (sizes 13, 26) |
| C16_pm_1_6  | 16 | 47 |  73 | 1 (size 32)      |
| C20_pm_4_9  | 20 | 59 | 131 | 1 (size 40)      |
| C17_skew    | 17 | 51 |  85 | 17 |
| C19_skew    | 19 | 57 | 114 | 19 |
| P18_parity  | 18 | 54 |  99 | 9  |
| P24_parity  | 24 | 59 | 217 | 1 (size 24) |
| B12_3x4     | 12 | 35 |  31 | 1 (size 24) |
| B20_4x5     | 20 | 64 | 126 | 1 (size 40) |
| C13_sidon_1_2_4_10 | 13 | 39 |  39 | 13 |
| C25_sidon   | 25 | 75 | 225 | 25 |
| C29_sidon   | 29 | 87 | 319 | 29 |

No forced-zero squared distance occurs on any built-in pattern, so the
filter does not directly fire as an obstruction.  The forced-equal
classes are however very informative.

## Filter 2: row-chord-order

**Statement (with cyclic order).** Let `i` be a center with witnesses
`w_0, w_1, w_2, w_3` in cyclic angular order around `p_i`.  By L7
(chord formula on a circle of radius `r_i`), the chord length
`|w_a - w_b|` is strictly monotone in the angular gap `b - a`
(positions in 0..3).  In particular, the gap-3 chord `|w_0 - w_3|` is
strictly longer than every gap-1 or gap-2 chord.

If the kite identity + row-equalities force two row-internal chords
into the same squared-distance class but their angular gaps (in the
supplied cyclic order) differ, the pattern is exactly obstructed in
that order.

**Why the filter is novel.** The existing `crossing_bisector` filter
only checks chord *crossings*, not chord *lengths*.  The existing
`min_radius_filter` checks consecutive-pair coverage, not equal-length
identifications.  The row-chord-order filter is the cleanest L7-based
within-row contradiction we know.

**Empirical results.** In natural cyclic order, the filter fires on:

```
C9_pm_2_4         18 violations
C12_pm_2_5        24 violations
C13_pm_3_5        26 violations
P24_parity        24 violations
```

These are all already known obstructed patterns, killed by other
filters (mutual-rhombus collapse for C9, C12, C13; crossing-bisector
adjacency for P24).  The new filter re-derives the kills via an
independent route: same forced-equal classes, but checked against L7
within-row monotonicity instead of midpoint matrix nullspace or chord
crossings.

`B12_3x4_danzer_lift`, `C16_pm_1_6`, `C20_pm_4_9`, `B20_4x5_FR_lift`,
and other obstructed patterns *do not* fire row_chord_order in natural
order — their forced-equal classes contain row-radii but not inter-
witness chords.

## Filter 3: few-distance 5-tuple

**Statement.** Let `{x, y, a, b}` be a mutual phi 2-cycle (rhombus on
four labels) and let `c` be any fifth distinct vertex label.  If all 10
chord-pairs among `{x, y, a, b, c}` lie in a single forced-equal class
of the kite-identity matrix, the 5 points are pairwise equidistant.
This is impossible in `R^2` (any 4 pairwise equidistant points have
non-zero Cayley-Menger determinant `4 r^6`, so at most 3 pairwise
equidistant points exist).  Exact obstruction.

**Empirical results.** No built-in pattern triggers this filter — even
when forced-equal classes are very large (e.g. size 40 in C20), they
do not extend to a 5-point all-equal subset.  The filter is included
for completeness because it is cheap once the kite matrix is computed
and may fire on patterns outside the current catalog.

## Filter 4: triple-shared-witness (informational)

For each label `v`, list mutual phi 2-cycles whose chord pair
``({x,y},{a,b})`` contains `v`.  When `v` is shared by `>=3` such
2-cycles, the three center chords through `v`'s neighborhood form a
constrained pencil.

Currently informational (does not fire as an obstruction); listed in
the report so future strengthening (rank check on the chord-direction
matrix) can use it.

## Filter 5: kite-row-collapse (informational)

The kite identity `4 X_{x,a} = X_{x,y} + X_{a,b}` combined with row
equalities at center `x` (so `X_{x,a} = r_x^2`) and at center `y`
gives `4 r_x^2 = X_{x,y} + X_{a,b} = 4 r_y^2`, i.e. `r_x = r_y`.
Mutual phi 2-cycles thus partition centers into equal-radius
equivalence classes.

When the equivalence reduces to a single class, the polygon has
uniform selected radius (the open Erdős-Fishburn subcase, §5.5 of the
canonical synthesis).  Otherwise the partition is informative but not
directly obstructive without further chord-length comparisons.

## Honest assessment

- The kite-identity filter is **mathematically novel** as a squared-
  distance linear system but produces **no exact obstructions on its
  own** for the catalog patterns.
- The row-chord-order filter **does fire** on known-obstructed
  patterns C9, C12, C13, P24 in natural order, providing an independent
  (and arguably simpler) obstruction proof.  It does **not** add kills
  beyond the union of mutual-rhombus and crossing-bisector filters on
  the registered catalog.
- The few-distance-5 filter is an exact necessary condition but does
  not fire on any built-in pattern.
- Triple-shared-witness and kite-row-collapse are informational; both
  could be strengthened to obstructions with additional metric data.

The filters are exact (rational arithmetic only, no numerics) and
provably necessary for any 4-regular selected-witness counterexample.

## Files

- `src/erdos97/new_filters.py` — five filter implementations and combined
  runner.
- `scripts/test_new_filters.py` — runs all filters on every built-in
  pattern, writes `data/certificates/new_filters_test.json`.
- `data/certificates/new_filters_test.json` — full machine-readable
  results.
- `docs/new-filter-mining.md` — this document.

## Future work

1. **Cayley-Menger 6-point determinant** on rhombus + two extras — when
   rhombus chains overlap, more squared-distance constraints are
   forced, and CM determinant might collapse to non-zero polynomial.
2. **Combine kite identity with global Ptolemy** — if a row's forced
   class includes inter-witness chords, the row-circle Ptolemy equality
   becomes a polynomial in fewer free parameters.
3. **Rank arguments on the perpendicularity graph** — three independent
   perpendicularity directions through a vertex should be impossible
   in `R^2`; an integer-rank check on chord-direction subspaces might
   formalize this.
