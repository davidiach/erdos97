# C25 residual-seed augmentation probe

Status: bounded exact-clause coverage comparison for one fixed C25 quotient.
No general proof, all-order C25 obstruction, geometric counterexample, or
official-status change is claimed.

## Target

The residual compression in
`docs/sparse-full-cone-c25-transfer-residual-compression.md` found eight exact
circuits of widths `3`--`9`. Its predeclared continuation rule called for a
fresh order probe comparing the original three transferred seed orbits,
width-3-only residual augmentation, and augmentation by all eight residual
orbits before spending another certificate-learning budget.

`scripts/exploration/probe_sparse_full_cone_c25_residual_seed_augmentation.py`
performs that comparison without activating any full-cone clauses during order
generation. This makes coverage counterfactual: all measured seed hits are
evaluated only after each inverse-pair-escape order is found.

## Exact history and seed packets

All 112 previously stored C25 orders are blocked under cyclic rotation and
reversal:

| History packet | Orders |
| --- | ---: |
| Prior probe/seeded packet | 24 |
| First fresh stream | 32 |
| Second fresh stream | 32 |
| Transfer-CEGAR probe | 16 |
| Transfer-CEGAR residuals | 8 |
| **Total** | **112** |

The 112 orders are pairwise distinct under the same dihedral equivalence.
History blocking is a novelty device, not an all-order proof rule.

The comparison uses three nested exact packets:

| Packet | Seed orbits | Exact affine images | Unique clauses |
| --- | ---: | ---: | ---: |
| Transferred only | 3 | 75 | 75 |
| Transferred plus residual width 3 | 4 | 100 | 100 |
| Transferred plus all residuals | 11 | 275 | 275 |

Every certificate and affine image is replayed exactly through the pinned
compression, CEGAR, transfer, and fresh-stream provenance chain.

## Fresh-probe result

The order probe reaches its 32-order limit after 563 Z3 iterations and 14,901
learned inverse-pair clauses. All 32 orders survive the vertex-circle and both
Altman lightweight filters.

| Packet | Covered orders | Matching affine-clause occurrences |
| --- | ---: | ---: |
| Transferred only | 32/32 | 280 |
| Transferred plus residual width 3 | 32/32 | 417 |
| Transferred plus all residuals | 32/32 | 809 |

The residual circuits increase the number of matching clauses but add no
covered order. The width-3 residual has zero marginal coverage over the
transferred packet, and the other seven residuals have zero marginal coverage
over width-3 augmentation.

Individual transferred-seed coverage is:

| Transferred width | Covered orders | Matching occurrences |
| ---: | ---: | ---: |
| 3 | 32/32 | 206 |
| 5 | 22/32 | 26 |
| 14 | 32/32 | 48 |

Thus the original width-3 and width-14 orbits each independently cover the
entire new probe.

## Decision and next target

The predeclared marginal-coverage rule returns
`STOP_C25_RESIDUAL_SEED_AUGMENTATION_AFTER_BOUNDED_PROBE`. Do not add the eight
residual orbits to the next CEGAR merely because they create more matching
clause occurrences.

The predeclared follow-up is now completed in
`docs/sparse-full-cone-c25-persistent-escape-screen.md`. The two original
transfer-CEGAR probe orders `probe:0` and `probe:1` survive the lightweight
filters and remain outside all three transferred and eight compressed residual
seed orbits, but exact positive circuits of widths `201` and `196` obstruct
them in the full Kalmanson cone. Neither is a coordinate target. Compress those
two new circuits and test their affine reuse before extending order-search
limits.

Replay:

```bash
python scripts/exploration/probe_sparse_full_cone_c25_residual_seed_augmentation.py \
  --check data/runs/sparse_full_cone_c25_residual_seed_probe_2026-07-29/summary.json
```
