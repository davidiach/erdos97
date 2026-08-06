# Fragile-cycle halo slot budget

Status: exact bounded incidence lemma and proof-mining certificate. This note
does not force the `23=27` core, prove Euclidean realizability, prove `n=11`
or `n=12`, prove Erdos Problem #97, or claim a counterexample.

## Question

The first active-halo packet closes the fixed core with at most two halos by a
generic hinge/splice endgame. The stored three-halo continuation closes the
next fixed slice by vertex-circle and Kalmanson certificates. The apparent
remaining gap was an arbitrary number of active halo roles.

For the fixed `23=27` core, the retained rows have required witness pairs

```text
1 -> {0,4}
3 -> {4,5}
4 -> {0,2}
6 -> {2,5}
```

and each row has exactly two further witness slots.

## Slot-budget lemma

The four required pairs cover exactly the core roles `{0,2,4,5}`. Therefore
the free slots must cover the three missing core roles `{1,3,6}` and every
active halo role. There are four retained rows and two free slots per row, so

```text
3 + halo_count <= 4 * 2 = 8.
```

Consequently an active retained-row cover has at most five halos. This is a
direct counting proof, not a finite-search inference.

Call a halo role **retained-private** when it occurs in exactly one of the four
retained rows. If there are four halos, the eight slots cover seven mandatory
roles and have only one spare occurrence. Hence at most one halo can be
repeated and at least three halos are retained-private. With five halos all
eight mandatory roles occur exactly once, so all five halos are
retained-private.

This term is deliberately narrow. Retained-private does not mean private in a
full selected-row extension, a full rich-class system, or the bootstrap-core
deletion-closure sense.

## Exact coverage-first census

The checker generates only free-slot multisets that already cover every
mandatory role, partitions them into the four retained rows, and then applies
the same self-exclusion, crossing, witness-pair capacity, and essential-row
matching rules as the earlier halo frontier. It also runs the generic
equilateral-hinge and Kalmanson-splice occurrence tests.

| Halos | Placements | Essential covers | Hinge covers | Splice-only | Motif-free | Retained-private halo histogram |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 4 | 210 | 529,200 | 0 | 10,440 | 518,760 | `3: 239,400`; `4: 289,800` |
| 5 | 462 | 512,820 | 0 | 0 | 512,820 | `5: 512,820` |

For four halos, the unique spare occurrence is classified exactly as:

```text
duplicated halo:         239,400
duplicated missing core: 117,180
required-anchor reuse:   172,620
```

The large motif-free population is a negative result for an overstrong local
claim: hinge/splice membership of the retained rows alone does not close the
four- or five-halo regimes.

## Complete fixed-core alternative map

Combining checked packets gives the following bounded map once the `23=27`
core and the formal active-cover contract are assumed:

```text
0 halos: no retained-row cover
1 halo: cover exists, but no full selected-row extension
2 halos: every full extension contains an equilateral hinge
3 halos: no full extension survives the vertex-circle/Kalmanson endgame
4 halos: at least three retained-private halos
5 halos: all five halos retained-private
6+ halos: impossible by the eight-slot budget
```

This is an alternative map, not fixed-core closure. The four/five-halo rows
were not exhaustively extended to full selected systems, and retained-private
roles may be reused by other selected rows or belong to larger rich classes.

## Next bridge target

The remaining Contract F obligation is now more specific:

```text
force the 23=27 core from genuine fragile-cycle geometry,
or show that three or more retained-private halo roles force
a full-rich-class, deletion-profile, critical-radius, or metric obstruction.
```

The companion deletion-profile crosswalk now performs that experiment. It
finds a retained-exclusive mutual pair in 310,320 covers; each such pair
forces the conditional alternative of an added T4 endpoint-reuse row or a
T5/T44 certifier. The other 731,700 covers are pair-free and already
T4-certify every deletion pair with the retained rows. Thus deletion coverage
alone cannot upgrade the retained-private roles in that residue. See
`docs/fragile-cycle-halo-deletion-crosswalk.md`; the next target must exploit
the triggered rich-class alternative or add metric/full-extension geometry to
the pair-free branch.

## Replay

```bash
python scripts/check_fragile_cycle_halo_slot_budget.py \
  --check --assert-expected --summary-json

python -m pytest -q tests/test_fragile_cycle_halo_slot_budget.py
```

The generated artifact is
`data/certificates/fragile_cycle_halo_slot_budget.json`; do not edit it
directly.
