# n=9 Review Gate Ledger

Status: `REVIEW_GATE_LEDGER_ONLY`.

This note explains the machine-readable review-gate ledger in
`metadata/n9_review_gate_ledger.yaml`. The ledger is planning and audit
infrastructure only. It does not prove Erdos Problem #97, does not prove
`n=9`, does not claim a counterexample, does not complete independent review,
and does not update the official/global status.

## Purpose

The compact `n=9` candidate harness now has two checked metadata layers:

```bash
python scripts/check_n9_candidate_review_manifest.py --check --summary-json
python scripts/check_n9_review_gate_ledger.py --check --summary-json
```

The route manifest records which commands the harness runs. The gate ledger
records why those commands matter for independent review: which reduction-chain
steps they support, which review gate remains open, and which acceptance
outcome would consume the gate.

The companion evidence matrix is
`metadata/n9_review_evidence_matrix.yaml`. It records the expected output
invariants for each command named by the route manifest and this gate ledger.

This separation keeps the review surface honest. A command can be reproducible
and still leave a proof-facing gate open.

## Gate Families

The ledger tracks eight mathematical review gates:

| Gate | Reduction steps | Route | Status |
| --- | --- | --- | --- |
| `frontier_enumeration` | A6, A7, B0, D0, D1 | shared source frontier | machine-checked review-pending |
| `vertex_circle_geometry` | A8 | vertex-circle | proof-facing review-pending |
| `quotient_obstruction_replay` | A9, A10 | vertex-circle | machine-checked review-pending |
| `turn_geometry` | B1, B2 | turn-packing | proof-facing review-pending |
| `turn_arithmetic_replay` | B3, B4 | turn-packing | machine-checked review-pending |
| `kalmanson_corroboration` | C0, C4 | corroboration | machine-checked review-pending |
| `kalmanson_geometry` | D2 | Kalmanson | proof-facing review-pending |
| `kalmanson_selfedge_replay` | D3, D4 | Kalmanson | machine-checked review-pending |

It also tracks two infrastructure gates:

| Gate | Boundary |
| --- | --- |
| `lean_compilation` | Lake is required before treating Lean pilot files as compile-checked |
| `independent_review` | written independent review is required before theorem-style use |

Every listed gate remains open.

## Acceptance Outcomes

The ledger mirrors the acceptance standard in `docs/n9-review-packet.md`:

- `accepted_vertex_circle_route` requires `frontier_enumeration`,
  `vertex_circle_geometry`, and `quotient_obstruction_replay`.
- `accepted_turn_route` requires `frontier_enumeration`, `turn_geometry`, and
  `turn_arithmetic_replay`.
- `accepted_kalmanson_route` requires `frontier_enumeration`,
  `kalmanson_geometry`, and `kalmanson_selfedge_replay`.
- `accepted_corrob_only` requires only the corroborating Kalmanson gate and
  does not justify status promotion.
- `gap_found` records a precise mathematical or implementation gap.

Only the three primary-route outcomes would justify a separate source-of-truth
PR proposing a repo-local `n=9` finite-case status change. None of those
outcomes would prove the general problem for larger polygons.

## Checker Contract

`scripts/check_n9_review_gate_ledger.py` validates that:

- all source-of-truth files referenced by the ledger exist;
- all gate IDs, outcome IDs, and forbidden promotions are present;
- each mathematical gate points to reduction-chain steps that exist in
  `docs/n9-reduction-chain.md`;
- each evidence command is present in `metadata/n9_candidate_review.yaml`;
- every review gate in the route manifest is covered by either a mathematical
  gate or an infrastructure gate;
- the acceptance outcomes remain documented in `docs/n9-review-packet.md`.

The checker does not run the mathematical replay commands. It is a contract
checker for review bookkeeping, not mathematical evidence.
