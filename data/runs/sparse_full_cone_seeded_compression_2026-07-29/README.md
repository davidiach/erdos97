# Sparse full-cone seeded certificate compression (2026-07-29)

`summary.json` records deterministic randomized compression of the sixteen
exact C25/C29 certificates in the seeded full-cone CEGAR packet, followed by
direct and translation-orbit coverage over all 48 stored fresh orders.

The checker:

- verifies the source seeded-CEGAR artifact SHA-256;
- exact-replays all 16 compressed positive circuits;
- exact-replays all 432 quotient-preserving affine certificate images;
- reconstructs the 48 target orders from the source packet;
- recomputes direct and translation-orbit coverage;
- recomputes the quotient-vector overlap ledger.

Expected summary: 48 verified target orders, 16 verified compressed exact
certificates, and 432 verified exact affine certificate images.

Artifact SHA-256:

```text
7abd2868e3bd7fad660dbd76fbfa5167dd15040c72c228b6e032a619618fd211
```

Replay:

```bash
python scripts/exploration/compress_sparse_full_cone_seeded_certificates.py \
  --check data/runs/sparse_full_cone_seeded_compression_2026-07-29/summary.json
```

This is bounded fixed-pattern evidence. It is not an all-order obstruction,
geometric realization result, counterexample, or proof of Erdos Problem #97.
