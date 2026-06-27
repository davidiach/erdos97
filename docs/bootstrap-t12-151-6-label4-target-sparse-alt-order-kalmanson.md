# Bootstrap T12 151:6 Label-4 Target-Sparse Alternate-Order Kalmanson

Status: `EXACT_ROUTE_PRUNING_CERTIFICATE`.

No general proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note records an order-sensitivity follow-up for the bootstrap/T12
source-`151`, row-`6`, label-`4` target-sparse lane. It uses the same three
assignment-`0` endpoint rows left by the full-cone miss packet:

```text
[0,1,4,6]
[0,2,4,6]
[0,4,6,7]
```

The natural-order full-cone follow-up stores exact dual certificates proving
that the current natural-order `255`-row Kalmanson/Altman family cannot produce
either normalized LP screen for these three quotients. This packet goes in the
other direction for one fixed alternate cyclic order:

```text
[0,1,2,3,4,5,7,8,6]
```

## What Is Certified

For each endpoint row, the checker builds the same selected-distance quotient
from centered classes:

```text
2 -> [0,3,4,8]
5 -> [4,6]
6 -> [0,5]
8 -> endpoint row
```

It then verifies a positive integer combination of Kalmanson strict rows whose
reduced quotient vector is exactly zero. The three certificates use only rows
whose quads are subsequences of the fixed alternate order.

The certificate sizes are:

```text
endpoint [0,1,4,6]: 10 Kalmanson rows, weight sum 10
endpoint [0,2,4,6]: 10 Kalmanson rows, weight sum 11
endpoint [0,4,6,7]:  9 Kalmanson rows, weight sum 10
```

Each quotient has `28` selected-distance classes. The fixed-order strict-row
family available for comparison has `252` Kalmanson rows plus `3` Altman gap
rows, but the stored certificates need only Kalmanson rows.

## Exact Proof Shape

For one fixed cyclic order, each listed Kalmanson row is a strict necessary
inequality. If positive integer weights combine their reduced selected-distance
vectors to the zero vector, then the weighted sum is the identically zero
distance expression on the quotient. But the same weighted sum must be strictly
positive in any configuration realizing all those fixed-order strict
inequalities. This is impossible.

The checker verifies every reduced vector and the final zero sum by exact
integer arithmetic.

## What This Does Not Prove

This is a fixed-order local obstruction only. It does **not** prove an all-order
obstruction for the three quotients. It does **not** prove assignments `0` or
`11` possible or impossible. It does **not** prove support existence, center
migration, row forcing, endpoint-`8` forcing, pair `[3,5]` impossibility,
`n=9`, the bootstrap bridge, or Erdos Problem #97. It is not a counterexample
or a global status update.

The useful bridge signal is that these misses are order-sensitive: the natural
order is route-pruned by dual infeasibility certificates, while one nearby
alternate order is killed by tiny exact Kalmanson zero-sum certificates. A
future bridge step must either force useful cyclic-order structure or replace
this fixed-order certificate with an all-order exact certificate.

## Reproduction

From the repository root:

```bash
python scripts/check_bootstrap_t12_151_6_label4_target_sparse_alt_order_kalmanson.py --check --assert-expected --json
```

Expected compact summary:

```json
{
  "all_exact_zero_sum_verified": true,
  "all_order_obstruction_proved": false,
  "available_fixed_order_strict_row_count_each": [255],
  "certificate_count": 3,
  "certificate_row_count_each": [10, 10, 9],
  "certificate_weight_sum_each": [10, 11, 10],
  "fixed_cyclic_order": [0, 1, 2, 3, 4, 5, 7, 8, 6],
  "ok": true,
  "solves_erdos97": false,
  "solves_n9": false,
  "source_miss_count": 3
}
```

## Files

```text
scripts/check_bootstrap_t12_151_6_label4_target_sparse_alt_order_kalmanson.py
data/certificates/bootstrap_t12_151_6_label4_target_sparse_alt_order_kalmanson.json
docs/bootstrap-t12-151-6-label4-target-sparse-alt-order-kalmanson.md
tests/test_bootstrap_t12_151_6_label4_target_sparse_alt_order_kalmanson.py
```
