# C13 Kalmanson Pilot

Status: superseded fixed-order pilot.

This note records a small Kalmanson/Farkas pilot on the registered non-natural
`C13_sidon_1_2_4_10` order that previously survived the sparse-frontier fixed
filters.

The fixed-order certificate below is now superseded by
`docs/kalmanson-two-order-search.md`, which checks that every cyclic order of
this fixed C13 pattern has a two-inequality Kalmanson obstruction. Neither
result proves Erdos Problem #97.

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

The registered C13 order remains useful as a benchmark: it survives the older
crossing, Altman, vertex-circle, minimum-radius, and radius-propagation
filters, but it is not a live fixed-order survivor once Kalmanson/Farkas
certificates are included.

The C13 all-order question for this fixed abstract incidence pattern is now
closed by the exact two-certificate order search. The analogous `C19_skew`
all-order question remains open.

The bounded follow-up pilot over seven explicit fixed cyclic orders remains
recorded as provenance in `docs/c13-kalmanson-order-pilot.md` and
`data/certificates/c13_kalmanson_bounded_order_pilot.json`. It closes those
seven fixed orders by exact Kalmanson/Farkas certificates, but it is not an
all-order search.

A subsequent prefix-branch pilot remains recorded in
`docs/c13-kalmanson-prefix-branch-pilot.md` and
`data/certificates/c13_kalmanson_prefix_branch_pilot.json`. It adds
reflection pruning before LP calls and closes twelve sampled fixed
completions, but it is also not an all-order search.

The first partial-branch closure pass remains recorded in
`docs/c13-kalmanson-partial-branch-closures.md` and
`data/certificates/c13_kalmanson_partial_branch_closures.json`. It uses only
Kalmanson inequalities forced by each two-sided boundary prefix and closes
5,108 of the 5,940 canonical two-boundary-pair prefixes. The remaining 832
prefixes are unresolved by this pass.

A third-pair refinement remains recorded in
`docs/c13-kalmanson-third-pair-refinement.md` and
`data/certificates/c13_kalmanson_third_pair_refinement.json`. It appends one
more forced left/right boundary pair to those 832 prefixes and closes 46,567
of 46,592 child branches by exact prefix-forced Kalmanson certificates. The
remaining 25 child branches are unresolved by that pass.
