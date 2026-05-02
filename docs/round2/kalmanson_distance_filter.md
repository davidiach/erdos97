# Kalmanson distance filter for fixed cyclic orders

Status: exact obstruction when a positive integer certificate is supplied and checked.

This filter works in ordinary pair-distance variables after quotienting by selected-distance equalities. It uses all convex quadrilateral inequalities available from a fixed cyclic order.

## Lemma

For vertices `a,b,c,d` in cyclic order in a strictly convex polygon:

```text
d(a,c) + d(b,d) > d(a,b) + d(c,d)
d(a,c) + d(b,d) > d(a,d) + d(b,c)
```

The proof is by the diagonal-crossing point and strict triangle inequality. These are ordinary-distance inequalities. In the selected-witness problem, equality of squared selected distances implies equality of ordinary selected distances, so the ordinary-distance quotient is valid.

## Certificate format

The JSON certificate contains:

```text
pattern.name
pattern.n
pattern.circulant_offsets
cyclic_order
inequalities: list of {kind, quad, weight}
```

Each `quad=[a,b,c,d]` must be listed in the supplied cyclic order. Each `weight` must be a positive integer.

`kind` is one of:

```text
K1_diag_gt_sides: d(a,c)+d(b,d) > d(a,b)+d(c,d)
K2_diag_gt_other: d(a,c)+d(b,d) > d(a,d)+d(b,c)
```

The checker builds selected-distance equivalence classes, expands each inequality as an integer vector over those classes, and verifies that the positive weighted sum is exactly zero. The contradiction is then `0 > 0`.

## Promoted certificate

```text
File: data/certificates/round2/c19_kalmanson_known_order_unsat.json
Pattern: C19_skew
Offsets: [-8,-3,5,9]
Cyclic order: [18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1]
Strict inequalities: 94
Distance classes: 114
```

Safe claim:

```text
This fixed order of this fixed selected-witness pattern is impossible.
```

Unsafe claim:

```text
Do not claim an all-order C19_skew obstruction.
```
