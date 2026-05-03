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

Current audit entrypoint:

```bash
python scripts/independent_check_n8_artifacts.py --check --json
```

This command checks the checked-in survivor, completeness, compatible-order,
and exact-analysis artifacts as input data. It is an artifact-consistency and
exact-obstruction audit entrypoint, not an independent regeneration of the full
incidence enumeration.

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

## Priority 5 - audit the n=9 vertex-circle exhaustive checker

Target: `docs/n9-vertex-circle-exhaustive.md`.

The 2026-05-03 archive bundle has been refactored into a repo-native checker
that leaves 0 full `n=9` selected-witness assignments after exact
vertex-circle pruning. Treat this as review-pending until an independent audit
checks:

- the necessity of the two-overlap crossing, witness-pair cap, indegree cap,
  and vertex-circle strict-cycle filters;
- the absence of a hidden symmetry quotient in the 70 row0 choices;
- that minimum-remaining-options branching changes only search order;
- that the raw 184/16 and 102-certificate archive variants agree with the
  repo-native counts after their conventions are documented.

Acceptance standard: a written review should either promote the checker to the
same repo-local finite-case status as `n <= 8`, or identify the exact
mathematical or implementation gap.

## Priority 6 - mine a reusable vertex-circle lemma

Target: `docs/n9-vertex-circle-obstruction-shapes.md` and
`docs/n9-vertex-circle-motif-families.md`.

The n=9 obstruction-shape diagnostic shows that the 184 pre-vertex-circle
frontier assignments are killed by 158 self-edges and 26 strict cycles, all
strict cycles having length 2 or 3. This makes the most promising proof push a
quotient-graph lemma: selected-distance equalities collapse ordinary pair
distances into classes, vertex-circle interval containment orients strict
edges between classes, and realizability requires the resulting strict graph to
be irreflexive and acyclic.

Next steps:

- classify the 13 self-edge dihedral incidence families into local lemmas;
- classify the 3 strict-cycle dihedral incidence families into directed
  quotient-cycle templates;
- use `docs/n9-vertex-circle-local-cores.md` as the row-local certificate list
  to keep those lemmas small;
- test whether the same motifs appear in the P18 obstruction and fail in the
  known `C19_skew` vertex-circle survivor;
- use `docs/n9-vertex-circle-frontier-comparison.md` as the current guardrail:
  exact n=9 cores do not embed into P18 or C19, although P18 shares a loose
  strict-cycle span shape;
- identify the extra exact ingredient needed for `C19_skew`, likely
  Altman/Kalmanson or stronger radius propagation.

Acceptance standard: a reusable lemma should state precise incidence/order
hypotheses and produce a self-edge or strict cycle without enumerating all n=9
selected-witness assignments.

## Priority 7 - keep the frontier separate

Keep `n >= 9`, abstract `C19_skew`, and broader SAT/SMT work separate from the
small-case claim. The compact round-two Kalmanson certificate kills one fixed
`C19_skew` cyclic order with two strict inequalities, not the abstract pattern
over all orders. These are
research-frontier workstreams, not prerequisites for the repo-local `n <= 8`
artifact.

Next exact frontier step: turn the two-inequality Kalmanson inverse-pair
finder into an all-order avoidance search. A positive result would show every
cyclic order of a fixed sparse pattern contains some inverse-pair obstruction;
a negative result would produce a new registered order that needs stronger
geometry.

## Priority 8 - extend the C13 Kalmanson pilot

The first C13 Kalmanson pilot now kills the registered non-natural
`C13_sidon_1_2_4_10` order with an exact 34-inequality certificate. Before
attempting exhaustive `C19_skew` cyclic-order search, extend the smaller C13
pilot toward all cyclic orders: normalize by dihedral symmetry, prune partial
orders cheaply, run LP dual checks on closed branches, and emit exact integer
certificates for branches that close.

## Priority 9 - strengthen only productive filters

The minimum-radius short-chord filter in `docs/minimum-radius-filter.md` is a
valid exact necessary condition, but it is weak: it does not kill `C19_skew`.
Treat it as recorded negative information unless it is extended into a genuine
radius-inequality propagation system or combined with cyclic-order search.
