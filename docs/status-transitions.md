# Evidence-backed status transitions

The current accepted metadata and mathematical claims are unchanged. No active
`metadata/status_transition.json` is supplied by this change. Without that file,
the existing baseline status checks and overclaim detector run unchanged.

The optional transition path removes the need to modify checker code whenever
a stronger reviewed result becomes acceptable. It is **not** a way to promote
pending work, manufacture an independent review, or infer exact equalities from
numerical residuals. External problem status and local accepted results remain
separate; accepting a local result does not automatically update the website's
reported status.

## Review process

Prepare the exact proof or certificate, a validation report, a separately
sourced external-status record, and the proposed metadata and public wording.
Ask an independent reviewer to assess the precise scope and evidence, then
record their decision and provenance. The maintainer must verify that person's
identity, independence, and acceptance in the PR before merging a transition.
The checker validates the recorded decision and hashes, **not the authenticity
of the reviewer or the correctness of a mathematical proof**. A JSON field
saying `independent: true` is not itself independent review.

Candidate results remain in the existing review-pending metadata lists until
this process finishes. Do not put a pending transition at the active path.
The active proposal fails closed on missing/mutated evidence, pending review,
metadata drift, unsupported verification, path escape, or an unbound review.

## Proposal contract

The active JSON object has these fields (paths and hashes below are placeholders,
not an accepted result):

```json
{
  "schema": 1,
  "local_claim": "none",
  "finite_bound": 11,
  "problem": {
    "official_status": "<separately checked website status>",
    "official_status_last_checked": "YYYY-MM-DD",
    "official_page": "<source URL>"
  },
  "local_repo": {
    "overall_claim": "No general proof and no counterexample are claimed.",
    "strongest_result": "<exact reviewed statement containing n <= 11>",
    "strongest_result_proof": "docs/<proof>.md",
    "strongest_result_review_status": "<accurate completed-review description>"
  },
  "evidence": {
    "proof": {"path": "docs/<proof>.md", "sha256": "<hash>"},
    "verification": {"path": "reports/<validation>.json", "sha256": "<hash>"},
    "official_source": {"path": "reports/<status-source>.json", "sha256": "<hash>"}
  },
  "approved_statements": {},
  "review": {"path": "docs/reviews/<acceptance>.json", "sha256": "<hash>"}
}
```

`local_claim` is `none`, `proof`, or `counterexample`. The finite bound is a
positive integer for a finite-only transition and may be null for a global
claim. The example bound is a **schema illustration**, not an n=11 promotion.
The four `local_repo` fields and three `problem` fields must exactly match
`metadata/erdos97.yaml` after the proposed transition.

The validation JSON requires `status: "passed"`, `proof_sha256` matching the
proof artifact, nonempty `details`, and a `method` of `exact_certificate`,
`formal_proof`, or `paper_review`. Counterexample transitions require one of
the first two; a floating residual or prose-only review cannot pass that gate.
The external-status JSON repeats the three `problem` fields from its actual
source check. Do not update the checked date without performing that check.

The independent review JSON requires:

```json
{
  "decision": "accepted",
  "independent": true,
  "reviewer": "<actual reviewer identity>",
  "review_url": "<actual review provenance URL>",
  "reviewed_on": "YYYY-MM-DD",
  "proposal_sha256": "<digest of the exact proposal without its review field>"
}
```

Compute that last digest with
`scripts.status_transitions.proposal_digest(proposal)`: SHA256 of UTF-8
`json.dumps(proposal_without_review, sort_keys=True, separators=(",", ":"))`.
This avoids a circular hash dependency and binds the review to every proposed
claim, evidence hash, and approved paragraph. Hash the review file afterward
and place its reference in the proposal. Changes require renewed review.

## Public text and non-overclaiming

The three top-level status documents must include the exact reviewed overall
claim, strongest-result wording, and externally reported status. Retain accurate
archival labels for superseded statements and the metadata link.

For finite-only transitions, the no-general-proof/no-counterexample statement
and existing positive-overclaim checks remain mandatory. Such a transition
cannot provide any `approved_statements` exemptions.

For an accepted global result only, `approved_statements` can map `README.md`,
`STATE.md`, `RESULTS.md`, and `docs/claims.md` to literal, independently reviewed
paragraphs. Only complete matching paragraphs (ignoring whitespace wrapping)
are exempt from the global-overclaim lexical detector. Substrings, regexes,
statements in other files, and additional unreviewed paragraphs are not exempt.
No blanket disable switch is provided. These paragraphs are part of the
review-bound proposal digest.

All existing trust-policy booleans, official-date freshness checks, pattern
catalog consistency, and archival checks still run. The transition mechanism
validates evidence and consistency; it does not replace publication review,
formal verification, or the mathematical work still required.
