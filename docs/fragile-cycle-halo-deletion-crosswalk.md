# Fragile-cycle halo deletion-profile crosswalk

Status: exact bounded deletion-profile crosswalk and negative control. This
note assumes the fixed `23=27` core. It does not force that core, a full
selected-row extension, Euclidean realizability, `n=11`, `n=12`, Erdos
Problem #97, or a counterexample.

## Question

The slot-budget lemma leaves at least three retained-private halo roles in
every four-halo cover and five in every five-halo cover. Retained privacy is
not full-rich-class privacy, so the next useful question is whether minimal
two-deletion structure already upgrades those covers.

The exact trigger from the two-deletion profile lemma is an **exclusive mutual
pair** in the T4 coverage graph. For the four retained critical rows, define

```text
Gamma_R(x) = {retained T4 centers y : x lies in F_y}.
```

A pair `{x,z}` is retained-exclusive when

```text
Gamma_R(x) = {z}  and  Gamma_R(z) = {x}.
```

## Exact dichotomy

A deletion pair has no retained T4 certifier exactly when it is
retained-exclusive. In a full rich-class system, one of two things must then
happen:

1. an additional T4 row centered outside the retained family contains `x` or
   `z`, breaking retained exclusivity; or
2. no such row exists, the pair remains globally exclusive, and the minimal
   two-deletion profile lemma forces a T5 or T44 certifier outside the pair.

This is a genuine deletion-profile alternative, but it is conditional: the
crosswalk does not decide which branch occurs.

Center `4` can never participate. Required rows `1` and `3` both contain `4`,
so `Gamma_R(4)` has size at least two. The only candidate pairs are therefore
`{1,3}`, `{1,6}`, and `{3,6}`. Exclusive pairs are vertex-disjoint, so at most
one can occur on these three candidate endpoints.

## Exhaustive census

The checker reuses the coverage-first four/five-halo contract and exhausts all
canonical cyclic placements.

| Halos | Placements | Essential covers | One exclusive pair | Pair-free |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 210 | 529,200 | 144,000 | 385,200 |
| 5 | 462 | 512,820 | 166,320 | 346,500 |

The pair identities are:

| Halos | `{1,3}` | `{1,6}` | `{3,6}` |
| ---: | ---: | ---: | ---: |
| 4 | 41,760 | 52,920 | 49,320 |
| 5 | 55,440 | 55,440 | 55,440 |

For four halos, the trigger split refines the retained-private/spare ledger:

| Retained-private halos | Spare kind | Triggered | Pair-free |
| ---: | --- | ---: | ---: |
| 3 | duplicated halo | 75,960 | 163,440 |
| 4 | duplicated missing core | 10,080 | 107,100 |
| 4 | required-anchor reuse | 57,960 | 114,660 |

All five-halo covers have five retained-private halos and no spare occurrence;
166,320 are triggered and 346,500 are pair-free.

## Negative-control boundary

If a retained cover has no exclusive pair, its four retained T4 rows already
certify every two-vertex deletion: for every pair, some retained center outside
the pair has a row meeting it. Thus the 731,700 pair-free covers show exactly
what singleton and two-deletion T4 coverage do **not** prove. Those coverage
lemmas alone cannot force an added halo-reuse row or a T5/T44 profile.

This is a coverage-level negative control, not an abstract incidence
counterexample and not a Euclidean configuration. Other minimality, crossing,
critical-radius, vertex-circle, Kalmanson, or full-extension constraints may
still reject a pair-free cover.

## Next bridge target

The endpoint-reuse follow-up exhausts the first target and finds that every
triggered cover admits a compatible one-row escape:

```text
exclusive-pair covers:
    all pass the current one-row incidence/crossing/vertex-circle filters;

pair-free covers:
    use metric/full-extension geometry, since deletion coverage alone is silent.
```

Thus the next step needs exact rich-class type, simultaneous full-extension,
critical-radius, or ordinary-distance information. See
`docs/fragile-cycle-halo-endpoint-reuse.md`. Neither branch should be described
as closed by these packets.

## Replay

```bash
python scripts/check_fragile_cycle_halo_deletion_crosswalk.py \
  --check --assert-expected --summary-json

python -m pytest -q tests/test_fragile_cycle_halo_deletion_crosswalk.py
```

The generated artifact is
`data/certificates/fragile_cycle_halo_deletion_crosswalk.json`; do not edit it
directly.
