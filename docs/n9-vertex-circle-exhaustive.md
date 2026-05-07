# n=9 Vertex-circle Exhaustive Check

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`.

This note records a repo-native integration of an incoming n=9 finite-case
checker. It does not claim a general proof of Erdos Problem #97 and does not
claim a counterexample. The official/global status remains falsifiable/open.
The established source-of-truth local result remains the repo-local,
machine-checked selected-witness `n <= 8` artifact until the n=9 package gets
independent review.

## What is checked

The checker labels a hypothetical bad nonagon in cyclic order `0,...,8` and
enumerates selected-witness rows `S_i`, each a 4-subset of the other vertices.
It uses only exact necessary conditions:

- two selected rows share at most two witnesses;
- if two selected rows share exactly two witnesses, the source chord and witness
  chord cross in the cyclic order;
- each witness pair appears in at most two selected rows;
- each target vertex has selected indegree at most
  `floor(2*(9-1)/(4-1)) = 5`;
- vertex-circle strict chord monotonicity creates no self-edge or strict
  directed cycle after quotienting by selected-distance equalities.

The vertex-circle step is the same geometric idea recorded in
`docs/vertex-circle-order-filter.md`: around a fixed center, nested witness
chords on the selected circle force strict inequalities between ordinary
distances. A self-edge or directed cycle of strict inequalities is impossible.

## Reproduced counts

The checked-in artifact is `data/certificates/n9_vertex_circle_exhaustive.json`.
It records stable counts, not elapsed timings:

```text
main search with vertex-circle pruning:
  row0 choices: 70
  nodes visited: 16752
  full assignments surviving all filters: 0
  partial self-edge prunes: 11271
  partial strict-cycle prunes: 11011

cross-check without vertex-circle pruning:
  row0 choices: 70
  nodes visited: 100817
  full assignments passing pair/crossing/count filters: 184
  vertex-circle status: 158 self-edge, 26 strict-cycle
```

The cross-check is important because it separates the earlier incidence/order
filters from the vertex-circle filter: 184 complete selected-witness systems
survive before vertex-circle reasoning, and every one is killed by an exact
vertex-circle obstruction.

The companion diagnostic `docs/n9-vertex-circle-obstruction-shapes.md` mines
those 184 obstructions. It finds 158 self-edge contradictions and 26 strict
directed cycles; every strict cycle has length 2 or 3. That diagnostic is meant
to guide a possible general lemma, not to strengthen the repo claim by itself.

Later review aids make the local quotient certificates easier to inspect:
`data/certificates/n9_vertex_circle_frontier_motif_classification.json`
classifies all 184 labelled assignments by motif family and local-core
template, while
`data/certificates/n9_vertex_circle_self_edge_path_join.json` transforms the
family representative equality paths back into each of the 158 labelled
self-edge assignments.
`data/certificates/n9_vertex_circle_self_edge_template_packet.json` compresses
those self-edge joins to 9 template-level reviewer records with canonical
family certificates.
`data/certificates/n9_vertex_circle_strict_cycle_path_join.json` similarly
transforms the strict-cycle local-core certificates back into each of the 26
strict-cycle assignments. Its local-core cycle-length counts (`2: 18`,
`3: 8`) are distinct from the first full-assignment obstruction-shape counts
(`2: 22`, `3: 4`). All of these are review-pending diagnostics only, not
independent proofs and not status promotions.

## Commands

Run the stable checker and assert the expected counts:

```bash
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected
```

Regenerate the JSON artifact:

```bash
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --write
```

Run the targeted test:

```bash
python -m pytest tests/test_n9_vertex_circle_exhaustive.py -q
```

The raw incoming bundle is preserved under
`incoming/archive-output-2026-05-03/`. That folder includes two additional n=9
Kalmanson verifier variants with different symmetry/count conventions, plus a
later external batch summarized in
`data/certificates/n9_late_archive_provenance.json`. Those are useful audit
material, but they are not the canonical repo check introduced here.

## Later archive cross-checks

A later external batch added two corroborating n=9 stories:

- a sequential row-order vertex-circle checker, locally rerun with
  `--assert-closed`, closes all 70 row0 choices with 37,614 visited nodes,
  2,628,150 row options considered, and zero full patterns reached;
- a row0-reflection-quotient certificate bundle reports 38 canonical row0
  classes, 102 full patterns, and classifications into 70 Kalmanson/Farkas
  certificates, 21 phi4 rectangle traps, and 11 odd forced-perpendicularity
  cycles, with no accepted frontier.

The zip bundle's embedded verifier was not executed during integration because
it is unreviewed external code. Its static JSON summaries and hashes are
recorded only as review-pending provenance; the verifier should be ported or
reviewed in-repo before those counts become a canonical check.

## Review standard

Before promoting this to the same source-of-truth status as the `n <= 8`
artifact, an independent review should check:

- the geometric necessity of every pruning rule;
- that the dynamic minimum-remaining-options row order does not omit cases;
- that row0 is not quotienting by a hidden symmetry in the exhaustive run;
- that the vertex-circle partial pruning is applied only from completed selected
  rows and selected-distance equalities that are already fixed;
- that the raw 184/16 and 102-certificate archive variants agree with the
  repo-native checker once their symmetry conventions are made explicit.
- that the sequential vertex-circle script and row0-quotient bundle in the
  late archive are independent enough to count as corroboration rather than
  just differently packaged output from the same search.
- that the obstruction-shape diagnostic really reflects reusable templates
  rather than artifacts of the first conflict selected by the miner.
