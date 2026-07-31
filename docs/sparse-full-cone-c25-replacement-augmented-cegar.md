# C25 width-4 replacement augmented CEGAR

Status: bounded fixed-pattern, history-blocked exact-clause diagnostic. No
general proof, all-order C25 obstruction, geometric counterexample, or
official-status change is claimed.

## Target

The compression in
`docs/sparse-full-cone-c25-selected-residual-augmented-escape-compression.md`
found that the old width-3 seed has no marginal target over the four parent
seeds. It selected a new width-4 orbit, also sourced from `residual:2`, as the
one-source minimum cover of all eight five-seed escapes.

This follow-up tests the replacement outside that source packet. It blocks the
complete current 192-order C25 history under rotation and reversal, retires the
old width-3 seed, and activates the three transferred seed orbits, persistent
width-4 orbit, and only the new replacement width-4 orbit. Twenty-four other
exact seed summaries remain inactive.

The five active certificates have widths `3, 5, 14, 4, 4` and produce 125
exact quotient-preserving affine images.

## Deterministic bounded protocol

`scripts/exploration/run_sparse_full_cone_c25_replacement_augmented_cegar.py`
uses random seed `20260802`, conflict cap `1024`, and two limits:

1. collect 16 history-disjoint inverse-pair-escape orders within at most 12,000
   Z3 iterations and compare exact seed coverage;
2. activate all five seed orbits and learn at most eight new exact full-cone
   certificate orbits within at most 12,000 iterations.

The numerical LP is only a certificate finder. Every stored certificate is
exactified and replayed with integer arithmetic. The checker also replays all
history identities, active and inactive seed certificates, affine images,
clause matches, and learned-clause exclusions.

## Fresh 16-order transfer result

The fresh probe reaches its 16-order limit after 421 iterations and 13,708
inverse-pair clauses. All 16 orders survive the stored vertex-circle and both
Altman lightweight filters.

| Seed packet | Covered probe orders | New over parent four |
| --- | ---: | ---: |
| Four parent seed orbits | 16/16 | -- |
| Replacement width-4 orbit only | 16/16 | 0 |
| Parent plus replacement | 16/16 | 0 |

The replacement orbit covers every probe order, but the four parent seeds
already cover the same 16 orders. Its one-source minimum-cover role in the
eight-order source packet therefore has zero marginal coverage on this fresh
bounded probe.

## Five-seed CEGAR result

With all five active seed orbits, bounded CEGAR finds eight further
history-disjoint orders. Every order is a strong lightweight survivor, escapes
all active and previously learned affine clauses at discovery, and has an
exact positive full-Kalmanson-cone certificate.

| Learned model | Z3 iteration | Exact certificate width |
| ---: | ---: | ---: |
| 0 | 46 | 198 |
| 1 | 47 | 193 |
| 2 | 48 | 195 |
| 3 | 49 | 195 |
| 4 | 50 | 196 |
| 5 | 51 | 200 |
| 6 | 52 | 199 |
| 7 | 53 | 201 |

The run stops at the configured eight-certificate limit with no unresolved
model. The learned orbits add 200 unique affine clauses. Together with 125
active seed images, the checker replays 325 exact affine certificate images.

## Decision and next target

The route decision is
`COMPRESS_NEW_C25_REPLACEMENT_AUGMENTED_ESCAPES`.

The next target is to compress these eight exact escapes and reassess marginal
affine coverage before any further order search. This remains a finite
fixed-pattern research packet, not evidence of an all-order obstruction.

Replay:

```bash
python scripts/exploration/run_sparse_full_cone_c25_replacement_augmented_cegar.py \
  --check data/runs/sparse_full_cone_c25_replacement_augmented_cegar_2026-07-31/summary.json
```
