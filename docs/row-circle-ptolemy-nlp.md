# Row-Circle Ptolemy NLP

Status: `NUMERICAL_NONLINEAR_DIAGNOSTIC`.

This diagnostic adds one geometric fact missing from the earlier Ptolemy-order
NLP: for each center `i`, the four selected witnesses `S_i` lie on a circle
centered at `i`. In their angular order around `i`, those four witnesses must
satisfy Ptolemy with equality.

No general proof of Erdos Problem #97 is claimed. No counterexample is claimed.
A numerical obstruction here is only an exactification target.

## Constraint Added

For row `i`, let the selected witnesses in angular order be

```text
a, b, c, d.
```

Then the row-circle Ptolemy equality is

```text
d(a,b) d(c,d) + d(b,c) d(a,d) = d(a,c) d(b,d).
```

The diagnostic uses ordinary distance-class variables, quotiented by selected
row equalities, and combines:

- Altman adjacent diagonal-gap inequalities;
- vertex-circle strict inequalities;
- ordinary triangle inequalities;
- global cyclic-quadrilateral Ptolemy inequalities;
- row-circle Ptolemy equalities for every selected witness row.

## Registered Sparse Orders

The generated artifact is
`data/certificates/row_circle_ptolemy_nlp_sparse_orders.json`.

For the registered `C19_skew` abstract-order survivor, SLSQP terminates
successfully with a negative strictness margin:

```text
max_margin = -0.00264843
row_ptolemy_max_abs_residual = 2.98e-19
```

This is a numerical obstruction in the strengthened relaxation, not an exact
obstruction. It should be treated as a promising target for exactification.

For the registered `C13_sidon_1_2_4_10` order, SLSQP reports incompatible
inequality constraints from the LP-based start and leaves small but nonzero
Ptolemy/row-equality residuals. That is recorded as optimizer failure, not as
an obstruction.

## C19 Active-Set Snapshot

The exactification helper
`scripts/dump_row_circle_ptolemy_snapshot.py` records the optimized
distance-class vector and the active numerical constraints for the registered
`C19_skew` survivor. The generated artifact is
`data/certificates/c19_row_circle_ptolemy_active_set.json`.

It records:

- all 114 quotient distance classes and their normalized numerical values;
- the 22 tight linear rows from the Altman / vertex-circle / triangle
  relaxation;
- the 74 tight global Ptolemy inequalities;
- all 19 row-circle Ptolemy equality residuals and their witness orders;
- the SciPy SLSQP multiplier summary for the normalization equality, row
  equalities, linear inequalities, and global Ptolemy inequalities.

This is still only a floating-point active set. It is useful because it exposes
the likely certificate support for a later rational or algebraic
exactification attempt. In the current snapshot, the nonzero multiplier counts
are 19 linear inequalities, 57 global Ptolemy inequalities, and all 19
row-circle equalities.

The reduction artifact
`data/certificates/c19_row_circle_multiplier_reduction.json` matches each
row-circle equality with the duplicate global Ptolemy inequality on the same
four witnesses. All 19 rows match. After combining each duplicate pair, the
largest absolute multiplier drops from about `2.95e17` to `24`, showing that
most of the enormous multipliers are redundant-constraint cancellation noise.

## Reproduction

```bash
python scripts/check_row_circle_ptolemy_nlp.py \
  --pattern C19_skew \
  --order 18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1 \
  --order-label vertex_circle_survivor \
  --assert-expected \
  --maxiter 500

python scripts/check_row_circle_ptolemy_nlp.py \
  --maxiter 500 \
  --out data/certificates/row_circle_ptolemy_nlp_sparse_orders.json \
  --assert-expected

python scripts/dump_row_circle_ptolemy_snapshot.py \
  --out data/certificates/c19_row_circle_ptolemy_active_set.json \
  --maxiter 500 \
  --assert-expected
```

The registered sweep is slow because of the `C19` nonlinear solve. CI checks
the artifact and the CLI import path instead of rerunning the full NLP.
