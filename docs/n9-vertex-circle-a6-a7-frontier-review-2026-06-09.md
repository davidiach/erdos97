# n=9 Vertex-circle A6/A7 Source-frontier Review - 2026-06-09

Status: `INTERNAL_REVIEW_NOTE`.

Claim scope: internal review of the A6/A7 source-frontier enumeration layer for
the review-pending `n=9` vertex-circle route. This note reviews row0 coverage,
row-level incidence filters, branch-option implementation, dynamic
minimum-remaining-options choices, regenerated frontier coverage, fixed-order
branch-order agreement, stored-frontier predicate checks, and compact
independent brancher corroboration. It assumes the selected-witness
formulation itself is the intended finite-case target. It does not review A8
strict-edge geometry, selected-distance quotient soundness, A10 local-lemma
completeness, the turn-packing route, the algebraic route, `n=9`, a
counterexample, or the official/global status of Erdos Problem #97.

## Outcome

Outcome: `accepted_A6_A7_source_frontier_internal`.

The internal review accepts, for the current selected-witness formulation and
repo-native finite predicates, that the checked brancher enumerates the
intended pre-vertex-circle source frontier as `184` full labelled assignments
after the pair/crossing/count filters, without a hidden row0 symmetry quotient
or a dynamic-MRO branch-order omission found by the audited checks.

This is not an external review-decision record. The machine-readable
`frontier_enumeration` gate in `metadata/n9_review_gate_ledger.yaml` remains
open until an explicit written decision is validated through the review-decision
intake or an equivalent source-of-truth review process.

## Commands Run

```bash
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
python scripts/check_n9_vertex_circle_input_audit.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_frontier_assignment_audit.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_branch_options.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_dynamic_mro_choices.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_mro_branching_replay.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_compact_brancher.py --check --assert-expected --json
python scripts/check_n9_mixed_rich_frontier_crosswalk.py --check --assert-expected --json
python scripts/check_n9_review_gate_ledger.py --check --summary-json
python scripts/check_n9_candidate_review_manifest.py --check --summary-json
python scripts/check_n9_review_decision_intake.py --check --summary-json
```

## Stable Invariants Observed

- Exhaustive checker main run: `70` row0 choices, `16752` nodes, `0` full
  assignments after vertex-circle pruning, `11271` partial self-edge prunes,
  and `11011` partial strict-cycle prunes.
- Exhaustive checker no-vertex-circle cross-check: `70` row0 choices,
  `100817` nodes, `184` full assignments, with status split `158` self-edge
  and `26` strict-cycle.
- Input-data audit: row0 witnesses are the `70` lexicographic 4-subsets of
  labels `1..8`; stored row0 masks match witnesses; stored summary arithmetic
  matches the checked artifact.
- Incidence-filter audit: two-overlap crossing compatibility errors `0`;
  chord-cross equivalence mismatches `0`; two-overlap crossing accepted
  `27720`, noncrossing rejected `55440`.
- Witness-pair cap audit: row-pair index mismatches `0`, local cap predicate
  mismatches `0`, increment/decrement roundtrip errors `0`, and `91854` local
  cap profiles tested.
- Selected-indegree audit: formula gives cap `5`, local predicate mismatches
  `0`, increment/decrement roundtrip errors `0`, and `163296` local column
  profiles tested.
- Stored frontier assignment audit: `184` assignments, `1656` selected rows,
  row-shape errors `0`, center-coverage errors `0`, intersection-cap
  violations `0`, two-overlap crossing violations `0`, witness-pair cap
  violations `0`, and selected-indegree cap violations `0`.
- Stored frontier assignment histograms: center-pair intersections and
  witness-pair frequencies both `0:72`, `1:3168`, `2:3384`; selected indegree
  values are all `4`.
- Branch-option audit: `520782` no-vertex-circle fixed-order nodes, `520598`
  option contexts, `520712` helper options, `297936` empty-option contexts,
  option mismatches `0`, count-array mismatches `0`, and `184` full
  assignments.
- Dynamic-MRO choice audit with vertex-circle pruning: `16752` nodes,
  `16752` choice contexts, `93837` center-option contexts, `751918` helper
  options, chosen-center mismatches `0`, chosen-option mismatches `0`,
  helper/direct option mismatches `0`, and count-array mismatches `0`.
- Dynamic-MRO choice audit without vertex-circle pruning: `100817` nodes,
  `100633` choice contexts, `406285` center-option contexts, `1596469`
  helper options, `184` full assignments, chosen-center mismatches `0`,
  chosen-option mismatches `0`, helper/direct option mismatches `0`, and
  count-array mismatches `0`.
- Frontier-coverage crosswalk: generated assignment count `184`, stored
  assignment count `184`, sequence matches `true`, set matches `true`,
  status mismatches `0`, missing generated assignments `0`, extra stored
  assignments `0`.
- Frontier digests: generated and stored ordered-row SHA256
  `d7807b69b9de27da17fa851b3325b1e26cfa0b6d86277abeda4bc4e3454b8e01`; sorted
  row-set SHA256 `dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55`.
- Fixed-center-order replay: main run closes with `37544` nodes and `0` full
  assignments; no-vertex-circle cross-check visits `520782` nodes and reaches
  the same `184` full assignments and `158`/`26` status split.
- Compact independent brancher: does not import the project n=9 brancher
  modules or read the stored 184-assignment frontier artifact; regenerates
  `184` frontier assignments with sorted row-set digest
  `dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55` and
  vertex-circle obstruction counts `158` self-edge and `26` strict-cycle.
- Mixed-rich frontier crosswalk: set matches `true` against the stored
  exact-four frontier; sorted row-set digest matches the same
  `dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55`; the
  six sequence-position mismatches are branch-order differences only.
- Review-gate ledger, candidate review manifest, and review-decision intake
  validation statuses: `passed`.

## Narrow Statement Supported

This pass supports the following narrow internal-review statement:

```text
Under the selected-witness formulation and the row-level incidence predicates
reviewed here, the current n=9 source-frontier brancher enumerates exactly the
stored 184 pre-vertex-circle labelled assignments, with no row0 quotient,
branch-helper drift, dynamic-MRO choice drift, fixed-order disagreement, or
frontier artifact drift found by the reviewed checks.
```

## Review Boundary

This pass does not support any of the following stronger statements:

- the selected-witness formulation itself is externally reviewed as equivalent
  to every bad nonagon;
- A8 strict-edge geometry is a source-of-truth accepted gate;
- selected-distance quotient soundness is a source-of-truth accepted gate;
- A10 local-lemma completeness is a source-of-truth accepted gate;
- the full vertex-circle route is accepted;
- the turn-packing route is accepted;
- no bad nonagon exists as a promoted source-of-truth claim;
- Erdos Problem #97 is proved;
- any counterexample is produced or certified;
- the official/global status changes.

## Next Review Step

The next source-of-truth step is an explicit `frontier_enumeration` gate
decision using the review-decision intake, or a combined vertex-circle route
decision that consumes the A6/A7, A8, and A10 internal review notes while
still preserving the repo's global non-claims.
