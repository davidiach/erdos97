# Relation-skeleton Catalog

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records a focused relation-skeleton extraction for proof mining. It
does not claim a proof of `n=9`, does not claim a counterexample,
does not complete independent review of the exhaustive checker, and does not
update the official/global status of Erdos Problem #97.

## Scope

The checked artifact is
`data/certificates/relation_skeleton_catalog.json`. It currently contains
sixteen vertex-circle selected-distance quotient skeletons extracted from the
focused local lemma packets:

```text
VC-T01-F09-strict-self-edge
VC-T02-F01-strict-self-edge
VC-T02-F04-strict-self-edge
VC-T02-F08-strict-self-edge
VC-T02-F14-strict-self-edge
VC-T03-F05-strict-self-edge
VC-T03-F15-strict-self-edge
VC-T04-F13-strict-self-edge
VC-T05-F10-strict-self-edge
VC-T06-F11-strict-self-edge
VC-T07-F06-strict-self-edge
VC-T08-F02-strict-self-edge
VC-T09-F03-strict-self-edge
VC-T10-F12-strict-directed-cycle
VC-T11-F07-strict-directed-cycle
VC-T12-F16-strict-directed-cycle
```

This matches the family-level coverage of the stored aggregate local-lemma
packet layer: 13 strict self-edge families and 3 strict-cycle families, covering
184 labelled pre-vertex-circle frontier assignments in that review-pending
packet accounting. It is still a proof-mining catalog, not an independent
review of that packet layer or the exhaustive `n=9` checker.

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

### T02 Shared-endpoint Self-edges

The T02 packet contributes four shared-endpoint self-edge skeletons:

```text
F01: [1,8] = [0,8] = [0,1] = [1,2]
F04: [0,2] = [0,1] = [1,2] = [2,3]
F08: [1,8] = [0,8] = [0,1] = [1,2]
F14: [1,8] = [0,8] = [0,1] = [1,2]
```

Each skeleton records one vertex-circle strict edge whose outer and inner
ordinary pair distances are identified by the displayed selected-distance
chain, producing a reflexive strict edge in the quotient graph.

### T03/F05 And T03/F15 Self-edges

The two T03 family packets are recorded as separate skeletons because their
local rows and equality chains differ. Both have four selected rows and one
vertex-circle strict edge whose endpoints are identified by a length-3
selected-distance path.

The skeletons record the equality chains:

```text
F05: [3,7] = [2,3] = [1,2] = [1,7]
F15: [1,4] = [1,2] = [2,3] = [3,4]
```

In each case the listed vertex-circle strict edge returns to the same quotient
class, giving a strict self-edge.

### T04/F13 Self-edge

The T04/F13 local core is recorded as:

```text
0: {1,2,5,7}
1: {2,3,6,8}
3: {1,4,5,8}
5: {1,3,6,7}
```

The selected-distance path gives:

```text
[1,5] = [3,5] = [1,3] = [1,2]
```

Row `0` has witness order `[1,2,5,7]`, so vertex-circle monotonicity gives
`[1,5] > [1,2]`. Thus the quotient graph has a strict self-edge.

### T05-T09 Selected-path Self-edges

The T05 through T09 packets add five more selected-path self-edge skeletons:

```text
T05/F10: [1,8] = [7,8] = [2,7] = [1,2]
T06/F11: [3,8] = [6,8] = [6,7] = [5,7] = [3,5]
T07/F06: [1,4] = [4,5] = [5,6] = [2,6] = [1,2]
T08/F02: [1,3] = [1,7] = [6,7] = [5,6] = [2,5] = [1,2]
T09/F03: [1,3] = [0,1] = [0,8] = [4,8] = [3,4] = [2,3] = [1,2]
```

As with T03 and T04, each selected path identifies the endpoints of a stored
vertex-circle strict inequality, yielding a strict self-edge after quotienting.

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

### T11/F07 And T12/F16 Strict Cycles

The T11 and T12 skeletons record three-edge directed strict cycles. They are
the same local arguments as the focused lemma notes, normalized into the common
relation-skeleton schema:

```text
T11/F07: [0,2] > [0,3] > [5,7] > [0,2]
T12/F16: [0,3] > [2,8] > [1,7] > [0,3]
```

The skeleton entries keep the selected rows, equality chains, strict
vertex-circle edges, and quotient-cycle steps separate so a reviewer can check
the local lemma without reading the exhaustive `n=9` brancher.

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

Cross-check the catalog against the aggregate local-lemma scan and the simple
packet replay:

```bash
python scripts/check_relation_skeleton_local_lemma_crosswalk.py --check --assert-expected --json
```

Cross-check the same catalog against the closed-descent reformulation of the
stored local-core quotient obstructions:

```bash
python scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py --check --assert-expected --json
```

This crosswalk is an accounting audit. It checks that the 16 relation
skeletons and the local-lemma replay chain agree family by family on template
ids, family ids, obstruction kind, and assignment counts. It does not certify
that the local-lemma packets are complete for `n=9`, and it does not review the
exhaustive brancher.

The closed-descent crosswalk is another accounting audit. It checks that the 13
strict self-edge skeletons map to one-class descent regions and that the 3
strict directed-cycle skeletons map to multi-class descent regions, with the
same `184` assignment/orbit total. It is packet bookkeeping only, not
local-lemma completeness, a bridge proof, or an `n=9` proof.

## Review Standard

A reviewer should be able to restate each skeleton as a local lemma without
using template or family ids as theorem names. The proof obligation is to check
that the listed selected rows force the displayed quotient equalities and that
the listed vertex-circle order forces the displayed strict edge or cycle.

This catalog is a proof-mining aid. It is not an independent proof of the
`n=9` finite case, not a global theorem, and not evidence for a counterexample.
