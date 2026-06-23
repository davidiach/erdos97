# n=9 Vertex-circle Route Decision Request

Status: `REVIEW_DECISION_REQUEST_ONLY`.

Claim scope: reviewer request packet for the review-pending `n=9`
vertex-circle route. This note does not accept any review gate, does not prove
`n=9`, does not prove Erdos Problem #97, does not claim a counterexample,
does not complete independent review, and does not update the official/global
status.

## Purpose

The route preflight says the internal A6/A7, A8, and A10 notes are ready to
hand to decision intake. This request packet turns that into an explicit ask:
review the vertex-circle route and, only if the written review supports it,
record an `accepted_vertex_circle_route` decision that accepts exactly:

- `frontier_enumeration`;
- `vertex_circle_geometry`;
- `quotient_obstruction_replay`;
- `independent_review`.

The turn-packing, Kalmanson corroboration, and Lean compilation gates remain
outside this request.

## Checked Request

Run:

```bash
python scripts/check_n9_vertex_circle_route_decision_request.py --check --summary-json
```

The checker validates:

- the request metadata and linked documents;
- the existing vertex-circle route preflight;
- the internal A6/A7, A8, and A10 review-note references;
- the requested gate partition against the decision-intake schema;
- the required boundary acknowledgements.

## Reviewer Workflow

Preflight the route:

```bash
python scripts/check_n9_vertex_circle_route_decision_preflight.py --check --summary-json
```

Capture a live run digest for the checkout under review:

```bash
python scripts/check_n9_review_run_bundle.py --check --run --summary-json
```

Print the accepted-route decision draft:

```bash
python scripts/check_n9_vertex_circle_route_decision_preflight.py --accepted-route-template
```

Validate a filled written decision:

```bash
python scripts/check_n9_review_decision_intake.py --decision path/to/decision.yaml --check --summary-json
```

The generic intake template remains available from
`python scripts/check_n9_review_decision_intake.py --template` when a reviewer
needs a different outcome shape, such as a precise gap record.

## Boundary

This request packet is not the written decision. Even a valid accepted route
decision would only support a separate source-of-truth proposal for the
repo-local `n=9` finite case. It would not prove Erdos Problem #97 for all
larger polygons, produce a counterexample, or change the official/global
status.
