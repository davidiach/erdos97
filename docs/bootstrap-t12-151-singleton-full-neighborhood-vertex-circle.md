# Bootstrap T12 151 Singleton Full-Neighborhood Vertex-Circle Audit

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This packet extends the source-`151` singleton-support row audits for the two
one-outside-label targets:

```text
151:5
151:8
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.json`.

## Scan Scope

The source input is the existing source-`151` singleton-support audit packet:

```text
data/certificates/bootstrap_t12_151_singleton_support_audit.json
```

For row `151:5`, the target row ranges over the nine selected rows containing
bootstrap-core witnesses `[2,4]` and at least one singleton support label from
`[7,8]`.

For row `151:8`, the target row ranges over the nine selected rows containing
bootstrap-core witnesses `[1,2]` and at least one singleton support label from
`[5,7]`.

For each target, all eight other centers may choose arbitrary selected `4`-sets.
The implicit space for each target is therefore

```text
9 * 70^8 = 5,188,320,900,000,000
```

candidate assignments before pruning, or
`10,376,641,800,000,000` candidate assignments across the two targets.

The scan applies the selected-row filters used by the review-pending `n=9`
vertex-circle checker:

- row-pair cap;
- witness-pair cap;
- selected-indegree cap;
- two-overlap crossing in the natural cyclic order;
- exact vertex-circle quotient replay for the complete basic-filter survivors.

No Euclidean realization, exact distance equation, minimality hypothesis, or
rich-class forcing hypothesis is used.

## Result

The full-neighborhood scan has `50` basic-filter complete assignments in total:

```text
151:5 -> 34 basic-filter complete assignments
151:8 -> 16 basic-filter complete assignments
```

All `50` assignments are vertex-circle obstructed:

```text
self_edge     -> 37
strict_cycle  -> 13
ok            -> 0
```

The target-level status table is:

```text
target   search nodes   empty domains   basic survivors   non-original target survivors   self_edge   strict_cycle   ok
151:5    15,674         8,148           34                27                              27          7              0
151:8     7,035         3,811           16                 9                              10          6              0
```

The checked scan status is:

```text
FULL_NEIGHBORHOOD_BASIC_SURVIVORS_ALL_VERTEX_CIRCLE_OBSTRUCTED
```

## Remaining Gap

This closes a full-selected-row-neighborhood version of the narrow local escape
route for source-`151` singleton-support targets under the `n=9` checker filters
and vertex-circle quotient replay. It still does not prove that singleton
support labels are forced by a genuine rich-class catalogue, and it does not
model additional auxiliary rich supports.

## What This Does Not Prove

This artifact does not prove singleton support existence, row forcing, `n=9`,
the bootstrap bridge, or Erdos Problem #97. It is a finite proof-mining
diagnostic for two T12 row targets.
