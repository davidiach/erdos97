# n=9 Vertex-circle Local-lemma Audit Note - 2026-06-07

Status: `REVIEW_NOTE`.

Claim scope: internal audit of the review-pending `n=9` vertex-circle
local-lemma packet bookkeeping and replay chain. This note does not prove
`n=9`, does not claim a counterexample, does not complete independent
mathematical review of packet soundness, does not review the exhaustive
brancher, and does not update the official/global status of Erdos Problem #97.

## Outcome

Outcome: `accepted_A10_bookkeeping` for the checked artifact handoff chain.

Packet soundness remains `REVIEW_PENDING_DIAGNOSTIC`: this pass checked the
stored packet records, per-template replays, aggregate handoffs, relation
skeletons, and targeted artifact tests, but it is not an external human
geometry review of every local proof obligation.

No handoff, schema, digest, coverage, or replay gap was found in this pass.

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
python scripts/check_n9_vertex_circle_local_lemma_simple_replay.py --check --assert-expected --json
python scripts/check_relation_skeleton_catalog.py --check --assert-expected --json
python -m pytest tests/test_relation_skeleton_catalog.py -q -m "artifact"
python -m pytest -q -m "artifact" tests/test_n9_vertex_circle_template_lemma_catalog.py tests/test_n9_vertex_circle_t01_self_edge_lemma_packet.py tests/test_n9_vertex_circle_t02_self_edge_lemma_packet.py tests/test_n9_vertex_circle_t03_self_edge_lemma_packet.py tests/test_n9_vertex_circle_t04_self_edge_lemma_packet.py tests/test_n9_vertex_circle_t05_self_edge_lemma_packet.py tests/test_n9_vertex_circle_t06_self_edge_lemma_packet.py tests/test_n9_vertex_circle_t07_self_edge_lemma_packet.py tests/test_n9_vertex_circle_t08_self_edge_lemma_packet.py tests/test_n9_vertex_circle_t09_self_edge_lemma_packet.py tests/test_n9_vertex_circle_t10_strict_cycle_lemma_packet.py tests/test_n9_vertex_circle_t11_strict_cycle_lemma_packet.py tests/test_n9_vertex_circle_t12_strict_cycle_lemma_packet.py tests/test_n9_vertex_circle_local_lemmas.py tests/test_n9_vertex_circle_local_lemma_simple_replay.py tests/test_n9_vertex_circle_local_lemma_replay_crosswalk.py tests/test_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py tests/test_relation_skeleton_local_lemma_crosswalk.py tests/test_n9_relation_skeleton_closed_descent_crosswalk.py tests/test_n9_vertex_circle_local_lemma_audit_path.py
```

The 12 focused packet checkers and 12 packet-specific mini-replay checkers
were also run with `--check --assert-expected --json`.

## Stable Invariants Observed

- Combined audit-path validation status: `passed`.
- Audit contract components: `10` passed, `0` failed.
- Manifest contracts: `7` passed, `0` failed.
- Layer count: `5`.
- Template ids: `T01` through `T12`.
- Family count: `16`.
- Assignment count: `184`.
- Self-edge coverage: `13` families covering `158` assignments.
- Strict-cycle coverage: `3` families covering `26` assignments.
- Relation-skeleton count: `16`.
- Closed-descent companion: `13` one-class regions, `1` two-class region, and
  `2` three-class regions.
- Input manifest: `33` listed artifacts, no missing paths, no unreferenced
  paths, SHA256 digest consistency passed.

The focused packet assignment counts were:

```text
T01: 6
T02: 40
T03: 20
T04: 2
T05: 18
T06: 18
T07: 18
T08: 18
T09: 18
T10: 18
T11: 6
T12: 2
```

These sum to `184`.

## Review Boundary

This pass supports the following narrow statement:

```text
The current T01-T12 local-lemma packet bookkeeping, mini-replays,
aggregate/simple replay, exhaustive/local-lemma handoff, relation-skeleton
handoff, and closed-descent companion agree on the stored 184-assignment
review-pending frontier accounting.
```

It does not support any of the following stronger statements:

- the packet soundness has been externally reviewed;
- the local-lemma layer is complete outside the stored frontier accounting;
- the exhaustive `n=9` brancher is independently reviewed;
- no bad nonagon exists as a promoted source-of-truth claim;
- Erdos Problem #97 is proved;
- any counterexample is produced or certified.

## Remaining Review Work

The next review step is mathematical, not more bookkeeping: for each focused
packet or relation skeleton, check that the displayed selected rows force the
listed selected-distance quotient equalities and that the listed cyclic
vertex-circle order forces the displayed strict edge or directed cycle.
