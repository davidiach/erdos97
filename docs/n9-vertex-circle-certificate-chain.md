# n=9 Vertex-circle Certificate-chain Reduction

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note states the exact bridge contract currently supplied by the
`n=9` vertex-circle artifacts. It does not claim a proof of `n=9`, does not
claim a counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global status.

## Reduction

Let `U` be the set of labelled full selected-witness assignments in the
review-pending `n=9` pre-vertex-circle frontier. The certificate chain is the
following sequence of finite artifacts:

1. `data/certificates/n9_vertex_circle_frontier_motif_classification.json`
   assigns each element of `U` to a dihedral family, local template id, and
   obstruction status.
2. `data/certificates/n9_vertex_circle_self_edge_path_join.json` replays the
   selected-distance equality path and strict edge for the self-edge part.
3. `data/certificates/n9_vertex_circle_strict_cycle_path_join.json` replays
   the selected-distance equality connectors and strict cycle for the
   strict-cycle part.
4. `data/certificates/n9_vertex_circle_template_lemma_catalog.json` groups the
   same assignments into 12 local template buckets.

If the exhaustive frontier source and these checked joins are accepted, then
every assignment in `U` contains one of the recorded local quotient-graph
obstructions: either a selected-path self-edge or a directed strict cycle.

This is a reduction of review work, not an independent theorem. The separate
work still required is to audit the exhaustive frontier source and to verify
the local selected-row equality connectors and vertex-circle strict edges used
inside each template.

## Exact Chain Audit

A one-off JSON partition audit checked the assignment-id universe across the
classification, path joins, and template catalog.

```text
classification assignment ids unique: true
classification assignments:          184
classification families:              16
classification templates:             12
classification status counts:         self_edge=158, strict_cycle=26
self path join matches self subset:   true
strict path join matches strict subset:true
self/strict subsets disjoint:         true
self/strict union equals frontier:    true
catalog assignment ids unique:        true
catalog ids match classification:     true
audit digest: 62a4ef4da2fdd57b57efe5276791aafe7ed494b84b6e1c49b06205223351fc51
```

The template assignment counts are:

```text
T01:  6
T02: 40
T03: 20
T04:  2
T05: 18
T06: 18
T07: 18
T08: 18
T09: 18
T10: 18
T11:  6
T12:  2
```

Thus the current checked chain has no duplicate catalog assignment ids and no
assignment id lost between the classification, the two path joins, and the
template catalog.

## Relation To The Two Local Criteria

The final real-number contradictions are recorded separately:

- `docs/n9-vertex-circle-self-edge-criterion.md` covers templates `T01`
  through `T09`.
- `docs/n9-vertex-circle-strict-cycle-criterion.md` covers templates `T10`
  through `T12`.

The certificate-chain reduction supplies the assignment-to-template bridge for
the current artifacts. The two criterion pages supply the final local
contradiction once a reviewer accepts the corresponding selected-distance
equality paths and vertex-circle strict edges.

## Review Standard

To promote this reduction into a finite-case proof component, a reviewer would
need to check two independent inputs.

First, the exhaustive checker must be accepted as enumerating exactly the
`n=9` pre-vertex-circle frontier, with no hidden loss from symmetry choices,
branch ordering, or pruning assumptions.

Second, each local template witness must be checked without relying on the
template id as a theorem name: selected rows must force the displayed equality
paths, and vertex-circle witness orders must force the displayed strict
edges.

Only after both inputs are accepted may the assignment-id partition be used as
a finite bridge from exhaustive assignments to local quotient-graph
contradictions.

## Commands

Check the relevant artifact chain:

```bash
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected

python scripts/check_n9_vertex_circle_frontier_motif_classification.py \
  --check \
  --assert-expected \
  --json

python scripts/check_n9_vertex_circle_self_edge_path_join.py \
  --check \
  --assert-expected \
  --json

python scripts/check_n9_vertex_circle_strict_cycle_path_join.py \
  --check \
  --assert-expected \
  --json

python scripts/check_n9_vertex_circle_template_lemma_catalog.py \
  --check \
  --assert-expected \
  --json
```
