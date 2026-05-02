# Altman diagonal-order sum obstruction

Status: `EXACT_OBSTRUCTION` for natural-cyclic-order selected patterns.

No general proof of Erdos Problem #97 is claimed. No counterexample is claimed.

## Theorem

Let `P` be a strict convex `n`-gon in cyclic order. Define

```text
U_k = sum_{i=0}^{n-1} |p_i - p_{i+k}|,
1 <= k <= floor(n/2),
```

with indices modulo `n`. For even `n` and `k=n/2`, this convention counts each
maximal diagonal twice.

Altman's theorem gives

```text
U_1 < U_2 < ... < U_floor(n/2).
```

## Proof Source

E. Altman, "Some theorems on convex polygons", Canadian Mathematical Bulletin
15(3), 1972, 329-340, Theorem 1. DOI: `10.4153/CMB-1972-060-0`.

## Application Rule

For a constant cyclic-offset selected pattern

```text
S_i = {i+o_1, i+o_2, i+o_3, i+o_4},
```

if the natural label order `0,1,...,n-1` is the polygonal cyclic order, the
equal-distance row constraints imply equal ordinary distances from each center
to all four selected offsets. Summing over all rows forces equality among the
diagonal sums `U_ord(o_r)`. If at least two selected offsets have distinct
cyclic chord orders, this contradicts Altman's strict chain.

Squared-distance equalities imply ordinary-distance equalities because
distances are nonnegative and selected witnesses are distinct from their
centers.

## C19_skew

For `C19_skew`,

```text
n = 19
S_i = {i-8, i-3, i+5, i+9}.
```

The natural-order selected equalities imply

```text
|p_i-p_{i-8}| = |p_i-p_{i-3}| = |p_i-p_{i+5}| = |p_i-p_{i+9}|.
```

The chord orders are `8`, `3`, `5`, and `9`, so summing over all `i` gives

```text
U_8 = U_3 = U_5 = U_9.
```

Altman gives

```text
U_3 < U_5 < U_8 < U_9.
```

Thus `C19_skew` is exactly obstructed in natural cyclic order.

## Caveats

- The constant-offset application above is natural-cyclic-order only.
- The order-dependent signature extension below can check any supplied cyclic
  order, but it is not a complete abstract-order search.
- `C19_skew` remains an abstract-incidence sparse survivor of the current
  `phi`, midpoint, forced-perpendicularity, and vertex-circle filters.

## Order-Dependent Signature Filter

The script also has a fixed-order extension:

```bash
python scripts/check_altman_diagonal_sums.py \
  --pattern C19_skew \
  --order 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18 \
  --assert-natural-killed
```

For a supplied cyclic order, the checker unions the distance classes forced by
the selected rows. It then writes every Altman diagonal sum `U_k` as a formal
multiset of those distance classes. If two distinct diagonal orders have the
same formal multiset, the selected equalities force the corresponding `U_k`
values to be equal, contradicting Altman's strict chain.

This recovers the natural-order `C19_skew` obstruction as an exact fixed-order
signature contradiction:

```text
equal diagonal groups: [[3, 5, 8, 9]]
```

The known abstract `C19_skew` cyclic order that passes the crossing plus
vertex-circle filter also passes this signature filter:

```bash
python scripts/check_altman_diagonal_sums.py \
  --pattern C19_skew \
  --order 18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1
```

So the order-dependent signature filter is useful bookkeeping but does not
close the `C19_skew` abstract-order gap.

## Altman LP Relaxation

There is also a numerical linear diagnostic:

```bash
python scripts/check_altman_diagonal_sums.py \
  --pattern C19_skew \
  --order 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18 \
  --lp-diagnostic \
  --assert-natural-killed
```

It assigns one nonnegative variable to each selected-distance class, normalizes
their sum to `1`, and maximizes `gamma` subject to

```text
U_{k+1} - U_k >= gamma
```

for every adjacent diagonal order. A positive optimum means the selected
distance classes can satisfy Altman's strict chain at this relaxation level. A
nonpositive optimum is a `NUMERICAL_LINEAR_DIAGNOSTIC` obstruction for the
fixed order.

For natural-order `C19_skew`, the optimum is `-0.0`, matching the exact
signature obstruction above. For the known abstract `C19_skew` order, the
optimum is `0.08333333333333333`, so this broader relaxation still does not
kill that order. This is useful negative information, not evidence of
geometric realizability.

## Exact Linear Certificates

The same adjacent-gap bookkeeping can emit an exact rational certificate:

```bash
python scripts/check_altman_diagonal_sums.py \
  --pattern C19_skew \
  --order 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18 \
  --rational-certificate \
  --assert-natural-killed
```

A certificate is a nonnegative rational combination of adjacent Altman gaps
`U_{k+1} - U_k` whose selected-distance-class coefficients are all
nonpositive. If all adjacent Altman gaps were strictly positive, every
nonzero nonnegative combination would be positive. The verified nonpositive
coefficient vector is therefore an exact fixed-order obstruction.

For natural-order `C19_skew`, the shortest certificate found uses the single
adjacent gap

```text
U_9-U_8.
```

The selected rows force the formal coefficient vector to be identically zero,
so Altman's strict inequality `U_8 < U_9` is impossible. The known abstract
`C19_skew` order has no such rational certificate with denominator at most
`1000` under the current search. That is only a certificate-search miss, not a
realizability claim.

## Sweep

The checked-in sweep generator applies the exact certificate search to every
built-in natural order plus the registered non-natural `C19_skew` survivor:

```bash
python scripts/sweep_altman_linear_certificates.py \
  --assert-expected \
  --out data/certificates/altman_linear_certificate_sweep.json
```

The artifact records that the natural orders of `C13_sidon_1_2_4_10`,
`C25_sidon_2_5_9_14`, and `C29_sidon_1_3_7_15` are all exactly killed by
Altman linear certificates. The registered abstract `C19_skew` order remains
a certificate-search miss. This narrows the sparse-overlap wall to non-natural
cyclic orders; it does not prove or disprove realizability of any abstract
survivor.
