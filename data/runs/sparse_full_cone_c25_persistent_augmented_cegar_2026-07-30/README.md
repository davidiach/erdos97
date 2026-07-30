# C25 persistent width-4 augmented CEGAR

This packet blocks the complete current 144-order C25 history and activates
only the three transferred exact seed orbits plus the selected persistent
width-4 orbit. The dominated persistent width-5 orbit and all eight
zero-marginal compressed residual orbits remain explicitly inactive.

On a deterministic 16-order history-disjoint probe:

- the three transferred seeds cover `0/16`;
- the selected width-4 orbit covers `16/16`;
- all 16 orders are strong lightweight survivors.

After activating the four seed orbits, bounded CEGAR learns eight further exact
full-Kalmanson-cone certificates of widths:

`197, 197, 193, 194, 192, 200, 191, 195`

The run stops at its eight-certificate limit with no unresolved model. The
checker replays 144 blocked identities, four active and nine inactive exact
seed certificates, 16 probe orders, eight learned certificates, 200 new affine
clauses, and 300 exact affine certificate images.

The decision is `COMPRESS_NEW_C25_PERSISTENT_AUGMENTED_RESIDUALS`.

This is a finite, history-blocked, fixed-pattern diagnostic. It is not an
all-order C25 obstruction, geometric realizability result, proof of Erdos
Problem #97, counterexample, or official/global status update.

Replay:

```bash
python scripts/exploration/run_sparse_full_cone_c25_persistent_augmented_cegar.py \
  --check data/runs/sparse_full_cone_c25_persistent_augmented_cegar_2026-07-30/summary.json
```

SHA-256 of `summary.json`:

`623d1a9408226243c24e47cb18635e16e6f7a044eaccb07877956230fd70c569`
