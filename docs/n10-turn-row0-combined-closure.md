# n=10 Row0 Turn + Vertex-Circle Combined Closure

Status: `FINITE_BOOKKEEPING_NOT_A_PROOF`.

This derived crosswalk joins the bounded `n=10` row0-index-0 turn pilot with
its four vertex-circle escape templates. It is not a proof of `n=10`, not a
complete `n=10` search, not a counterexample, and not a source-of-truth status
update.

## Artifact

```bash
data/certificates/n10_turn_row0_combined_closure.json
```

Regenerate and check it with:

```bash
python scripts/check_n10_turn_row0_combined_closure.py --write --assert-expected
python scripts/check_n10_turn_row0_combined_closure.py --check --assert-expected --json
```

## What the Crosswalk Checks

The checker treats the two existing artifacts as inputs:

```bash
data/certificates/n10_turn_row0_pilot.json
data/certificates/n10_turn_row0_escape_self_edges.json
```

It verifies that:

- the row0-index-0 pilot has `160` full assignments;
- `156` assignments have stored weak-turn Farkas certificates;
- the remaining weak-turn SAT assignments are exactly
  `[74, 103, 156, 157]`;
- those four SAT assignments are exactly the four stored row0-local
  vertex-circle self-edge records;
- the turn-closed and escape-closed sets are disjoint; and
- their union covers all `160` assignments in this bounded slice.

The four escape templates remain the row0-local self-edge templates already
recorded in `docs/n10-turn-row0-escape-self-edges.md`:

```text
[1, 3] > [1, 2]
[1, 3] > [2, 3]
[1, 4] > [1, 2]
[2, 4] > [2, 3]
```

## Interpretation

This is a useful packaging step for the turn route. In the first raw `n=10`
row0 slice, the candidate turn inequalities close almost all assignments, and
the vertex-circle row0 self-edge templates close exactly the four turn escapes.
That does not show the turn inequalities scale to `n=10`; it identifies the
small local vertex-circle ingredient needed for this one bounded row0 slice.

Safe claim:

```text
For the bounded n=10 row0-index-0 pilot, stored weak-turn Farkas certificates
plus the four stored row0-local vertex-circle self-edge escape templates form a
checked disjoint closure partition of the 160 recorded assignments.
```

Unsafe claim:

```text
The turn inequalities prove n=10.
```
