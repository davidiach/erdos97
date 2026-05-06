# C19 Fourth-Pair Frontier Classifier

Status: `EXACT_CERTIFICATE_DIAGNOSTIC`.

This diagnostic classifies the fourth-pair frontier recorded by the compact
C19 prefix-window sweep. It reconstructs the ordered fourth-pair child labels
below every direct prefix survivor, marks the children that required fifth-pair
subdivision in the source artifact, and reports the current high-cost parent
patterns.

It does not run LPs, does not certify any branch beyond the source artifact,
does not prove Erdos Problem #97, and does not produce a counterexample.

## Artifact

```text
reports/c19_fourth_pair_frontier_classifier.json
```

Regenerate it with:

```bash
python scripts/analyze_c19_fourth_pair_frontier.py \
  --assert-expected \
  --out reports/c19_fourth_pair_frontier_classifier.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

## Source

The diagnostic reads:

```text
data/certificates/c19_kalmanson_prefix_window_sweep_128_287.json
```

The source sweep closes deterministic C19 prefix-window branches 128 through
287 by exact prefix/fourth/fifth Kalmanson/Farkas finite subdivision. This
classifier only reorganizes the sweep's direct-survivor and fourth-survivor
records.

## Counts

| Count | Value |
|---|---:|
| Direct prefix survivor parents | 48 |
| Fourth-pair child attempts below them | 6,336 |
| Fourth-pair children closed at fourth-pair depth | 6,248 |
| Fourth-pair children requiring fifth-pair subdivision | 88 |
| Parents requiring fifth-pair subdivision | 33 |
| Parents closed by fourth-pair subdivision only | 15 |

The heaviest parent remains:

```text
c19_prefix_branch_0269
boundary_left = [1, 3, 11]
boundary_right_reflection_side = [2, 5, 15]
fourth-pair survivors = 9
fifth-pair children below those survivors = 810
```

The nine added left/right pairs that survive fourth-pair subdivision for that
parent are:

```text
(8, 4), (8, 7), (9, 7), (9, 13), (10, 7),
(10, 9), (10, 13), (17, 4), (17, 18)
```

## Claim Boundary

This is exact accounting and classification over a checked artifact, not a
mathematical obstruction by itself. It is intended to guide the next exact C19
scaling step by turning the fifth-pair cost spike into a concrete finite
frontier for prefilter or classifier design.

The follow-up sub-frontier diagnostic in
`docs/c19-branch269-fifth-pair-subfrontier.md` reconstructs the 810 fifth-pair
child labels below these nine branch-269 fourth-pair survivors.
