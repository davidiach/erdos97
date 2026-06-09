# n=9 Vertex-circle A10 Aggregate Review - 2026-06-09

Status: `INTERNAL_REVIEW_NOTE`.

Claim scope: internal aggregate review of the Step A10 local-lemma
quotient-obstruction packet chain after the focused T01-T12 packet-soundness
notes. This note assumes the stored `184` pre-vertex-circle frontier rows and
the vertex-circle strict-edge rule are reviewed elsewhere. It does not prove
`n=9`, does not claim a counterexample, does not independently review the
exhaustive brancher, does not review A6/A7 frontier coverage, does not review
A8 strict-edge geometry in general, and does not update the official/global
status of Erdos Problem #97.

## Outcome

Outcome: `accepted_packet_soundness_T01_T12` for the focused local packets,
plus `accepted_A10_bookkeeping_after_packet_soundness` for the stored
aggregate handoff chain.

This is an internal review-note outcome. It does not by itself update
`README.md`, `STATE.md`, `RESULTS.md`, or `metadata/erdos97.yaml` to mark A10
as a promoted source-of-truth gate. A future source-of-truth decision still
needs to pass through the n=9 review-decision intake or an equivalent explicit
review record.

No handoff, schema, coverage, replay, or packet-soundness gap was found in
this pass.

## Evidence Reviewed

The focused packet-soundness notes reviewed before this aggregate pass were:

| template | families | assignments | local outcome |
| --- | --- | ---: | --- |
| `T01` | `F09` | 6 | `accepted_packet_soundness_T01` |
| `T02` | `F01,F04,F08,F14` | 40 | `accepted_packet_soundness_T02` |
| `T03` | `F05,F15` | 20 | `accepted_packet_soundness_T03` |
| `T04` | `F13` | 2 | `accepted_packet_soundness_T04` |
| `T05` | `F10` | 18 | `accepted_packet_soundness_T05` |
| `T06` | `F11` | 18 | `accepted_packet_soundness_T06` |
| `T07` | `F06` | 18 | `accepted_packet_soundness_T07` |
| `T08` | `F02` | 18 | `accepted_packet_soundness_T08` |
| `T09` | `F03` | 18 | `accepted_packet_soundness_T09` |
| `T10` | `F12` | 18 | `accepted_packet_soundness_T10` |
| `T11` | `F07` | 6 | `accepted_packet_soundness_T11` |
| `T12` | `F16` | 2 | `accepted_packet_soundness_T12` |

These focused notes cover `184` stored frontier assignments across `16`
families: `158` assignments by self-edge packets and `26` assignments by
strict-cycle packets.

## Commands Run

```bash
python scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py --check --assert-expected --summary-json
python scripts/check_relation_skeleton_local_lemma_crosswalk.py --check --assert-expected --summary-json
python scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_local_lemmas.py --check --assert-expected --json
```

## Stable Invariants Observed

- Combined audit-path validation status: `passed`.
- Audit contract components: `10` passed, `0` failed.
- Manifest contracts: `7` passed, `0` failed.
- Input manifest: `33` listed artifacts, no missing paths, no unreferenced
  paths, and SHA256 digest consistency passed.
- Layer count: `5`.
- Adjacent handoff checks: `4` passed with no mismatches.
- Template ids: `T01` through `T12`.
- Family count: `16`.
- Assignment count: `184`.
- Self-edge coverage: `13` families covering `158` assignments.
- Strict-cycle coverage: `3` families covering `26` assignments.
- Focused packet catalog: zero duplicate assignment ids, zero duplicate
  family ids, zero missing packet templates, zero extra packet templates,
  zero packet coverage mismatches, zero source-catalog mismatches, zero
  source-template mismatches, and zero aggregate focused-crosscheck
  mismatches.
- Focused mini-replay crosswalk: `12` mini-replays, all obstruction-flagged,
  with zero source-packet mismatches, zero source-schema mismatches, zero
  family mismatches, zero assignment-count mismatches, and zero
  obstruction-flag mismatches.
- Aggregate/simple replay crosswalk: `16` aggregate families and `16`
  simple-replay families match all `184` assignments.
- Exhaustive/local-lemma crosswalk: the review-pending exhaustive count
  artifact, frontier motif classification, aggregate local-lemma scan, and
  simple replay agree on the same `184` assignments and `158`/`26` status
  split.
- Relation-skeleton/local-lemma crosswalk: `16` relation skeletons match the
  same `16` local families and `184` assignments.
- Relation-skeleton/closed-descent companion: contradiction counts are
  `strict_self_edge: 13` and `strict_directed_cycle: 3`; region-class counts
  are `1: 13`, `2: 1`, and `3: 2`.
- Aggregate local-lemma artifact: `7` lemma records cover all `184`
  source assignments and all `16` source families, with zero uncovered
  assignments and zero uncovered families.

## Narrow Statement Supported

This pass supports the following narrow internal-review statement:

```text
Assuming the stored 184 pre-vertex-circle frontier assignments and the
vertex-circle strict-edge rule, the current T01-T12 local-lemma packet chain
has focused packet-soundness notes for every stored local packet and the
aggregate audit path connects those reviewed packets to all 184 stored
frontier assignments.
```

## Review Boundary

This pass does not support any of the following stronger statements:

- the A6/A7 brancher coverage of the `184` frontier is reviewed;
- the A8 vertex-circle strict-edge geometry is reviewed in general;
- the exhaustive `n=9` brancher is independently reviewed;
- the local-lemma layer is complete outside the stored frontier accounting;
- the turn-packing route is reviewed;
- the algebraic Groebner route is reviewed;
- no bad nonagon exists as a promoted source-of-truth claim;
- Erdos Problem #97 is proved;
- any counterexample is produced or certified.

## Next Review Step

The next source-of-truth step is not another focused packet note. It is either
an explicit A10 gate decision using the review-decision intake, still under the
stored-frontier and strict-edge assumptions, or a move upstream to review A6/A7
frontier coverage and A8 strict-edge geometry.
