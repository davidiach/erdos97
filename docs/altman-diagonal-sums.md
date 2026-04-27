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

- Altman's diagonal-order obstruction is natural-cyclic-order only.
- It does not kill abstract-incidence versions with arbitrary cyclic relabeling.
- `C19_skew` remains an abstract-incidence sparse survivor of the current
  `phi`, midpoint, and forced-perpendicularity filters.
