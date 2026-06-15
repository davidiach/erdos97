# Bootstrap T12 151:6 Label-4 Target-Sparse Full-Cone Misses

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note follows the target-sparse support-cone packet. That packet added the
row-`5` `[4,6]` and row-`6` `[0,5]` cascade support equalities to the
target-sparse local quotients and then found bounded one- or two-row
Kalmanson/Altman cone certificates for `27` of `30` endpoint-augmented probes.
The three misses were all assignment-`0` endpoint rows:

```text
[0,1,4,6]
[0,2,4,6]
[0,4,6,7]
```

This packet asks the next finite diagnostic question:

```text
For those same three local quotients, does the full current natural-order
Kalmanson/Altman strict-row family contain any normalized nonnegative
combination that is zero-sum or nonpositive?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_target_sparse_full_cone_misses.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_target_sparse_full_cone_misses.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_target_sparse_full_cone_misses.json
```

## Input

This packet depends on:

- `data/certificates/bootstrap_t12_151_6_label4_target_sparse_support_cone.json`.

## Gate Result

The full-cone miss gate is:

```text
NOT_READY_FULL_CONE_MISSES_REMAIN_OPEN
```

Pinned summary:

| Quantity | Value |
| --- | ---: |
| source endpoint probes | `30` |
| source endpoint bounded certificates | `27` |
| source endpoint misses | `3` |
| full-cone probes | `3` |
| strict rows tested per quotient | `255` |
| zero-sum LP feasible screens | `0` |
| nonpositive LP feasible screens | `0` |
| exact infeasibility certificates stored | `0` |

The two screens are normalized by `sum(weights)=1` and require nonnegative
weights over the same fixed natural-order row family as the previous packet:
all Kalmanson rows for `n=9` plus Altman gap rows `1`, `2`, and `3`.

## Reading

The useful conclusion is:

```text
The obvious higher-row extension of the current support-cone row family does
not produce a solver witness for the three uncovered endpoint quotients.
```

This is intentionally not an exact nonexistence statement. HiGHS reports both
LP screens infeasible for all three quotients, but this packet stores no exact
dual infeasibility certificate. The result is therefore only a route-pruning
diagnostic until an exact dual, rational Farkas certificate, SMT certificate,
or formal replay is added.

The next exact task should be one of:

- certify the LP infeasibility screens exactly;
- add a stronger strict-row family and rerun the three quotients;
- prove a geometric source lemma excluding the three endpoint rows;
- add a new support-geometry condition for the target-sparse assignments.

## What This Does Not Prove

This artifact does not prove that no current-row-family certificate exists,
does not prove assignments `0` and `11` are impossible, does not prove support
existence, does not prove center migration, does not prove row forcing, does
not prove endpoint-`8` forcing, does not prove that pair `[3,5]` is impossible,
does not prove `n=9`, does not prove the bootstrap bridge, and does not prove
Erdos Problem #97.
