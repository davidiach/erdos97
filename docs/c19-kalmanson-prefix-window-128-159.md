# C19 Kalmanson Prefix Window 128-159

Status: `EXACT_OBSTRUCTION` for the deterministic C19 three-boundary-prefix
window with canonical branch indices 128 through 159.

This is a bounded sampled-window artifact, not an all-order C19 search. It
does not prove Erdos Problem #97, does not kill abstract `C19_skew`, and does
not produce a counterexample.

## Artifact

```text
data/certificates/c19_kalmanson_prefix_window_128_159.json
```

Regenerate it with:

```bash
python scripts/certify_c19_kalmanson_prefix_window.py \
  --assert-expected \
  --out data/certificates/c19_kalmanson_prefix_window_128_159.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

## Method

The script scans the next deterministic reflection-pruned three-boundary-prefix
window after the first 128 sampled prefixes. The window contains canonical
branch indices 128 through 159.

For each prefix, it first uses only Kalmanson inequalities whose cyclic order
is forced by the three-boundary prefix. If a direct certificate is not found,
the script appends one ordered left/right boundary pair and checks the
fourth-pair children. If a fourth-pair child remains unclosed, the script
appends one more ordered left/right boundary pair and checks fifth-pair
children.

## Counts

| Count | Value |
|---|---:|
| Three-boundary-prefix branches scanned | 32 |
| Direct prefix certificates | 31 |
| Direct prefix survivors | 1 |
| Fourth-pair children below direct survivor | 132 |
| Fourth-pair child certificates | 130 |
| Fourth-pair child survivors | 2 |
| Fifth-pair children below fourth-pair survivors | 180 |
| Fifth-pair child certificates | 180 |
| Fifth-pair child survivors | 0 |
| Prefix branches closed by the recorded chain | 32 |

The one direct survivor is `c19_prefix_branch_0156`, with boundary prefix:

```text
left = [1, 3, 17]
right_reflection_side = [2, 4, 5]
```

Its two fourth-pair survivors are:

```text
c19_window_fourth_child_0156_0063
c19_window_fourth_child_0156_0065
```

Both fourth-pair survivors close after fifth-pair subdivision.

## Claim Boundary

Each listed certificate is an exact obstruction for every completion of the
recorded boundary prefix at that branch depth. The window conclusion is only a
finite-subdivision conclusion for branch indices 128 through 159.

Together with the first sampled-prefix chain, the currently recorded C19
sampled-prefix coverage is:

```text
128 initial sampled prefixes closed by the prefix/fourth/fifth chain
+ 32 next-window prefixes closed by this chain
= 160 deterministic sampled three-boundary-prefix branches closed
```

This remains a tiny sampled slice of 6,683,040 canonical three-boundary-prefix
states. It does not affect the global status of Erdos Problem #97.

## Next Step

The next exact C19 move should add a reusable window driver or increase the
window size while keeping artifacts compact. The following window is recorded
in `docs/c19-kalmanson-prefix-window-160-191.md`; the direct pass remains
cheap, but scaling the fifth-pair fallback across many windows may require
cheaper pre-pruning or shared branch utilities.
