# Bootstrap T12 151:6 Label-4 Target-Sparse Order-Sensitivity Crosswalk

Status: `EXACT_ROUTE_PRUNING_CERTIFICATE`.

No general proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note crosswalks two exact local packets for the same three source-`151`,
row-`6`, label-`4` target-sparse endpoint quotients:

```text
[0,1,4,6]
[0,2,4,6]
[0,4,6,7]
```

## Exact Inputs

The natural-order dual-certificate packet fixes cyclic order
`[0,1,2,3,4,5,6,7,8]` and proves that the current `255`-row
Kalmanson/Altman family cannot produce either normalized screen for these
three quotients. The exact separating potentials have weight sums:

```text
250
253
243
```

The alternate-order Kalmanson packet fixes cyclic order
`[0,1,2,3,4,5,7,8,6]` and gives exact zero-sum Kalmanson certificates for the
same endpoint quotients. The certificate row counts are:

```text
10
10
9
```

## Route Decision

These two facts are compatible only if the current certificate route is
order-sensitive. The alternate order is exactly obstructed by tiny Kalmanson
zero-sum certificates, while the natural order is exactly route-pruned for the
current row family.

Therefore the current evidence should not be treated as a no-new-ingredient
all-order certificate route. A future bridge step needs at least one new
ingredient:

```text
prove useful cyclic-order structure from geometry
add a stronger strict-row family with an exact source
prove a geometric endpoint exclusion for the target-sparse lane
prove center migration for the off-center [0,4,6] rows
```

## What This Does Not Prove

This crosswalk proves only a route decision for the current certificate
machinery. It does **not** prove an all-order obstruction. It does **not** prove
assignments `0` or `11` possible or impossible. It does **not** prove support
existence, center migration, row forcing, endpoint-`8` forcing, pair `[3,5]`
impossibility, `n=9`, the bootstrap bridge, or Erdos Problem #97. It is not a
counterexample or a global status update.

## Reproduction

From the repository root:

```bash
python scripts/check_bootstrap_t12_151_6_label4_target_sparse_order_sensitivity_crosswalk.py --check --assert-expected --json
```

Expected compact summary:

```json
{
  "all_order_obstruction_proved": false,
  "alternate_order": [0, 1, 2, 3, 4, 5, 7, 8, 6],
  "alternate_order_certificate_row_count_each": [10, 10, 9],
  "current_row_family_all_order_route_ready": false,
  "natural_order_current_row_family_size_each": [255],
  "natural_order_potential_weight_sum_each": [250, 253, 243],
  "ok": true,
  "solves_erdos97": false,
  "solves_n9": false,
  "source_miss_count": 3,
  "target_row_key": "151:6"
}
```

## Files

```text
scripts/check_bootstrap_t12_151_6_label4_target_sparse_order_sensitivity_crosswalk.py
data/certificates/bootstrap_t12_151_6_label4_target_sparse_order_sensitivity_crosswalk.json
docs/bootstrap-t12-151-6-label4-target-sparse-order-sensitivity-crosswalk.md
tests/test_bootstrap_t12_151_6_label4_target_sparse_order_sensitivity_crosswalk.py
```
