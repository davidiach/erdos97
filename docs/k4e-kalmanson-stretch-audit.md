# K4-e Kalmanson Stretch Audit

Status: `EXACT_FIXED_PATTERN_AUDIT`; review-pending as a reusable filter.

This note records a narrow exact audit layer for selected-distance quotients.
It does not prove or disprove Erdos Problem #97, does not exclude `n=10`, and
does not change the repository status. It kills only the displayed
quotient-level `n=10` survivor pattern and one `n=9` diagnostic pattern under
their stated fixed cyclic orders.

Replay:

```bash
python scripts/check_k4e_kalmanson_stretch_audit.py --assert-expected
```

## Lemma

Let one exact ordinary distance class of a planar point set contain exactly
five of the six edges on four distinct vertices. Then the missing edge has
length `sqrt(3)` times the common class length.

Indeed, if the missing edge is `{c,d}`, then the five equal edges include two
equilateral triangles sharing the edge `{a,b}`. The two possible third
vertices for an equilateral triangle on `{a,b}` are on opposite sides of the
line `ab` unless they coincide. Since the vertices are distinct, `c` and `d`
are the opposite equilateral apexes, and therefore `|cd| = sqrt(3) |ab|`.

Thus a `K4-e` found inside a selected-distance quotient class `Q` gives an
exact stretch relation

```text
rho(target missing-edge class) = sqrt(3) rho(Q).
```

The checker substitutes one such relation at a time into the ordinary strict
Kalmanson inequalities for a fixed cyclic order. Coefficients are represented
exactly in `Q(sqrt(3))`, so the audit uses no floating point arithmetic.

## Displayed n=10 Survivor

The displayed pattern has selected rows:

```text
S_0 = {1,4,5,8}
S_1 = {2,3,6,9}
S_2 = {0,1,3,4}
S_3 = {1,2,5,6}
S_4 = {0,3,5,7}
S_5 = {0,4,6,8}
S_6 = {2,4,7,9}
S_7 = {3,5,8,9}
S_8 = {1,6,7,9}
S_9 = {0,2,7,8}
```

Selected-distance quotienting gives four nontrivial classes:

```text
Q01 size 9: 01 04 05 08 34 45 47 56 58
Q02 size 9: 02 12 13 16 19 23 24 35 36
Q09 size 9: 09 18 29 37 57 68 78 79 89
Q26 size 4: 26 46 67 69
```

There is no same-distance `K4` and no same-distance codegree-3 obstruction in
these classes. The checker extracts two `K4-e` stretch relations:

```text
Q48 = sqrt3 * Q01 from quad (0,4,5,8), missing 48
Q26 = sqrt3 * Q02 from quad (1,2,3,6), missing 26
```

The second relation is decisive. Since `46` is in `Q26`,
`d46 = sqrt(3) rho(Q02)`. The Kalmanson inequality on cyclic quadruple
`0 < 1 < 4 < 6` is

```text
d01 + d46 <= d04 + d16.
```

Substitution gives

```text
rho(Q01) + sqrt(3) rho(Q02) <= rho(Q01) + rho(Q02),
```

or

```text
(sqrt(3) - 1) rho(Q02) <= 0,
```

which is impossible because `rho(Q02) > 0`.

The replay finds two additional Kalmanson contradictions from the same stretch
relation:

```text
(2,3,4,6): d23 + d46 <= d24 + d36
(3,4,6,7): d34 + d67 <= d36 + d47
```

Both reduce to the same positive coefficient
`(sqrt(3) - 1) rho(Q02)`.

## Methodological Role

This audit retires the displayed `n=10` quotient-level survivor only. It
supports adding a `K4-e` stretch layer before heavier midpoint, EDM-rank, or
Farkas machinery:

```text
row-overlap / crossing / parity
-> selected-distance quotient
-> K4 and codegree-3 checks
-> K4-e extraction
-> symbolic Kalmanson-stretch check
-> midpoint / EDM / Farkas checks
```

The result is a filter improvement, not an `n=10` exclusion. The next search
loop should rerun with this layer enabled and report the next survivor, if any,
under the same non-overclaiming rules.
