# Fragile hypergraph follow-up, 2026-04-28

Status: research artifact only. This does not prove or disprove Erdos #97.

## Main conclusion

After the fragile-cover lemma is repaired, the deletion-critical witness map
does not add a new independent constraint. If a fragile row S_u covers v, then
deleting v already makes u non-bad: the unique four-cohort of u drops to size
three, and there is no other rich radius for u.

Thus a witness map is just a choice of one covering fragile center for each
vertex.

## Consequence

The current second-stage axioms are too weak by themselves. There are abstract
covering pointed 4-uniform hypergraphs satisfying:

- self-exclusion;
- cover;
- pairwise intersection at most two;
- the two-overlap cyclic crossing rule;
- a valid witness map.

The new `block6` family gives examples for every n divisible by 6. In each
six-vertex block b,...,b+5, use fragile centers b and b+3 with rows

```text
b   -> {b+1,b+2,b+3,b+4}
b+3 -> {b,b+2,b+4,b+5}
```

The two rows share {b+2,b+4}; the center pair {b,b+3} separates that shared
pair in cyclic order. Different blocks are disjoint.

## Added tooling

`src/erdos97/fragile_hypergraph.py` checks the fragile-cover hypergraph layer.
`scripts/check_fragile_hypergraph.py` emits or verifies the block-6 family.

Passing this checker is not a geometric realization certificate. Its purpose is
to show that the fragile-cover route needs a stronger metric or cyclic
constraint beyond the currently isolated hypergraph axioms.

## Next target

Look for an additional condition that uses the fact that fragile centers are
part of a full minimal bad polygon, not just an abstract cover. Good candidates:

1. constraints involving non-fragile centers and their selected cohorts;
2. a stronger cyclic rule for disjoint or one-overlap fragile cohorts;
3. metric inequalities involving two fragile centers in the same block-like
   component;
4. exact finite enumeration of fragile covers plus full selected rows for
   small n.
