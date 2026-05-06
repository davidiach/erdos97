# C19 Fifth-Pair Frontier Classifier

Status: `EXACT_CERTIFICATE_DIAGNOSTIC`.

This diagnostic classifies the full fifth-pair frontier recorded by the compact
C19 prefix-window sweep. It reconstructs fifth-pair child labels below every
recorded fourth-pair survivor, compares per-window label digests with the
source sweep artifact, and records the top prefix parents by fifth-pair
workload.

It does not run LPs, does not certify any branch beyond the source sweep
artifact, does not prove Erdos Problem #97, and does not produce a
counterexample.

## Artifact

```text
reports/c19_fifth_pair_frontier_classifier.json
```

Regenerate it with:

```bash
python scripts/analyze_c19_fifth_pair_frontier.py \
  --assert-expected \
  --out reports/c19_fifth_pair_frontier_classifier.json
```

Use `.venv/bin/python` in this checkout if the system `python` does not have
the repository dependencies installed.

## Sources

The diagnostic reads:

```text
reports/c19_fourth_pair_frontier_classifier.json
data/certificates/c19_kalmanson_prefix_window_sweep_128_287.json
```

## Counts

| Count | Value |
|---|---:|
| Fourth-pair survivor parents | 88 |
| Fifth-pair child labels reconstructed | 7,920 |
| Source fifth-pair child count | 7,920 |
| Source unclosed fifth-pair children | 0 |
| Prefix parents requiring fifth-pair subdivision | 33 |

Per-window fifth-pair child counts:

| Window | Fifth-pair children |
|---|---:|
| 128-159 | 180 |
| 160-191 | 630 |
| 192-223 | 1,350 |
| 224-255 | 810 |
| 256-287 | 4,950 |

Top prefix parents by fifth-pair workload:

```text
c19_prefix_branch_0269: 810
c19_prefix_branch_0278: 630
c19_prefix_branch_0260: 450
c19_prefix_branch_0261: 450
c19_prefix_branch_0265: 450
c19_prefix_branch_0273: 450
```

## Claim Boundary

This is exact label reconstruction and source-artifact accounting, not a new
obstruction by itself. Its purpose is to give a complete compact map of the
current fifth-pair frontier so future exact prefilters can be tested against a
known finite workload.

The first such prefilter checkpoint is
[`c19-fifth-pair-two-row-prefilter.md`](c19-fifth-pair-two-row-prefilter.md):
it closes 7,917 of these 7,920 recorded children by exact two-row Kalmanson
cancellations and uses ordinary exact Farkas fallback for the remaining three.
