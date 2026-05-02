# Metric Order LP Diagnostic

Status: numerical fixed-order linear diagnostic. No general proof and no
counterexample are claimed.

This diagnostic combines three necessary conditions for a fixed cyclic order:

- Altman's adjacent diagonal-sum gaps, `U_{k+1} - U_k > 0`;
- vertex-circle strict chord inequalities from completed selected rows;
- ordinary metric triangle inequalities.

The variables are ordinary distance classes after quotienting by the selected
row equalities. The LP normalizes the sum of all distance-class variables to
`1` and maximizes a shared strictness margin `gamma` for the Altman and
vertex-circle inequalities. Triangle inequalities are non-strict.

Passing the LP is not evidence of geometric realizability. Failing it would
still be only a numerical linear diagnostic until converted into an exact
rational certificate.

## Reproducible command

```bash
python scripts/check_metric_order_lp.py \
  --assert-expected \
  --out data/certificates/metric_order_lp_survivors.json
```

The checked-in artifact covers the registered sparse-order survivors from
`data/certificates/sparse_order_survivors.json`.

## Snapshot

| Pattern order | n | Status | Max margin | Distance classes | Inequalities | Triangle inequalities |
|---|---:|---|---:|---:|---:|---:|
| `C13_sidon_1_2_4_10:sample_full_filter_survivor` | 13 | `PASS_METRIC_ORDER_LP_RELAXATION` | `0.0021978` | 39 | 980 | 858 |
| `C19_skew:vertex_circle_survivor` | 19 | `PASS_METRIC_ORDER_LP_RELAXATION` | `0.00143164` | 114 | 3086 | 2907 |

Thus this combined relaxation still does not kill the two registered
non-natural sparse survivors. In particular, adding all triangle inequalities
to the Altman and vertex-circle linear constraints leaves positive-margin
solutions.

## Interpretation

This closes one tempting sparse-overlap route in its current form: the failure
of the separate Altman and vertex-circle filters is not fixed merely by adding
metric triangle inequalities over the same selected-distance classes.

A stronger exact filter must use additional Euclidean or convex-position
structure, such as Ptolemy-type constraints, oriented area relations,
circle-center compatibility, or an exact certificate extracted from a tighter
nonlinear relaxation.
