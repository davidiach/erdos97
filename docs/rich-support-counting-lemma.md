# Rich-support counting lemma

Status: `LEMMA` / proof-facing edge-sensitive counting bound. This note does
not claim a general proof of Erdos Problem #97 and does not claim a
counterexample.

## Setup

Let `V` be the vertex set of a strictly convex `n`-gon in its cyclic hull
order. For each center `i in V`, choose one same-radius support

```text
R_i subset V \ {i}
```

meaning that all vertices of `R_i` lie on one circle centered at `i`. The set
`R_i` may have size larger than four; for example, it may be a maximum rich
class witnessing `E(i)`.

## Lemma

For any such choice of supports,

```text
sum_i binom(|R_i|, 2) <= n(n - 2).
```

Proof: fix an unordered witness pair `{a,b}`.

If `{a,b}` is not a hull edge, then every center `i` with
`{a,b} subset R_i` is equidistant from `a` and `b`, hence lies on the
perpendicular bisector of segment `ab`. A line contains at most two vertices of
a strictly convex polygon, so this non-edge witness pair can occur together in
at most two supports.

If `{a,b}` is a hull edge, its perpendicular bisector already meets the polygon
boundary at the midpoint of that edge. The same perpendicular bisector cannot
coincide with the edge line. Its intersection with the boundary of a convex
polygon therefore has at most one further boundary point, so it contains at
most one polygon vertex that can serve as a center. Thus a hull-edge witness
pair can occur together in at most one support.

There are `n` hull-edge witness pairs and `binom(n,2)-n` non-edge witness
pairs. Double-counting triples `(i,{a,b})` with `{a,b} subset R_i` gives

```text
sum_i binom(|R_i|, 2)
  <= n + 2 * (binom(n,2) - n)
   = n(n - 2).
```

## Consequences

If every center has a same-radius support of size at least `k`, then the
edge-sensitive pair count gives

```text
n * binom(k, 2) <= n(n - 2),
```

so

```text
n >= binom(k, 2) + 2.
```

For `k=4`, this gives the pair-counting support-level wall `n >= 8`.

In particular, this pair-sharing count gives `n >= 12` for a strict convex
polygon in which every vertex has five equidistant witnesses. The companion
support-saturation obstruction rules out the equality wall and improves the
proof-facing threshold to `n >= 13` for the all-five-rich case. See
`docs/support-saturation-obstruction.md`.
The `n=12` equality wall also has an independent support-incidence determinant
obstruction: if the edge-sensitive pair capacities were saturated, the forced
column Gram matrix of the `12 x 12` incidence matrix would have determinant
`2,592,000 = 720^2 * 5`, not a square. See
`docs/n12-rich-support-determinant-obstruction.md`.

For a hypothetical 4-bad nonagon, choose a maximum rich support at every
center, so `|R_i| = E(i) >= 4`. The same inequality gives

```text
sum_i (binom(E(i), 2) - binom(4, 2)) <= 9*7 - 9*6 = 9.
```

Since any center with `E(i) >= 5` costs at least `binom(5,2)-binom(4,2)=4`,
at most two centers can have `E(i) >= 5`. Equivalently, any hypothetical 4-bad
nonagon has at least seven exact-four centers.

### Nonagon profile-deficiency refinement

The raw nonagon pair budget permits only four sorted support-size profiles for
a 4-bad nonagon:

```text
4^9,
5 4^8,
5^2 4^7,
6 4^8.
```

The last three are impossible by a vertex-deficiency refinement of the same
counting argument. For a label `a`, let `m_ab` be the number of supports
containing the witness pair `{a,b}`, and let `c_ab` be the pair capacity: `1`
for hull edges and `2` for non-edges. In a nonagon,

```text
sum_b c_ab = 2*1 + 6*2 = 14.
```

Define the label deficiency

```text
D_a = 14 - sum_{i : a in R_i} (|R_i| - 1).
```

Because `m_ab <= c_ab` for every pair, `D_a >= 0`, and

```text
sum_a D_a = 2 * (unused pair-capacity slack).
```

Now compare this required total deficiency with the congruence forced by row
sizes. Exact-four rows contribute `3` to the weighted degree of any label they
contain; size-five rows contribute `4`; size-six rows contribute `5`.

- For profile `5 4^8`, the pair slack is `5`, so `sum_a D_a = 10`. The five
  labels in the size-five row have weighted degree congruent to `1 mod 3`, so
  each has deficiency at least `1`; the other four labels have weighted degree
  congruent to `0 mod 3`, so each has deficiency at least `2`. Hence
  `sum_a D_a >= 5*1 + 4*2 = 13`, contradiction.
- For profile `5^2 4^7`, the pair slack is `1`, so `sum_a D_a = 2`. Starting
  from the exact-four residue lower bound `2` at each of nine labels, the ten
  size-five witness incidences can lower the total deficiency by at most `10`,
  leaving `sum_a D_a >= 18 - 10 = 8`, contradiction.
- For profile `6 4^8`, the pair slack is `0`, so `sum_a D_a = 0`. The six
  labels in the size-six row can have deficiency `0`, but the three labels
  outside that support still have exact-four residue deficiency at least `2`,
  giving `sum_a D_a >= 6`, contradiction.

Therefore any hypothetical 4-bad nonagon has `E(i)=4` at every center.
Choosing one maximum support per center gives nine exact-four selected rows.
For each label, the same deficiency count then forces selected indegree exactly
`4`. This profile-deficiency refinement is an independent count-level
cross-check of the localized per-label cap below; neither route proves the
review-pending exact-four vertex-circle frontier.

The corresponding necessary counting relaxation gives at least five exact-four
centers in any hypothetical 4-bad decagon and at least three exact-four centers
in any hypothetical 4-bad hendecagon.

The companion localized counting lemma strengthens the `n=9` consequence: by
counting support pairs incident to each fixed witness label, a hypothetical
4-bad nonagon is forced into the all-exact-four, selected-indegree-four support
case before any mixed-support catalogue or vertex-circle replay. See
`docs/localized-rich-support-counting.md`.

The same count also gives a short support-level exclusion of `n <= 7`: a 4-bad
`n`-gon would require `6n <= n(n-2)`, hence `n >= 8`. This agrees with the
repository's separate sharpened incidence and geometric proof-note routes; the
older `n=7` Fano enumeration remains useful structural provenance.

## Verification command

The helper script

```bash
python scripts/check_rich_support_counting_bound.py --check --json
```

checks the pair-counting threshold `n >= 12` for all-centers size-five support,
the small `n=8..12` surplus table used above, and the nonagon
profile-deficiency refinement. The companion saturation checker verifies the
equality-wall upgrade to `n >= 13`. These are counting-bound checkers; they are
not realization searches.

## Boundary

This global pair-counting lemma alone does not rule out mixed exact-four and
size-five catalogues. For `n=9`, the profile-deficiency refinement above and
the localized companion lemma both rule out that mixed support layer by
counting alone, reducing hypothetical nonagons to the all-exact-four support
frontier. This still does not replace the review-pending exact-four
vertex-circle checker. The existing `n=9` all-five-rich and mixed support
checkers remain useful as crossing-aware catalogue regressions and as
provenance for the richer support-search machinery, but their nonagon support
reduction is now preceded by these proof-facing counts.
