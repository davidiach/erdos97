# n=10 Row0 Escape Self-Edge Templates

Status: `FINITE_BOOKKEEPING_NOT_A_PROOF`.

This derived diagnostic isolates the four weak-turn SAT escapes from the
bounded `n=10` row0-index-0 turn pilot. It records only the first
vertex-circle self-edge template that kills each escape.

It is not a proof of `n=10`, not a complete `n=10` search, not a
counterexample, and not a source-of-truth status update.

## Artifact

```bash
data/certificates/n10_turn_row0_escape_self_edges.json
```

Regenerate and check it with:

```bash
python scripts/check_n10_turn_row0_escape_self_edges.py --write --assert-expected
python scripts/check_n10_turn_row0_escape_self_edges.py --check --assert-expected --json
```

The check command is registered in the scheduled/manual artifact audit runner
(`make audit-artifacts`).

## Summary

All four weak-turn SAT escapes have their first vertex-circle contradiction in
row `0`, with witness order `[1,2,3,4]`. In each case the equal-distance class
`[0,1]` is forced to be both the outer chord class and the inner chord class,
contradicting the strict chord inequality on a selected circle.

The four recorded row0 templates are:

- `[1, 3] > [1, 2]`
- `[1, 3] > [2, 3]`
- `[1, 4] > [1, 2]`
- `[2, 4] > [2, 3]`

This is useful as a compact target for a future local lemma combining weak
turn certificates with row-local vertex-circle self-edge templates.
