# C13 Kalmanson Pilot

Status: `EXACT_OBSTRUCTION` for one fixed selected-witness pattern and one
fixed cyclic order only.

This note records a small Kalmanson/Farkas pilot on the registered non-natural
`C13_sidon_1_2_4_10` order that previously survived the sparse-frontier fixed
filters.

It does not prove the abstract `C13_sidon_1_2_4_10` pattern impossible across
all cyclic orders, and it does not prove Erdos Problem #97.

## Fixed Order Killed

Pattern:

```text
C13_sidon_1_2_4_10
n = 13
offsets = [1, 2, 4, 10]
cyclic order = [5,0,10,8,9,7,4,6,2,11,12,3,1]
```

Certificate:

```text
data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json
```

The certificate is a positive integer combination of strict convex-quadrilateral
Kalmanson distance inequalities. After quotienting ordinary pair-distance
variables by the selected row equalities, the total coefficient vector is
exactly zero, giving the contradiction `0 > 0`.

Checked summary:

```text
positive inequalities: 2
distance classes after selected equalities: 39
weight sum: 2
max weight: 1
```

The earlier 34-inequality certificate remains checked at
`data/certificates/c13_sidon_order_survivor_kalmanson_unsat.json` as
provenance, but the two-inequality inverse-pair certificate is the preferred
review target.

## Reproduction

Generate and check the certificate:

```bash
python scripts/find_kalmanson_two_certificate.py \
  --name C13_sidon_1_2_4_10 \
  --n 13 \
  --offsets 1,2,4,10 \
  --order 5,0,10,8,9,7,4,6,2,11,12,3,1 \
  --assert-found \
  --summary-json

python scripts/check_kalmanson_certificate.py \
  data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json \
  --summary-json
```

The compact finder does not use numerical optimization. It scans the exact
Kalmanson rows for an inverse pair and checks the resulting weight-`1,1`
certificate with `scripts/check_kalmanson_certificate.py`.

## Frontier Impact

The registered C13 order still remains useful as a benchmark: it survives the
older crossing, Altman, vertex-circle, minimum-radius, and radius-propagation
filters, but it is no longer a live fixed-order survivor once Kalmanson/Farkas
certificates are included.

The remaining C13 question is all-order: whether every cyclic order of this
fixed abstract incidence pattern has an exact obstruction, or whether some
other order can survive stronger Euclidean constraints.
