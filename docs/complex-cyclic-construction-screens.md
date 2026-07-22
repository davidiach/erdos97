# Complex cyclic construction screens

Trust label: `NUMERICAL_EVIDENCE` for both retained sweeps. The displayed
doubled-hexagon calculation is an exact algebraic identity within one family.

These screens test whether adding complex Fourier coefficients to a regular
polygon produces a strictly convex counterexample to Erdos Problem #97. They
found no candidate. They do not obstruct either family and do not change the
official/global or repository-local problem status.

## Relation to the existing real two-mode certificate

The exact bounded certificate in [`two-mode-cyclic-exact-n80.md`](two-mode-cyclic-exact-n80.md)
covers the real family

```text
z_i = w^i + t w^(k i),  t real,
```

for `9 <= n <= 80`. The first screen below targets complex `c`, but only for
`9 <= n <= 30` and with floating tolerances. It complements the exact real
slice; it neither supersedes nor extends that certificate at exact trust.

## Complex two-mode enumeration

Consider

```text
z_i = w^i + c w^(k i),  c=x+iy,  R=|c|^2.
```

For one center and target shift, write the two Fourier differences as `a` and
`b`. Then

```text
|a+c b|^2 = |a|^2 + R |b|^2
             + 2 Re(b conjugate(a)) x
             - 2 Im(b conjugate(a)) y.
```

Thus four selected squared distances agree only if `(R,x,y)` satisfies three
affine equations, together with the quadratic surface `R=x^2+y^2`. The screen
enumerates row-zero four-sets and handles the affine ranks separately:

1. rank three gives one affine point, checked against the quadratic surface;
2. rank two gives an affine line with at most two surface intersections;
3. rank one gives a plane, crossed with collision planes from other centers;
4. every resulting complex coefficient is checked against all centers and
   the full distinctness/strict-convexity diagnostics.

The `9 <= n <= 30`, `2 <= k <= n-2` replay produced:

| Quantity | Value |
| --- | ---: |
| `(n,k)` cells | 363 |
| row-zero quadruples | 3,253,635 |
| deduplicated candidate coefficients | 128,434 |
| rank-at-most-one quadruples | 36,844 |
| rank-zero identity quadruples | 0 |
| continuous all-row rank-one planes | 0 |
| exact-looking invalid coefficients | 1,617 |
| strictly convex hits | 0 |

The best strictly convex coefficient occurred at `n=15`, `k=7`, with maximum
relative spread `0.0273661273589857`, normalized turn margin
`0.00248098061229757`, and normalized pair separation `0.128312313256038`.
It is not close to the exactification gate.

### The doubled-hexagon mirage is exact

At `n=12`, `k=7`, let

```text
w = exp(i*pi/6),  c = i(2+sqrt(3)).
```

Since `w^(7j)=(-1)^j w^j`,

```text
z_j = w^j (1 + (-1)^j c).
```

Direct algebra gives `(1+c)/(1-c)=w^5`. Hence for every even `e`,

```text
z_(e+5) = w^(e+5)(1-c) = w^e(1+c) = z_e.
```

The twelve indexed vertices form six coincident pairs:

```text
(0,5), (1,8), (2,7), (3,10), (4,9), (6,11).
```

This explains the machine-zero four-distance spreads without treating them as
a near-counterexample: the point set is a doubled hexagon and fails
distinctness and strict convexity exactly.

Artifact and replay details:
[`data/runs/complex_two_mode_cyclic_2026-07-22/README.md`](../data/runs/complex_two_mode_cyclic_2026-07-22/README.md).

## Complex three-mode construction search

The next family was

```text
z_i = w^i + c w^(k i) + d w^(ell i),  c,d complex.
```

For Fourier differences `a,b,e`, the squared distance `|a+c b+d e|^2` is
linear in the nine lifted quantities

```text
1, |c|^2, |d|^2, Re(c), Im(c), Re(d), Im(d),
Re(c conjugate(d)), Im(c conjugate(d)).
```

The lifted variables obey nonlinear compatibility relations, so this screen
is constructive rather than an exhaustive affine enumeration. Each cycle
selects every center's minimum-spread four-distance window, refines the four
real coefficient components by nonlinear least squares, then reselects the
windows. Candidate acceptance also requires normalized pair separation at
least `2e-3` and normalized hull-side margin at least `2e-6`.

The retained run covered every unordered mode pair `2 <= k < ell < n` for
`12 <= n <= 18`: 560 cells, 12 deterministic starts per cell, and at most 8
selection/refinement cycles per start. It found zero cells below the `1e-10`
relative-spread candidate gate. The best robust cell was `n=15`, modes
`(10,13)`, with spread `0.0198748713248327`, side margin
`0.00267608633453876`, and pair separation `0.128455903709775`.

Artifact and replay details:
[`data/runs/complex_three_mode_cyclic_2026-07-22/README.md`](../data/runs/complex_three_mode_cyclic_2026-07-22/README.md).

## Interpretation and non-claims

- Complex coefficients do create many algebraic distance collisions, but the
  machine-small two-mode collisions found here sit on nonconvex or coincident
  configurations.
- Adding a third mode did not produce an interior guarded solution at the
  recorded search budget; its best robust residual remains macroscopic.
- The two-mode enumeration uses floating rank and surface tolerances. It is
  not an exact classification of complex coefficients.
- The three-mode run is a finite seeded nonlinear search. It is not exhaustive
  even on the stated finite mode grid.
- Neither zero-hit result proves a restricted-family obstruction, a general
  theorem, or a counterexample.

The practical route decision is to stop polishing these Fourier families
unless a new exact structural mechanism appears. Further construction work
should change the incidence geometry rather than merely increase restart
counts in the same ansatz.
