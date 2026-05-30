# n=9 Two-overlap Crossing Audit

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note audits one row-level filter in the repo-native `n=9` vertex-circle
exhaustive checker: when two selected-witness rows share exactly two
witnesses, the checker requires the center-center chord and shared-witness
chord to cross in the fixed cyclic order. It does not claim a proof of `n=9`,
does not claim a counterexample, does not complete independent review of the
exhaustive checker, and does not update the official/global status.

## Radical-axis Crossing Lemma

Let `P` be a strictly convex polygon in cyclic order. Suppose distinct centers
`x,y` have selected witness sets `S_x,S_y` with

```text
S_x cap S_y = {a,b}.
```

Because both `x` and `y` are equidistant from `a` and `b`, the line `xy` is
the perpendicular bisector of segment `ab`. The midpoint `m` of `ab` lies in
the relative interior of the chord `ab` and in the convex hull of `P`. If
`xy` were a polygon edge, its line would support the strictly convex polygon,
but the perpendicular-bisector line has `a` and `b` on opposite sides. Hence
`xy` is not a polygon edge. The line through two nonadjacent vertices of a
strictly convex polygon meets the polygon in exactly the chord segment
`[x,y]`, so `m in [x,y]`. Hence the chords `{x,y}` and `{a,b}` cross at `m`,
which in a cyclic order is equivalent to their endpoints alternating.

Equivalently, a two-overlap on adjacent centers is impossible. Thus the same
crossing test also rejects adjacent-center two-overlaps.

## Checker Equivalence

The checked source block is
`src/erdos97/n9_vertex_circle_exhaustive.py`.

For centers `i < j`, the checker precomputes a compatibility table over all
row masks:

```python
common = row_i & set(MASK_BITS[mj])
ok = True
if len(common) > PAIR_CAP:
    ok = False
elif len(common) == PAIR_CAP:
    target = pair(*tuple(common))
    ok = chords_cross(source, target)
if ok:
    allowed.add(mj)
```

Here `PAIR_CAP = 2`. Thus a row pair is accepted by this filter exactly when:

- the two rows share at most two witnesses; and
- if they share exactly two witnesses, the source chord `{i,j}` crosses the
  shared-witness chord in the natural cyclic order `0,1,...,8`.

The helper `rows_compatible` uses the same table symmetrically for either row
order, and `valid_options_for_center` tests a candidate row against every
already assigned row through `rows_compatible`.

The crossing predicate is:

```python
return in_open_arc(a, b, c) != in_open_arc(a, b, d)
```

for disjoint chords `{a,b}` and `{c,d}`. This is exactly the alternating
endpoints criterion in the natural cyclic order. In the selected-row setting,
the source and shared-witness chords are automatically disjoint: label `i`
cannot lie in `S_i`, and label `j` cannot lie in `S_j`, so neither center can
belong to `S_i cap S_j`.

## One-off Audit

The audit is now replayable together with the other row-level incidence
filters:

```bash
python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --summary-json
```

The command recomputes the two-overlap crossing table for every pair of
centers and every pair of selected-row masks, then compares it with the
checker compatibility table. Use `--json` instead when the full histogram
blocks are needed. The transcript below records the historical one-off counts
now stabilized by that command.

A one-off predicate audit compared the checker with the shared
`incidence_filters.chords_cross_in_order` implementation on all nonagon chord
pairs and recomputed the row-pair compatibility rule for every pair of centers
and every pair of row masks.

```text
chord_cross equivalence mismatches: 0
compatibility errors: 0
row-pair candidate overlap histogram:
  0 common witnesses: 7560
  1 common witness:   57960
  2 common witnesses: 83160
  3 common witnesses: 26460
  4 common witnesses: 1260
two-overlap crossing accepted: 27720
two-overlap noncrossing rejected: 55440
```

The audit is not an independent implementation of the full exhaustive search.
It only checks that this row-level crossing filter matches the radical-axis
crossing lemma and the repository's standard cyclic crossing predicate.

## Scope

This audit covers only the two-overlap crossing filter in the fixed natural
cyclic order used by the `n=9` checker.

It does not audit the witness-pair cap, indegree cap, vertex-circle strict-edge
lemma, vertex-circle quotient obstruction, row0 coverage, archive
reconciliation, or the 184 frontier assignments. It does not prove the full
`n=9` finite case, does not prove Erdos Problem #97, and does not give a
counterexample.
