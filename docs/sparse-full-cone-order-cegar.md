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

The run stopped at a certificate limit, not UNSAT, so it supplies no all-order
conclusion. The first compression follow-up is now recorded in
`docs/sparse-full-cone-certificate-compression.md`: alternative exact circuits
reduce the strong C25 clause from 205 to 100 ordered quads and the three strong
C29 clauses from 302--306 to 204--213. One compressed C29 clause covers two
source models.

That target is now completed in
`docs/sparse-full-cone-seeded-cegar.md`. Across 32 fresh counterfactual probe
orders, the exact translation orbits of the compressed seeds recorded zero
hits. The separate seeded searches learned eight new exact certificate orbits
per pattern and stopped at their configured limits. No model escaped the full
cone in this packet.

Replay:

```bash
python scripts/exploration/pilot_sparse_full_cone_order_cegar.py \
  --check data/runs/sparse_full_cone_cegar_2026-07-22/summary.json
```
