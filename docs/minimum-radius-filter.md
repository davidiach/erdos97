# Minimum-radius short-chord filter

Status: `LEMMA` / exact necessary filter for fixed cyclic orders.

No general proof of Erdos Problem #97 is claimed. No counterexample is claimed.

## Lemma

Fix a selected-witness pattern `S_i` and a cyclic order of a strict convex
polygon realizing it. Let `r_i` be the selected radius at row `i`. If `i` has
globally minimum selected radius, then in the angular order of the four
witnesses `S_i` around `i`, at least one consecutive witness pair `{a,b}` is
uncovered by selected incidence:

```text
b notin S_a and a notin S_b.
```

Equivalently, if every consecutive witness pair around `i` is selected in at
least one direction, then `i` cannot be a minimum-radius center. If this blocks
every possible minimum center in a fixed cyclic order, that order is
impossible.

## Proof

At a strict convex hull vertex, all other vertices lie in the open angular cone
between the two incident edges, except for the two adjacent boundary vertices.
The angular span is therefore less than `pi` for the four selected witnesses.

Put the four witnesses in angular order around center `i`, with consecutive
angular gaps `delta_1, delta_2, delta_3`. Since

```text
delta_1 + delta_2 + delta_3 < pi,
```

at least one gap is smaller than `pi/3`. If `{a,b}` is the witness pair across
that gap, then

```text
|p_a - p_b| = 2 r_i sin(delta/2) < r_i.
```

If `b in S_a`, then `r_a = |p_a-p_b| < r_i`. If `a in S_b`, then
`r_b = |p_a-p_b| < r_i`. Either case contradicts global minimality of `r_i`.
Thus at least one consecutive witness pair around a minimum-radius center must
be uncovered in both directions.

## What the filter proves and does not prove

This is only a necessary condition. A row that has an uncovered consecutive
witness pair is not geometrically certified; it merely survives this one
minimum-radius test.

The order-free version is stronger but rare: if all six pairs among the four
witnesses of row `i` are selected in at least one direction, then `i` is blocked
for every possible cyclic order. If every center is order-free blocked, the
fixed selected pattern is impossible. The complete `n=5` all-other-vertices
pattern is a toy example killed this way.

There is also an order-free escape certificate in the other direction. Build
the covered-pair graph on the four witnesses of row `i`, joining two witnesses
when at least one endpoint selects the other. The row can be blocked in some
local witness order exactly when this covered-pair graph has a Hamiltonian path.
If it has no such path, every possible local witness order has an uncovered
consecutive pair, so that row always survives the minimum-radius short-chord
test. If every row has this property, then every cyclic order admits the
all-empty radius-propagation choice. This certifies a blind spot of the filter,
not geometric realizability.

## Current impact on built-in patterns

The current built-in candidate patterns all pass the natural-order version of
this filter; every center remains compatible with being the minimum-radius
center under this filter alone. This includes the main live abstract-incidence
pattern `C19_skew`.

For `C19_skew` in the natural order, row `0` has

```text
S_0 = {5, 9, 11, 16}
witness order = [5, 9, 11, 16]
consecutive pairs = {5,9}, {9,11}, {11,16}
uncovered consecutive pairs = {5,9}, {9,11}
```

Thus the minimum-radius idea does not by itself kill `C19_skew`. It should be
recorded as a weak exact filter, not promoted as a central route unless it is
combined with additional cyclic-order or radius-inequality propagation.

For the sparse/Sidon frontier, the issue is sharper: in the natural order every
frontier row has at least one uncovered consecutive witness pair, so the current
radius-propagation filter can choose an all-empty set of short gaps and force no
strict radius inequalities. For `C19_skew`, `C25_sidon_2_5_9_14`, and
`C29_sidon_1_3_7_15`, the new covered-path test certifies that this all-empty
escape persists for every cyclic order. The `C13_sidon_1_2_4_10` pattern does
not have this order-free escape certificate, which is why adversarial cyclic
orders remain useful for it. See `docs/sparse-frontier-diagnostic.md`.

## Reproducible check

```bash
python scripts/check_min_radius_filter.py --pattern C19_skew --assert-pass
python scripts/check_min_radius_filter.py --pattern C19_skew --json
```

The first command should report `PASS`, with all 19 centers still possible as
minimum centers. This is not evidence for realizability; it is a negative
result for this particular proposed attack.
