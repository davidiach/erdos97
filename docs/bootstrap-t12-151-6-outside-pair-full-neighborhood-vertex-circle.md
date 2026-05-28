# Bootstrap T12 151:6 Outside-Pair Full-Neighborhood Vertex-Circle Packet

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet extends the source-`151` row-`6` outside-pair audit beyond the
fixed-neighborhood, one-row-drop, and two-row-drop scans. Center `6` remains
inside the thirteen bootstrap-core-plus-outside-pair activation rows from
`docs/bootstrap-t12-151-6-outside-pair-audit.md`, while every other center may
choose an arbitrary selected `4`-set.

Run the checker with:

```bash
python scripts/check_bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.py --check --assert-expected --json
```

Regenerate the artifact with:

```bash
python scripts/check_bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.py --write --assert-expected
```

The checked artifact is:

```text
data/certificates/bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.json
```

## Scan Scope

The scan uses the stored source-`151` row-`6` outside-pair audit as input. It
checks the implicit full-neighborhood space where:

- center `6` uses one of the `13` candidate rows containing bootstrap-core
  witness `[0]` and outside support pair `[3,5]`, `[3,8]`, or `[5,8]`;
- all other centers `0,1,2,3,4,5,7,8` may use any of their `70` selected
  `4`-sets;
- row-pair, witness-pair, selected-indegree, and two-overlap crossing filters
  prune the search;
- each complete basic-filter assignment is replayed through the exact
  vertex-circle quotient self-edge / strict-cycle checker.

This is an implicit search over:

```text
13 * 70^8 = 7,494,241,300,000,000
```

selected-row assignments. The implementation uses minimum-remaining-options
backtracking; it does not enumerate this space directly.

No Euclidean realization, exact distance equation, minimality hypothesis,
formal bridge lemma, or rich-class forcing hypothesis is used.

## Result

The full-neighborhood scan visits `13,439` search nodes. Basic filters leave
`28` complete assignments:

```text
basic-filter complete assignments:     28
non-original row-6 assignments:         21
vertex-circle surviving assignments:    0
```

The exact vertex-circle quotient replay kills all `28` basic-filter survivors:

```text
self-edge:     20
strict-cycle:   8
```

The checked scan status is:

```text
FULL_NEIGHBORHOOD_BASIC_SURVIVORS_ALL_VERTEX_CIRCLE_OBSTRUCTED
```

## Remaining Gap

This closes the full selected-row-neighborhood version of the `151:6`
outside-pair activation-row diagnostic. It does not prove outside-pair support
existence, does not prove the row is forced by minimal or rich-class geometry,
does not model additional auxiliary rich supports, and does not promote the
review-pending `n=9` checker.

## What This Does Not Prove

This artifact does not prove `n=9`, the bootstrap bridge, Erdos Problem #97, or
a counterexample. It is a finite proof-mining diagnostic for one
relation-sufficient outside-pair row target.
