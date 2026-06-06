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
- `lean/Erdos97/OfficialBridge.lean` proves the first dependency-free adapter:
  official-shaped four-point radius fibers imply the local
  `HasFourEquidistantProperty` interface;
- `lean/Erdos97/CertificateFormats.lean` records tiny certificate shapes for
  later Python-to-Lean kernels;
- `lean/Erdos97/TurnPacking.lean` records the formalization-facing contract for
  the review-pending turn-packing route: forward/reverse weak interval supports
  and the elementary dual-certificate arithmetic kernel;
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

The remaining upstream bridge is explicit: prove that the Formal Conjectures
`HasNEquidistantProperty 4` predicate yields the
`HasFourPointFiberWitnesses` row data in `OfficialBridge.lean`, by unpacking
the finite filter/cardinality assertion. Then connect point-set witnesses to
any labelled cyclic-order certificate format.

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

1. Exterior-turn inequality bridge: instantiate the abstract
   `TurnLemmaForcesWeakIntervals` contract in `lean/Erdos97/TurnPacking.lean`
   from a real Euclidean strict-convex polygon model, matching
   `docs/turn-inequality-lemma.md`.
2. Two-circle intersection cap: if two distinct circles share at least three
   points, contradiction.
3. Pair-sharing cap: for distinct centers `a,b`, `|S_a cap S_b| <= 2`.
4. Incidence count ruling out `n <= 6`.
5. `n=7` Fano/parity obstruction, if feasible.
6. Certificate checker for `n=8` survivor obstruction.

## Longer-term targets

- A Lean-readable certificate format for finite incidence patterns.
- A Lean-readable turn-packing certificate format connected to the Python
  `n9_turn_inequality_frontier` integer dual records.
- A verified checker for perpendicularity/equal-distance obstruction steps.
- A bridge from local selected-witness artifacts to the Lean
  `HasNEquidistantProperty 4` statement.

## Non-goals

- Do not claim a Lean proof of #97.
- Do not mark the problem solved because the statement is formalized.
- Do not merge informal numerical evidence into formal theorem claims.
