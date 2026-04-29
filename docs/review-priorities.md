# Review priorities

Status: planning guidance only; not mathematical evidence.

This file turns current review feedback into concrete work items. It does not
change the repository claims: no general proof and no counterexample are
claimed, the official/global status remains falsifiable/open, and the local
`n <= 8` selected-witness result remains repo-local and machine-checked pending
independent review.

## Priority 1 - review the octagon proof note

Target: `docs/n8-geometric-proof.md`.

Ask independent geometry reviewers to check:

- the base-apex lemma and its strict-convexity use;
- the isosceles-triangle count `T(A) <= n(n-2)`;
- equality saturation in the octagon case;
- the length-2 diagonal step forcing all side lengths equal;
- the length-3 diagonal step forcing a cover of adjacent exterior-turn pairs;
- the final vertex-cover and total-turn contradiction.

Acceptance standard: a written review should identify every accepted lemma and
any exact gap. If the note survives review, keep it as the main human-readable
small-case proof route, with the computational pipeline as an audit appendix.

## Priority 2 - build an independent n=8 checker

Build a minimal checker for the `n=8` finite artifact that treats the checked-in
JSON and certificate data as inputs, not as generated truth. It should avoid
reusing the current canonicalization and algebra-helper code except where the
input format forces it.

Suggested inputs:

- `data/incidence/n8_reconstructed_15_survivors.json`;
- `data/incidence/n8_incidence_completeness.json`;
- `certificates/n8_exact_analysis.json`.

Suggested checks:

- the 15 survivor classes are valid selected-witness incidence systems;
- claimed cyclic-order eliminations are reproducible;
- named exact certificates for classes `3`, `4`, `5`, and `14` verify from the
  certificate data;
- the checker reports only `EXACT_OBSTRUCTION` or explicit uncertainty.

## Priority 3 - isolate class 14

Class `14` is the most delicate current survivor obstruction because it uses
PB+ED Groebner reasoning plus a strict-interior conclusion. Move toward a short,
standalone certificate file with a minimal verifier that checks:

- the polynomial system under the stated normalization;
- the claimed Groebner basis or an equivalent exact contradiction;
- every solution branch used in the argument;
- the strict-interior or non-strict-convexity conclusion.

This should be small enough for an external reviewer to audit without reading
the full search pipeline.

## Priority 4 - pin literature coverage

Before any paper-style or public theorem-style claim, run a literature sweep
covering repeated distances in convex polygons, isosceles-triangle counts,
metric oriented matroids, and order-k Voronoi degeneracies. Record both found
references and negative search results in `docs/literature-risk.md`.

Do not use unchecked literature summaries to alter the official/global status.
Recheck the official Erdos Problems page before any status update.

## Priority 5 - keep the frontier separate

Keep `n >= 9`, `C19_skew`, and broader SAT/SMT work separate from the small-case
claim. They are research-frontier workstreams, not prerequisites for the
repo-local `n <= 8` artifact.

## Priority 6 - strengthen only productive filters

The minimum-radius short-chord filter in `docs/minimum-radius-filter.md` is a
valid exact necessary condition, but it is weak: it does not kill `C19_skew`.
Treat it as recorded negative information unless it is extended into a genuine
radius-inequality propagation system or combined with cyclic-order search.
