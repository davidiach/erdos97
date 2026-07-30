# C25 persistent-augmented residual compression

Status: bounded exact alternative-circuit and cross-coverage diagnostic for
one fixed C25 selected-witness quotient. No general proof, all-order C25
obstruction, geometric counterexample, or official-status change is claimed.

## Target

The history-blocked search in
`docs/sparse-full-cone-c25-persistent-augmented-cegar.md` activates the three
transferred seed orbits and the selected persistent width-4 orbit. It covers
all 16 fresh probe orders but learns eight further active-seed-escaping exact
positive Kalmanson circuits of widths `191`--`200`.

This follow-up searches for smaller exact circuits for precisely those eight
fixed residual orders. It then expands each retained circuit through all 25
quotient-preserving translations and measures exact coverage over the source
packet's 16 probe and eight residual orders.

## Deterministic objective budgets

The objective seeds are `20260731 + 1000 * model_index`. Each budget is the
first pretested deterministic packet selected for the source; the search is
not exhaustive and does not establish width optimality.

| Residual | Source width | Trials | Best trial | Compressed width |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 197 | 32 | 20 | 6 |
| 1 | 197 | 32 | 14 | 6 |
| 2 | 193 | 32 | 3 | 3 |
| 3 | 194 | 64 | 56 | 8 |
| 4 | 192 | 32 | 11 | 4 |
| 5 | 200 | 32 | 20 | 7 |
| 6 | 191 | 32 | 4 | 3 |
| 7 | 195 | 112 | 104 | 4 |

All eight retained supports replay as exact positive circuits. Their canonical
affine-orbit hashes are new relative to the four active seeds. The checker
replays 200 exact affine certificate images.

## Exact 24-order coverage

The active seeds cover all 16 probe targets and none of the eight residual
targets. The compressed residual circuits cover all eight residual targets
and no probe target, so their roles are complementary inside this finite
packet:

| Seed packet | Probe covered | Residual covered | Total covered |
| --- | ---: | ---: | ---: |
| Four active seed orbits | 16/16 | 0/8 | 16/24 |
| Eight compressed residual orbits | 0/16 | 8/8 | 8/24 |
| Combined | 16/16 | 8/8 | 24/24 |

Across the eight sources, exact replay finds 22 direct and 54 affine
cross-source coverage edges. Exhaustive source-subset enumeration verifies
that the affine orbit from `residual:2` alone covers all eight residual
targets. It is an exact one-source minimum cover of total width 3; no other
compressed source is selected for the next search.

The compressed certificates contain 40 distinct quotient-vector hashes. One
hash is shared by `residual:4` and `residual:7`; all other cross-source vector
overlaps are zero.

## Decision and next target

The predeclared stopping rule returns
`ADD_MINIMUM_COMPRESSED_RESIDUAL_COVER_BEFORE_NEXT_C25_ORDER_SEARCH`.
The completed follow-up in
`docs/sparse-full-cone-c25-selected-residual-augmented-cegar.md` blocks 168
history classes and activates the three transferred orbits, persistent
width-4 orbit, and only this selected width-3 orbit. The four parent seeds
cover all 16 fresh probe orders; width 3 covers four of those same orders and
therefore adds zero marginal coverage outside its source packet.

Five-seed CEGAR nevertheless learns eight new exact full-cone certificates of
widths `210`--`220` before its configured limit. Compress those eight and
reassess marginal coverage before choosing a possible 192-history seed packet.

This is finite clause engineering for one fixed quotient, not evidence of an
all-order C25 obstruction.

Replay without rerunning the numerical objective search:

```bash
python scripts/exploration/compress_sparse_full_cone_c25_persistent_augmented_residuals.py \
  --check data/runs/sparse_full_cone_c25_persistent_augmented_residual_compression_2026-07-30/summary.json
```
