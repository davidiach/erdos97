# Review priorities

Status: planning guidance only; not mathematical evidence.

This file turns current review feedback into concrete work items. It does not
change the repository claims: no general proof and no counterexample are
claimed, the official/global status remains falsifiable/open, and the local
`n <= 8` selected-witness result remains repo-local and machine-checked pending
independent review.

For a Codex-ready task list with issue links, commands, acceptance criteria,
trust deltas, and forbidden overclaiming text, see `docs/codex-backlog.md`.

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

## Priority 2 - audit and extend the n=8 checker

Audit the current checker, and extend it toward a more independent `n=8`
finite-artifact check that treats the checked-in JSON and certificate data as
inputs, not as generated truth. Any extension should avoid reusing the current
canonicalization and algebra-helper code except where the input format forces
it.

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

Partial SymPy-free independent cross-check:

```bash
python scripts/independent_n8_obstruction_recheck.py --check --json
```

This command independently replays the compatible cyclic-order counts, the
class `12` cyclic-order kill, and the `y_2`-in-PB-span kill for ten classes
using pure-Python rational arithmetic. It does not verify the Groebner-based
classes `3`, `4`, `5`, or `14`.

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
- review the 3 strict-cycle dihedral incidence families as directed
  quotient-cycle local templates, using the focused T10/T11/T12 notes;
- use `docs/n9-vertex-circle-local-cores.md` as the row-local certificate list
  to keep those lemmas small;
- use `data/certificates/n9_vertex_circle_self_edge_path_join.json` as the
  assignment-level replay aid for transformed self-edge equality paths;
- use `data/certificates/n9_vertex_circle_self_edge_template_packet.json` to
  review the 9 self-edge template packets before attempting reusable local
  lemmas;
- use `data/certificates/n9_vertex_circle_strict_cycle_path_join.json` as the
  assignment-level replay aid for transformed strict-cycle local-core
  quotient cycles, keeping its local-core cycle counts separate from first
  full-assignment obstruction-shape counts;
- use `data/certificates/n9_vertex_circle_strict_cycle_template_packet.json`
  to review the 3 strict-cycle template packets before attempting reusable
  quotient-cycle lemmas;
- use `data/certificates/n9_vertex_circle_template_lemma_catalog.json` as a
  single 12-template lemma-candidate crosswalk before writing proof-facing
  local lemmas;
- use `data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json` as
  the first focused review-pending T01/F09 self-edge local lemma packet;
- use `data/certificates/n9_vertex_circle_t02_self_edge_lemma_packet.json` as
  the next focused review-pending T02 multi-family self-edge local lemma packet;
- use `data/certificates/n9_vertex_circle_t03_self_edge_lemma_packet.json` to
  replay the focused review-pending T03 multi-family self-edge local lemma
  packet;
- use `data/certificates/n9_vertex_circle_t04_self_edge_lemma_packet.json` to
  replay the focused review-pending T04/F13 four-row selected-path self-edge
  proof note;
- use `data/certificates/n9_vertex_circle_t10_strict_cycle_lemma_packet.json`
  to replay the focused review-pending T10/F12 strict-cycle local lemma packet;
- use `data/certificates/n9_vertex_circle_t11_strict_cycle_lemma_packet.json`
  to replay the focused review-pending T11/F07 strict-cycle local lemma packet;
- use `data/certificates/n9_vertex_circle_t12_strict_cycle_lemma_packet.json`
  to replay the focused review-pending T12/F16 strict-cycle local lemma packet;
- review the aggregate local-lemma scan after the T01/T02/T03/T04 self-edge and
  T10/T11/T12 strict-cycle integrations, keeping it scoped as proof-mining
  coverage of stored packets rather than an independent `n=9` proof;
- test whether the same motifs appear in the P18 obstruction and fail in the
  recorded `C19_skew` vertex-circle-only survivor, which is now retired as a
  fixed abstract pattern by the separate Z3 Kalmanson certificate;
- use `docs/n9-vertex-circle-frontier-comparison.md` as the current guardrail:
  exact n=9 cores do not embed into P18 or C19, although P18 shares a loose
  strict-cycle span shape;
- identify the extra exact ingredient needed for `C19_skew`, likely
  Altman/Kalmanson or stronger radius propagation.

Acceptance standard: a reusable lemma should state precise incidence/order
hypotheses and produce a self-edge or strict cycle without enumerating all n=9
selected-witness assignments.

## Priority 6b - audit the n=10 singleton-slice draft

Target: `docs/n10-vertex-circle-singleton-slices.md` and
`data/certificates/n10_vertex_circle_singleton_slices.json`.

The incoming n=10 continuation covers all 126 row0 singleton slices and records
zero full selected-witness assignments under the pair/crossing/count plus
vertex-circle filters. Treat this as a draft until an independent audit checks:

- the generic checker source against the exact pruning lemmas;
- the row0 singleton coverage `[0,126)` and absence of hidden symmetry
  quotienting;
- the secondary first-five replay in
  `data/certificates/2026-05-05/n10_secondary.json`, which cross-checks only
  rows `0..4` under an extra triple-intersection necessary filter;
- that minimum-remaining-options branching changes only search order;
- that partial vertex-circle pruning uses only already-fixed selected rows and
  selected-distance equalities;
- that a second implementation or replayable terminal-conflict certificate
  agrees with all 126 slices, not only the current selected row0 spot-checks.

Acceptance standard: a reviewer should either promote the artifact to the same
review-pending finite-case status as n=9, or identify the exact implementation,
coverage, or certificate gap. This may not update the official/global status or
the repo source-of-truth strongest result without a broader review decision.

## Priority 7 - review the C19 all-order Kalmanson SMT certificate

Target: `data/certificates/c19_skew_all_orders_kalmanson_z3.json` and
`scripts/check_kalmanson_two_order_z3.py`.

The C19 sparse fixed-pattern lead is now killed across all cyclic orders by a
Z3 refinement certificate. Keep this separate from the small-case claim and
from the global Erdos #97 status.

Review checklist:

- every stored forbidden ordered-quadrilateral pair is validated as a genuine
  inverse pair of Kalmanson row vectors after selected-distance quotienting;
- label `0` at position `0` is only a cyclic-order representation choice, not a
  hidden loss of cases;
- the Z3 constraints encode exactly "not both ordered quadrilaterals occur";
- replaying the stored clauses gives UNSAT without relying on the refinement
  search history;
- the all-order UNSAT step is replayed by at least one Z3-independent route,
  such as a DIMACS/DRAT/LRAT proof, another SMT solver with a checkable proof,
  or a pure finite-order proof checker for the stored clauses;
- an UNSAT core alone is not treated as a proof object unless a separate
  checker verifies it;
- the claim remains scoped to the fixed abstract `C19_skew` selected-witness
  pattern.

Acceptance standard: a reviewer should either accept the certificate as an
exact all-order obstruction for fixed abstract `C19_skew` with an independent
UNSAT replay path, or identify a specific encoding, solver-trust, or verifier
gap. Until then, the stored artifact remains a checked Z3 certificate rather
than a solver-independent proof object.

## Priority 7b - audit the C19 sampled-prefix catalog prefilter

Target:
`data/certificates/c19_kalmanson_prefix_window_catalog_prefilter_sweep_288_479.json`,
`reports/c19_prefilter_catalog_unit_supports.json`, and
`scripts/sweep_c19_kalmanson_prefix_windows_catalog_prefilter.py`.

The catalog-prefilter sweep is exact for sampled C19 prefix windows 288-479
and should remain separate from the all-order Z3 certificate above. It applies
the two-row prefilter first, then three cataloged unit supports for the eight
recorded two-row misses, leaving zero ordinary fifth-pair Farkas fallbacks in
that sampled range.

Review checklist:

- the three catalog supports sum to zero after selected-distance quotienting;
- each catalog support row is forced by the recorded fallback child state;
- the sweep records the same 192 sampled prefixes and 10,350 fifth-pair
  children as the two-row-only compact sweep;
- catalog support use is limited to children missed by the two-row lookup;
- the claim remains scoped to sampled prefix indices 288-479.

Acceptance standard: a reviewer should either accept the catalog prefilter as
an exact sampled-window replay optimization, or identify a specific mismatch
between the catalog support artifact and the sweep accounting.

## Priority 8 - extend the two-certificate search beyond retired sparse leads

The C13 Sidon pattern and C19 skew pattern are now both killed across all cyclic
orders by exact two-inequality Kalmanson inverse-pair methods. Use them as
benchmarks for the larger frontier:

- classify the inverse-pair templates that prune C13 and C19;
- test whether the same templates appear in newly mined sparse incidence
  patterns;
- use the recorded C29 fixed-order certificate
  `data/certificates/c29_sidon_fixed_order_kalmanson_165_unsat.json` as the
  benchmark for full-cone Kalmanson/Farkas certificates that are not visible to
  the two-inequality inverse-pair filter;
- try to turn full-cone fixed-order certificates into reusable order-search
  clauses for larger sparse/Sidon patterns;
- look for a bridge from arbitrary selected-witness counterexamples to a
  classified family where Kalmanson/SMT certificates can be applied.

## Priority 8b - strengthen the fragile-cover bridge

Target: `docs/minimal-fragile-cover-bridge.md` and
`src/erdos97/fragile_hypergraph.py`.

Minimality proves that every minimal counterexample has a fragile-cover
witness system, but the block-6 abstract family shows the current hypergraph
axioms are too weak. The current checker now also has an optional full-row
extension diagnostic: it rejects the single six-vertex block but still permits
two disjoint blocks. The next useful bridge work is to add a geometric
condition that the surviving multi-block family does not automatically satisfy:

- dependency-cycle restrictions for the witness map `pi`;
- critical-radius ordering or deletion-dependency inequalities;
- exact row-circle constraints on the fragile rows;
- interaction between fragile-cover rows and stuck-set/ear-orderability
  failures.
- adaptive radius-blocker analysis, as recorded in
  `docs/adaptive-radius-blocker-bridge.md`, which keeps all rich distance
  classes visible instead of fixing one selected row per center.
- bootstrap-core/private-halo analysis, as recorded in
  `docs/bootstrap-core-bridge.md`, which adds a `rho > 3` closure-rank witness,
  deletion closures, and weighted cyclic outside-pair capacity.
- bootstrap-core crosswalk evidence, as recorded in
  `docs/bootstrap-core-crosswalk.md`, showing that the current singleton-rich
  sparse/frontier motifs have rank greater than 3 but retain positive weighted
  capacity margin; any useful next condition should reduce that slack or add
  additional private-pair demand.
- bootstrap / vertex-circle overlay evidence, as recorded in
  `docs/bootstrap-vertex-circle-overlay.md`, showing that the two tight
  non-ear-orderable `n=9` rows both join to the `T12/F16` strict-cycle template
  but not by a bootstrap-core-only contradiction.
- bootstrap/T12 forcing-target evidence, as recorded in
  `docs/bootstrap-t12-forcing-targets.md`, showing that source `81` has no
  direct private-pair hit and source `151` has only partial direct hits, so the
  next useful condition should force missing row centers or equality connectors
  rather than rely on private pairs alone.
- bootstrap/T12 row-pressure evidence, as recorded in
  `docs/bootstrap-t12-row-pressure.md`, splitting the six missing row centers
  into deletion-closure-exposed rows, one-outside-label rows, and one
  outside-pair row with partial private-pair support.
- bootstrap/T12 closure-exposed evidence, as recorded in
  `docs/bootstrap-t12-closure-exposed.md`, isolating the two activation-ready
  deletion-closure rows before attacking the one-outside-label and outside-pair
  cases.
- bootstrap/T12 one-outside-label evidence, as recorded in
  `docs/bootstrap-t12-one-outside.md`, isolating the three singleton-support
  rows where pair-capacity arguments do not directly apply.
- bootstrap/T12 outside-pair evidence, as recorded in
  `docs/bootstrap-t12-outside-pair.md`, isolating the remaining row where the
  private-pair ledger has partial direct support.
- bootstrap/T12 activation-requirement evidence, as recorded in
  `docs/bootstrap-t12-activation-requirements.md`, separating connector-pair
  and strict-edge endpoint requirements from the still-unproved row-forcing
  step.
- bootstrap/T12 bridge-target-map evidence, as recorded in
  `docs/bootstrap-t12-bridge-target-map.md`, joining those packets into six
  explicit next-lemma targets, with `151:7`, `151:8`, and `151:5` as the main
  hard/open rows.
- bootstrap/T12 hard strict-endpoint evidence, as recorded in
  `docs/bootstrap-t12-hard-strict-endpoints.md`, isolating `151:7` and
  `151:8` as the rows where strict-edge endpoint sets are still not supplied
  by closure exposure or singleton support.
- bootstrap/T12 open connector-pair evidence, as recorded in
  `docs/bootstrap-t12-open-connector-pair.md`, isolating `151:5` as the row
  where connector pair `[7,8]` is still split across singleton support and
  partial closure evidence.
- bootstrap/T12 relation-sufficient row evidence, as recorded in
  `docs/bootstrap-t12-relation-sufficient-rows.md`, isolating `81:3`, `81:8`,
  and `151:6` as rows where connector relation evidence is present but
  row/rich-class forcing remains open.
- bootstrap/T12 focused `81:3` closure-target evidence, as recorded in
  `docs/bootstrap-t12-81-3-closure-target.md`, isolating the unique target
  where full-row deletion-closure exposure, relation sufficiency, and the
  final `T12/F16` equality connector role coincide; this is still an open
  row/rich-class forcing target.
- bootstrap/T12 focused `81:3` rich-triple contract evidence, as recorded in
  `docs/bootstrap-t12-81-3-rich-triple-contract.md`, weakening the target to
  the connector pair `[0,1]`: any genuine rich class at center `3` containing
  that pair gives `[1,3]=[0,3]`, while a connector-avoiding activation must
  expose label `6` first.
- bootstrap/T12 focused `81:3` order-escape evidence, as recorded in
  `docs/bootstrap-t12-81-3-order-escape.md`, checking that the fixed
  singleton-rich closure does not expose label `6` before center `3`; any
  successful escape now needs genuine rich-class data that supplies label `6`
  first, or a proof that no such supply exists.
- bootstrap/T12 focused `81:3` escape-CSP evidence, as recorded in
  `docs/bootstrap-t12-81-3-escape-auxiliary-csp.md` and
  `docs/bootstrap-t12-81-3-trigger-uniqueness.md`, ruling out the specified
  one-supply/one-connector auxiliary trigger model and showing each specified
  trigger family is same-center unique. The remaining target is outside those
  specified trigger families or a genuine rich-class/minimality hypothesis,
  not more copies of the same supply or connector trigger at the same center.
- bootstrap/T12 focused `81:3` rich-support evidence, as recorded in
  `docs/bootstrap-t12-81-3-escape-rich-support-csp.md`, extending the auxiliary
  escape CSP from 4-set trigger classes to larger rich supports at centers `3`
  and `6`. The remaining target is now support existence, additional
  auxiliary supports at other centers, or a different bridge target.
- bootstrap/T12 focused `81:8` singleton-support evidence, as recorded in
  `docs/bootstrap-t12-81-8-singleton-support-audit.md`, showing that the fixed
  source-`81` neighborhood and one-row-drop relaxation have no non-original
  row-`8` activation survivor under basic incidence/crossing filters. The
  remaining target is still genuine singleton-support or row-forcing
  geometry, not a proof that row `8` is forced.
- bootstrap/T12 focused `151:6` outside-pair evidence, as recorded in
  `docs/bootstrap-t12-151-6-outside-pair-audit.md`, showing that the fixed
  source-`151` neighborhood and one-row-drop relaxation have no non-original
  row-`6` activation survivor under basic incidence/crossing filters. The
  remaining target is still genuine outside-pair support or row-forcing
  geometry, not a proof that row `6` is forced.
- bootstrap/T12 focused source-`151` singleton-support evidence, as recorded
  in `docs/bootstrap-t12-151-singleton-support-audit.md`, showing that rows
  `151:5` and `151:8` have no non-original activation survivor in the fixed
  source-`151` neighborhood or one-row-drop relaxation. The remaining target
  is still genuine singleton-support or row-forcing geometry, not a proof that
  either row is forced.

Acceptance standard: a strengthened bridge should be stated as a necessary
condition for minimal counterexamples and should reject at least one abstract
fragile-cover family that passes the current pairwise/crossing checks.

## Priority 9 - strengthen only productive filters

The minimum-radius short-chord filter in `docs/minimum-radius-filter.md` is a
valid exact necessary condition, but it is weak: it does not kill `C19_skew`.
Treat it as recorded negative information unless it is extended into a genuine
radius-inequality propagation system or combined with cyclic-order search.
