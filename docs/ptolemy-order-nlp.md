# Ptolemy Order NLP Diagnostic

Status: numerical nonlinear diagnostic. No general proof and no counterexample
are claimed.

This diagnostic strengthens `docs/metric-order-lp.md` by adding Ptolemy's
inequality for every four vertices in the supplied cyclic order:

```text
d_ac d_bd <= d_ab d_cd + d_bc d_ad
```

for each cyclic quadrilateral `(a,b,c,d)`. The other constraints are the same
as the metric-order LP: selected distance classes, Altman adjacent diagonal
gaps, vertex-circle strict inequalities, triangle inequalities, nonnegative
ordinary distances, and `sum x = 1`.

The solve uses SLSQP and is not an exact certificate. A positive-margin pass
only means this relaxation did not find an obstruction. A failure would still
need exactification before becoming a proof-facing obstruction.

## Reproducible command

```bash
python scripts/check_ptolemy_order_nlp.py \
  --assert-expected \
  --out data/certificates/ptolemy_order_nlp_survivors.json
```

## Snapshot

| Pattern order | n | Status | Max margin | Linear inequalities | Ptolemy inequalities |
|---|---:|---|---:|---:|---:|
| `C13_sidon_1_2_4_10:sample_full_filter_survivor` | 13 | `PASS_PTOLEMY_ORDER_NLP_RELAXATION` | `0.00176461` | 980 | 715 |
| `C19_skew:vertex_circle_survivor` | 19 | `PASS_PTOLEMY_ORDER_NLP_RELAXATION` | `0.00106142` | 3086 | 3876 |

Thus Ptolemy constraints alone still do not close the registered sparse orders.
This is a miss of this nonlinear relaxation, not evidence that either abstract
order is realizable. The registered fixed orders are killed separately by
Kalmanson/Farkas certificates.

## Interpretation

The Ptolemy pass says that a proof needs still more Euclidean structure than
generic metric, cyclic-quadrilateral, Altman, and vertex-circle inequalities
over selected distance classes. Plausible next strengthenings include full
Euclidean-distance-matrix rank conditions, Cayley-Menger equalities for
quadruples in the plane, or explicit circle-center compatibility constraints.
