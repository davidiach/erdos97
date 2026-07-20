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

Every rank-nine system is an affine line. Substituting its rational line
parameter into all `2-by-2` minors gives polynomials of degree at most two; the
common rational polynomial gcd decides whether the line has a real rank-at-
most-one point. All `199349` rank-nine marked triples fail the combined
nonzero, PSD, and degree-four planar Gram gate: their retained real rank-one
roots are negative semidefinite, never Gram matrices of real planar graph
coefficients.

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
deduplication leaves 315 affine lines. Their exact minor intersections contain
only negative-semidefinite rank-one roots and no rank-one PSD degree-four Gram
matrix. Thus the exceptional frontier is empty after center `-4`; no later
center is needed to close this fixed family.

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

The checked search concerns one fixed equally-spaced parameter set, one graph
coordinate form, and degree exactly four. The result does not cover other
parameter sets, parametric or implicit quartics, higher-degree graphs,
multi-arc samples, or arbitrary strictly convex polygons. It is a failed
search family, not a bridge lemma and not a proof of Erdos Problem #97.
