# Bootstrap/T12 source-81 row-8 full-neighborhood vertex-circle packet

Status: proof-mining diagnostic only.  No proof of Erdos Problem #97 and no
counterexample are claimed.

This packet widens the source-`81` row-`8` singleton-support audit.  The
previous audit fixed the source-`81` selected-row neighborhood, or allowed one
additional non-target row to move, and found that only the original row
`[0,2,5,6]` survived the basic incidence/crossing filters.  Here center `8` is
fixed to each activation row containing bootstrap-core witnesses `[0,2]` and at
least one singleton support label from `[5,6]`, while all other centers
`0..7` may choose arbitrary selected four-sets.

The result is an explicit boundary for future bridge lemmas: basic filters do
not force the original row once the full selected-row neighborhood is allowed
to move.  They leave `34` complete assignments, including `27` with a
non-original row `8`.  However, exact vertex-circle quotient replay kills all
`34` complete assignments: `27` by self-edge and `7` by strict cycle.

Run the checker with:

```bash
python scripts/check_bootstrap_t12_81_8_full_neighborhood_vertex_circle.py --check --assert-expected --json
```

Regenerate the artifact with:

```bash
python scripts/check_bootstrap_t12_81_8_full_neighborhood_vertex_circle.py --write --assert-expected
```

## Scope

The packet checks a fixed source-`81` singleton-support target under the
natural `n=9` cyclic order.  It uses selected-row row-pair, witness-pair,
two-overlap crossing, selected-indegree, and vertex-circle quotient filters. It
does not prove the singleton support exists in a genuine rich-class catalogue,
does not prove row forcing, does not prove `n=9`, does not prove the bootstrap
bridge, and is not a counterexample.

## Summary counts

| Quantity | Value |
|---|---:|
| target center classes | 9 |
| free row centers | 8 |
| implicit selected-assignment space | 5,188,320,900,000,000 |
| search nodes visited | 16,010 |
| empty domains | 8,436 |
| basic-filter complete assignments | 34 |
| non-original row-8 basic assignments | 27 |
| vertex-circle self-edges | 27 |
| vertex-circle strict cycles | 7 |
| vertex-circle survivors | 0 |

The target-row split is:

| row `8` class | basic survivors | vertex-circle statuses |
|---|---:|---|
| `[0,1,2,5]` | 0 | none |
| `[0,1,2,6]` | 0 | none |
| `[0,2,3,5]` | 0 | none |
| `[0,2,3,6]` | 0 | none |
| `[0,2,4,5]` | 0 | none |
| `[0,2,4,6]` | 5 | `4` self-edge, `1` strict cycle |
| `[0,2,5,6]` | 7 | `3` self-edge, `4` strict cycle |
| `[0,2,5,7]` | 12 | `10` self-edge, `2` strict cycle |
| `[0,2,6,7]` | 10 | `10` self-edge |

## Interpretation

This is useful mainly as a negative control.  A bridge proof cannot simply
extend the one-row-drop singleton-support audit and claim that basic incidence
filters force the original row `8`; the full-neighborhood CSP supplies
non-original basic-filter survivors.  Any future forcing argument for this
subtarget must either use additional minimal/rich-class structure before the
full-neighborhood move, or use a geometric filter such as the vertex-circle
quotient obstruction after the selected rows are present.
