# Localized rich-support counting cap

Status: `LEMMA` / proof-facing localized counting bound. This note does not
claim a general proof of Erdos Problem #97 and does not claim a counterexample.

## Setup

Let `V` be the vertex set of a strictly convex `n`-gon in cyclic hull order. For
each center `i in V`, choose one same-radius support

```text
R_i subset V \ {i}
```

meaning that all vertices of `R_i` lie on one circle centered at `i`. The set
`R_i` may have size larger than four. In a hypothetical 4-bad polygon one may
choose, for each center, a maximum rich class, so `|R_i| = E(i) >= 4`.

## Localized cap

For each fixed witness label `x`,

```text
sum_{i : x in R_i} (|R_i| - 1) <= 2n - 4.
```

Proof: double-count pairs `{x,y}` inside supports. For each `y != x`, every
center `i` with `{x,y} subset R_i` is equidistant from `x` and `y`, hence lies
on the perpendicular bisector of segment `xy`.

If `{x,y}` is a hull edge, that perpendicular bisector already meets the
polygon boundary at the midpoint of the edge. Since it cannot coincide with the
edge line, it has at most one further intersection point with the boundary of a
convex polygon, and therefore contains at most one polygon vertex that can serve
as a center.

If `{x,y}` is not a hull edge, a line contains at most two vertices of a
strictly convex polygon, so the pair can occur with at most two centers.

There are two hull neighbors of `x` and `n - 3` non-neighbor labels. Thus the
pair budget incident to `x` is

```text
2 * 1 + (n - 3) * 2 = 2n - 4.
```

This proves the displayed inequality.

## Consequence for nonagons

Assume `n = 9` and choose a same-radius support of size at least four at every
center. Every occurrence `x in R_i` contributes at least `3` to the localized
sum for `x`, so each label occurs in at most

```text
floor((2n - 4) / 3) = floor(14 / 3) = 4
```

supports. Summing over the nine labels gives

```text
sum_i |R_i| <= 9 * 4 = 36.
```

But the 4-bad hypothesis gives `sum_i |R_i| >= 9 * 4 = 36`. Hence equality
holds everywhere:

- every chosen support has size exactly four;
- every label occurs in exactly four chosen supports.

Therefore any hypothetical 4-bad nonagon is forced into the all-exact-four,
selected-indegree-four case before using cyclic-order crossing, witness-pair
capacity, selected-distance quotienting, or vertex-circle pruning.

This strengthens the older support-level counting consequence for `n = 9`,
which only forced at least seven exact-four centers. It does not prove the
`n = 9` selected-witness case: the exact-four frontier and its vertex-circle
obstructions still require the separate review-pending finite-case pipeline.

## Small-n table

Combining the localized occurrence cap with the edge-sensitive global pair
budget gives this necessary counting summary for hypothetical 4-bad polygons:

```text
n = 8: at least 8 exact-four centers; exact-four indegree is forced to be 4
n = 9: at least 9 exact-four centers; exact-four indegree is forced to be 4
n = 10: at least 5 exact-four centers by the global pair budget
n = 11: at least 3 exact-four centers by the global pair budget
n = 12: no exact-four center is forced by these two budgets alone
```

For `n = 5, 6, 7`, the edge-sensitive global pair budget already rules out
4-bad supports.

A review-pending near-saturation strengthening of the global pair budget
(`docs/near-saturation-support-obstruction.md`) sharpens the `n = 10` and
`n = 11` floors in this table to six and four exact-four centers and forces
one exact-four center at `n = 12` from the budget alone; the rows above
record only what the raw budgets prove.

The support-saturation obstruction in `docs/support-saturation-obstruction.md`
adds a separate equality-wall count: all centers having support size at least
five is impossible for `n <= 12`. Thus a hypothetical 4-bad dodecagon has at
least one exact-four center once that equality-wall obstruction is also used.

## Verification command

The helper script

```bash
python scripts/check_localized_rich_support_counting.py --check --json
```

checks the localized per-label budget, the `n = 9` all-exact-four consequence,
and the small `n = 5..12` counting table. It is only a counting-bound checker;
it is not a realization search and it does not replay the `n = 9` vertex-circle
frontier.

## Boundary

This lemma is necessary structure only. It rules out mixed exact-four/richer
support choices for a hypothetical nonagon, but it does not rule out the
all-exact-four selected-witness frontier by itself. It does not prove `n = 9`,
`n = 10`, `n = 11`, or Erdos Problem #97.
