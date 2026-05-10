# n=9 T01/F09 Vertex-circle Template Loop

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

Trust label: `REVIEW_PENDING_DIAGNOSTIC`.

This report records a bounded prompt loop for the `T01/F09` self-edge packet in
the reusable `n=9` vertex-circle lemma path. It is proof-facing scaffolding
only. It does not claim a proof of the `n=9` selected-witness case, does not
claim a counterexample, does not complete independent review of the exhaustive
checker, and does not update the official/global falsifiable-open status of
Erdos Problem #97.

## Bridge value

The bridge being strengthened is the reusable vertex-circle local-template
path:

```text
Given exact local selected-witness rows and a cyclic witness order,
selected-distance quotienting plus vertex-circle monotonicity forces
a strict self-edge.
```

This helps separate a small local obstruction from the full review-pending
`n=9` enumeration. It does not show that arbitrary counterexamples reduce to
this template.

## Inputs read

- `AGENTS.md`
- `README.md`
- `STATE.md`
- `RESULTS.md`
- `metadata/erdos97.yaml`
- `docs/claims.md`
- `docs/review-priorities.md`
- `docs/codex-backlog.md`
- `docs/codex-strategy-instructions.md`
- `docs/n9-vertex-circle-template-lemma-catalog.md`
- `docs/n9-vertex-circle-t01-self-edge-lemma.md`
- `data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json`
- `docs/n9-vertex-circle-exhaustive.md`

## Exact local object

Use labels `0,...,8` in the natural cyclic order. A selected row is written as
`[center, witness_1, witness_2, witness_3, witness_4]`, meaning that the four
witnesses are selected at the same distance from the center.

The focused packet studies the three local rows

```text
[0, 1, 2, 4, 8]
[1, 0, 3, 5, 8]
[2, 0, 1, 4, 6]
```

and the row-`0` selected witness order

```text
[1, 2, 4, 8].
```

The packet covers the six labelled frontier assignments

```text
A014, A024, A031, A140, A166, A175
```

inside family `F09` and template id `T01`. This coverage statement is a
review-pending diagnostic crosswalk, not a theorem name.

## Cycle 1: Propose

Candidate local lemma statement:

If a strictly convex labelled nonagon in cyclic order `0,...,8` has the three
selected rows above, then the selected-distance quotient identifies the
ordinary pair distances `[1,8]` and `[1,2]`. Row `0` simultaneously gives the
strict vertex-circle inequality `[1,8] > [1,2]`. Therefore the quotient strict
graph has a reflexive strict edge.

The equality path is exactly

```text
[1,8] -- row 1 --> [0,1]
[0,1] -- row 0 --> [0,2]
[0,2] -- row 2 --> [1,2].
```

The strict inequality is exactly

```text
row 0 witness order [1,2,4,8] forces [1,8] > [1,2].
```

Reason: on the selected circle centered at `0`, the chord with endpoints
`1,8` strictly contains the chord with endpoints `1,2` in the row-`0`
vertex-circle order. The vertex-circle strict monotonicity rule therefore
orients a strict edge from the quotient class of `[1,8]` to the quotient class
of `[1,2]`. The equality path makes those classes equal.

## Cycle 2: Audit

The compact packet verifier already exists:

```bash
python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py --check --assert-expected --json
```

It was run in this loop and returned `ok: true`, with:

```text
artifact: data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json
schema: erdos97.n9_vertex_circle_t01_self_edge_lemma_packet.v1
status: REVIEW_PENDING_DIAGNOSTIC_ONLY
trust: REVIEW_PENDING_DIAGNOSTIC
template_id: T01
family_id: F09
assignment_count: 6
core_size: 3
replay_status: self_edge
strict_edge_count: 27
self_edge_conflict_count: 2
validation_errors: []
```

The targeted artifact tests for the focused packet were also run:

```bash
python -m pytest tests/test_n9_vertex_circle_t01_self_edge_lemma_packet.py -q -m "artifact"
```

They passed with 3 artifact tests selected and 8 non-artifact tests deselected.

The nearby catalog checker was also run:

```bash
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
```

It returned `ok: true`, with 12 template records covering 184 review-pending
frontier assignments: 158 self-edge assignments and 26 strict-cycle
assignments.

For context, the review-pending exhaustive checker was run:

```bash
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
```

It reproduced the stored counts: the main search leaves 0 full assignments
under vertex-circle pruning, while the cross-check without vertex-circle
pruning reaches 184 full assignments and classifies them as 158 self-edge and
26 strict-cycle obstructions. This contextual command does not promote the
`n=9` result beyond `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`.

Audit result: no packet-consistency issue was found. The existing compact
verifier is enough for this report; no new checker was needed.

## Cycle 3: Refine

Refined proof-facing statement:

Under the exact local hypotheses consisting of the natural cyclic order
`0,...,8`, the three selected rows

```text
S_0 = {1,2,4,8}
S_1 = {0,3,5,8}
S_2 = {0,1,4,6}
```

and the row-`0` selected witness order `[1,2,4,8]`, the rows force

```text
|p_1-p_8| = |p_0-p_1| = |p_0-p_2| = |p_1-p_2|.
```

The same row-`0` vertex-circle order forces

```text
|p_1-p_8| > |p_1-p_2|.
```

Thus the selected-distance quotient has a strict self-edge. Equivalently, the
local hypotheses are unrealizable by a strictly convex labelled nonagon if the
vertex-circle monotonicity rule applies as stated.

## What this rules out

This rules out any realization satisfying this exact local T01/F09 row/order
configuration. It gives a compact local obstruction that a reviewer can inspect
without reading the full exhaustive brancher.

## What remains review-pending

- The packet remains `REVIEW_PENDING_DIAGNOSTIC_ONLY`.
- The six-assignment coverage of the T01/F09 packet depends on the
  review-pending n=9 frontier/template artifacts.
- The full `n=9` vertex-circle exhaustive checker remains
  `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`.
- This report does not prove that all possible `n=9` systems reduce to this
  packet or to the twelve cataloged packets.
- This report does not prove Erdos Problem #97 and does not claim a
  counterexample.

## Existing verification commands

Packet-level verifier:

```bash
python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py --check --assert-expected --json
```

Targeted packet artifact tests:

```bash
python -m pytest tests/test_n9_vertex_circle_t01_self_edge_lemma_packet.py -q -m "artifact"
```

Catalog cross-check:

```bash
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
```

Exhaustive n=9 context checker:

```bash
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
```
