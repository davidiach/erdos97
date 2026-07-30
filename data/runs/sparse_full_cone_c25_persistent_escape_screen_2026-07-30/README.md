# C25 persistent-escape full-cone screen

This packet exactly classifies the two predeclared transfer-CEGAR targets
`probe:0` and `probe:1` for the fixed `C25_sidon_2_5_9_14` selected-witness
pattern.

Both orders:

- survive the stored vertex-circle and Altman lightweight filters;
- escape the exact two-inequality Kalmanson inverse-pair filter;
- match none of the three transferred or eight compressed residual seed
  orbits; and
- have exact positive integer zero-sum certificates in the complete
  fixed-order Kalmanson cone.

| Target | Strict rows screened | Positive certificate rows | Ordered quads |
| --- | ---: | ---: | ---: |
| `probe:0` | 25,300 | 201 | 201 |
| `probe:1` | 25,300 | 196 | 196 |

The checker replays the pinned residual-seed augmentation provenance chain,
all 11 seed orbits and 275 quotient-preserving affine images, each target
order and filter audit, and both exact positive circuits.

The decision is
`CONTINUE_C25_CLAUSE_ROUTE_WITH_EXACT_POSITIVE_CIRCUITS`. The next bounded
target is to compress these two circuits and test their affine reuse before
extending cyclic-order search limits.

This is a two-order, fixed-pattern exact obstruction packet. It is not an
all-order C25 obstruction, a geometric realizability result, a proof of Erdos
Problem #97, a counterexample, or an official/global status update.

Replay:

```bash
python scripts/exploration/screen_sparse_full_cone_c25_persistent_escapes.py \
  --check data/runs/sparse_full_cone_c25_persistent_escape_screen_2026-07-30/summary.json
```
