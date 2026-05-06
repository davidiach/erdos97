# n=9 Vertex-circle Motif Families

Status: `REVIEW_PENDING_DIAGNOSTIC`.

This note canonicalizes the 184 labelled `n=9` selected-witness assignments
that survive the non-vertex-circle filters. It does not claim a general proof
of Erdos Problem #97 and does not claim a counterexample. The official/global
status remains falsifiable/open.

## Dihedral Incidence Families

Under rotations and reflections of the cyclic labels, the 184 labelled
pre-vertex-circle assignments collapse to 16 full selected-witness incidence
families.

Checked counts:

```text
labelled assignments: 184
dihedral incidence families: 16
orbit sizes: 9 families of size 18, 2 families of size 6, 5 families of size 2
self-edge families: 13
strict-cycle families: 3
```

This is the main new information. Literal first-conflict certificates remain
too detailed to read as a theorem template, but the complete frontier is small
after cyclic symmetry.

The checked-in artifact is
`data/certificates/n9_vertex_circle_motif_families.json`.

The derived assignment-level classification
`data/certificates/n9_vertex_circle_frontier_motif_classification.json` makes
this join explicit for all 184 labelled assignments. For each assignment it
stores the full selected-row system, the deterministic dihedral map to the
canonical family representative, the local-core template id, and the compact
core rows transformed back into the assignment labels. The checker replays
both the full assignment and the transformed compact core. This is a
review-pending diagnostic classification, not an independent proof and not a
promotion of the n=9 finite-case status.

The self-edge equality-path join
`data/certificates/n9_vertex_circle_self_edge_path_join.json` then restricts
to the 158 self-edge assignments and stores the transformed equality path that
identifies the outer and inner chord distances in each labelled core. Its
checker verifies the source classification, the source local-core
certificates, the stored label maps, the transformed core rows, and the
replayed strict inequality. This is a review-pending diagnostic for lemma
mining only; the path join is not an independent proof of `n=9`.

The local-core follow-up in `docs/n9-vertex-circle-local-cores.md` shows that
each of the 16 family representatives has a vertex-circle certificate using at
most 6 selected rows. Its template diagnostic groups those 16 local cores into
12 replay-derived shape buckets: 9 self-edge templates and 3 strict-cycle
templates. These buckets are review aids for lemma mining; they are not an
independent n=9 proof path.

## Loose Obstruction Shapes

As a deliberately coarse diagnostic, the artifact also buckets the first
obstruction by label-free shape data:

- self-edge buckets record the number of shared endpoints in the strict
  inequality, the shortest selected-distance equality path length, and the
  outer/inner witness-interval spans;
- strict-cycle buckets record the cycle length and the multiset of
  outer/inner witness-interval spans around the cycle.

Those coarse buckets give 16 self-edge shape families and 8 strict-cycle span
families. These are proof-search hints only. They discard too much incidence
data to be certificates.

## Proof Implication

The next useful mathematical question is now sharper:

```text
Can each of the 16 dihedral incidence families be replaced by a reusable
local lemma, preferably one that also explains why the same obstruction
must appear beyond n=9?
```

A promising route is to classify the 13 self-edge families by the equality
path that brings an outer and inner vertex-circle chord into the same selected
distance class, and classify the 3 strict-cycle families by the directed
quotient-cycle template.

The local-core diagnostic reduces this to a row-local problem: the family
representatives need only 3 to 6 rows to certify the contradiction.
The template diagnostic is a first pass at that classification, but it only
records replay shapes for the listed n=9 representatives. Any reusable lemma
still needs precise incidence/order hypotheses and separate proof.

The current result still does not solve the global problem. The known
`C19_skew` order that survives the vertex-circle filter remains a useful
guardrail for vertex-circle-only lemmas, although the fixed abstract
`C19_skew` pattern is now killed by the separate Z3 Kalmanson certificate.
Any general lemma must either add hypotheses that exclude such vertex-circle
survivors or combine vertex-circle structure with an extra exact ingredient.

## Reproduction

Generate and check the motif-family artifact:

```bash
python scripts/analyze_n9_vertex_circle_motif_families.py \
  --assert-expected \
  --write
```

Generate and check the assignment-level motif classification:

```bash
python scripts/check_n9_vertex_circle_frontier_motif_classification.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_frontier_motif_classification.py \
  --check \
  --assert-expected \
  --json
```

Generate and check the self-edge equality-path join:

```bash
python scripts/check_n9_vertex_circle_self_edge_path_join.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_self_edge_path_join.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact test:

```bash
python -m pytest \
  tests/test_n9_vertex_circle_motif_families.py \
  tests/test_n9_vertex_circle_frontier_motif_classification.py \
  tests/test_n9_vertex_circle_self_edge_path_join.py \
  -q
```
