# Quartic Marked-Root Gram Pilot

Status: `EXACT_OBSTRUCTION` / `FAILED_SEARCH_FAMILY`.

This note records a predeclared decisive test for the degree-four boundary in
`docs/cubic-graph-half-branch-model-case.md`. It asks whether the flexibility
that permits one four-rich row on a strictly convex quartic graph can close all
rows of the smallest equally spaced nine-parameter sample. The test is exact,
but its family is deliberately narrow. It does not prove or refute Erdos
Problem #97.

## Decisive-Test Contract

The fixed parameter set is

```text
T = {-4,-3,-2,-1,0,1,2,3,4}.
```

The graph family is

```text
gamma_a(t) = (t, a1*t + a2*t^2 + a3*t^3 + a4*t^4),  a4 != 0.
```

The two predeclared outcomes were:

- `LOCAL_ONLY`: the one-rich-row quartic phenomenon fails the planar rank-one
  gate or every exceptional affine state dies when further center rows are
  imposed;
- `FIXED_GRID_CLOSURE`: an exact degree-four planar Gram matrix survives all
  nine center rows and the strict finite-convexity check.

An exact negative conclusion is permitted only if every positive-dimensional
affine state is either resolved by the rank-one minors or extended through the
remaining centers. A timeout, an irrational quadratic component, or a
higher-dimensional final state must instead be retained as `UNRESOLVED`.

## Lifted Row Equations

Put

```text
v(t) = (t,t^2,t^3,t^4)^T,
f_a(t) = a^T v(t),
A = a*a^T.
```

For a center parameter `s` and witness parameter `q`, squared distance is

```text
D_A(s,q) = (q-s)^2 + (v(q)-v(s))^T A (v(q)-v(s)).
```

The ten variables are the upper-triangular entries

```text
(A11,A12,A13,A14,A22,A23,A24,A33,A34,A44).
```

For a marked witness quartet `q0<q1<q2<q3`, the three equations

```text
D_A(s,qk) - D_A(s,q0) = 0,  k=1,2,3,
```

are affine-linear over the rationals in those ten variables. Equivalently, if

```text
Q(X) = product_k (X-qk),
```

then `Q` divides the degree-at-most-eight distance fiber after its radius is
subtracted. The implementation checks this divisibility independently on the
positive control, rather than using it as a restatement of the three row
equations.

Every such affine system contains the distinguished matrix

```text
A* = -E11.
```

Indeed, its quadratic term cancels the horizontal `(q-s)^2` term, so all
lifted squared distances are zero. This is not a graph Gram: it is rank one
and negative semidefinite. The full-Gram interpretation below identifies it
with the zero coefficient Gram.

Linear feasibility is only a relaxation. A planar polynomial graph requires

```text
A != 0,
all 2-by-2 minors of A vanish,
A is positive semidefinite,
A44 > 0.
```

A higher-rank positive-semidefinite matrix represents a curve in a higher
ambient dimension and is rejected.

## Anchor Enumeration

The anchor centers are `0,3,4`. Each center has `binom(8,4)=70` possible
marked witness quartets, so there are `70^3=343000` raw marked triples.

Two different circle centers cannot have three common witnesses. Therefore
the exact two-circle intersection cap safely removes anchor pairs whose marked
quartets overlap in more than two labels. It leaves `202080` marked triples.
The affine ranks are:

```text
rank 8:   2731 marked triples
rank 9: 199349 marked triples
```

Every rank-nine system is an affine line through `A*`. Substituting its
rational line parameter into all `2-by-2` minors gives polynomials of degree
at most two; the common rational polynomial gcd decides whether the line has
a real rank-at-most-one point. All `199349` rank-nine marked triples fail the
combined planar graph gate: their only retained real rank-one root is `A*`,
not a nonzero PSD degree-four Gram matrix `a*a^T` of real graph coefficients.

The rank-eight triples collapse to `2729` canonical affine RREF states. These
states, rather than a selected representative matrix from each state, are the
exceptional frontier passed to the remaining centers.

## Exceptional-Frontier Continuation

For each unused center, every one of its 70 marked quartets is appended to
every current RREF state. Consistent child systems are canonicalized and
deduplicated before applying nonlinear gates:

- a unique Gram matrix is checked for exact rank one, PSD, and `A44>0`;
- an affine line is intersected with all rank-one minors exactly;
- an irrational real quadratic component or a whole rank-at-most-one line is
  retained for the next center;
- dimension at least two is retained as an affine state;
- a rational degree-four Gram is checked directly against the exact distance
  partition at every center.

No witness-overlap filter is used after RREF states are merged. This makes the
continuation a harmless superset search and prevents state deduplication from
hiding a future witness choice.

At the first extension center, `-4`, the `2729` input states and 70 row choices
give `191030` linearly consistent state-row branches. Canonical RREF
deduplication leaves 315 affine solution states: 314 affine lines and the
singleton `{A*}`. The only rank-at-most-one matrix retained by any of these
states is again `A*`; there is no rank-one PSD degree-four graph Gram. Thus the
exceptional frontier is empty after center `-4`; no later center is needed to
close this fixed family.

The terminal result is

```text
unresolved affine states:        0
rank-one degree-four Grams:       0
strict finite full closures:      0
```

Consequently, no degree-exactly-four polynomial graph on this parameter set
has all nine rows four-rich, even before a convexity assumption is imposed.

The checked extension accounting and terminal frontier are stored in
`data/certificates/quartic_marked_root_gram.json`. The artifact is regenerated
and compared byte-for-structure by

```bash
python scripts/check_quartic_marked_root_gram.py \
  --check --assert-expected --json
```

## Post-Hoc Full-Gram Upgrade

The following strengthening was derived after the decisive-test contract and
is not one of its predeclared outcomes. It reclassifies the same exact marked
row systems with the full coefficient Gram; it does not change the original
graph certificate.

Let

```text
gamma(t) = C*v(t) = sum_{k=1}^4 c_k*t^k,
B = C^T*C.
```

Translations can remove an arbitrary constant coefficient without changing
distances. For `u(s,q)=v(q)-v(s)`,

```text
|gamma(q)-gamma(s)|^2 = u(s,q)^T*B*u(s,q).
```

Every marked equal-distance equation is therefore homogeneous and linear in
`B`. Conversely, every nonzero solution `B >= 0` of rank at most `d` factors
as `C^T*C` and realizes the marked equations in `R^d`; degree exactly four is
equivalent to `B44>0`. In the graph specialization,

```text
B = E11 + A.
```

Thus an affine graph solution space is exactly `-E11 + ker(L)`, and the
universal point `A*=-E11` is `B=0`. In particular, the repeated
negative-semidefinite root in the original accounting is a homogenization
base point, not evidence that every nonzero full Gram has negative sign.
All marked-row matrices have rational entries, so their rational nullspaces
base-change to their complete real nullspaces; this classification does not
discard polynomial maps with irrational real coefficients.

For a one-dimensional homogeneous kernel with generator `K`, a planar
realization can exist only when `K` is positive or negative semidefinite and
has rank at most two. A nonzero determinant already excludes the plane;
when the determinant vanishes, exact inertia is needed. The post-hoc exact
classification of the 315 extension states is

```text
zero kernel:                         1
nonsingular Lorentzian kernels:    231
nonsingular inertia-(2,2) kernels:   6
definite rank-four kernels:         66
singular inertia-(1,1,2) kernels:   11
```

The 66 definite kernels show why this is a planar result, not an obstruction
in every Euclidean dimension: they factor in dimension four.

The rigid rank-nine anchor stratum has exactly two PSD rank-two rays. In the
upper-triangular order used above they are generated by

```text
K1 = (2308,108,-232,24,183,18,-21,28,-6,3),
K2 = (292,-248,-88,44,211,74,-37,28,-14,7).
```

Both are degenerate controls rather than polygon candidates. Their maximum
positive-radius multiplicities at centers `-4,-3,...,4` are

```text
(2,4,4,4,4,4,4,4,4).
```

For `K1`, the sampled map identifies parameter pairs `(-3,4)`, `(-2,-1)`,
and `(2,3)`. For `K2`, it depends only on `t*(1-t)` and identifies
`(-3,4)`, `(-2,3)`, `(-1,2)`, and `(0,1)`. Hence neither ray gives nine
distinct points, and neither supplies a four-witness row at center `-4`.

Combining those two rigid-ray checks with the exact classification of every
rank-eight state extended through center `-4` gives the post-hoc lemma:

> Let `gamma:R->R^2` be a real polynomial map of degree at most four, and
> sample it at nine equally spaced parameters. If the nine sampled points are
> pairwise distinct, then at least one of the four sample centers corresponding
> to parameters `-4,0,3,4` is not four-rich within the sample.

For a progression `beta+alpha*T`, with `alpha != 0`, the explicit
normalization is

```text
gamma_tilde(u) = gamma(beta+alpha*u) - gamma(beta).
```

This preserves all sample distances and coordinate degree, and reduces the
progression to `T`. Convexity is not used. Pairwise distinctness is required
by the planar two-circle overlap pruning. The lemma does not cover irregular
parameter sets, polynomial degree above four, higher-dimensional samples,
implicit or general algebraic quartics, multi-arc constructions, or arbitrary strictly
convex polygons.

## Calibrated Controls

The exact positive one-rich-row fixture is

```text
f(t) = (-51017/6552)*t
     + (337469/393120)*t^2
     - (2503/65520)*t^3
     + (253/393120)*t^4.
```

At center `s=0`, its witnesses are

```text
(7,-24), (15,-20), (20,-15), (24,-7),
```

all at squared distance `625`. Its second derivative has positive minimum

```text
229153/14208480
```

on `[0,24]`. It must pass the marked equations, independent divisibility,
rank-one, degree-four, and convexity gates. It remains one rich row only.

For the higher-rank relaxation trap, add `c*c^T` with

```text
c = (-15180,1553,-66,1)
```

to the positive-control Gram matrix. The three marked-row equations still hold
and the resulting matrix is PSD, but it has rank two and is rejected as a
planar quartic graph.

## Claim Boundary

The predeclared artifact concerns one fixed equally-spaced parameter set, one
graph coordinate form, and degree exactly four. The post-hoc full-Gram lemma
extends the planar polynomial-parametrization scope to degree at most four and
all affine copies of the equally-spaced grid, but no further. Neither result
covers irregular parameter sets, general implicit quartics, higher degree,
multi-arc samples, or arbitrary strictly convex polygons. This remains a
failed search family, not a global bridge and not a proof of Erdos Problem
#97.
