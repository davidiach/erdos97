# C25 persistent-escape certificate compression

Status: bounded exact alternative-circuit and affine-reuse diagnostic for one
fixed C25 quotient. No general proof, all-order C25 obstruction, geometric
counterexample, or official-status change is claimed.

## Target

The exact screen in
`docs/sparse-full-cone-c25-persistent-escape-screen.md` found positive
full-Kalmanson-cone circuits of widths `201` and `196` for the two original
transfer-CEGAR escapes. Both fixed orders remained outside the three
transferred and eight compressed residual seed orbits.

The predeclared next step was to compress those two wide circuits, construct
their quotient-preserving affine orbits, and measure exact reuse before
increasing the C25 cyclic-order search budget.

## Deterministic objective budgets

`scripts/exploration/compress_sparse_full_cone_c25_persistent_escapes.py`
samples 64 deterministic alternative LP objectives per source. Numerical LP
supports are only witness candidates. Every retained support is integer
exactified, replayed as a positive zero sum, checked as a positive circuit, and
expanded through all 25 valid translations.

| Source target | Source width | Seed | Trials | Best trial | Exact compressed width |
| --- | ---: | ---: | ---: | ---: | ---: |
| `transfer_cegar_probe:0` | 201 | 20260730 | 64 | 55 | 4 |
| `transfer_cegar_probe:1` | 196 | 20261730 | 64 | 3 | 5 |

Both compressed circuits are new relative to all 11 existing seed orbits. The
objective search is deterministic-budget but not exhaustive, so no optimality
claim is made for widths 4 and 5. The exact claims concern only the retained
certificates and their replayed affine images.

## Exact reuse over the current C25 packet

The checker reconstructs all 144 pairwise dihedrally distinct C25 orders in the
current provenance chain: 112 stored history orders plus the 32 latest
residual-augmentation probes.

| Target stream | Targets | Existing seeds | New compressed orbits | Combined | New marginal |
| --- | ---: | ---: | ---: | ---: | ---: |
| Prior packet | 24 | 16 | 7 | 23 | 7 |
| First fresh stream | 32 | 31 | 0 | 31 | 0 |
| Second fresh stream | 32 | 18 | 14 | 32 | 14 |
| Transfer-CEGAR probe | 16 | 14 | 2 | 16 | 2 |
| Transfer-CEGAR residual | 8 | 8 | 0 | 8 | 0 |
| Augmentation probe | 32 | 32 | 0 | 32 | 0 |
| **Total** | **144** | **119** | **23** | **142** | **23** |

The width-4 orbit covers all 23 targets marginal over the existing seeds,
including both persistent targets. The width-5 orbit covers 21 of the same 23
targets and contributes no additional marginal target. Across both stored
circuits the checker replays 50 exact affine certificate images, two direct
cross-target edges, and 42 affine cross-target edges.

The two targets still uncovered by the combined 11 old seed orbits and both
new compressed orbits are:

- `first_fresh:fresh:0`;
- `prior:seeded:0`.

This is a coverage statement about the finite 144-order packet, not all cyclic
orders.

## Exact minimum-cover decision

Exhaustive enumeration over the two new source orbits verifies that the exact
minimum cover of all 23 marginal targets has one source and total width 4:

`transfer_cegar_probe:0`

The same orbit is also the one-source, width-4 minimum cover of the two
persistent targets. Therefore the route decision is
`ADD_MINIMUM_COMPRESSED_MARGINAL_COVER_BEFORE_C25_ORDER_SEARCH`.

The next bounded experiment should block the complete 144-order history and
run C25 order CEGAR with the three transferred seed orbits plus only this new
width-4 orbit. Keep the width-5 orbit and all eight zero-marginal compressed
residual orbits inactive. This remains clause engineering for one fixed
selected-witness quotient, not evidence of an all-order obstruction.

Replay:

```bash
python scripts/exploration/compress_sparse_full_cone_c25_persistent_escapes.py \
  --check data/runs/sparse_full_cone_c25_persistent_escape_compression_2026-07-30/summary.json
```
