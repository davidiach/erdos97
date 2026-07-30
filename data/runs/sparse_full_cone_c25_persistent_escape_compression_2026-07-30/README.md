# C25 persistent-escape certificate compression

This packet deterministically samples 64 alternative LP objectives for each of
the two exact positive circuits from the C25 persistent-escape screen.
Numerical supports are retained only after exact integer zero-sum replay and a
positive-circuit audit.

| Source target | Source width | Best trial | Exact compressed width |
| --- | ---: | ---: | ---: |
| `transfer_cegar_probe:0` | 201 | 55 | 4 |
| `transfer_cegar_probe:1` | 196 | 3 | 5 |

Both circuits are new relative to the three transferred and eight compressed
residual seed orbits. Their 50 exact quotient-preserving affine images cover 23
of the 25 orders left uncovered by the old seeds across the complete current
144-order C25 packet. The width-4 orbit alone covers all 23 marginal targets;
the width-5 orbit adds no marginal target.

The 11 old seed orbits plus the width-4 orbit cover 142/144 stored orders. The
two remaining finite-packet misses are `first_fresh:fresh:0` and
`prior:seeded:0`.

The exact minimum marginal-cover decision is
`ADD_MINIMUM_COMPRESSED_MARGINAL_COVER_BEFORE_C25_ORDER_SEARCH`. The next
bounded target is a 144-history-blocked C25 CEGAR run with the three
transferred seeds plus only the new width-4 orbit.

The objective search is deterministic-budget but non-exhaustive. This packet
does not claim an all-order C25 obstruction, geometric realizability result,
proof of Erdos Problem #97, counterexample, or official/global status update.

Replay:

```bash
python scripts/exploration/compress_sparse_full_cone_c25_persistent_escapes.py \
  --check data/runs/sparse_full_cone_c25_persistent_escape_compression_2026-07-30/summary.json
```

SHA-256 of `summary.json`:

`7bf2872171f0c9a5f6fd088d664a91eb24cf3cf96d3c7d739ac1bcc7e19e4f5a`
