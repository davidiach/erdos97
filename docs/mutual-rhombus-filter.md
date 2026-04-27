# Mutual-rhombus filter

Status: `EXACT_OBSTRUCTION` for fixed selected-witness incidence patterns.

## Summary

This note records two exact filters:

1. crossing-bisector: a two-overlap row-pair forces the source chord and the
   common-witness chord to cross at the witness chord midpoint;
2. mutual-rhombus: a reciprocal `phi` 2-cycle gives an exact midpoint equality.

These are fixed-pattern obstructions. They do not prove Erdos Problem #97.

## Crossing-bisector lemma

Let `P` be a strictly convex polygon with selected witness sets `S_i`. If

```text
S_x cap S_y = {a,b}
```

for distinct centers `x,y`, then:

1. the line `p_x p_y` is the perpendicular bisector of segment `p_a p_b`;
2. segment `p_x p_y` contains the midpoint of segment `p_a p_b`;
3. chords `{x,y}` and `{a,b}` cross in the cyclic order;
4. neither `{x,y}` nor `{a,b}` is a polygon edge.

Proof. Since `a,b in S_x cap S_y`, both `p_x` and `p_y` are equidistant from
`p_a` and `p_b`. Hence both centers lie on the perpendicular bisector of
segment `p_a p_b`, so the line `p_x p_y` is that perpendicular bisector.

Let

```text
m = (p_a + p_b)/2.
```

The point `m` lies on segment `ab`, hence in `conv(P)`, and also lies on the
line `xy`.

If `xy` were a polygon edge, its line would support the strictly convex polygon.
But `a` and `b` lie on opposite sides of their perpendicular bisector, a
contradiction. Hence `xy` is a diagonal.

For a strictly convex polygon, the intersection of the line through two
nonadjacent vertices `x,y` with `conv(P)` is exactly the segment `[p_x,p_y]`.
Since `m` lies on that line and in `conv(P)`, `m in [p_x,p_y]`.

Also `m` lies in the relative interior of `[p_a,p_b]`. Therefore chords `xy`
and `ab` cross at `m`. A polygon boundary edge cannot be crossed in its
relative interior by a chord contained in the convex polygon, so `ab` is not a
polygon edge either.

Consequently,

```text
adjacent x,y  =>  |S_x cap S_y| <= 1
```

and, for any proposed cyclic order,

```text
|S_x cap S_y| = 2  =>  chord {x,y} crosses chord S_x cap S_y.
```

## Sharpened n >= 8 lower bound

Let

```text
d_v = #{ i : v in S_i }.
```

Then `sum_v d_v = 4n`, and Jensen gives

```text
sum_v binom(d_v,2) >= n * binom(4,2) = 6n.
```

Also

```text
sum_v binom(d_v,2) = sum_{i<j} |S_i cap S_j|.
```

By the two-circle cap, every row-pair has intersection size at most `2`. By the
adjacent-row consequence above, the `n` adjacent row-pairs have intersection
size at most `1`. Therefore

```text
sum_{i<j} |S_i cap S_j|
  <= n + 2*(binom(n,2) - n)
  = n(n-2).
```

Thus `6n <= n(n-2)`, so every selected-witness counterexample satisfies

```text
n >= 8.
```

This is a shorter exact proof excluding `n <= 7`. The repo still keeps the
Fano enumeration for `n=7` because it is structurally useful and reproducible.
The existing `n <= 8` theorem still depends on the separate exact `n=8`
pipeline.

For `n=8`, equality holds throughout the count. Thus every witness indegree is
4, adjacent row-pairs have intersection size 1, and nonadjacent row-pairs have
intersection size 2. The `phi` map is therefore defined on all 20 diagonals of
the octagon. Since the pair-sharing cap makes this map injective on diagonals,
it is a crossing permutation of the 20 octagon diagonals. This is a useful
compression of the `n=8` search target, not a substitute for the checked exact
survivor analysis.

## The phi map

For a row-pair with exactly two common witnesses, define

```text
phi({x,y}) = S_x cap S_y.
```

The source and target are unordered chords.

## Mutual-rhombus lemma

If

```text
phi(e) = f
phi(f) = e
```

for unordered chords `e={x,y}` and `f={a,b}`, then `e` and `f` are mutual
perpendicular bisectors. Therefore they share a midpoint:

```text
p_x + p_y = p_a + p_b.
```

This yields an exact integer linear equation on scalar label variables:

```text
X_x + X_y - X_a - X_b = 0.
```

The same equation holds separately for the two coordinate axes. If exact
rational row reduction of the resulting matrix forces `X_u = X_v` for distinct
labels `u,v`, then any geometric realization has `p_u = p_v`, so the fixed
selected pattern cannot realize a strictly convex polygon.

This kills fixed selected-witness incidence patterns. It does not prove that no
other 4-subset selection on the same hypothetical coordinate set could work.

## Exact integer matrix test

The script builds one integer row for each reciprocal `phi` pair:

```text
X_e0 + X_e1 - X_f0 - X_f1 = 0.
```

It computes the rank and nullspace over exact rational arithmetic using SymPy.
Labels `u,v` are reported as forced equal exactly when every nullspace basis
vector has equal coordinates in positions `u` and `v`.

## Verified fixed-pattern kills

These outcomes are checked by
`python scripts/check_mutual_rhombus_filter.py --assert-expected`.

| Pattern | Filter | Rank | Forced class summary |
|---|---|---:|---|
| `B12_3x4_danzer_lift` | mutual-rhombus midpoint | 8 | `[0,4,8]`, `[1,5,9]`, `[2,6,10]`, `[3,7,11]` |
| `B20_4x5_FR_lift` | mutual-rhombus midpoint | 15 | residues mod 5 collapse |
| `C20_pm_4_9` | mutual-rhombus midpoint | 16 | residues mod 4 collapse |
| `C16_pm_1_6` | mutual-rhombus midpoint | 14 | parity collapse |
| `C13_pm_3_5` | mutual-rhombus midpoint | 12 | all labels collapse |
| `C9_pm_2_4` | mutual-rhombus midpoint | 8 | all labels collapse |
| `C17_skew` | odd forced-perpendicularity cycle | 0 | length-17 odd cycle |

The built-in smoke pattern `C12_pm_2_5` is also killed by the same midpoint
filter, with parity classes forced equal. It is not listed as a live ranked
pattern in `candidate-patterns.md`.

## Natural-order-only kills

Under the natural cyclic order `0,1,...,n-1`, the parity patterns
`P18_parity_balanced` and `P24_parity_balanced` have adjacent row-pairs with
two common witnesses. The crossing-bisector lemma therefore kills them under
that cyclic order.

Their abstract-incidence status remains separate. The exact crossing CSP in
`docs/cyclic-crossing-csp.md` records that `P18_parity_balanced` has compatible
arbitrary cyclic orders under crossing constraints alone, while
`P24_parity_balanced` has no cyclic order satisfying all 36 crossing
constraints. The stronger vertex-circle order filter then kills
`P18_parity_balanced` when combined with the crossing constraints; see
`docs/vertex-circle-order-filter.md`.

The sparse pattern `C19_skew` has no `phi` edges, so it is invisible to the
mutual-rhombus and forced-perpendicularity filters. It is nevertheless killed
in natural cyclic order by Altman's diagonal-order sums; see
`docs/altman-diagonal-sums.md`. It also passes the known vertex-circle
acyclic-order sanity check. This does not kill the same abstract incidence
pattern under arbitrary cyclic relabeling.

## Reproduction

```bash
pip install -e .[dev]
python scripts/check_mutual_rhombus_filter.py --assert-expected
python scripts/check_mutual_rhombus_filter.py --json
python scripts/check_vertex_circle_order_filter.py --pattern P18_parity_balanced --search --assert-obstructed
pytest -q
```

## Caveats

- These filters kill fixed selected patterns, not arbitrary selections.
- The crossing test depends on cyclic order.
- Natural label order is not automatically the geometric cyclic order unless
  explicitly assumed by the pattern or search mode.
- No general proof or counterexample is claimed.
