# n=9 Vertex-circle Local Cores

Status: `REVIEW_PENDING_DIAGNOSTIC`.

This note records local row-core certificates for the 16 dihedral
selected-witness motif families in the `n=9` vertex-circle frontier. It does
not claim a general proof of Erdos Problem #97 and does not claim a
counterexample. The official/global status remains falsifiable/open.

## Core Counts

Each of the 16 motif-family representatives has a local vertex-circle
certificate using at most 6 selected rows.

Checked counts:

```text
local core size counts:
  3 rows: 5 families
  4 rows: 6 families
  5 rows: 2 families
  6 rows: 3 families

self-edge cores:
  3 rows: 5 families
  4 rows: 4 families
  5 rows: 2 families
  6 rows: 2 families

strict-cycle cores:
  4 rows: 2 families
  6 rows: 1 family
```

The checked-in artifact is
`data/certificates/n9_vertex_circle_local_cores.json`.

## Certificate Shape

A self-edge core consists of:

- one strict vertex-circle chord-containment inequality
  `outer chord > inner chord`;
- a selected-distance equality path showing that the outer and inner chord
  lengths lie in the same selected-distance class.

Together these give `d > d`, an immediate contradiction.

A strict-cycle core consists of:

- a directed cycle of strict vertex-circle inequalities;
- selected-distance equality paths connecting each inner chord to the next
  outer chord in the cycle.

Together these give a strict chain returning to its starting distance class.

## Why This Is Progress

The n=9 frontier no longer looks like 184 unrelated assignments. It now looks
like 16 symmetry families, each with a row-local proof core of size at most 6.
That is close to the right granularity for human lemmas:

```text
If a selected-witness incidence pattern contains one of these local row-core
motifs in the recorded cyclic order, then it is impossible.
```

This is still not a solution. The next question is whether those local cores
are forced by general incidence and cyclic-order constraints, or whether they
are special to the n=9 enumeration.

The comparison in `docs/n9-vertex-circle-frontier-comparison.md` shows the
caution needed here: the n=9 cores do not embed exactly into the recorded P18
or C19 patterns. P18 is killed by a related loose strict-cycle shape, while the
recorded C19 order still passes the vertex-circle filter.

## Reproduction

Generate and check the local-core artifact:

```bash
python scripts/analyze_n9_vertex_circle_local_cores.py \
  --assert-expected \
  --write
```

Run the targeted artifact test:

```bash
python -m pytest tests/test_n9_vertex_circle_local_cores.py -q
```
