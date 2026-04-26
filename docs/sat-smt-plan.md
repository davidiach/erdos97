# SAT / SMT / ILP finite abstraction plan

## Base incidence SAT

Boolean variable:

```text
x[i,j] = 1 iff vertex j is selected by center i.
```

Necessary constraints:

```text
x[i,i] = 0
sum_j x[i,j] = 4                  for every i
sum_j (x[a,j] AND x[b,j]) <= 2    for every a != b
```

The last condition is the circle-intersection cap.

## What UNSAT proves

If only necessary constraints are used, UNSAT for a given `n` proves that no counterexample of that size exists at the incidence level.

## What UNSAT does not prove

UNSAT after adding balance, cyclic-spread, symmetry, or search-convenience constraints only rules out that restricted class. SAT gives only an incidence pattern, not a convex Euclidean realization.

## Next strengthening ideas

- Enumerate the `n=7` equality/Fano cases up to dihedral cyclic order.
- Add radical-axis perpendicularity templates for common selected pairs.
- Add order-type or oriented-matroid constraints only when they are proved necessary.
- Keep heuristic filters in a separate namespace from proved filters.
