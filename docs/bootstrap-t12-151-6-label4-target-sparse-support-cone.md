# Bootstrap T12 151:6 Label-4 Target-Sparse Support Cone

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines the target-sparse residual assignments `0` and `11` left by
the center-`8` residual target-row packet. The previous target-sparse packets
show that one-row, one-completion plus one-repair, and one-completion plus
two-repair selected-row repairs all fail basic filters. This packet asks a
different local exact-certificate question:

```text
If the row-5 [4,6] and row-6 [0,5] cascade support equalities are added to a
target-sparse local row, does a bounded one- or two-row Kalmanson/Altman cone
certificate appear?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_target_sparse_support_cone.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_target_sparse_support_cone.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_target_sparse_support_cone.json
```

## Inputs

This packet joins:

- `data/certificates/bootstrap_t12_151_6_label4_center8_residual_target_rows.json`;
- `data/certificates/bootstrap_t12_151_6_label4_center8_target_sparse_completions.json`;
- `data/certificates/bootstrap_t12_151_6_label4_support_hypothesis_ledger.json`.

## Gate Result

The support-cone gate is:

```text
NOT_READY_SUPPORT_CONE_PARTIAL_ENDPOINT_COVERAGE
```

Pinned summary:

| Quantity | Value |
| --- | ---: |
| target-sparse assignments | `[0,11]` |
| cascade support equalities | center `5` with `[4,6]`; center `6` with `[0,5]` |
| strict rows tested per quotient | `255` |
| target-pair probes | `6` |
| target-pair bounded certificates | `0` |
| completion probes | `12` |
| completion bounded certificates | `0` |
| endpoint-augmented probes | `30` |
| endpoint-augmented bounded certificates | `27` |
| endpoint-augmented misses | `3` |

The bounded search uses all fixed natural-order Kalmanson rows for `n=9`
plus Altman gap rows `1`, `2`, and `3`. It checks exact one-row and unordered
unit-weight two-row cone sums after quotienting by the local centered
equalities.

## Reading

The useful conclusion is:

```text
Cascade support equalities alone do not give the current bounded cone checker
a target-sparse local obstruction.
```

Adding a center-`8` exact target row containing `[0,4,6]` gives a sharply
partial result. Every assignment-`11` endpoint augmentation has a bounded
certificate. Assignment `0` still has three endpoint rows uncovered:

```text
[0,1,4,6]
[0,2,4,6]
[0,4,6,7]
```

The immediate higher-row follow-up is now recorded in
`docs/bootstrap-t12-151-6-label4-target-sparse-full-cone-misses.md`. It probes
those three quotients with arbitrary nonnegative weights over the same current
Kalmanson/Altman row family and finds no solver witness, while storing no exact
dual infeasibility certificate. So the next exact task is now to certify that
LP infeasibility, add a stronger row family, prove that genuine geometry cannot
supply those endpoint rows, or add a different support condition that reaches
assignment `0`.

## What This Does Not Prove

This artifact does not prove assignments `0` and `11` are impossible, does not
prove support existence, does not prove center migration, does not prove row
forcing, does not prove endpoint-`8` forcing, does not prove that pair `[3,5]`
is impossible, does not prove `n=9`, does not prove the bootstrap bridge, and
does not prove Erdos Problem #97.
