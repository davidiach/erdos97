# Formalization alignment

## Existing formal statement

The Formal Conjectures repository contains
`FormalConjectures/ErdosProblems/97.lean`. It defines
`HasNEquidistantProperty 4` and states the open theorem using `ConvexIndep A`.

## Local mathematical convention

This repository often uses the language of a strictly convex polygon with
cyclically ordered vertices. When comparing with Lean, clarify the relationship
between:

- strict convex polygon / cyclic order;
- finite point set in convex independent position;
- `ConvexIndep A`;
- selected-witness 4-sets `S_i`.

## Near-term formalization targets

Do not start by formalizing the entire open problem. Start with local finite
and geometric lemmas:

1. Two-circle intersection cap: if two distinct circles share at least three
   points, contradiction.
2. Pair-sharing cap: for distinct centers `a,b`, `|S_a cap S_b| <= 2`.
3. Incidence count ruling out `n <= 6`.
4. `n=7` Fano/parity obstruction, if feasible.
5. Certificate checker for `n=8` survivor obstruction.

## Longer-term targets

- A Lean-readable certificate format for finite incidence patterns.
- A verified checker for perpendicularity/equal-distance obstruction steps.
- A bridge from local selected-witness artifacts to the Lean
  `HasNEquidistantProperty 4` statement.

## Non-goals

- Do not claim a Lean proof of #97.
- Do not mark the problem solved because the statement is formalized.
- Do not merge informal numerical evidence into formal theorem claims.
