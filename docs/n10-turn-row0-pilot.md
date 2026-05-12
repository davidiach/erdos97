# n=10 Turn Row0 Pilot

Status: `FINITE_BOOKKEEPING_NOT_A_PROOF`.

This bounded pilot tests the candidate turn inequalities on the first raw
`n=10` row0 slice, before vertex-circle pruning. It is not a proof of `n=10`,
not a counterexample, not a completeness result, and not a source-of-truth
status update.

## Scope

The pilot fixes row0 choice index `0` in the natural cyclic order and enumerates
all full assignments satisfying the pair/crossing/count filters for that slice.
It then checks the candidate weak turn inequalities and the existing
vertex-circle filter.

Artifact:

```bash
data/certificates/n10_turn_row0_pilot.json
```

Commands:

```bash
python scripts/check_n10_turn_row0_pilot.py --assert-expected --write
python scripts/check_n10_turn_row0_pilot.py --check --assert-expected --json
```

## Result

The row0-index-0 slice has:

- raw full assignments: `160`;
- assignment SHA-256:
  `ec0fa48ec4db8a4a133bffbd86647ade7f33444a1ccb7eea098aae04df4d42b7`;
- turn Farkas/dual certificate kills: `156`;
- weak-turn SAT escapes: `4`;
- vertex-circle status: all `160` are `self_edge`;
- turn-certificate SHA-256:
  `c55eb78466233cc7c9c379ffd1d8d555304349e4bc4eaf588c79be5638ee4a55`.

The four weak-turn escapes are assignments `74`, `103`, `156`, and `157` in
the stored row0 slice. All four are killed already in row `0`, whose witness
order is `[1,2,3,4]`; the first stored self-edge conflict always identifies
the outer and inner distance classes as `[0,1]`. This is a compact target for a
row0-local vertex-circle self-edge template.

## Interpretation

This is useful negative information about the turn route. The turn inequalities
kill most assignments in this bounded `n=10` slice, but they do not close the
slice by themselves: four assignments satisfy the weak turn system. Those four
are still killed by the existing vertex-circle self-edge filter.

So the next proof-facing move should not be "turn inequalities alone scale to
`n=10`." A realistic next step is to combine turn certificates with a compact
vertex-circle self-edge template, or to mine the four weak-turn escapes for a
small reusable obstruction.
