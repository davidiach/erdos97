# C19 Kalmanson Prefix Window 160-191

Status: `EXACT_OBSTRUCTION` for the deterministic C19 three-boundary-prefix
window with canonical branch indices 160 through 191.

This is a bounded sampled-window artifact, not an all-order C19 search. It
does not prove Erdos Problem #97, does not kill abstract `C19_skew`, and does
not produce a counterexample.

## Artifact

```text
data/certificates/c19_kalmanson_prefix_window_160_191.json
```

Regenerate it with:

```bash
python scripts/certify_c19_kalmanson_prefix_window.py \
  --start-index 160 \
  --window-size 32 \
  --out data/certificates/c19_kalmanson_prefix_window_160_191.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed. The regression test replays this window
and compares the full JSON artifact.

## Method

The script scans the next deterministic reflection-pruned three-boundary-prefix
window after branch 159. It first tries direct three-boundary-prefix
Kalmanson/Farkas certificates. Direct survivors are subdivided by one ordered
left/right boundary pair. Fourth-pair survivors are subdivided by one more
ordered left/right boundary pair.

## Counts

| Count | Value |
|---|---:|
| Three-boundary-prefix branches scanned | 32 |
| Direct prefix certificates | 23 |
| Direct prefix survivors | 9 |
| Fourth-pair children below direct survivors | 1,188 |
| Fourth-pair child certificates | 1,181 |
| Fourth-pair child survivors | 7 |
| Fifth-pair children below fourth-pair survivors | 630 |
| Fifth-pair child certificates | 630 |
| Fifth-pair child survivors | 0 |
| Prefix branches closed by the recorded chain | 32 |

The direct survivors are:

```text
c19_prefix_branch_0161
c19_prefix_branch_0162
c19_prefix_branch_0164
c19_prefix_branch_0166
c19_prefix_branch_0167
c19_prefix_branch_0168
c19_prefix_branch_0182
c19_prefix_branch_0186
c19_prefix_branch_0187
```

The seven fourth-pair survivors all close after fifth-pair subdivision.

## Claim Boundary

Each listed certificate is an exact obstruction for every completion of the
recorded boundary prefix at that branch depth. The window conclusion is only a
finite-subdivision conclusion for branch indices 160 through 191.

Together with the previous sampled-prefix chains, the currently recorded C19
sampled-prefix coverage is:

```text
128 initial sampled prefixes closed by the prefix/fourth/fifth chain
+ 32 prefixes in window 128-159
+ 32 prefixes in window 160-191
= 192 deterministic sampled three-boundary-prefix branches closed
```

This remains a tiny sampled slice of 6,683,040 canonical three-boundary-prefix
states. It does not affect the global status of Erdos Problem #97.

## Next Step

The compact sweep artifact is recorded in
`docs/c19-kalmanson-prefix-window-sweep.md`. It covers windows 128 through 287,
including this one, with compact per-window accounting and survivor lists.
