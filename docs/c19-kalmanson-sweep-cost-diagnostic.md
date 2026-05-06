# C19 Kalmanson Sweep Cost Diagnostic

Status: `EXACT_CERTIFICATE_DIAGNOSTIC`.

This diagnostic summarizes exact branch-attempt accounting from the compact
C19 prefix-window sweep. It does not run LPs, does not certify any branch beyond
the source sweep artifact, does not prove Erdos Problem #97, and does not
produce a counterexample.

## Artifact

```text
reports/c19_kalmanson_sweep_cost_diagnostic.json
```

Regenerate it with:

```bash
python scripts/analyze_c19_kalmanson_sweep_costs.py \
  --assert-expected \
  --out reports/c19_kalmanson_sweep_cost_diagnostic.json
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
diagnostic only reorganizes the sweep's recorded branch counts and survivor
lists.

## Counts

| Count | Value |
|---|---:|
| Sweep windows | 5 |
| Prefix branches in source sweep | 160 |
| Direct prefix attempts | 160 |
| Direct prefix survivors | 48 |
| Fourth-pair child attempts | 6,336 |
| Fourth-pair child survivors | 88 |
| Fifth-pair child attempts | 7,920 |
| Fifth-pair child survivors | 0 |
| Total recorded branch attempts | 14,416 |
| Direct survivors requiring fifth-pair subdivision | 33 |
| Direct survivors closed after fourth-pair subdivision only | 15 |

The heaviest window is branch range 256-287:

```text
direct prefix attempts:       32
fourth-pair child attempts:   2,244
fifth-pair child attempts:    4,950
total branch attempts:        7,226
```

The heaviest recorded prefix parent is:

```text
c19_prefix_branch_0269
fourth-pair survivors: 9
fifth-pair child attempts: 810
```

The follow-up classifier in `docs/c19-fourth-pair-frontier-classifier.md`
reconstructs the exact fourth-pair frontier below all direct prefix survivors
and records the nine added left/right pairs that survive below branch 269.

## Claim Boundary

This is exact accounting over a checked artifact, not a mathematical
obstruction by itself. Its purpose is to identify where the current C19 sweep
pays subdivision cost. The large 256-287 fifth-pair frontier suggests that the
next C19 scaling step should add an exact prefilter or a finer subdivision-cost
classifier before extending many more windows.
