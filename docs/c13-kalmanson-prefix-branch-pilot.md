# C13 Kalmanson Prefix Branch Pilot

Status: `EXACT_CERTIFICATE_DIAGNOSTIC`.

This is a bounded prefix-branch pilot for `C13_sidon_1_2_4_10`. It is not an
all-order cyclic-order search and does not prove that the abstract C13 Sidon
pattern is impossible across all cyclic orders.

## Artifact

```text
data/certificates/c13_kalmanson_prefix_branch_pilot.json
```

Regenerate it with:

```bash
python scripts/branch_c13_kalmanson_prefix_pilot.py \
  --assert-expected \
  --out data/certificates/c13_kalmanson_prefix_branch_pilot.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

The committed artifact is a compact summary. Add `--include-certificates` to
emit the full exact certificate objects for independent inspection.

## Scope

The brancher fixes label `0` as the cyclic anchor, branches on two labels from
each side of the remaining cyclic order, and prunes reflection duplicates as
soon as a boundary prefix is lexicographically larger than its reflected
boundary prefix.

For the default two-boundary-pair run:

| Count | Value |
|---|---:|
| Raw boundary states | 11,880 |
| Canonical boundary states after reflection pruning | 5,940 |
| Reflection-pruned boundary states | 5,940 |
| Prefix extensions considered | 6,072 |
| Prefix extensions pruned before LP | 66 |
| Sampled LP/certificate calls | 12 |
| Closed sampled completions | 12 |
| Unclosed sampled completions | 0 |

Each sampled boundary state is completed deterministically by putting the
remaining labels in ascending order. All twelve sampled completions close by
exact positive-integer Kalmanson/Farkas certificates. The script checks each
generated certificate with `scripts/check_kalmanson_certificate.py`; the
committed artifact records checked summaries and branch accounting.

## Claim Boundary

The prefix pruning is search accounting only: it avoids reflection-duplicate
boundary branches before LP calls. The exact obstructions apply only to the
twelve sampled fixed cyclic orders listed in the artifact.

This does not cover the remaining canonical boundary states, does not close
all cyclic orders of `C13_sidon_1_2_4_10`, and does not prove Erdos Problem
#97.

## Next Step

The next exact extension is to replace deterministic sampled completions with
branch certificates that are valid for every completion of a partial boundary
state, or to continue the brancher with additional exact pruning before each
LP/certificate call.

That extension is started in
`docs/c13-kalmanson-partial-branch-closures.md`: prefix-forced Kalmanson
certificates close 5,108 of the 5,940 canonical two-boundary-pair states,
leaving 832 prefixes for deeper exact search.
