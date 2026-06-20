# Bootstrap T12 151:6 Label-4 Target-Sparse Full-Cone Dual Certificates

Status: `EXACT_ROUTE_PRUNING_CERTIFICATE`.

No general proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note records an exact follow-up for the bootstrap/T12 source-`151`,
row-`6`, label-`4` target-sparse lane. It addresses the three assignment-`0`
endpoint rows left by the existing full-cone LP screen:

```text
[0,1,4,6]
[0,2,4,6]
[0,4,6,7]
```

The existing packet reported that HiGHS found both normalized LP screens infeasible, but did not store exact dual infeasibility certificates. This overlay supplies exact integer certificates for those infeasibility claims.

## What is certified

For each of the three endpoint rows, the checker builds the same local selected-distance quotient from these centered classes:

```text
2 -> [0,3,4,8]
5 -> [4,6]
6 -> [0,5]
8 -> endpoint row
```

It then generates the current natural-order strict-row family:

```text
all Kalmanson rows for 4-subsets of [0,1,2,3,4,5,6,7,8]
plus Altman gap rows for gap orders 1, 2, 3
```

That gives `252 + 3 = 255` strict rows. In the deterministic selected-distance quotient there are `28` distance classes for each endpoint row.

For each endpoint row, the JSON artifact lists a nonnegative integer potential `c` on the 28 quotient distance classes. The exact checker verifies that every strict row vector `v_j` satisfies

```text
<c, v_j> >= 1.
```

The three potential weight sums are:

```text
endpoint [0,1,4,6]: 250
endpoint [0,2,4,6]: 253
endpoint [0,4,6,7]: 243
```

The minimum strict-row dot is `1` in all three cases.

## Exact proof of LP-screen infeasibility

Let `v_j` range over the 255 reduced strict-row coefficient vectors for one endpoint quotient, and let `c` be the stored nonnegative integer potential for that endpoint.

Assume there is a normalized zero-sum certificate: weights `lambda_j >= 0` with `sum_j lambda_j = 1` and

```text
sum_j lambda_j v_j = 0.
```

Pairing with `c` gives

```text
0 = <c, 0> = sum_j lambda_j <c, v_j> >= sum_j lambda_j = 1,
```

which is impossible.

Assume instead there is a normalized coordinatewise-nonpositive certificate: weights `lambda_j >= 0` with `sum_j lambda_j = 1` and

```text
x = sum_j lambda_j v_j <= 0
```

coordinatewise. Since every coordinate of `c` is nonnegative, `<c, x> <= 0`. But the same row-wise lower bound gives

```text
<c, x> = sum_j lambda_j <c, v_j> >= 1,
```

again impossible.

All entries of `c` and `v_j` are integers, so this is an exact arithmetic certificate rather than a solver tolerance claim.

## What this does not prove

This is route-pruning evidence. It proves that the current natural-order Kalmanson/Altman strict-row family cannot certify the three local endpoint quotients by either normalized zero-sum or coordinatewise-nonpositive cone combination.

It does **not** prove that the three local quotients are geometrically realizable. It does **not** prove assignments `0` or `11` possible or impossible. It does **not** prove support existence, center migration, row forcing, endpoint-`8` forcing, `n=9`, the bootstrap bridge, or Erdos Problem #97. It is not a counterexample.

## Reproduction

From the repository root after applying this overlay:

```bash
python scripts/check_bootstrap_t12_151_6_label4_target_sparse_full_cone_dual_certificates.py --check --json
```

Expected compact summary:

```json
{
  "distance_class_count_each": [28],
  "minimum_strict_row_dot_each": [1, 1, 1],
  "miss_count": 3,
  "ok": true,
  "potential_weight_sum_each": [250, 253, 243],
  "solves_erdos97": false,
  "solves_n9": false,
  "strict_row_count_each": [255]
}
```

## Files

```text
scripts/check_bootstrap_t12_151_6_label4_target_sparse_full_cone_dual_certificates.py
data/certificates/bootstrap_t12_151_6_label4_target_sparse_full_cone_dual_certificates.json
docs/bootstrap-t12-151-6-label4-target-sparse-full-cone-dual-certificates.md
tests/test_bootstrap_t12_151_6_label4_target_sparse_full_cone_dual_certificates.py
```
