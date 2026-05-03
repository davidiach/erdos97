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

The local-core follow-up in `docs/n9-vertex-circle-local-cores.md` shows that
each of the 16 family representatives has a vertex-circle certificate using at
most 6 selected rows.

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

The current result still does not solve the global problem. The known
`C19_skew` order that survives the vertex-circle filter remains the guardrail:
any general lemma must either add hypotheses that exclude that survivor or
combine vertex-circle structure with an extra exact ingredient.

## Reproduction

Generate and check the motif-family artifact:

```bash
python scripts/analyze_n9_vertex_circle_motif_families.py \
  --assert-expected \
  --write
```

Run the targeted artifact test:

```bash
python -m pytest tests/test_n9_vertex_circle_motif_families.py -q
```
