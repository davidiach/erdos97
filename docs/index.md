# Documentation index

Use this index as the fast route into the project notes. Keep `STATE.md` short;
put detailed reconciliation in the canonical synthesis.

## Core state

- [`../STATE.md`](../STATE.md): short working dashboard.
- [`../metadata/erdos97.yaml`](../metadata/erdos97.yaml): canonical status
  metadata separating official/global status from local repo claims.
- [`upstream-alignment.md`](upstream-alignment.md): alignment notes for
  `teorth/erdosproblems` and the official problem page.
- [`reviewer-guide.md`](reviewer-guide.md): audit route for finite-case
  artifacts and exact certificates.
- [`review-priorities.md`](review-priorities.md): current independent-review
  priorities; planning guidance only, not mathematical evidence.
- [`canonical-synthesis.md`](canonical-synthesis.md): long-form canonical
  synthesis, claim taxonomy, failed-route reconciliation, and source/hash
  inventory.
- [`../RESULTS.md`](../RESULTS.md): compact results ledger.

## Claims and obstructions

- [`claims.md`](claims.md): proved local facts, conditional programs, and
  proof-facing caveats.
- [`mutual-rhombus-filter.md`](mutual-rhombus-filter.md): crossing-bisector and
  mutual-midpoint filters for fixed selected-witness patterns.
- [`phi4-rectangle-trap.md`](phi4-rectangle-trap.md): exact even
  perpendicularity 4-cycle obstruction for fixed selected-witness patterns.
- [`phi4-frontier-scan.md`](phi4-frontier-scan.md): reusable phi4
  rectangle-trap sweep over registered fixed patterns and sparse orders.
- [`altman-diagonal-sums.md`](altman-diagonal-sums.md): natural-order
  diagonal-sum obstruction for cyclic-offset patterns.
- [`cyclic-crossing-csp.md`](cyclic-crossing-csp.md): exact cyclic-order
  crossing CSP for two-overlap patterns.
- [`vertex-circle-order-filter.md`](vertex-circle-order-filter.md): exact
  row-wise convexity-distance filter for cyclic orders.
- [`metric-order-lp.md`](metric-order-lp.md): combined fixed-order LP
  diagnostic using Altman gaps, vertex-circle inequalities, and triangle
  inequalities; records a relaxation miss on the registered sparse orders.
- [`round2/round2_merged_report.md`](round2/round2_merged_report.md):
  round-two fixed-order `C19_skew` Kalmanson/Farkas certificate and C17 method
  note summary.
- [`round2/kalmanson_distance_filter.md`](round2/kalmanson_distance_filter.md):
  exact Kalmanson distance certificate format for fixed cyclic orders.
- [`kalmanson-c13-pilot.md`](kalmanson-c13-pilot.md): exact fixed-order
  Kalmanson/Farkas certificate for the registered non-natural C13 Sidon order.
- [`kalmanson-certificate-diagnostics.md`](kalmanson-certificate-diagnostics.md):
  deterministic support diagnostics for the checked C13 and C19 fixed-order
  Kalmanson/Farkas certificates.
- [`kalmanson-two-order-search.md`](kalmanson-two-order-search.md): exact
  all-cyclic-order two-inequality Kalmanson obstruction for the fixed C13 Sidon
  pattern.
- [`c13-kalmanson-order-pilot.md`](c13-kalmanson-order-pilot.md): bounded
  C13 fixed-order Kalmanson pilot over seven explicit cyclic orders; not an
  all-order search.
- [`c13-kalmanson-prefix-branch-pilot.md`](c13-kalmanson-prefix-branch-pilot.md):
  bounded C13 prefix brancher with reflection pruning and twelve sampled exact
  fixed-order Kalmanson closures; not an all-order search.
- [`c13-kalmanson-partial-branch-closures.md`](c13-kalmanson-partial-branch-closures.md):
  exact prefix-forced Kalmanson certificates for 5,108 of 5,940 canonical
  two-boundary-pair C13 branches; not an all-order search.
- [`c13-kalmanson-third-pair-refinement.md`](c13-kalmanson-third-pair-refinement.md):
  exact prefix-forced Kalmanson certificates for 46,567 of 46,592 third-pair
  refinements of the remaining C13 two-pair frontier; not an all-order search.
- [`ptolemy-order-nlp.md`](ptolemy-order-nlp.md): numerical nonlinear
  diagnostic adding Ptolemy inequalities for cyclic quadrilaterals; records a
  relaxation miss on the registered sparse orders.
- [`two-orbit-radius-propagation.md`](two-orbit-radius-propagation.md): exact
  obstruction for a half-step two-orbit near-regular ansatz.
- [`minimum-radius-filter.md`](minimum-radius-filter.md): weak exact
  minimum-radius short-chord filter; records why it does not kill `C19_skew`
  by itself.
- [`minimal-fragile-cover-bridge.md`](minimal-fragile-cover-bridge.md):
  partial bridge theorem showing that every minimal counterexample admits a
  fragile-cover witness system; also records why this is not sufficient.
- [`sparse-frontier-diagnostic.md`](sparse-frontier-diagnostic.md): exact
  fixed-order witness-pair source diagnostic explaining the sparse/Sidon
  radius-propagation blind spot.
- [`stuck-set-miner.md`](stuck-set-miner.md): fixed-selection stuck-set mining
  for the bridge/peeling program.
- [`stuck-frontier-snapshot.md`](stuck-frontier-snapshot.md): first stuck-set,
  radius-propagation, and fragile-cover pass over the live sparse frontier.
- [`n7-fano-enumeration.md`](n7-fano-enumeration.md): reproducible `n=7`
  selected-witness obstruction.
- [`n8-incidence-enumeration.md`](n8-incidence-enumeration.md): reproducible
  `n=8` incidence-completeness enumeration.
- [`n8-exact-survivors.md`](n8-exact-survivors.md): exact obstruction pass for
  the 15 `n=8` incidence survivor classes.
- [`n8-geometric-proof.md`](n8-geometric-proof.md): proof-note draft giving a
  compact geometric obstruction for bad convex octagons via isosceles-triangle
  counting and exterior-turn angles.
- [`n9-vertex-circle-exhaustive.md`](n9-vertex-circle-exhaustive.md):
  review-pending exhaustive `n=9` selected-witness checker using the
  vertex-circle strict-chord filter.
- [`octagon-trap.html`](octagon-trap.html): interactive visualization of the
  isosceles-triangle count and octagon equality trap.
- [`reproduction-log.md`](reproduction-log.md): fast, artifact, and exhaustive
  check commands with current environment notes.
- [`failed-ideas.md`](failed-ideas.md): rejected proof routes and stale claims
  that should not be retried without a genuinely new idea.

## Computation and certification

- [`candidate-patterns.md`](candidate-patterns.md): live, speculative, and
  killed incidence patterns.
- [`verification-contract.md`](verification-contract.md): requirements for
  numerical candidates and certified counterexamples.
- [`../requirements-lock.txt`](../requirements-lock.txt): known-good direct
  dependency snapshot for reproduction.
- [`exactification-plan.md`](exactification-plan.md): route from numerical
  artifacts to exact or certified verification.
- [`sat-smt-plan.md`](sat-smt-plan.md): finite abstraction and solver plan.
- [`formalization.md`](formalization.md): Lean/formalization alignment and
  near-term formal targets.
- [`oeis-possibilities.md`](oeis-possibilities.md): exploratory OEIS sequence
  ideas and submission policy.
- [`../data/runs/README.md`](../data/runs/README.md): numerical artifact
  conventions.

## Planning and provenance

- [`literature-risk.md`](literature-risk.md): external-reference risks and
  unit-distance caveats.
- [`prompt-roadmap.md`](prompt-roadmap.md): prompt-derived planning roadmap and
  next recommended workstreams; heuristic guidance only, not mathematical
  evidence.
- [`n9-base-apex-frontier.md`](n9-base-apex-frontier.md): corrected exploratory
  slack ledger for the first `n=9` base-apex workstream; not a proof.
- [`repo-roadmap.md`](repo-roadmap.md): staged repository plan.
- [`initial-issues.md`](initial-issues.md): seed issue list.
- [`../AGENTS.md`](../AGENTS.md): repository-level Codex guidance.
