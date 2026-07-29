# C25 transferred-clause seeded CEGAR

Status: bounded history-disjoint fixed-pattern exact-clause diagnostic. No
all-order obstruction, geometric counterexample, general proof, or
official-status update is claimed.

This run seeds the C25 order solver with the exact width-3 and width-5 circuits
that transferred across both outside-source packets, plus the width-14
secondary prior-packet circuit. Their 75 quotient-preserving affine images are
active from the start.

All 88 known C25 orders from the prior, first-fresh, and second-fresh packets
are blocked under cyclic rotation and reversal before both the probe and the
seeded CEGAR phases.

## Result

- Counterfactual probe: 16 history-disjoint inverse-pair escapes, all
  lightweight survivors; 14 are covered by transferred seeds.
- Seeded CEGAR: eight seed-escaping history-disjoint orders, all lightweight
  survivors.
- Exact learned certificates: 8/8, with widths 190-200.
- Learned affine clauses: 200.
- Exact affine certificate images replayed: 275, including the 75 seed images.
- Stop condition: configured eight-certificate limit, not UNSAT.

Generate:

```bash
python scripts/exploration/run_sparse_full_cone_c25_transfer_cegar.py \
  --out data/runs/sparse_full_cone_c25_transfer_cegar_2026-07-29/summary.json
```

Replay without rerunning Z3; the checker validates solver termination metadata,
model/iteration provenance, exact certificate summaries, and affine images:

```bash
python scripts/exploration/run_sparse_full_cone_c25_transfer_cegar.py \
  --check data/runs/sparse_full_cone_c25_transfer_cegar_2026-07-29/summary.json
```

SHA-256 of `summary.json`:

`7d61f34c8bc0e96b9ce70a9021f735f0cbdbe93647574239c0234aa5bb48e5c4`
