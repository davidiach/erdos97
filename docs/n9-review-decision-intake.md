# n=9 Review Decision Intake

Status: `REVIEW_DECISION_INTAKE_ONLY`.

This note explains `metadata/n9_review_decision_intake.yaml` and
`scripts/check_n9_review_decision_intake.py`. The decision intake is a checked
schema for written independent review records. It does not prove Erdos Problem
#97, does not prove `n=9`, does not claim a counterexample, does not complete
independent review, and does not update the official/global status.

## Purpose

The dossier explains what to inspect, and the run bundle records what a
checkout executed. The decision intake defines how a reviewer can record the
result of that inspection without accidentally promoting a theorem-style
claim.

A decision record must:

- assign every review or infrastructure gate to exactly one of
  `accepted_gates`, `rejected_gates`, or `not_reviewed_gates`;
- acknowledge that no general proof, counterexample, or official/global status
  update is being claimed;
- cite the reviewed commit and optional run-bundle digest;
- choose one allowed outcome from the review-gate ledger;
- record precise gaps whenever the outcome is `gap_found`.

## Commands

Validate the intake contract:

```bash
python scripts/check_n9_review_decision_intake.py --check --summary-json
```

Print a decision-record template:

```bash
python scripts/check_n9_review_decision_intake.py --template
```

Validate a filled decision record:

```bash
python scripts/check_n9_review_decision_intake.py --decision path/to/decision.yaml --check --summary-json
```

Render the Markdown worksheet to stdout:

```bash
python scripts/check_n9_review_decision_intake.py --markdown
```

## Boundary

Even a valid final decision record is only intake validation. An accepted
primary route can support a separate source-of-truth proposal for the repo-local
`n=9` finite case, but the decision file itself does not update `README.md`,
`STATE.md`, `RESULTS.md`, `metadata/erdos97.yaml`, the official/global status,
or any public theorem-style claim.
