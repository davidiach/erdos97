# C19 Branch 269 Fifth-Pair Sub-Frontier

Status: `EXACT_CERTIFICATE_DIAGNOSTIC`.

This diagnostic classifies the fifth-pair children below the nine fourth-pair
survivors of `c19_prefix_branch_0269`, the highest-cost parent in the compact
C19 sweep currently recorded by this repository.

It does not run LPs, does not certify any branch beyond the source sweep
artifact, does not prove Erdos Problem #97, and does not produce a
counterexample.

## Artifact

```text
reports/c19_branch269_fifth_pair_subfrontier.json
```

Regenerate it with:

```bash
python scripts/analyze_c19_branch269_fifth_pair_subfrontier.py \
  --assert-expected \
  --out reports/c19_branch269_fifth_pair_subfrontier.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

## Sources

The diagnostic reads:

```text
reports/c19_fourth_pair_frontier_classifier.json
data/certificates/c19_kalmanson_prefix_window_sweep_128_287.json
```

The source sweep records that the 256-287 window has 4,950 fifth-pair children
and that all 4,950 are certified. This diagnostic reconstructs the 810
fifth-pair children below the branch-269 sub-frontier and checks that the
source window records zero unclosed fifth-pair children.

## Counts

```text
focus parent: c19_prefix_branch_0269
boundary_left = [1, 3, 11]
boundary_right_reflection_side = [2, 5, 15]
fourth-pair survivor parents = 9
fifth-pair children below them = 810
unclosed fifth-pair children in source window = 0
```

Each of the nine fourth-pair survivor parents contributes 90 fifth-pair child
labels. The fourth-pair survivor added left/right pairs are:

```text
(8, 4), (8, 7), (9, 7), (9, 13), (10, 7),
(10, 9), (10, 13), (17, 4), (17, 18)
```

## Claim Boundary

This is exact label reconstruction and source-artifact accounting, not a new
obstruction by itself. Its purpose is to make the branch-269 fifth-pair
workload concrete enough for a future exact prefilter or classifier attempt.
The full frontier classifier in `docs/c19-fifth-pair-frontier-classifier.md`
performs the same label reconstruction across all 88 recorded fourth-pair
survivors.
