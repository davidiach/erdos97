# Rich-support counting lemma

Status: `LEMMA` / proof-facing counting bound. This note does not claim a
general proof of Erdos Problem #97 and does not claim a counterexample.

## Setup

Let `V` be the vertex set of a strictly convex `n`-gon. For each center
`i in V`, choose one same-radius support

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

Proof: fix an unordered witness pair `{a,b}`. If `{a,b} subset R_i`, then the
center `i` is equidistant from `a` and `b`, so `i` lies on the perpendicular
bisector of segment `ab`.

For a non-boundary pair `{a,b}`, this gives the usual capacity `2`: a line
contains at most two vertices of a strictly convex polygon. For a boundary edge
`{a,b}`, the perpendicular bisector enters the polygon through the midpoint of
that edge. The line-section of the polygon therefore has that midpoint as an
endpoint, so it can contain at most one polygon vertex as a center. Thus the
`n` boundary-edge witness pairs have capacity `1`, while the remaining
`binom(n,2)-n` witness pairs have capacity `2`. Double-counting triples
`(i,{a,b})` with `{a,b} subset R_i` gives

```text
n*1 + (binom(n,2) - n)*2 = n(n - 2).
```

## Consequences

If every center has a same-radius support of size at least `k`, then

```text
n * binom(k, 2) <= n(n - 2),
```

so

```text
n >= binom(k, 2) + 2.
```

For `k=4`, this gives the support-level wall `n >= 8`.

In particular, a strict convex polygon in which every vertex has five
equidistant witnesses must have `n >= 12`. Thus the `n=9`, `n=10`, and `n=11`
all-five-rich support subcases are already impossible by this pair-sharing
count, before using cyclic order, crossing, selected-distance quotienting, or
vertex-circle pruning.

For a hypothetical 4-bad nonagon, choose a maximum rich support at every
center, so `|R_i| = E(i) >= 4`. The same inequality gives

```text
sum_i (binom(E(i), 2) - binom(4, 2)) <= 9*7 - 9*6 = 9.
```

Since any center with `E(i) >= 5` costs at least `binom(5,2)-binom(4,2)=4`,
at most two centers can have `E(i) >= 5`. Equivalently, any hypothetical 4-bad
nonagon has at least seven exact-four centers.

The corresponding necessary counting relaxation gives at least five exact-four
centers in any hypothetical 4-bad decagon, and at least three exact-four
centers for `n=11`.

## Verification command

The helper script

```bash
python scripts/check_rich_support_counting_bound.py --check --json
```

checks the threshold `n >= 12` for all-centers size-five support and the small
`n=5..11` surplus table used above. It is only a counting-bound checker; it is
not a realization search.

## Boundary

This lemma does not rule out mixed exact-four and size-five catalogues. For
`n=9`, it narrows such a catalogue by forcing at least seven exact-four centers,
but it does not replace the review-pending exact-four frontier or the mixed
support crosswalk. The existing `n=9` all-five-rich checker remains useful as a
crossing-aware support-catalogue regression and as provenance for the richer
support-search machinery.
