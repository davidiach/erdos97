# C25 selected-residual augmented escape compression

Status: bounded exact alternative-circuit and seed-replacement diagnostic for
one fixed C25 selected-witness quotient. No general proof, all-order C25
obstruction, geometric counterexample, or official-status change is claimed.

## Target

The 168-history search in
`docs/sparse-full-cone-c25-selected-residual-augmented-cegar.md` found that the
selected old width-3 orbit adds zero marginal coverage over the four parent
seeds on 16 fresh probe orders, while five-seed CEGAR learns eight new exact
positive Kalmanson circuits of widths `210`--`220`.

This follow-up compresses precisely those eight fixed residual orders, expands
each retained circuit through all 25 quotient-preserving translations, and
measures whether a new exact residual cover can replace the nonmarginal old
width-3 seed.

## Deterministic objective budgets

The objective seeds are `20260801 + 1000 * model_index`. Each budget is the
first fixed pretested packet selected for its source:

| Residual | Source width | Trials | Best trial | Compressed width |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 219 | 64 | 50 | 7 |
| 1 | 220 | 64 | 47 | 6 |
| 2 | 214 | 112 | 77 | 4 |
| 3 | 216 | 112 | 65 | 4 |
| 4 | 211 | 112 | 67 | 9 |
| 5 | 217 | 32 | 5 | 6 |
| 6 | 219 | 32 | 24 | 4 |
| 7 | 210 | 64 | 37 | 3 |

All eight retained supports replay as exact positive circuits. Their canonical
affine-orbit hashes are new relative to all five active source seeds. The
objective search is not exhaustive and does not establish width optimality.

## Exact 24-order seed comparison

The source packet contains 16 probe targets and eight five-seed-escaping
residual targets:

| Seed packet | Covered targets |
| --- | ---: |
| Four parent seed orbits | 16/24 |
| Old selected width-3 orbit only | 4/24 |
| All five old active seeds | 16/24 |
| Eight new compressed affine orbits | 20/24 |
| Four parent seeds plus new compressed orbits | 24/24 |

The old selected width-3 seed's four targets are all already covered by the
four parent seeds, so its marginal target set is empty.

Exact replay finds 31 direct and 129 affine cross-source coverage edges among
the new compressed certificates. Exhaustive source-subset enumeration verifies
that the new width-4 orbit from `residual:2` alone covers all eight residual
targets. It is the exact one-source minimum residual cover with total width 4.
The smaller width-3 orbit from `residual:7` does not cover the full residual
packet.

The eight compressed certificates contain 43 distinct quotient-vector hashes
with no cross-certificate hash reuse.

## Decision and next target

The route decision is
`REPLACE_NONMARGINAL_WIDTH3_WITH_MINIMUM_COMPRESSED_ESCAPE_COVER`.

The completed 192-history follow-up in
`docs/sparse-full-cone-c25-replacement-augmented-cegar.md` activates the four
parent seed orbits and only the new width-4 `residual:2` replacement selected
here. The prior width-3 seed is retired.

On 16 fresh probe orders, both the four parent seeds and the replacement alone
cover 16/16, so the replacement adds zero marginal fresh-probe coverage.
Bounded five-seed CEGAR nevertheless learns eight new exact certificates of
widths `193`--`201` before its configured limit. The next target is to compress
those eight replacement-seed escapes and reassess exact marginal affine
coverage.

Replay without rerunning the numerical objective search:

```bash
python scripts/exploration/compress_sparse_full_cone_c25_selected_residual_augmented_escapes.py \
  --check data/runs/sparse_full_cone_c25_selected_residual_augmented_escape_compression_2026-07-30/summary.json
```
