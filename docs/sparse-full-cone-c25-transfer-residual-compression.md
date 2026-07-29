# C25 transfer-residual certificate compression

Status: bounded exact alternative-circuit and cross-coverage diagnostic for
one fixed C25 quotient. No general proof, all-order C25 obstruction, geometric
counterexample, or official-status change is claimed.

## Target

The transferred-clause seeded CEGAR in
`docs/sparse-full-cone-c25-transfer-cegar.md` learned eight exact positive
Kalmanson circuits after blocking 88 known C25 orders and activating three
transferred clause orbits. Their ordered-quadrilateral widths were
`190`--`200`, so the predeclared next step was to search for smaller exact
circuits before increasing the CEGAR limit.

`scripts/exploration/compress_sparse_full_cone_c25_transfer_residuals.py`
samples deterministic alternative LP objectives for exactly those eight fixed
orders. A numerical support is retained only after integer exactification,
zero-sum replay, and a positive-circuit rank audit.

## Deterministic objective budgets

The objective seeds are `20260804 + 1000 * model_index`. Trial budgets stop
after the first pretested deterministic packet large enough to expose a small
circuit for each source:

| Residual | Source width | Trials | Best trial | Exact compressed width |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 199 | 32 | 16 | 7 |
| 1 | 190 | 32 | 9 | 9 |
| 2 | 200 | 32 | 12 | 5 |
| 3 | 193 | 32 | 23 | 3 |
| 4 | 194 | 64 | 50 | 7 |
| 5 | 197 | 64 | 56 | 4 |
| 6 | 191 | 32 | 31 | 6 |
| 7 | 199 | 112 | 105 | 4 |

The checker requires exactly one compressed row for each of the eight sources
and validates trial counts, seeds, improvement history, numerical-support
histograms, and exact certificate summaries. All eight compressed certificates
are exact positive circuits. Their
canonical clause-orbit hashes are distinct from the three active transferred
seed orbits. The selected-distance quotient admits translations only, so the
eight circuits produce 200 exact affine images.

The randomized objective family is not exhaustive. The exact claim concerns
only the eight retained certificates, not optimality of their widths.

## Exact 24-order cross-coverage

Coverage is replayed over the 16 history-disjoint probe orders and the eight
seed-escaping residual orders stored in the source packet.

| Target stream | Targets | Direct covered | Affine covered | Direct cross-edges | Affine cross-edges |
| --- | ---: | ---: | ---: | ---: | ---: |
| Probe | 16 | 0 | 14 | 0 | 98 |
| Residual | 8 | 8 | 8 | 16 | 52 |
| **Total** | **24** | **8** | **22** | **16** | **150** |

The width-3 orbit from residual `seeded:3` covers all eight residual targets
and all 14 probe targets already reached by the transferred seeds. Exhaustive
enumeration of the eight stored source orbits verifies that `seeded:3` alone
is a minimum-cardinality affine cover of the residual packet, with minimum
total width 3.

The two original transferred-seed probe escapes, `probe:0` and `probe:1`,
remain uncovered by every compressed residual orbit. Thus the compression
finds strong reusable clauses but does not erase the exact two-order transfer
boundary.

The eight compressed circuits use 45 distinct quotient-vector hashes; no hash
occurs in two certificates. Their order-family reuse therefore comes from
complete clause geometry, not literal reuse of quotient vectors.

## Decision and next target

The predeclared continuation rule fires: all eight residual circuits have
width at most 9, all eight reuse affinely across residual orders, and every
orbit reaches probe orders. The next bounded experiment should extend the C25
history-disjoint order search, while preserving the two probe escapes as a
counterfactual control:

1. block all 112 known C25 orders under rotation and reversal;
2. compare the original three transferred seeds plus the new width-3 orbit
   against the full augmentation by all eight compressed residual orbits;
3. measure marginal seed coverage on a new probe before learning more
   full-cone certificates;
4. stop on any unresolved full-cone model, and never interpret a bounded or
   history-blocked solver result as an all-order conclusion.

Replay:

```bash
python scripts/exploration/compress_sparse_full_cone_c25_transfer_residuals.py \
  --check data/runs/sparse_full_cone_c25_transfer_residual_compression_2026-07-29/summary.json
```
