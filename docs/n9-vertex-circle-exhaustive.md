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
For a broader dependency map from a hypothetical bad nonagon to the 184
frontier and the current obstruction routes, see `docs/n9-reduction-chain.md`.

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
(`2: 22`, `3: 4`).
`data/certificates/n9_vertex_circle_strict_cycle_template_packet.json`
compresses those strict-cycle joins to 3 template-level reviewer records with
canonical family cycles.
`data/certificates/n9_vertex_circle_local_core_packet.json` keeps one compact
row-local certificate for each of the 16 motif representatives, and the
local-core subset audit checks that those compact rows are exact subsets of
the full representatives and already force the same obstruction.
`data/certificates/n9_vertex_circle_template_lemma_catalog.json` combines the
9 self-edge templates and 3 strict-cycle templates into one derived
lemma-candidate crosswalk for proof mining. All of these are review-pending
diagnostics only, not independent proofs and not status promotions.
The focused packet catalog audit
`scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py --check --assert-expected --summary-json`
checks that the 12 focused packet JSON files, the source template packets, the
template catalog, and the aggregate local-lemma focused-note ledger agree on
packet coverage. This is bookkeeping only, not packet soundness or an `n=9`
proof.
The focused mini-replay crosswalk
`scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py --check --assert-expected --summary-json`
then joins those focused packets to their 12 packet-specific mini-replay
artifacts, checking identity, families, source schemas, obstruction flags, and
compact local shape counts only.

The audit command
`scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py` checks the
stored accounting chain from this exhaustive artifact to the motif
classification and then to the aggregate/simple local-lemma replay artifacts:

```bash
python scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py --check --assert-expected --json
```

This command does not rerun or independently review the exhaustive brancher.
It verifies only that the checked-in artifacts agree on the same
review-pending `184 = 158 + 26` frontier accounting and the same 16 motif
families.

The combined local-lemma audit-path command
`scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --json`
checks the focused packet/catalog, focused mini-replay, aggregate/simple
replay, exhaustive/local-lemma, and relation-skeleton/local-lemma handoffs as
one review-pending diagnostic chain. It is still bookkeeping only, not packet
soundness or an `n=9` proof.

The input-data audit command
`scripts/check_n9_vertex_circle_input_audit.py` treats the checked-in
exhaustive JSON as stored data:

```bash
python scripts/check_n9_vertex_circle_input_audit.py --check --assert-expected --json
```

It recomputes the row-0 choices directly as the 70 lexicographic 4-subsets of
labels `1..8`, checks the stored witness lists and masks, and verifies the
summary count arithmetic and no-overclaiming scope. It does not rerun the
brancher, replay vertex-circle certificates, prove `n=9`, or complete the
independent review.

The incidence-filter audit command checks the row-level two-overlap crossing,
witness-pair cap, and selected-indegree cap tables:

```bash
python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --json
```

It recomputes the finite row-pair and row-mask predicates directly and compares
them with the checker tables. It is a row-level filter audit only, not a
brancher replay, strict-edge geometry audit, or quotient-soundness audit.

The branch-option audit command checks the branch helper against a direct
implementation on fixed-order no-vertex-circle search states:

```bash
python scripts/check_n9_vertex_circle_branch_options.py --check --assert-expected --json
```

It walks 520,598 nonterminal option contexts, compares
`valid_options_for_center` with direct row-pair crossing, witness-pair
capacity, and selected-indegree predicates, and also compares maintained count
arrays with direct recomputation. This is branch-option implementation
diagnostics only, not dynamic-MRO branch coverage, strict-edge geometry,
quotient soundness, or a completed `n=9` review.

The dynamic-MRO choice audit command checks the actual dynamic branch choice:

```bash
python scripts/check_n9_vertex_circle_dynamic_mro_choices.py --check --assert-expected --json
```

It replays the vertex-circle-pruned search and the no-vertex-circle
cross-check, recomputes every unassigned center's option list with a direct
predicate at every reached state, and checks first-minimum tie breaking. It
records zero center-choice mismatches, zero helper/direct option mismatches,
and zero maintained-count mismatches. This is dynamic branch-choice
implementation diagnostics only, not filter soundness, strict-edge geometry,
quotient soundness, or a completed `n=9` review.

The frontier-coverage crosswalk command compares regenerated dynamic frontier
rows against the stored motif-classification artifact:

```bash
python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check --assert-expected --json
```

It reruns the dynamic no-vertex-circle brancher, collects the 184 complete
selected-row assignments, and checks that the generated row sequence, row set,
and vertex-circle status labels match the stored frontier classification. This
is stored-frontier coverage bookkeeping against the current brancher, not
filter soundness, strict-edge geometry, quotient soundness, or a completed
`n=9` review.

The compact independent brancher command gives a smaller second audit path:

```bash
python scripts/check_n9_vertex_circle_compact_brancher.py --check --assert-expected --json
```

It does not import the project n=9 brancher modules and does not read the
stored 184-assignment frontier artifact. It regenerates the same sorted
frontier row-set digest, `dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55`,
and replays `158` self-edge plus `26` strict-cycle vertex-circle quotient
obstructions. This is independent audit evidence only, not completed review of
the n=9 finite case.

The mixed-rich/frontier crosswalk checks that the newer four/five support
catalogue lands on this same exact-four frontier:

```bash
python scripts/check_n9_mixed_rich_frontier_crosswalk.py --check --assert-expected --json
```

It reruns the mixed support search and compares its `184` all-exact-four
terminal assignments with the stored motif-classification rows as a labelled
set. The brancher sequences differ in six positions, but the sorted row-set
digest matches. This is support-to-frontier bookkeeping only, not a proof of
the mixed support reduction, filter soundness, strict-edge geometry, quotient
soundness, or a completed `n=9` review.

The dihedral-orbit audit command checks stored motif-family orbit bookkeeping:

```bash
python scripts/check_n9_vertex_circle_dihedral_orbit_audit.py --check --assert-expected --json
```

It independently enumerates the 18 dihedral relabelings of the stored 16
motif representatives, checks canonical representatives and orbit sizes, and
verifies that the stored frontier-classification rows match the disjoint orbit
union with stable canonical label maps. This is orbit bookkeeping only, not
frontier coverage, filter soundness, strict-edge geometry, quotient soundness,
or a completed `n=9` review.

The motif-obstruction audit command checks the stored representative
certificates for those 16 motif families:

```bash
python scripts/check_n9_vertex_circle_motif_obstruction_audit.py --check --assert-expected --json
```

It recomputes the selected-distance quotient classes and vertex-circle
strict interval inequalities with a small local implementation, then verifies
each stored self-edge equality path or strict-cycle edge chain. This is
stored-certificate bookkeeping only, not frontier coverage, brancher
soundness, incidence-filter soundness, dihedral orbit bookkeeping, or a
completed `n=9` review.

The local-core subset audit command checks the compact local cores against the
full motif representatives:

```bash
python scripts/check_n9_vertex_circle_local_core_subset_audit.py --check --assert-expected --json
```

It verifies that every compact local-core row is copied from the corresponding
full motif representative and that the compact row set alone gives the stored
self-edge or strict-cycle status under a direct quotient replay. This is
cross-artifact bookkeeping only, not local-lemma completeness or a completed
`n=9` review.

The frontier-assignment audit command checks the stored 184 frontier rows
directly against the base incidence/order filters:

```bash
python scripts/check_n9_vertex_circle_frontier_assignment_audit.py --check --assert-expected --json
```

It verifies row shape, center coverage, pairwise row-intersection cap,
two-overlap crossing, witness-pair capacity, and selected-indegree capacity on
the stored frontier assignments. This is stored-frontier diagnostics only, not
frontier coverage, brancher soundness, strict-edge geometry, quotient
soundness, or a completed `n=9` review.

The MRO branching replay command checks a separate fixed center order against
the stored dynamic minimum-remaining-options artifact:

```bash
python scripts/check_n9_vertex_circle_mro_branching_replay.py --check --assert-expected --json
```

It closes the fixed-order vertex-circle-pruned search and reaches the same
`184 = 158 + 26` no-vertex-circle frontier classification. It is a
branch-order audit only, not a proof of the filters or a completed `n=9`
review.

The strict-edge geometry audit command checks the local vertex-circle
inequality generator:

```bash
python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --json
```

It independently enumerates proper interval containments for all 630 candidate
selected rows and compares them with the checker strict-edge table. This is a
local geometry-rule audit only, not selected-distance quotient or exhaustive
coverage review.

The quotient-soundness audit command checks selected-distance quotient status
agreement on the stored local-core and frontier rows:

```bash
python scripts/check_n9_vertex_circle_quotient_soundness.py --check --assert-expected --json
```

It compares the exhaustive checker, the reusable quotient replay helper, and a
small direct quotient/status replay. This is implementation agreement only, not
branch coverage, strict-edge geometry, or a completed `n=9` review.

The partial-pruning audit command checks stored-frontier row subsets:

```bash
python scripts/check_n9_vertex_circle_partial_pruning.py --check --assert-expected --json
```

It scans all 94,024 nonempty row subsets from the 184 stored frontier
assignments, checks that every obstructed subset extends only to a stored full
assignment that remains obstructed, and compares checker status with the
reusable quotient replay. This is stored-frontier pruning diagnostics only, not
frontier coverage, brancher soundness, strict-edge geometry, quotient
soundness, or a completed `n=9` review.

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
