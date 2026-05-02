# Phi 4-cycle rectangle trap

Status: `EXACT_OBSTRUCTION` for fixed selected-witness incidence patterns.

This note records a fixed-pattern filter that is not covered by the existing
mutual-rhombus 2-cycle or odd forced-perpendicularity-cycle filters. It does
not prove Erdos Problem #97 and does not produce a counterexample.

## Setup

For a row-pair with exactly two common witnesses, write

```text
phi({x,y}) = S_x cap S_y.
```

The crossing-bisector lemma says that `{x,y}` is the perpendicular bisector of
`phi({x,y})`, and that the midpoint of `phi({x,y})` lies on segment `xy`.

Consider a directed `phi` 4-cycle

```text
e0 -> e1 -> e2 -> e3 -> e0
```

with eight distinct endpoint labels. Write

```text
e0 = {A,A_bar}
e1 = {B,B_bar}
e2 = {C,C_bar}
e3 = {D,D_bar}
```

The rectangle trap applies when these eight labels occur in cyclic order

```text
A, C, B, D, C_bar, A_bar, D_bar, B_bar.
```

The same test is applied after reversing the supplied cyclic order, since the
orientation of a polygon boundary is conventional.

## Geometry

After a rigid motion and reflection, the four perpendicular-bisector relations
give the coordinate normalization

```text
A     = ( L0, 0)       A_bar = (-L0, 0)
B     = ( a,  L1)      B_bar = ( a, -L1)
C     = ( a + L2, b)   C_bar = ( a - L2, b)
D     = ( 0, b + L3)   D_bar = ( 0, b - L3)
```

with positive half-lengths `L0,L1,L2,L3`.

The cyclic order gives the signs of the midpoint rectangle offsets:

- along chord `A-A_bar`, the `B-B_bar` crossing precedes the `D-D_bar`
  crossing, so `a > 0`;
- along chord `B-B_bar`, the `C-C_bar` crossing precedes the `A-A_bar`
  crossing, so `b > 0`.

These are ordinary chord-intersection order facts inside a strictly convex
polygon: for a fixed diagonal, crossings with chords whose endpoints lie on
opposite boundary arcs occur in the corresponding boundary order.

## Determinant certificate

Use the cyclic subsequence

```text
A, C, B, D, C_bar, A_bar, D_bar, B_bar.
```

Let `D_i` be the signed turn determinant at position `i` in this subsequence.
Strict convexity requires every `D_i` to have the same strict sign after
choosing the boundary orientation. In the orientation above, it requires
`D_i > 0`.

Exact expansion gives

```text
D1 =  L1*L2 + L1*a - L2*L3 - L2*b - a*b
D3 = -L0*L3 + L2*L3 + L2*b - L3*a - a*b
D5 = -L0*L1 + L0*L3 - L0*b + L3*a - a*b
D7 =  L0*L1 + L0*b - L1*L2 - L1*a - a*b
```

and hence

```text
D1 + D3 + D5 + D7 = -4*a*b.
```

Since `a > 0` and `b > 0`, the right side is negative. Therefore these four
strictly positive turns cannot coexist. This kills any fixed selected-witness
pattern containing this directed cycle with this cyclic order type.

## Registered n=9 certificate

The first registered pattern killed by this filter is

```text
S0 = {1,2,3,8}
S1 = {0,2,4,7}
S2 = {1,3,5,7}
S3 = {1,4,6,8}
S4 = {0,2,5,6}
S5 = {3,4,6,7}
S6 = {2,5,7,8}
S7 = {0,3,6,8}
S8 = {0,1,4,5}
```

It has the directed cycle

```text
{0,6} -> {2,8} -> {1,5} -> {4,7} -> {0,6}
```

and cyclic subsequence

```text
0, 1, 2, 4, 5, 6, 7, 8.
```

The machine-readable certificate is
`data/certificates/n9_phi4_rectangle_trap.json`.

## Frontier scan

The reusable scanner
`scripts/check_phi4_frontier_scan.py` applies this filter to the registered
positive `n=9` case, all built-in natural-order candidate patterns, and the
registered sparse non-natural orders. The generated artifact is
`data/certificates/phi4_frontier_scan.json`; see
`docs/phi4-frontier-scan.md`.

## Reproduction

```bash
python scripts/check_phi4_rectangle_trap.py --assert-expected
python scripts/check_phi4_rectangle_trap.py --assert-expected --write
python scripts/check_phi4_frontier_scan.py --assert-expected
pytest tests/test_incidence_filters.py -q
```

The `--write` command regenerates the JSON certificate. The artifact is a
fixed-pattern obstruction only; it is not an `n=9` completeness result.
