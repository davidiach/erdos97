# Vertex-circle order filter

Status: `EXACT_OBSTRUCTION` for fixed selected-witness incidence patterns.

No general proof of Erdos Problem #97 is claimed. No counterexample is claimed.

## Summary

This note records an exact cyclic-order filter for a selected-witness pattern.
It uses only:

- the cyclic order of labels;
- the fact that each selected row lies on a circle centered at its row label;
- distance-class equalities forced by the selected rows.

It does not use coordinates, floating-point arithmetic, or numerical
optimization.

## Vertex-circle nesting lemma

Let `P` be a strict convex polygon in cyclic order. Fix a vertex `i`, and let
`a_0,...,a_m` be other vertices lying on one circle centered at `p_i`.

The angular order of the vertices around `p_i` is the polygon boundary order
with `i` removed, up to reversal. All angular separations among those vertices
lie in `(0, pi)`, because all other polygon vertices lie in the open angle
formed by the two boundary edges incident to the hull vertex `i`.

If the angular interval from `a_r` to `a_s` properly contains the angular
interval from `a_u` to `a_v`, then

```text
|p_{a_r} - p_{a_s}| > |p_{a_u} - p_{a_v}|.
```

Indeed, both chords lie on the same circle centered at `p_i`. A chord with
central angle `theta` has length `2R sin(theta/2)`, and this is strictly
increasing for `theta in (0, pi)`.

## Strict-cycle obstruction

Given a selected-witness pattern `S` and a proposed cyclic order:

1. Create a distance-class variable for every unordered pair `{u,v}`.
2. For every row `i`, union the classes `{i,w}` for all `w in S_i`.
3. For every row `i`, sort the four witnesses `S_i` in angular order around
   `i` using the cyclic order.
4. For every proper interval containment among witness-witness chords in that
   row, add a strict directed inequality

```text
class({outer endpoints}) > class({inner endpoints}).
```

If any strict edge is a self-edge, or if these strict directed inequalities
contain a directed cycle, the proposed cyclic order is impossible.

This is a finite exact obstruction for the fixed selected pattern and order.

## P18 human certificate

The crossing-only CSP records the following compatible order for
`P18_parity_balanced`:

```text
0,8,4,15,1,5,11,9,3,7,17,13,2,6,14,10,16,12
```

The vertex-circle filter kills that order. Write `d(u,v)` for ordinary
Euclidean distance.

Row `13` has selected witnesses `{5,9,15,2}`, so

```text
d(5,13) = d(2,13).
```

Row `2` has selected witnesses `{13,0,6,10}`, so

```text
d(2,13) = d(2,10).
```

Around center `3`, the selected witnesses occur in the order

```text
17,13,10,5.
```

The interval `[13,5]` properly contains `[10,5]`, hence

```text
d(5,13) > d(5,10).
```

Around center `12`, the selected witnesses occur in the order

```text
5,2,10,16.
```

The interval `[5,10]` properly contains `[2,10]`, hence

```text
d(5,10) > d(2,10).
```

Therefore

```text
d(5,13) > d(5,10) > d(2,10) = d(5,13),
```

a contradiction.

## Full P18 search

The script

```bash
python scripts/check_vertex_circle_order_filter.py \
  --pattern P18_parity_balanced \
  --search \
  --assert-obstructed \
  --write-certificate data/certificates/p18_vertex_circle_order_unsat.json
```

performs a deterministic insertion search. It uses the same crossing seed
normalization as `scripts/check_cyclic_crossing_csp.py`, rejects a crossing
constraint only when all four endpoints are placed, and applies the
vertex-circle strict-cycle filter only when a row center and all four selected
witnesses are placed.

The checked result is:

```text
P18_parity_balanced, crossing + vertex-circle nesting filter:
  result: UNSAT
  crossing constraints: 27
  nodes visited: 2466
  max depth: 16
  crossing prunes: 22652
  vertex-circle prunes: 3724
```

The result artifact is stored at
`data/certificates/p18_vertex_circle_order_unsat.json`.

Safe claim:

```text
EXACT_OBSTRUCTION: P18_parity_balanced is killed as a fixed
selected-witness abstract incidence pattern by the crossing-bisection
constraints plus the vertex-circle order strict-cycle filter.
```

## C19 caveat

This filter does not kill abstract-incidence `C19_skew`. The order

```text
18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1
```

has no vertex-circle self-edge or strict directed cycle under this filter.
Thus `C19_skew` remains the main sparse abstract-incidence survivor of the
current fixed-pattern filters, even though its natural cyclic order is killed
by Altman's diagonal-order sums.

## Reproduction

```bash
python scripts/check_vertex_circle_order_filter.py \
  --pattern P18_parity_balanced \
  --order 0,8,4,15,1,5,11,9,3,7,17,13,2,6,14,10,16,12 \
  --assert-obstructed

python scripts/check_vertex_circle_order_filter.py \
  --pattern P18_parity_balanced \
  --search \
  --assert-obstructed

python scripts/check_vertex_circle_order_filter.py \
  --pattern C19_skew \
  --order 18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1 \
  --assert-sat
```

The corresponding regression tests are in
`tests/test_vertex_circle_order_filter.py`.

## Caveats

- This is a fixed selected-pattern obstruction, not a global proof.
- It does not certify a counterexample.
- It does not kill abstract-incidence `C19_skew`.
- Numerical near-misses remain numerical evidence only.
