# Fragile-cycle quotient hierarchy

Status: exact certificate diagnostic and proof-mining aid. This note does not
claim a fragile-cycle bridge, a proof of `n=9`, a general proof, a Euclidean
realization, or a counterexample.

## Why this pilot exists

The [OpenAI reasoning walkthroughs](https://cdn.openai.com/pdf/reasoning-walkthroughs.pdf)
suggest a useful research habit: extract small, independently checkable
intermediate objects from a successful reasoning trace, then test which parts
survive simplification. The PDF is methodological context, not mathematical
evidence for this repository.

Here the intermediate objects are three existing strict Kalmanson
certificates:

1. the one-row `n=9` equilateral hinge;
2. the two-row fixed-order `Z/16` marked-three-cycle inverse pair; and
3. the four-row `k=8` member of the scalable bridge-control family.

The new question is exact and finite: after forgetting unused halo roles,
which identifications of the remaining formal roles preserve the certificate?

## Admissible role quotients

For a template with formal role set (R), retained equal-distance classes,
and marked strict Kalmanson quadrilaterals, a set partition of (R) is
admissible when:

- no marked strict quadrilateral loses a vertex;
- no retained distance pair becomes a loop; and
- all mapped quadrilaterals fit one cyclic order of the quotient roles.

The checker exhausts every set partition, not a sampled subset. It then
rebuilds every mapped strict row and retained equality class with exact integer
arithmetic.

The reusable algebraic point is conditional but elementary. If a nonnegative
combination of strict rows has coordinate coefficients (c_Cleq 0) in one
distance quotient, merging quotient classes replaces a target coefficient by
(sum_{Cmapsto D}c_C). It therefore remains nonpositive. In the three
stored templates the checked combinations are stronger: every mapped sum is
identically zero.

This pushforward statement certifies an admissible quotient of a known
template. It does not prove that a hypothetical minimal counterexample
contains the template.

## Exact classification

| Template | Formal roles | Partitions checked | Strict rows | Admissible partitions | Compatible ordered quotients | Nontrivial partitions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `n9_equilateral_hinge` | 4 | 15 | 1 | 1 | 1 | 0 |
| `z16_marked_three_cycle_inverse` | 5 | 52 | 2 | 1 | 1 | 0 |
| `scalable_k8_four_circuit` | 8 | 4,140 | 4 | 3 | 5 | 2 |

The first two templates are role-rigid under these admissibility rules. The
scalable four-row template has exactly two proper quotients, both on seven
roles:

- identify roles (18) and (23); or
- identify roles (23) and (27).

Each proper quotient has one compatible cyclic order. The unmerged
eight-role template has three compatible cyclic orders, giving five ordered
quotients at that level and seven across the full hierarchy.

For the `Z/16` equality quotient, an independent fixed-order scan also checks
all (2inom{16}{4}=3,640) individual strict Kalmanson rows. None is
coordinatewise nonpositive, while the stored two-row inverse pair sums to
zero. This records fixed-order support minimality only.

## What this teaches us

- The one-, two-, and four-row certificates are closed under every admissible
  role identification in this finite catalogue.
- Quotienting exposes two smaller seven-role forms of the scalable
  certificate. They are better local targets than the original eight-role
  labelling when looking for a forcing lemma.
- The hinge and `Z/16` inverse pair cannot be simplified by role
  identification without destroying a marked strict quadrilateral or its
  cyclic-order compatibility.
- The unresolved step is geometric and structural: force one of these
  certificate templates, or a separately stated rich-class/deletion
  alternative, from a genuine fragile matching cycle and its halos.

The catalogue is deliberately incomplete. It forgets unused halo roles,
preserves only marked quadrilateral orders, and does not check Euclidean
realizability. It is a proof-mining hierarchy, not a bridge theorem.

## Replay

```bash
python scripts/check_fragile_cycle_quotient_hierarchy.py \
  --check --assert-expected --summary-json

python scripts/check_fragile_turn_pivot_guardrail.py \
  --check --assert-expected --summary-json

python scripts/check_scalable_kalmanson_inverse_control.py \
  --assert-expected --json

python scripts/check_scalable_kalmanson_three_control.py \
