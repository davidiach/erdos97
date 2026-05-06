# Paraboloid-Lift Filter (proof-of-concept)

Status: `EXPLORATORY_DRAFT_REVIEW_PENDING`. This note documents an honest
proof-of-concept and reports a **negative** structural finding: the dual
column-determinant Plucker subsystem is, after gauge fix and elimination of
the auxiliary `c_i` variables, an algebraic *consequence* of the existing row
equidistance system. It does NOT add new content beyond
`scripts/check_affine_circuit_certificates.py` or
`data/runs/2026-05-05/groebner_attack.py`.

This file exists so the negative result is explicitly recorded, and so the
small structural diagnostics added in
`src/erdos97/paraboloid_lift_filters.py` are reproducible.

## Setup (canonical-synthesis.md, Section 1.3, equivalence #4)

Each polygon vertex `p_i = (x_i, y_i)` lifts to
`hat_p_i = (x_i, y_i, x_i^2 + y_i^2)` on the paraboloid `z = x^2 + y^2`.
The strong witness condition "vertex `i` has 4 equidistant other vertices" is
equivalent to: the 4 lifted witnesses lie on a hyperplane `H_i` *parallel
to the tangent plane* of the paraboloid at `hat_p_i`. The tangent plane has
normal `(2 x_i, 2 y_i, -1)`, and `H_i` has equation

    z = 2 x_i x + 2 y_i y + c_i

for a vertex-dependent constant `c_i`.

## Two equivalent algebraic encodings

ROW form (existing). For each row `i` and witness `j in S_i` we have

    x_j^2 + y_j^2 - 2 x_i x_j - 2 y_i y_j - c_i = 0.

Eliminating `c_i` by setting `c_i = q_a - 2 x_i x_a - 2 y_i y_a` for any
chosen `a in S_i` gives the standard equidistance polynomial

    D(i, a) = D(i, j),

equivalent to `||v_i - v_a|| = ||v_i - v_j||`. This is the polynomial system
in `data/runs/2026-05-05/groebner_attack.py`.

COLUMN (dual) form. For each vertex `j` with indegree `d_j >= 4`, every
4-subset `{i_1, ..., i_4}` of incidents-to-`j` produces the rank-3 condition

    rank [ 2 x_{i_k}, 2 y_{i_k}, c_{i_k}, x_j^2 + y_j^2 ]_{k=1..4} <= 3,

equivalently, the 4x4 determinant vanishes. This is the column-determinant
Plucker identity for the dual configuration: the lifted vertex `hat_p_j`
lies on the four parallel-tangent hyperplanes `H_{i_1}, ..., H_{i_4}`.

## What is the column form's algebraic content?

After substituting `c_{i_k} = q_a - 2 x_{i_k} x_{a_k} - 2 y_{i_k} y_{a_k}`
for some chosen `a_k in S_{i_k}`, the column 4x4 determinant simplifies to

    q_j * det of 3x3,

where the 3x3 matrix is (after row 1 subtraction)

    [ 2 (x_{i_k} - x_{i_1}),  2 (y_{i_k} - y_{i_1}),
      -2 (x_{i_k} - x_{i_1}) * x_{a_k} - 2 (y_{i_k} - y_{i_1}) * y_{a_k}
      + (other contributions from c_{i_1} - c_{i_k} mixing) ]

When `a_1 = a_2 = a_3 = a_4 = j` (which holds whenever there is a common
"all-incidents-share-witness-j" structure), the third column is exactly
`-x_j * col1 - y_j * col2`, so the 3x3 determinant is identically zero.
For more general choices of `a_k` the column is a linear combination that
remains zero modulo the four row equations
`D(i_k, a_k) = D(i_k, j)`. We verified this empirically on the 15 n=8
survivors: the column-Plucker polys, when computed after `c_i` elimination
and reduced modulo the row Groebner basis, all collapse to zero.

CONCLUSION (the negative finding). The column-determinant Plucker subsystem
is an **algebraic consequence** of the row equidistance subsystem. It does
not add new exact obstructions. This is the dual incarnation of the same
algebraic content; its only practical use is as a structural diagnostic.

## What this module does add (modest, non-novel content)

1. `column_determinant_indegree(rows, n)` reports `d_j = #{ i : j in S_i }`.
2. `column_determinant_rank_summary(rows, n)` reports the per-vertex count
   of nonzero column-Plucker polys (after gauge fix; some collapse to zero
   simply because of the gauge choice `x_0 = y_0 = 0`).
3. `incidence_matrix_rank_diagnostics(rows, n)` reports `rank_QQ` and
   `rank_GF2` of the 0/1 incidence matrix `B[i, j]`. This is a structural
   fingerprint, not an obstruction. Empirically on the 15 n=8 survivors:
   * `rank_QQ in {5, 7, 8}`, with patterns 0, 6, 11 having rank 5 (the
     symmetric Q3-cube class), pattern 2 having full rank 8, and the
     remaining 11 patterns having rank 7.
   * `rank_GF2` matches `rank_QQ` for these patterns.
4. `run_row_groebner_with_column_pucker_enrichment(rows, n,
    use_column_pucker=True)` runs a SymPy Groebner over QQ with the row
   polys augmented by the column-Plucker polys. By the negative finding
   above this is mathematically the same as the row-only Groebner.
   Empirically on the 15 n=8 survivors:
   * 14 / 15 patterns produce trivial GB `{1}` in 1.6 to 7.2 seconds; this
     matches the existing row-only result.
   * The remaining pattern (id=14) produces a non-trivial zero-dimensional
     GB; same as in the existing row-only result.
   * Total wall-clock on 15 patterns is approximately 50 s. This is roughly
     10x slower than the row-only Groebner (which is ~3.4 s total per the
     existing certificate `data/certificates/2026-05-05/n8_groebner_results.json`).
   * Conclusion: enrichment costs more, gains nothing.

## Files

| Path | Purpose |
|---|---|
| `src/erdos97/paraboloid_lift_filters.py` | Module with the dual filter, eliminated column polys, GB drivers, rank diagnostics. |
| `scripts/test_paraboloid_filters.py` | Test harness that exercises the module on the 15 n=8 survivors and on small cyclic-shift n=10/n=11 candidates. |
| `data/certificates/paraboloid_lift_test.json` | JSON aggregate of GB and rank diagnostics for the n=8 mode (15 patterns). |
| `data/certificates/paraboloid_lift_test_n8.json` | Saved copy of the n=8 run. |
| `data/certificates/paraboloid_lift_test_n9.json` | n=9 run on the 16 Groebner-2026-05-05 families. |
| `data/certificates/paraboloid_lift_test_n10.json` | n=10 cyclic-shift exploratory run. |
| `data/certificates/paraboloid_lift_test_n11.json` | n=11 cyclic-shift exploratory run. |

## Empirical comparison with existing row Groebner

| n | Family / id | Existing row GB size | row+Plucker GB size | Existing vcof verdict | Match? |
|---|---|---|---|---|---|
| 8 | id=0..13 | 1 (trivial) | 1 (trivial) | n/a | yes |
| 8 | id=14 | 4 (zero-dim) | 15 (zero-dim) | n/a | same realisation locus |
| 9 | F01..F06, F10, F11, F14, F15, F16 | 1 (trivial) | 1 (trivial) | obstructed | yes |
| 9 | F07, F08, F09, F13 | 62 (non-trivial) | 62 (non-trivial) | obstructed | yes |
| 9 | F12 | 14 (non-trivial, has y8^2 + 1/4) | 14 (non-trivial) | obstructed | yes |
| 10 | cyclic S={1,2,3,5} | not run by existing GB | 1 (trivial) | obstructed | redundant; existing crossing-bisector filter kills it |
| 10 | cyclic S={1,2,4,7} | not run by existing GB | 17 (zero-dim, degenerate) | obstructed | redundant; existing vcof kills it |
| 10 | cyclic S={1,3,4,7} | not run by existing GB | 1 (trivial) | obstructed | redundant; existing vcof kills it |
| 11 | cyclic S={1,2,4,8} | not run by existing GB | not run | obstructed (3 cycles) | vcof alone is faster |
| 11 | cyclic S={1,3,4,9} | not run by existing GB | not run | obstructed (3 cycles) | vcof alone is faster |
| 11 | cyclic S={1,3,5,9} | not run by existing GB | not run | obstructed (11 self-edges) | vcof alone is faster |
| 11 | cyclic S={2,3,5,8} | not run by existing GB | not run | obstructed (77 self-edges) | vcof alone is faster |

Net new exact obstructions on patterns NOT killed by existing toolkit: **0**.

## Honest summary: is anything NEW for #97?

No. The dual paraboloid filter is mathematically equivalent to the existing
row Groebner system. It does not kill any pattern that the existing finite-
case toolkit accepts, and it does not produce a smaller proof object. The
filter is recorded here so that the paraboloid lift formulation is no
longer "open" as an unevaluated angle: it has been evaluated, and its
algebraic content is identical to what is already in
`src/erdos97/affine_circuit_certificates.py` and the existing row-Groebner
attack.

The structural diagnostic (`rank_QQ` of the incidence matrix) is a useful
**fingerprint** for organizing patterns into symmetry classes, but it is
NOT an obstruction in any of the senses recorded in `RESULTS.md`.

## What was NOT tried (deferred)

* Schubert calculus / projective rigidity bounds on the lifted variety.
  These would require Macaulay2 or Sage and a careful semialgebraic
  treatment.
* Positivstellensatz / SOS certificates that combine equidistance with
  strict-convexity inequalities. These are a candidate for a separate
  filter and would be a genuinely new direction.
* Cayley-Bacharach style residue conditions for 9 points on the
  paraboloid quadric. The paraboloid intersected with a generic hyperplane
  gives a circle (1-dim family of circles); 9 points on a circle is a
  pencil of cubics, but the n=9 problem at hand has 9 vertices arranged
  on the paraboloid, not on a single circle, so the standard Cayley-
  Bacharach argument does not apply directly.

This document does NOT claim a proof of Erdos #97 in any form.
