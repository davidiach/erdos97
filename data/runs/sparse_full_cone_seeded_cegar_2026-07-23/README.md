# Sparse full-cone seeded affine CEGAR (2026-07-23)

`summary.json` records a bounded C25/C29 order-search experiment seeded by the
four compressed exact certificates from the preceding compression packet.

The checker:

- verifies the seed artifact SHA-256;
- recomputes the exact selected-distance quotient automorphisms;
- exact-replays every transformed seed and learned certificate;
- independently checks all 32 counterfactual probe orders for inverse-pair
  escape and recomputes their seed-orbit hit counts;
- independently checks all 16 new seeded-CEGAR models, full certificates, and
  affine-orbit exclusions.

Expected summary: 32 verified probe orders, 16 verified new exact
certificates, and 544 verified exact affine certificate images.

Artifact SHA-256:

```text
4a4bce42f5cdef3a90c4cd596e817fca26fe81e97be457549e78e2787a02f214
```

Replay:

```bash
python scripts/exploration/run_sparse_full_cone_seeded_cegar.py \
  --check data/runs/sparse_full_cone_seeded_cegar_2026-07-23/summary.json
```

This is bounded fixed-pattern evidence. It is not an all-order obstruction,
geometric realization result, counterexample, or proof of Erdos Problem #97.
