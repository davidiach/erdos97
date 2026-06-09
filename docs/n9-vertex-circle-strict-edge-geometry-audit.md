# n=9 Vertex-circle Strict-edge Geometry Audit

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note audits the local geometric rule that creates directed strict edges
in the repo-native `n=9` vertex-circle checker. It does not claim a proof of
`n=9`, does not claim a counterexample, does not complete independent review
of the exhaustive checker, and does not update the official/global status.

## Definitions

Let `P` be a strictly convex polygon with vertices labelled in cyclic order.
Fix a center label `c` and a selected witness row

```text
S_c = {w_0,w_1,w_2,w_3}.
```

The selected-row condition says that all four witnesses lie on one circle
centered at `p_c`.

Order the four witnesses by their angular order around `p_c`; this agrees
with the polygon cyclic order with `c` removed, up to reversal. For indices
`0 <= r < s <= 3`, write `[r,s]` for the witness interval whose endpoints are
`w_r,w_s`.

An interval `[r,s]` properly contains `[u,v]` if

```text
r <= u < v <= s
```

and at least one of the two endpoint inequalities is strict.

## Strict-edge Lemma

If `[r,s]` properly contains `[u,v]` in the witness order of row `c`, then

```text
|p_{w_r} - p_{w_s}| > |p_{w_u} - p_{w_v}|.
```

Equivalently, the selected row creates a directed strict edge

```text
{w_r,w_s} > {w_u,w_v}
```

between ordinary pair-distance classes before quotienting by selected-row
equalities.

### Proof

At a vertex of a strictly convex polygon, all other vertices lie in the angle
between the two incident boundary rays, and that angle is less than `pi`.
Strict convexity also prevents two other vertices from lying on the same ray
from `p_c`. Hence the angular coordinates of the other vertices around
`p_c` are distinct and lie in an interval of length less than `pi`; along this
interval they follow the polygon cyclic order, up to reversal.

The four selected witnesses lie on one circle centered at `p_c`, say with
radius `R > 0`. If two selected witnesses have angular separation `theta`,
their ordinary chord length is

```text
2R sin(theta/2).
```

For `0 < theta < pi`, this expression is strictly increasing in `theta`.
Proper interval containment gives a strictly larger angular separation for
`[r,s]` than for `[u,v]`, so the containing chord is strictly longer.

The statement is invariant under reversing the witness order, because reversal
preserves interval containment.

## Checker Equivalence

The checked source blocks are:

- `src/erdos97/n9_vertex_circle_exhaustive.py`
- `src/erdos97/vertex_circle_quotient_replay.py`

Both implementations first sort the row witnesses by the cyclic position
relative to the center. They then enumerate all pairs of witness intervals
`outer_start < outer_end` and `inner_start < inner_end`, adding a strict edge
exactly when

```python
outer_start <= inner_start
and inner_end <= outer_end
and (outer_start < inner_start or inner_end < outer_end)
```

This is precisely the proper-containment condition in the lemma.

For four witnesses there are six witness intervals. The proper-containment
applications of the lemma give nine strict edges per selected row:

```text
outer span 2, inner span 1: 4
outer span 3, inner span 1: 3
outer span 3, inner span 2: 2
```

The checker intentionally does not add strict comparisons for non-contained
intervals. Such comparisons are not forced by cyclic order alone.

## One-off Audit

A one-off audit compared the strict-edge sets from the exhaustive checker and
the quotient replay checker against a direct proper-interval-containment
enumeration for every `n=9` center and every candidate 4-witness row.

```text
selected rows checked 630
n9 strict-edge mismatches 0
quotient replay strict-edge mismatches 0
strict edges per selected row {9: 630}
interval span histogram {'(2, 1)': 2520, '(3, 1)': 1890, '(3, 2)': 1260}
total strict edges 5670
```

The same audit is now replayable:

```bash
python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --summary-json
```

The script independently enumerates every proper interval containment for all
`9 * binom(8,4) = 630` candidate selected rows, compares the resulting strict
edge table with `src/erdos97/n9_vertex_circle_exhaustive.py`, and checks that
the quotient replay implementation records the same one-row strict-edge count.
Use `--json` instead when the full mismatch example block is needed.
It preserves the same scope boundary as this note: local strict-edge geometry
only, not quotient soundness or exhaustive coverage.

This audit checks implementation agreement with the strict-edge lemma. It
does not audit the later selected-distance quotient graph, self-edge
criterion, strict-cycle criterion, or exhaustive assignment coverage.

A 2026-06-09 internal review note records
`accepted_A8_strict_edge_geometry_internal` for this local strict-edge rule
and checker-equivalence contract. The machine-readable `vertex_circle_geometry`
gate remains open until an explicit written review decision is supplied.

## Scope

This audit covers only the local vertex-circle strict-edge generation rule:
proper containment of witness intervals on one selected circle forces a
strict inequality between the corresponding witness-witness chord lengths,
and the two checker implementations enumerate exactly those rule
applications.

It does not audit row0 coverage, minimum-remaining-options branching, the
two-overlap crossing filter, witness-pair cap, selected-indegree cap,
selected-distance quotienting, self-edge detection, strict-cycle detection,
archive reconciliation, or the 184 frontier assignments. It does not prove
the full `n=9` finite case, does not prove Erdos Problem #97, and does not
give a counterexample.
