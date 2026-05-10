# Relation-skeleton Catalog

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records a first narrow relation-skeleton extraction for proof
mining. It does not claim a proof of `n=9`, does not claim a counterexample,
does not complete independent review of the exhaustive checker, and does not
update the official/global status of Erdos Problem #97.

## Scope

The checked artifact is
`data/certificates/relation_skeleton_catalog.json`. It currently contains two
vertex-circle selected-distance quotient skeletons extracted from focused
local lemma packets:

```text
VC-T01-F09-strict-self-edge
VC-T10-F12-strict-directed-cycle
```

This is intentionally smaller than the full 12-template `n=9` catalog. The
goal is to give reviewers a reusable object shape before adding Kalmanson,
row-Ptolemy, or additional vertex-circle templates.

## Skeleton Fields

Each skeleton separates:

```text
hypotheses:
    cyclic order
    selected rows
    minimal local hypotheses
relation_quotient:
    selected-distance equality steps
    equality chains among ordinary pair distances
    strict edges from vertex-circle chord monotonicity
conclusion:
    strict self-edge or directed strict cycle in the quotient graph
coverage:
    source template/family and assignment ids
guardrails:
    what the skeleton does not prove
```

The common relation-skeleton object is deliberately about quotient relations,
not coordinates. It records which ordinary pair distances are identified by
selected rows and which strict inequalities are forced by the cyclic
vertex-circle order.

## Current Entries

### T01/F09 Self-edge

The three selected rows

```text
0: {1,2,4,8}
1: {0,3,5,8}
2: {0,1,4,6}
```

force the equality chain

```text
[1,8] = [0,1] = [0,2] = [1,2].
```

The row-0 vertex-circle order `[1,2,4,8]` gives the strict inequality

```text
[1,8] > [1,2].
```

Thus the selected-distance quotient strict graph has a strict self-edge.

### T10/F12 Strict Cycle

The four selected rows

```text
0: {1,2,5,6}
3: {0,1,4,6}
6: {1,3,4,7}
8: {0,3,6,7}
```

force the quotient cycle

```text
[0,6] > [0,3] = [3,6] = [1,6]
[1,6] > [0,1] = [0,6].
```

Thus the selected-distance quotient strict graph has a directed strict cycle
of length two.

## Commands

Generate and check the catalog:

```bash
python scripts/check_relation_skeleton_catalog.py \
  --assert-expected \
  --write

python scripts/check_relation_skeleton_catalog.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact tests:

```bash
python -m pytest tests/test_relation_skeleton_catalog.py -q -m "artifact"
```

## Review Standard

A reviewer should be able to restate each skeleton as a local lemma without
using `T01`, `T10`, `F09`, or `F12` as theorem names. The proof obligation is
to check that the listed selected rows force the displayed quotient equalities
and that the listed vertex-circle order forces the displayed strict edge or
cycle.

This catalog is a proof-mining aid. It is not an independent proof of the
`n=9` finite case, not a global theorem, and not evidence for a counterexample.
