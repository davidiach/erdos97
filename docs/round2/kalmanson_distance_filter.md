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

## Paired-square entry lemma

The following local form is useful when a Kalmanson certificate has already
reduced to one selected spoke class and one incident nonselected class.

Fix distinct labels `i` and `n`, with `{i,n}` not in the selected spoke class
at `i`.
Write

```text
R_i = class({i,s}) for selected witnesses s in S_i,
X = class({i,n}).
```

Assume `X` is distinct from `R_i`; if it is already the same quotient class,
the obstruction is a separate one-row or degenerate quotient case.

Suppose there are two selected-center squares for the same incident residual
pair. That is, for signs `+` and `-` there are selected witnesses
`s_+`, `s_-` in `S_i` and selected centers `j_+`, `j_-` such that

```text
{n,s_+} subset S_{j_+},
{n,s_-} subset S_{j_-}.
```

For each sign, the four labels `i,n,s_+,j_+` or `i,n,s_-,j_-` are assumed
distinct, so the Kalmanson row is a genuine strict quadrilateral inequality.

Assume the cyclic order forces the two strict Kalmanson inequalities

```text
d(i,s_+) + d(j_+,n) > d(i,n) + d(j_+,s_+),
d(i,n) + d(j_-,s_-) > d(i,s_-) + d(j_-,n).
```

After selected-distance quotienting, the first inequality reduces to

```text
R_i + R_{j_+} > X + R_{j_+},
```

and hence to `R_i > X`. The second reduces to

```text
X + R_{j_-} > R_i + R_{j_-},
```

and hence to `X > R_i`. Adding the two strict inequalities gives `0 > 0`.

This is a local entry lemma only. It does not prove that a selected-witness
pattern must expose the two selected-center squares, and it does not replace a
cyclic-order proof that the displayed matchings are diagonal. It records the
exact quotient-balance condition needed once those two inputs are known.
In particular, it should not be phrased as using both orientations of one
square: a single fixed four-label cyclic order makes only one of the two square
matchings diagonal.

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

All-order follow-up:

```text
The fixed abstract C19_skew pattern is now killed across all cyclic orders by
data/certificates/c19_skew_all_orders_kalmanson_z3.json; see
docs/kalmanson-two-order-search.md.
```
