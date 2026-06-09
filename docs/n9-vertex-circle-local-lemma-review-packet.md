# n=9 Vertex-circle Local-lemma Reviewer Packet

Status: `REVIEW_PACKET_ONLY`.

Claim scope: review-pending `n=9` vertex-circle local-lemma packet chain.

Source of truth: `docs/n9-reduction-chain.md`,
`docs/n9-review-packet.md`, `docs/n9-vertex-circle-local-lemmas.md`,
`docs/relation-skeleton-catalog.md`, and `metadata/erdos97.yaml`.

Last assembled: 2026-06-04.

## Non-claims

- This packet does not prove Erdos Problem #97.
- This packet does not claim a counterexample.
- This packet does not prove the `n=9` finite case.
- This packet does not independently review the exhaustive brancher.
- This packet does not prove local-lemma completeness outside the stored
  `n=9` frontier accounting.
- This packet does not update the official/global status.

## Review target

This packet packages the local-lemma layer behind Step A10 of
`docs/n9-reduction-chain.md`:

```text
Every one of the 184 pre-vertex-circle frontier assignments contains a
selected-distance quotient self-edge or strict directed cycle.
```

The local-lemma layer is narrower than the full `n=9` route. It assumes the
`184` frontier source rows and the vertex-circle strict-edge rule are already
under review elsewhere. Its job is to make the quotient-obstruction packet
auditable.

## Main files to inspect

- `docs/n9-vertex-circle-local-lemmas.md`
- `docs/n9-vertex-circle-local-cores.md`
- `docs/relation-skeleton-catalog.md`
- `docs/n9-vertex-circle-self-edge-criterion.md`
- `docs/n9-vertex-circle-strict-cycle-criterion.md`
- `docs/n9-vertex-circle-t01-self-edge-lemma.md`
- `docs/n9-vertex-circle-t01-soundness-review-2026-06-07.md`
- `docs/n9-vertex-circle-t02-self-edge-lemma.md`
- `docs/n9-vertex-circle-t02-soundness-review-2026-06-08.md`
- `docs/n9-vertex-circle-t03-self-edge-lemma.md`
- `docs/n9-vertex-circle-t03-soundness-review-2026-06-08.md`
- `docs/n9-vertex-circle-t04-self-edge-lemma.md`
- `docs/n9-vertex-circle-t04-soundness-review-2026-06-08.md`
- `docs/n9-vertex-circle-t05-self-edge-lemma.md`
- `docs/n9-vertex-circle-t05-soundness-review-2026-06-09.md`
- `docs/n9-vertex-circle-t06-self-edge-lemma.md`
- `docs/n9-vertex-circle-t06-soundness-review-2026-06-09.md`
- `docs/n9-vertex-circle-t07-self-edge-lemma.md`
- `docs/n9-vertex-circle-t07-soundness-review-2026-06-09.md`
- `docs/n9-vertex-circle-t08-self-edge-lemma.md`
- `docs/n9-vertex-circle-t08-soundness-review-2026-06-09.md`
- `docs/n9-vertex-circle-t09-self-edge-lemma.md`
- `docs/n9-vertex-circle-t09-soundness-review-2026-06-09.md`
- `docs/n9-vertex-circle-t10-strict-cycle-lemma.md`
- `docs/n9-vertex-circle-t10-soundness-review-2026-06-08.md`
- `docs/n9-vertex-circle-t11-strict-cycle-lemma.md`
- `docs/n9-vertex-circle-t11-soundness-review-2026-06-08.md`
- `docs/n9-vertex-circle-t12-strict-cycle-lemma.md`
- `docs/n9-vertex-circle-t12-soundness-review-2026-06-08.md`
- `docs/n9-vertex-circle-local-lemma-audit-note-2026-06-07.md`

The focused T-notes are reviewer-facing local arguments. The JSON artifacts
and scripts below check their accounting and replay contracts.

## Packet shape

The current local-lemma packet has:

- `12` template packets: `T01` through `T12`;
- `16` dihedral motif families;
- `184` labelled frontier assignments;
- `13` self-edge families covering `158` assignments;
- `3` strict-cycle families covering `26` assignments;
- `16` relation-skeleton entries, one per motif family.

The nine self-edge templates are `T01` through `T09`. The three strict-cycle
templates are `T10`, `T11`, and `T12`.

## Audit chain

Run the combined audit first:

```bash
python scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --summary-json
```

Expected stable invariants:

- `validation_status: passed`;
- `audit_contract_summary.status: passed`;
- `component_count: 10`;
- `layer_count: 5`;
- `template_count: 12`;
- `template_ids: T01,...,T12`;
- `family_count: 16`;
- `assignment_count: 184`;
- `self_edge_family_count: 13`;
- `self_edge_assignment_count: 158`;
- `strict_cycle_family_count: 3`;
- `strict_cycle_assignment_count: 26`;
- `relation_skeleton_count: 16`;
- input manifest has `33` listed artifacts and no missing or unreferenced
  paths.

The combined audit is a chain of these layers:

| layer | role | command |
| --- | --- | --- |
| `focused_packet_catalog` | checks the T01-T12 packet/catalog ledger | `python scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py --check --assert-expected --summary-json` |
| `focused_minireplay` | joins each focused packet to its packet-specific mini-replay | `python scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py --check --assert-expected --summary-json` |
| `aggregate_simple_replay` | compares aggregate local-lemma scan with the simple replay | `python scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py --check --assert-expected --summary-json` |
| `exhaustive_local_lemma` | connects local-lemma accounting back to the 184-frontier motif classification | `python scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py --check --assert-expected --summary-json` |
| `relation_skeleton_local_lemma` | checks the 16 relation skeletons against aggregate local-lemma accounting | `python scripts/check_relation_skeleton_local_lemma_crosswalk.py --check --assert-expected --summary-json` |

Companion check:

```bash
python scripts/check_n9_relation_skeleton_closed_descent_crosswalk.py --check --assert-expected --summary-json
```

Expected stable invariants:

- `family_count: 16`;
- `orbit_size_sum: 184`;
- contradiction counts `strict_self_edge: 13` and
  `strict_directed_cycle: 3`;
- region-class counts `1: 13`, `2: 1`, `3: 2`.

## Local proof obligations

For each focused packet or relation skeleton, a reviewer should check:

- the displayed selected rows are exactly the local hypotheses being used;
- each selected-distance equality step follows from one selected row;
- each strict edge follows from the stated vertex-circle witness order and
  chord-containment convention;
- a self-edge really gives `D > D`;
- a strict directed cycle really returns to its starting quotient class;
- the local argument does not rely on template names as theorem names.

The packet soundness review is mathematical. The audit commands check
bookkeeping, replay consistency, and schema contracts; they do not replace the
human review of each local relation.

The 2026-06-07 internal audit note records an `accepted_A10_bookkeeping`
outcome for the checked artifact handoff chain, while leaving packet soundness
and any `n=9` status movement review-pending.

The 2026-06-07 T01 soundness review records
`accepted_packet_soundness_T01` for the single T01/F09 self-edge implication
under its displayed local hypotheses.

The 2026-06-08 T02 soundness review records
`accepted_packet_soundness_T02` for the four-family T02/F01,F04,F08,F14
self-edge implication under its displayed local hypotheses.

The 2026-06-08 T03 soundness review records
`accepted_packet_soundness_T03` for the two-family T03/F05,F15 self-edge
implication under its displayed local hypotheses.

The 2026-06-08 T04 soundness review records
`accepted_packet_soundness_T04` for the single T04/F13 self-edge implication
under its displayed local hypotheses.

The 2026-06-09 T05 soundness review records
`accepted_packet_soundness_T05` for the single T05/F10 self-edge implication
under its displayed local hypotheses.

The 2026-06-09 T06 soundness review records
`accepted_packet_soundness_T06` for the single T06/F11 self-edge implication
under its displayed local hypotheses.

The 2026-06-09 T07 soundness review records
`accepted_packet_soundness_T07` for the single T07/F06 self-edge implication
under its displayed local hypotheses.

The 2026-06-09 T08 soundness review records
`accepted_packet_soundness_T08` for the single T08/F02 self-edge implication
under its displayed local hypotheses.

The 2026-06-09 T09 soundness review records
`accepted_packet_soundness_T09` for the single T09/F03 self-edge implication
under its displayed local hypotheses.

The 2026-06-08 T10 soundness review records
`accepted_packet_soundness_T10` for the single T10/F12 strict-cycle implication
under its displayed local hypotheses.

The 2026-06-08 T11 soundness review records
`accepted_packet_soundness_T11` for the single T11/F07 strict-cycle implication
under its displayed local hypotheses.

The 2026-06-08 T12 soundness review records
`accepted_packet_soundness_T12` for the single T12/F16 strict-cycle implication
under its displayed local hypotheses. It is bridge-facing because current
bootstrap/T12 diagnostics land on T12/F16, but it does not prove the missing
row-forcing or rich-support forcing bridge step.

Together, these notes check all nine self-edge packets and all three
strict-cycle packets. Focused packet-soundness notes are now recorded for
T01-T12, while aggregate A10 review, `n=9`, and global status remain
review-pending.

## Aggregate bookkeeping obligations

For the aggregate layer, a reviewer should check:

- the T01-T12 focused packets cover the same `16` families and `184`
  assignments as the aggregate local-lemma scan;
- focused mini-replays agree with the focused packet records;
- the simple replay agrees with the aggregate scan without sharing the main
  packet generator;
- the exhaustive/local-lemma crosswalk links back to the stored
  pre-vertex-circle frontier accounting;
- relation skeletons preserve the same family ids, obstruction kinds, and
  assignment counts;
- manifest contracts localize any future digest, schema, provenance, metadata,
  or claim-scope drift to a specific input layer.

## Relation to the n=9 route

If this packet survives review, it supports the A10 quotient-obstruction
dependency in the vertex-circle route. It still does not review:

- the A6/A7 brancher coverage of the `184` frontier;
- the A8 vertex-circle strict-edge geometry;
- the turn-packing route;
- the algebraic Groebner route;
- any bridge from larger counterexamples to `n=9`.

Thus the strongest possible outcome of this packet alone is:

```text
The stored 184-frontier local-lemma quotient-obstruction accounting is
reviewed, assuming the source frontier and strict-edge geometry.
```

It is not, by itself, a repo-local proof of `n=9`.

## Acceptance outcomes

A review should record one of these outcomes:

- `accepted_packet_soundness`: each focused local packet or relation skeleton
  is mathematically sound as a local obstruction.
- `accepted_A10_bookkeeping`: the audit chain convincingly connects the
  reviewed local packets to all `184` stored frontier assignments.
- `accepted_diagnostic_only`: commands reproduce, but packet soundness or
  aggregate completeness still needs review.
- `gap_found`: a precise packet, handoff, schema, or mathematical gap is found.

Only the first two outcomes together would support marking A10 as reviewed in a
future source-of-truth PR. That future PR must still leave the global problem
open and must not promote `n=9` unless A6/A7 and A8 have also survived review.
