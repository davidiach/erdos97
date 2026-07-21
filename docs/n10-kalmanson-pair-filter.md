# n=10 Kalmanson Pair-Filter Replay

Status: `MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING`.

This note records an exact labelled search in the ten-vertex selected-witness
domain.  It does not prove Erdos Problem #97, does not cover any `n > 10`, and
does not promote the repository's review-pending finite-case status.  Its role
is to give a short independent route to the existing draft `n=10` closure.

## Domain and necessary filters

Label a hypothetical bad decagon in cyclic order `0,...,9`, and choose one
four-witness row `S_i` at every center.  The search enumerates all

```text
binom(9,4) = 126
```

rows at every labelled center and imposes only these incidence conditions:

1. two selected rows intersect in at most two witnesses;
2. if two rows intersect in exactly two witnesses, their source chord crosses
   their common-witness chord;
3. an unordered witness pair occurs together in at most two selected rows;
4. every target has selected indegree at most six.

The first two conditions are the standard two-circle and radical-axis
consequences.  Condition 3 follows from them: three centers sharing one witness
pair would have to lie pairwise on opposite sides of that pair's chord, which
is impossible for a two-part cyclic partition.  For a fixed target `x`, every
row containing `x` contributes three witness pairs containing `x`.  Condition
3 therefore gives

```text
3 indeg(x) <= 2*9,
```

which proves condition 4.  Thus none of the four filters removes a possible
geometric decagon.

## One- and two-inequality obstruction

For cyclically ordered `a<b<c<d`, ordinary distances in a strictly convex
quadrilateral satisfy both strict Kalmanson inequalities

```text
d_ac + d_bd > d_ab + d_cd,
d_ac + d_bd > d_ad + d_bc.
```

At every partial assignment, the checker quotients the `45` unordered
pair-distance variables by all equalities contributed by the assigned rows.
It rejects in either of two exact situations:

- **self-edge:** one strict Kalmanson coefficient row becomes zero in the
  quotient, giving `0 > 0`;
- **inverse pair:** two primitive strict coefficient rows become exact
  negatives. Equivalently, the original rows are opposite positive scalar
  multiples, so a positive weighted sum gives `0 > 0`.

These conflicts are monotone under adding selected-row equalities, so detecting
one at a partial assignment is sound.  No linear programming, floating point,
or geometric optimizer is used.

Every reduced coefficient lies in `{-2,-1,0,1,2}`. The implementation divides
each nonzero vector by the gcd of its coefficients before comparison; this is
exact integer normalization, not a numerical tolerance.

The exhaustive C++ replay reports

```text
clean recursive nodes:       261,511
self-edge prunes:             360,742
inverse-pair prunes:        1,213,492
full assignments:                   0
```

The minimum-remaining-options choice changes only traversal order.  Labels are
fixed, row zero is not normalized by symmetry, and all `126` row-zero choices
are traversed.

## Independent Python slices

The Python implementation shares no search code with the C++ replay.  It
rebuilds row choices, pairwise compatibility, the selected-distance quotient,
and all

```text
2*binom(10,4) = 420
```

strict Kalmanson rows.  Three labelled row-zero slices agree exactly with the
C++ implementation:

| row-zero index | nodes | self-edge prunes | inverse-pair prunes | full |
|---:|---:|---:|---:|---:|
| 0 | 835 | 245 | 2,620 | 0 |
| 63 | 2,411 | 3,316 | 10,426 | 0 |
| 125 | 1,329 | 1,322 | 4,052 | 0 |

The slices are second-source spot checks, not a second full replay.

## Commands

Run the Python spot checks:

```bash
python scripts/check_n10_kalmanson_pair_filter.py --assert-expected
```

Compile and run the complete C++ traversal as an artifact-tier check:

```bash
python scripts/check_n10_kalmanson_pair_filter.py \
  --run-cpp \
  --assert-expected
```

Run the focused tests:

```bash
python -m pytest -q -o addopts= tests/test_n10_kalmanson_pair_filter.py
```

## Relationship to the existing draft

`docs/n10-vertex-circle-singleton-slices.md` records a separate complete
`n=10` draft using nested-chord self-edges and strict cycles, with a portable
C++ second source.  The replay here is narrower and algebraically different:
it uses only one strict Kalmanson inequality or a primitive inverse pair of two
such inequalities. Agreement strengthens the finite-case audit trail, but it
does not replace independent mathematical review and does not alter the global
open status.

In particular, the finite closure gives no bounded-localization theorem.  The
separate scalable strict-cycle negative control in
`docs/scalable-strict-cycle-bridge-control.md` shows why a global argument must
allow obstruction support to grow with `n`, or must add stronger genuinely
Euclidean structure.
