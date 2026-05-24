# Formalization alignment

## Existing formal statement

The Formal Conjectures repository contains
`FormalConjectures/ErdosProblems/97.lean`. It defines
`HasNEquidistantProperty 4` and states the open theorem using `ConvexIndep A`.

## Local Lean pilot

The local `lean/` directory is a proof-sketch pilot, not a formal proof of the
official problem. Its first layer is deliberately abstract:

- `lean/Erdos97/Basic.lean` defines a point-set selected-witness interface;
- `lean/Erdos97/SelectedWitness.lean` proves the choice-based extraction from
  that abstract interface;
- `lean/Erdos97/CertificateFormats.lean` records tiny certificate shapes for
  later Python-to-Lean kernels;
- `lean/Erdos97/Sketches/` contains AI-editable sketch shells marked with
  `-- EVOLVE-BLOCK-START` and `-- EVOLVE-BLOCK-END`.

Run the local guardrails with:

```bash
make verify-lean
```

If `lake` is not installed, this target still checks sketch integrity and
reports that Lean compilation was skipped. Use
`python scripts/check_lean_files.py --require-lean` when a Lean environment is
expected.

The missing bridge remains explicit: prove that the Formal Conjectures
`HasNEquidistantProperty 4` predicate implies the local
`HasFourEquidistantProperty` interface, then connect point-set witnesses to any
labelled cyclic-order certificate format.

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
