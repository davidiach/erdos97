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

The detailed checked-in artifact is
`data/certificates/n9_vertex_circle_local_cores.json`. A smaller reviewer
packet is also available at
`data/certificates/n9_vertex_circle_local_core_packet.json`; it stores only the
core selected rows for each family and is replayed by
`scripts/check_n9_vertex_circle_local_core_packet.py`.

The companion template diagnostic
`data/certificates/n9_vertex_circle_core_templates.json` groups the 16 compact
cores into 12 replay-derived shape buckets. The buckets record self-edge
conflict span/shared-endpoint shapes or strict-cycle span shapes, plus the
family ids covered by each bucket. These template ids are deterministic
artifact labels only; they are not theorem names and do not promote the n=9
finite-case status.

`data/certificates/n9_vertex_circle_frontier_motif_classification.json`
pushes the same local-core labels back down to all 184 labelled frontier
assignments. It stores each assignment's selected rows, its dihedral map to
the canonical family representative, and the compact core rows in the
assignment's original labels. The checker replays the transformed cores, so
the file is useful for reviewing the family classification without treating
template ids as theorem names.

`data/certificates/n9_vertex_circle_self_edge_path_join.json` adds a narrower
self-edge replay join for the 158 self-edge frontier assignments. It transforms
each family representative selected-distance equality path back into the
labelled assignment coordinates, preserves the dihedral map used for that
assignment, and replays the matching vertex-circle strict inequality from the
compact core rows. This is a lemma-mining and reviewer-navigation diagnostic
only; it is not an independent proof of `n=9` and does not promote the
exhaustive checker.

`data/certificates/n9_vertex_circle_strict_cycle_path_join.json` is the
parallel replay join for the 26 strict-cycle frontier assignments. It
transforms each family representative local-core cycle into labelled
assignment coordinates, checks each equality connector from a strict edge's
inner pair to the next strict edge's outer pair, and replays the transformed
strict edges from the compact core rows. Its cycle-length counts summarize the
transformed local-core certificates (`2: 18`, `3: 8`), not the first
full-assignment obstruction-shape cycles (`2: 22`, `3: 4`). This is also a
reviewer-navigation diagnostic only.

`data/certificates/n9_row_ptolemy_product_cancellations.json` contains a
dependent crosswalk from the row-Ptolemy hit families to these template labels:
`F02 -> T08`, `F09 -> T01`, and `F13 -> T04`. All three are self-edge
template families, and all strict-cycle template families remain no-hit
negative controls for the row-Ptolemy diagnostic. This is a consistency join
between artifacts, not an additional n=9 proof claim.

`data/certificates/n9_row_ptolemy_gap_self_edge_cores.json` applies the same
replay idea to the two zero-certificate row-Ptolemy admissible-order records.
It does not enumerate new n=9 cases; it compresses those two recorded `F13`
gap replays to minimal 3-row `self_edge` cores and stores the selected-distance
equality path responsible for each self-edge.

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

Generate and check the compact reviewer packet:

```bash
python scripts/check_n9_vertex_circle_local_core_packet.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_local_core_packet.py \
  --check \
  --assert-expected \
  --json
```

Generate and check the local-core template diagnostic:

```bash
python scripts/check_n9_vertex_circle_core_templates.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_core_templates.py \
  --check \
  --assert-expected \
  --json
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

Generate and check the strict-cycle path join:

```bash
python scripts/check_n9_vertex_circle_strict_cycle_path_join.py \
  --assert-expected \
  --write

python scripts/check_n9_vertex_circle_strict_cycle_path_join.py \
  --check \
  --assert-expected \
  --json
```

Run the targeted artifact test:

```bash
python -m pytest \
  tests/test_n9_vertex_circle_local_cores.py \
  tests/test_n9_vertex_circle_core_templates.py \
  tests/test_n9_vertex_circle_frontier_motif_classification.py \
  tests/test_n9_vertex_circle_self_edge_path_join.py \
  tests/test_n9_vertex_circle_strict_cycle_path_join.py \
  -q
```

Replay the 16 local quotient certificates with the small proof-facing kernel:

```bash
python scripts/replay_vertex_circle_quotient.py \
  data/certificates/n9_vertex_circle_local_cores.json \
  --assert-expected
```
