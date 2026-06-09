# n=9 Vertex-circle Route Decision Preflight

Status: `REVIEW_PREFLIGHT_ONLY`.

Claim scope: reviewer handoff preflight for the review-pending `n=9`
vertex-circle route. This note does not accept any review gate, does not prove
`n=9`, does not prove Erdos Problem #97, does not claim a counterexample, and
does not update the official/global status.

## Purpose

The internal A6/A7, A8, and A10 review notes now cover the current
vertex-circle route evidence bundle:

- A6/A7 source-frontier enumeration:
  `docs/n9-vertex-circle-a6-a7-frontier-review-2026-06-09.md`;
- A8 strict-edge geometry:
  `docs/n9-vertex-circle-a8-strict-edge-review-2026-06-09.md`;
- A10 quotient-obstruction packet chain:
  `docs/n9-vertex-circle-a10-aggregate-review-2026-06-09.md`.

Those notes are internal review evidence only. A source-of-truth route decision
still needs a written independent review record validated by the decision
intake.

## Checked Preflight

Run:

```bash
python scripts/check_n9_vertex_circle_route_decision_preflight.py --check --summary-json
```

The preflight checks that:

- the three internal review notes exist and retain their expected internal
  outcomes and boundary language;
- the ledger keeps `frontier_enumeration`, `vertex_circle_geometry`,
  `quotient_obstruction_replay`, and `independent_review` open;
- the `accepted_vertex_circle_route` decision-intake rule requires all four of
  those accepted gates;
- a schema-only draft shape for `accepted_vertex_circle_route` validates as a
  decision record shape, without recording or implying a real decision.

## Decision Boundary

The next required external artifact remains a filled decision record checked by:

```bash
python scripts/check_n9_review_decision_intake.py --decision path/to/decision.yaml --check --summary-json
```

Even a valid accepted route decision would only support a separate
source-of-truth proposal for the repo-local `n=9` finite case. It would not
prove Erdos Problem #97 for all larger polygons or change the official/global
status.
