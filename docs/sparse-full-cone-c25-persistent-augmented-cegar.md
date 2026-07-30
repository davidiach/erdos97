# C25 persistent width-4 augmented CEGAR

Status: bounded fixed-pattern, history-blocked exact-clause diagnostic. No
general proof, all-order C25 obstruction, geometric counterexample, or
official-status change is claimed.

## Target

The compression packet in
`docs/sparse-full-cone-c25-persistent-escape-compression.md` found that the
exact width-4 orbit from `transfer_cegar_probe:0` is the one-source minimum
cover of all 23 targets marginal over the 11 older seed orbits in the current
144-order C25 packet. The width-5 persistent orbit adds no marginal target.

This follow-up tests that seed-selection decision outside the source packet. It
blocks all 144 known C25 cyclic-order identities under rotation and reversal,
keeps the three transferred seed orbits plus only the selected width-4 orbit
active, and leaves these nine exact seed orbits inactive:

- the dominated width-5 persistent orbit;
- all eight compressed residual orbits, whose augmentation probe had zero
  marginal coverage.

The four active certificates have widths `3, 5, 14, 4` and produce 100 exact
quotient-preserving affine images.

## Deterministic bounded protocol

`scripts/exploration/run_sparse_full_cone_c25_persistent_augmented_cegar.py`
uses random seed `20260730`, conflict cap `1024`, and two limits:

1. collect 16 history-disjoint inverse-pair-escape orders within at most 12,000
   Z3 iterations without activating the full-cone seed clauses, then compare
   exact seed coverage;
2. activate the four seed orbits and learn at most eight new exact full-cone
   certificate orbits within at most 12,000 iterations.

The numerical LP is only a certificate finder. Every stored positive
certificate is exactified and replayed with integer arithmetic. All history
identities, seed certificates, affine images, clause matches, and learned
certificates are checked without rerunning the search.

## Fresh 16-order transfer result

The fresh probe reaches its 16-order limit after 454 iterations and 14,122
inverse-pair clauses. All 16 orders survive the stored vertex-circle and both
Altman lightweight filters.

| Seed packet | Covered probe orders | Covered strong orders |
| --- | ---: | ---: |
| Three transferred orbits | 0/16 | 0/16 |
| Selected width-4 orbit only | 16/16 | 16/16 |
| Transferred plus selected width 4 | 16/16 | 16/16 |

Thus every fresh probe order is marginally covered by the selected width-4
orbit. The transfer is exact for this bounded probe, not a claim about all C25
orders.

## Augmented CEGAR result

With all four active seed orbits, the CEGAR search excludes the 16 probe orders
and finds eight further history-disjoint orders. All eight are strong
lightweight survivors and escape every active seed and previously learned
clause at discovery. Each has an exact positive full-Kalmanson-cone
certificate.

| Learned model | Z3 iteration | Exact certificate width |
| ---: | ---: | ---: |
| 0 | 40 | 197 |
| 1 | 41 | 197 |
| 2 | 81 | 193 |
| 3 | 82 | 194 |
| 4 | 83 | 192 |
| 5 | 84 | 200 |
| 6 | 85 | 191 |
| 7 | 102 | 195 |

The run stops at the configured eight-certificate limit with no unresolved
model. The eight learned orbits contribute 200 unique affine clauses. Together
with the 100 active seed images, the checker replays 300 exact affine
certificate images.

## Decision and next target

The route decision is
`COMPRESS_NEW_C25_PERSISTENT_AUGMENTED_RESIDUALS`.

Before increasing the cyclic-order search budget, compress the eight new
width-191--200 certificates, construct their exact quotient-preserving affine
orbits, and measure reuse and marginal coverage against both the 16-order probe
and eight new residual orders. This remains bounded clause engineering for one
fixed selected-witness quotient.

Replay:

```bash
python scripts/exploration/run_sparse_full_cone_c25_persistent_augmented_cegar.py \
  --check data/runs/sparse_full_cone_c25_persistent_augmented_cegar_2026-07-30/summary.json
```
