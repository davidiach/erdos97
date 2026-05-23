# Sparse frontier Kalmanson escape audit

Status: `SPARSE_FRONTIER_TWO_INEQUALITY_FILTER_ESCAPE_AUDIT`.

Trust label: `EXACT_FIXED_ORDER_FILTER_DIAGNOSTIC`.

This note records a narrow negative-control audit for the sparse/Sidon frontier
orders in `data/certificates/c25_c29_sparse_frontier_probe.json`.  It does not
claim a counterexample, an all-order obstruction, a geometric realization, or a
proof of Erdos Problem #97.

## What was checked

The checker

```text
python scripts/check_sparse_frontier_kalmanson_escapes.py --check --assert-expected --json
```

treats the sparse-frontier probe artifact as input data and independently
recomputes:

1. the selected-distance quotient induced by the fixed circulant selected rows;
2. both strict Kalmanson row vectors, `K1_diag_gt_sides` and
   `K2_diag_gt_other`, for every four labels in the supplied cyclic order;
3. whether any two strict Kalmanson rows are exact inverse vectors after
   selected-distance quotienting.

The replay intentionally reimplements the small DSU and Kalmanson-vector logic
instead of importing the existing Kalmanson order-search modules.  It is an
audit of the fixed orders, not a rerun of the Z3 order-search probe.

## Results

| case | selected-distance classes | full Kalmanson rows checked | inverse-pair conflicts |
|---|---:|---:|---:|
| `C25_sidon_2_5_9_14:kalmanson_z3_step7_survivor` | 225 | 25,300 | 0 |
| `C29_sidon_1_3_7_15:z3_kalmanson_survivor` | 319 | 47,502 | 0 |

Thus both stored fixed orders remain exact escapes from the direct
two-inequality Kalmanson inverse-pair filter, even when the replay checks all
`2 * binom(n, 4)` strict Kalmanson rows.

## Metadata discrepancy

The older sparse-frontier probe records smaller `rows_seen` values:

| case | stored `rows_seen` | full replay rows | match? |
|---|---:|---:|---:|
| `C25_sidon_2_5_9_14:kalmanson_z3_step7_survivor` | 25,025 | 25,300 | no |
| `C29_sidon_1_3_7_15:z3_kalmanson_survivor` | 47,259 | 47,502 | no |

The zero-conflict conclusion agrees with the stored artifact, so this does not
change the sparse-frontier status.  It should be treated as a row-counter audit
cleanup: the fixed orders are still filter escapes, but the stored `rows_seen`
metadata appears to be stale, partial, or produced by a slightly different
counter.

## Interpretation

This is a negative result for one attractive route: a direct all-order argument
using only two-inequality Kalmanson inverse pairs cannot retire the C25/C29
sparse-frontier orders, because explicit fixed orders avoid that filter.

For C29, the recorded fixed order is already killed by the stronger stored
165-inequality fixed-order Kalmanson/Farkas certificate.  The audit here only
explains why the lightweight inverse-pair template is insufficient; it does not
supply an all-order C29 obstruction.

Useful next step: search for reusable higher-support Kalmanson templates from
that 165-inequality certificate, then test whether those templates can be
encoded as finite forbidden ordered-quad families for larger order searches.
