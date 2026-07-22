# Sparse full-Kalmanson-cone cyclic-order CEGAR

Status: bounded fixed-pattern exact-clause diagnostic. No general proof,
all-order C25/C29 obstruction, geometric counterexample, or official-status
change is claimed.

## Stronger order clauses

The earlier two-inequality order search learns a clause whenever two strict
Kalmanson rows are exact inverse vectors after quotienting by the selected
distance equalities. C25 and C29 both have explicit cyclic orders that escape
that lightweight mechanism.

The new pilot in
`scripts/exploration/pilot_sparse_full_cone_order_cegar.py` adds a second
counterexample-guided layer. For an inverse-pair escape order:

1. solve the full fixed-order Kalmanson/Farkas LP and exactify its positive
   rational dependency;
2. independently verify that the weighted quotient-vector sum is zero;
3. collect the distinct ordered quadrilaterals supporting the certificate;
4. add one Z3 disjunction saying at least one of those quadrilaterals must fail
   to occur in that orientation.

The clause is exact: any cyclic order containing the entire ordered-quad
support inherits the same fixed-pattern certificate. It can exclude many
orders at once. The clause is nevertheless certificate-specific and currently
large.

## Bounded result

The July 22 run learned three full-cone clauses for each pattern:

| Pattern | Iterations | Two-row clauses | Full-cone clauses | Full-clause widths | Strong prefilter survivors |
|---|---:|---:|---:|---|---:|
| `C25_sidon_2_5_9_14` | 530 | 14,921 | 3 | 196, 188, 205 | 1/3 |
| `C29_sidon_1_3_7_15` | 432 | 20,568 | 3 | 304, 302, 306 | 3/3 |

Here “strong prefilter survivor” means the order also escapes vertex-circle,
Altman signature, and exact Altman-linear checks. All six orders escape the
direct two-inequality Kalmanson filter exactly. All six are then killed by
their stored exact full-cone certificates.

This is the first checked C25 packet in this route containing an order that
simultaneously survives the inverse-pair, vertex-circle, and Altman filters but
is killed by a larger exact Kalmanson dependency. The C29 packet supplies three
such models.

## What remains

The run stopped at a certificate limit, not UNSAT. It therefore supplies no
all-order conclusion. The next useful target is clause compression: minimize
the ordered-quad supports while preserving an exact positive zero dependency,
then measure how many subsequent inverse-pair-escape models each compressed
clause blocks. If compression produces reusable small supports, those clauses
can be fed back into a longer exact CEGAR run. If a model has no exact
full-cone certificate, it becomes the first legitimate input to the guarded
free-Cartesian solver.

Replay:

```bash
python scripts/exploration/pilot_sparse_full_cone_order_cegar.py \
  --check data/runs/sparse_full_cone_cegar_2026-07-22/summary.json
```
