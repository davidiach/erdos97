# Sparse full-cone small-template fresh stream (2026-07-29)

`summary.json` stores seven explicit canonical exact C25/C29 positive-circuit
templates and a bounded transfer probe over 64 fresh inverse-pair-escape
orders.

Every fresh order is dihedrally distinct from all 48 orders in the source
compression packet and from every earlier order in its fresh stream. The
checker:

- verifies the source compression artifact SHA-256;
- reconstructs and exact-replays all seven canonical certificates;
- reconstructs all 187 quotient-preserving affine template images;
- validates the stored solver status, result, bounds, seeds, clause counts, and model iterations;
- checks permutation, anchoring, and dihedral freshness for all 64 orders;
- independently replays the inverse-pair and lightweight filters;
- recomputes every exact template match and coverage count.

Expected summary: seven canonical exact templates, 187 exact affine images,
and 64 verified history-disjoint fresh orders. None of the fresh orders matches
any template image.

Artifact SHA-256:

```text
4f1f444405a1316e0acf6fbd1da850a32932c2c6477bfe3e90b4aa62b3a1aa3c
```

Replay:

```bash
python scripts/exploration/probe_sparse_full_cone_small_templates.py \
  --check data/runs/sparse_full_cone_small_template_fresh_stream_2026-07-29/summary.json
```

“Fresh” means history-disjoint under cyclic rotation and reversal, not
statistically independent. This is bounded fixed-pattern evidence, not an
all-order obstruction, geometric realization result, counterexample, proof of
Erdos Problem #97, or official/global status update.
