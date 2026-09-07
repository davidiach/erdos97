# Provenance and claim boundaries

Date: 6 September 2026.

This work continues the user's request to attack the missing geometric
bridge for Erdős Problem 97. The preceding delivered packet was
`erdos97_chain_conic_obstructions_2026_09_06`, containing weak-chain,
convex-function-graph, and conic-plus-one obstructions. This continuation
has a different successful route: one-closer-point radii and a minimum-layer
triangular-face bound. It does not establish the preceding conic/chain
extraction bridge.

## Primary context inspected

The following connected repository files were read during this
continuation. They supply research context, not a proof of this packet's
new statements.

1. `davidiach/erdos97`,
   `incoming/radius-descent-n11-2026-09-05/proofs.md`:
   https://github.com/davidiach/erdos97/blob/main/incoming/radius-descent-n11-2026-09-05/proofs.md
   File blob SHA recorded by the connector:
   `d1a4df8331a8c88d9936ca233e7ef5ad1f42c107`.
   The independent-center and side-bound hypotheses there were not silently
   imported into the theorem here.

2. `incoming/side-cap-extension-2026-09-05/README.md`:
   https://github.com/davidiach/erdos97/blob/main/incoming/side-cap-extension-2026-09-05/README.md
   File blob SHA:
   `964345a1100c5af58420a8b704e33bcb6da799c8`.
   This is the earlier locally side-bounded four-witness-core obstruction.
   The present theorem does not require a radius bound by an incident side.

3. `docs/canonical-synthesis.md`, especially the retained failed
   middle-neighbor forest and false squared-distance Monge routes:
   https://github.com/davidiach/erdos97/blob/main/docs/canonical-synthesis.md
   The threshold graph here is a different graph, is only claimed to be
   noncrossing, and its proof uses ordinary-length inequalities.

4. PR #940, “Research: unbounded strictly convex family with exactly six
   good vertices”:
   https://github.com/davidiach/erdos97/pull/940
   Read head SHA: `494d0e4fbfaacf78cc4d29b33df7729cde6bbd84`.
   Its arbitrary-length construction is review-pending. This continuation
   did not reproduce that packet, and does not rely on it in the proof.

5. The public formal statement was checked against the primary
   Google DeepMind formal-conjectures repository:
   https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/97.lean
   No statement of a solution or status promotion was made.

The connected repository changed during the session. These are individual
reads and recorded file/PR identifiers, not a claim to have audited one
complete current checkout. A targeted search found no `second-nearest`
match in the repository; that is not an exhaustive repository or literature
novelty check.

## Derivation and exact control discovery

The one-closer-point theorem, minimum-layer deficiency, face injection, and
corollaries were derived in this continuation. Their proof is self-contained
in `proofs.md`. The mathematical ideas and code have not received external
independent review or proof-assistant formalization.

The eight-point rank-two propagation control was first found by a bounded
floating-point exploratory search, then reconstructed with small rational
circle parameters. The exact reconstruction has rational coordinates and
squared radii; all equalities and convexity assertions in this packet are
checked with rational arithmetic. The numerical search is not used as
proof of an equality, existence of an exact limit, exhaustive classification,
optimality, or nonexistence. Exploratory floating-point code and unrelated
abandoned experiments are not dependencies of this delivery.

The exact fixture is encoded both by retained coordinates in
`rank_two_exact_control.json` and by the rational circle formulas in
`fixtures.py`. The verifier compares their resulting points and radii, then
independently computes supporting-line signs and every distance class.
The two encodings are a consistency check, not independent research review.

## Validation and publication

This packet was validated locally with its own standard-library checks.
The final validation record states the exact commands and results. The
33-test suite and report regeneration are executions of the delivered
implementation. The additional matching/triangulation enumeration checks
the abstract face-count layer, not complete Euclidean realization.

No full repository checkout, repository-wide CI run, formal proof, PR,
merge, or repository status change is part of this continuation. The final
ZIP is a research handoff, not a published or independently accepted theorem.
