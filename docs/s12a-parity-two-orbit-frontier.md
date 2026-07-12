# S12A fixed-order equilateral-ear obstruction

Status: `EXACT_FIXED_PATTERN_FIXED_ORDER_OBSTRUCTION`.

This note records an exact elementary obstruction for one selected-witness
pattern in one cyclic order. It does not prove an all-order obstruction for the
abstract S12A pattern, Erdos Problem #97, or a counterexample. The
official/global status remains falsifiable/open, and the source-of-truth
strongest local result remains `n <= 8`.

## Pattern and order

Use the natural cyclic order `0,1,...,11`. The selected rows are

```text
even center c: S_c = c + {+/-1, +/-2} mod 12
odd  center c: S_c = c + {+/-2, +/-5} mod 12.
```

Equivalently, even centers use offsets `{1,2,10,11}` and odd centers use
offsets `{2,5,7,10}`.

## Elementary obstruction

For every even label `c`, the two even-center rows at `c` and `c+2` force the
consecutive triple

```text
(c, c+1, c+2)
```

to be equilateral. Indeed, row `c` gives

```text
d(c,c+1) = d(c,c+2),
```

while row `c+2` gives

```text
d(c+2,c) = d(c+2,c+1).
```

Thus all three side lengths agree. The six middle vertices

```text
1,3,5,7,9,11
```

each have interior angle `pi/3`, hence exterior turn `2*pi/3`. Their forced
turn sum is therefore

```text
6 * (2*pi/3) = 4*pi.
```

Every strictly convex polygon has positive exterior turns with total `2*pi`.
The fixed S12A pattern therefore has no strictly convex Euclidean realization
in the natural order.

## Exact replay

The standard-library checker constructs the selected-distance quotient,
detects all six equilateral ears, and verifies the turn-budget contradiction
using exact rational arithmetic:

```bash
python scripts/check_s12a_equilateral_ears.py \
  --check --assert-expected --summary-json
```

The managed certificate is
`data/certificates/s12a_equilateral_ear_obstruction.json`.

## Superseded frontier diagnostic

The earlier artifact
`data/certificates/s12a_parity_two_orbit_frontier.json` is retained as
superseded provenance. It records that S12A passed the implemented row-cap,
crossing, vertex-circle, Kalmanson-screen, and squared-distance value-row
filters. Those passes were necessary-condition diagnostics, never a
realizability claim. The elementary ear argument is strictly stronger for this
fixed natural order.

The superseded diagnostic remains replayable with

```bash
python scripts/check_s12a_frontier_pattern.py \
  --check --assert-expected --json
```

## Scope

The certificate fixes both the selected rows and the natural cyclic order. It
does not classify other cyclic orders of the same abstract S12A incidence
pattern and supplies no bridge from arbitrary minimal counterexamples.
