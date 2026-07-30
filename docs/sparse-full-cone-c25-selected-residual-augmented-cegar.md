# C25 selected-residual width-3 augmented CEGAR

Status: bounded fixed-pattern, history-blocked exact-clause diagnostic. No
general proof, all-order C25 obstruction, geometric counterexample, or
official-status change is claimed.

## Target

The compression in
`docs/sparse-full-cone-c25-persistent-augmented-residual-compression.md`
selected the affine orbit of `residual:2`, an exact width-3 positive circuit,
as the one-source minimum cover of all eight active-seed escapes in its
24-order source packet.

This follow-up tests that selection outside the source packet. It blocks the
complete current 168-order C25 history under rotation and reversal, activates
the three transferred seed orbits, persistent width-4 orbit, and only the
selected residual width-3 orbit, and leaves sixteen other exact seed summaries
inactive.

The five active certificates have widths `3, 5, 14, 4, 3` and produce 125
exact quotient-preserving affine images.

## Deterministic bounded protocol

`scripts/exploration/run_sparse_full_cone_c25_selected_residual_augmented_cegar.py`
uses random seed `20260731`, conflict cap `1024`, and two limits:

1. collect 16 history-disjoint inverse-pair-escape orders within at most 12,000
   Z3 iterations and compare exact seed coverage;
2. activate all five seed orbits and learn at most eight new exact full-cone
   certificate orbits within at most 12,000 iterations.

The numerical LP is only a certificate finder. Every stored certificate is
exactified and replayed with integer arithmetic. The checker also replays all
history identities, seed certificates, affine images, clause matches, and
learned-clause exclusions.

## Fresh 16-order transfer result

The fresh probe reaches its 16-order limit after 497 iterations and 14,485
inverse-pair clauses. All 16 orders survive the stored vertex-circle and both
Altman lightweight filters.

| Seed packet | Covered probe orders | New over parent four |
| --- | ---: | ---: |
| Four parent seed orbits | 16/16 | -- |
| Selected width-3 orbit only | 4/16 | 0 |
| Parent plus selected width 3 | 16/16 | 0 |

The selected width-3 orbit covers probe indices `0, 1, 2, 3`, but all four are
already covered by the parent seeds. Its one-source minimum-cover role in the
24-order source packet therefore does not transfer as marginal coverage to
this fresh bounded probe.

## Five-seed CEGAR result

With all five active seed orbits, bounded CEGAR finds eight further
history-disjoint orders. Every order is a strong lightweight survivor, escapes
all active and previously learned affine clauses at discovery, and has an
exact positive full-Kalmanson-cone certificate.

| Learned model | Z3 iteration | Exact certificate width |
| ---: | ---: | ---: |
| 0 | 74 | 219 |
| 1 | 75 | 220 |
| 2 | 76 | 214 |
| 3 | 77 | 216 |
| 4 | 78 | 211 |
| 5 | 79 | 217 |
| 6 | 80 | 219 |
| 7 | 81 | 210 |

The run stops at the configured eight-certificate limit with no unresolved
model. The learned orbits add 200 unique affine clauses. Together with 125
active seed images, the checker replays 325 exact affine certificate images.

## Decision and next target

The route decision is
`COMPRESS_NEW_C25_SELECTED_RESIDUAL_AUGMENTED_ESCAPES`.

Compress the eight new width-210--220 certificates, construct their exact
quotient-preserving affine orbits, and compare marginal coverage against both
the four parent seeds and the selected width-3 seed before choosing the seed
packet for a possible 192-history C25 CEGAR.

Replay:

```bash
python scripts/exploration/run_sparse_full_cone_c25_selected_residual_augmented_cegar.py \
  --check data/runs/sparse_full_cone_c25_selected_residual_augmented_cegar_2026-07-30/summary.json
```
