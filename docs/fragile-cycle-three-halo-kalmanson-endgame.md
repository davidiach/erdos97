# Fragile-cycle three-halo Kalmanson endgame

Status: exact bounded fixed-order metric certificate. This note does not claim
a geometric forcing lemma, a proof of `n=10`, a general proof, or a
counterexample.

## Purpose

The three-halo deep-frontier packet reduces the last two layers of one fixed
abstract search to thirteen vertex-circle-clean eight-row states. Its terminal
certificates use incidence dead ends or a forced ninth row. This follow-up asks
whether genuine convex metric information already rejects those states before
either terminal mechanism is needed.

For four vertices `a,b,c,d` in strict cyclic order, the two strict Kalmanson
inequalities are

```text
d(a,c) + d(b,d) > d(a,b) + d(c,d),
d(a,c) + d(b,d) > d(a,d) + d(b,c).
```

The checker quotients ordinary pair-distance variables by the selected
equalities of a partial row system and exhausts both inequalities for all
`C(10,4)=210` cyclic quadrilaterals.

## Exact result

Every one of the thirteen stored deep states contains a Kalmanson obstruction
using exactly three of its eight selected rows.

| Obstruction type | States | Strict inequalities | Selected rows |
| --- | ---: | ---: | ---: |
| One strict row collapses to equality | 11 | 1 each | 3 each |
| Two strict rows form an inverse pair | 2 | 2 each | 3 each |

The selected-row width is exactly three in every state: the checker exhausts
all subsets of widths zero, one, and two before enumerating every obstruction
at width three. Across the deterministically selected certificates there are
fifteen strict rows: four of Kalmanson kind `K1` and eleven of kind `K2`.

Thus the thirteen states need neither a ninth selected row nor the 1,386-row
incidence rejection ledger once natural cyclic-order metric information is
available. This is a smaller endgame for the already-fixed source catalog; it
does not explain why a minimal counterexample must enter that catalog.

## The two inverse pairs

State `S08` uses selected rows at centers `2`, `3`, and `5`:

```text
2 -> {0,3,4,6}
3 -> {0,1,5,7}
5 -> {2,4,6,7}
```

Add `K1(0,2,3,6)` and `K2(3,5,6,7)`. The `d(3,6)` terms cancel directly,
while the selected equalities give

```text
d(0,3) = d(3,7),
d(2,6) = d(0,2),
d(5,7) = d(5,6).
```

The sum of two strict positive expressions is therefore exactly zero.

State `S11` uses selected rows at centers `0`, `1`, and `3`:

```text
0 -> {1,2,4,8}
1 -> {0,2,6,9}
3 -> {1,5,8,9}
```

Add `K2(0,1,2,3)` and `K1(0,1,3,9)`. The `d(0,3)` terms cancel, and the
selected equalities identify the remaining three positive/negative pairs:

```text
d(0,2) = d(0,1),
d(1,3) = d(3,9),
d(1,9) = d(1,2).
```

Again the strict sum reduces to zero with unit weights.

## Certificate and minimality contract

For every state the artifact stores:

- the source halo placement and cyclic order;
- the selected three-row core in natural and original labels;
- one or two strict Kalmanson rows with exact integer weights;
- each strict row's positive and negative ordinary-distance pairs;
- its sparse coefficient vector after partial selected-distance quotienting;
- the number of subsets exhausted at every smaller width; and
- an independent exact replay of the combined zero coefficient vector.

No floating-point optimization result is part of the certificate. The search
uses only exact integer quotient vectors and exhaustive finite enumeration.

## Scope and next target

This packet supplies the ordinary-distance convex endgame requested by
Contract F once a source state has been reached. It remains conditional on the
fixed `23=27` quotient core, the three-halo placement model, and membership in
the thirteen-state catalog. It does not cover arbitrary fragile cycles or
force any retained row from deletion/minimality geometry.

The next genuine bridge target is therefore narrower: derive the `23=27`
core plus a three-row certificate core—or a separately checked alternative—
from a genuine fragile matching cycle and its active halos. Extending the
fixed halo count without such an entry argument is lower leverage.

## Replay

```bash
python scripts/check_fragile_cycle_three_halo_kalmanson_endgame.py \
  --check --assert-expected --summary-json

python scripts/check_fragile_cycle_three_halo_deep_frontier.py \
  --check --assert-expected --summary-json
```

The generated artifact is
`data/certificates/fragile_cycle_three_halo_kalmanson_endgame.json`; do not
edit it directly.
