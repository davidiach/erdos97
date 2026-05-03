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

## Promoted compact certificate

```text
File: data/certificates/round2/c19_kalmanson_known_order_two_unsat.json
Pattern: C19_skew
Offsets: [-8,-3,5,9]
Cyclic order: [18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1]
Strict inequalities: 2
Distance classes: 114
Max weight: 1
```

The same certificate format now also checks the compact C13 pilot certificate:

```text
File: data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json
Pattern: C13_sidon_1_2_4_10
Offsets: [1,2,4,10]
Cyclic order: [5,0,10,8,9,7,4,6,2,11,12,3,1]
Strict inequalities: 2
Distance classes: 39
Max weight: 1
```

The earlier larger certificates remain checked as provenance:
`data/certificates/round2/c19_kalmanson_known_order_unsat.json` has 94
inequalities, and
`data/certificates/c13_sidon_order_survivor_kalmanson_unsat.json` has 34.
The compact files are preferred for review because each is just an inverse pair
of strict Kalmanson rows whose coefficient vectors cancel exactly.

Regenerate the compact C19 certificate with:

```bash
python scripts/find_kalmanson_two_certificate.py \
  --name C19_skew \
  --n 19 \
  --offsets=-8,-3,5,9 \
  --order 18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1 \
  --assert-found \
  --out data/certificates/round2/c19_kalmanson_known_order_two_unsat.json
```

Safe claim:

```text
This fixed order of this fixed selected-witness pattern is impossible.
```

Unsafe claim:

```text
Do not claim an all-order C19_skew obstruction.
```
