# Codex Backlog

Status: operational planning guidance only; not mathematical evidence.

Live open issues were checked through GitHub on 2026-05-04. This backlog is a
Codex-facing companion to `docs/review-priorities.md`; it does not change the
repository claims. No general proof and no counterexample are claimed, and the
official/global status remains falsifiable/open unless manually rechecked and
updated from the official source.

For task-selection discipline, read `docs/codex-strategy-instructions.md`.
Before starting a task, identify which bridge it might strengthen; if it does
not strengthen a bridge, record the audit, provenance, or negative-control value
that justifies doing it anyway.

## Recommended next technical PRs

Use this queue when no more specific issue is selected.

1. Review the aggregate `n=9` vertex-circle local-lemma scan against the
   focused T03/T04 self-edge proof notes and the focused T10/T11/T12
   strict-cycle proof notes, keeping it scoped as proof-mining scaffolding
   rather than an `n=9` proof.
2. Audit whether the aggregate local-template coverage can be checked from the
   stored packet JSON by a second, simpler replay that does not share the
   current quotient-replay helper.
3. Strengthen the minimal fragile-cover bridge with one geometric necessary
   condition and test it against the block-6 negative controls.
4. Use the bootstrap-core crosswalk and the bootstrap / vertex-circle overlay
   in `docs/bootstrap-core-crosswalk.md` and
   `docs/bootstrap-vertex-circle-overlay.md` to design a sharper condition.
   The current singleton-rich stuck/frontier motifs all survive the weighted
   ledger, while the two tight `n=9` non-ear rows both land on the `T12/F16`
   strict-cycle template without yielding a bootstrap-core-only contradiction.
   The follow-up `docs/bootstrap-t12-forcing-targets.md` refines this into a
   row-center forcing target: source `81` has no direct private-pair hit, and
   source `151` has only partial direct private-pair hits.
   The row-pressure refinement in `docs/bootstrap-t12-row-pressure.md` splits
   the missing rows into deletion-closure-exposed, one-outside-label, and
   outside-pair cases for the next bridge attempt. The closure-exposed
   subpacket in `docs/bootstrap-t12-closure-exposed.md` isolates the two
   activation-ready deletion-closure rows as the smallest next lemma target.
   The one-outside-label subpacket in `docs/bootstrap-t12-one-outside.md`
   isolates the three singleton-support rows where a future bridge would need
   to force one outside label without relying on private-pair capacity.
   The outside-pair subpacket in `docs/bootstrap-t12-outside-pair.md` isolates
   the remaining pair-supported row, where private-pair capacity makes partial
   direct contact but still does not force the missing equality connector.
   The activation-support requirement ledger in
   `docs/bootstrap-t12-activation-requirements.md` separates the stored T12
   connector-pair and strict-edge endpoint requirements from the still-unproved
   row-forcing step, with source `151` row `7` as the main closure-exposure
   negative control.
   The bridge-target map in `docs/bootstrap-t12-bridge-target-map.md` joins the
   row-pressure, support, and activation ledgers into six explicit next-lemma
   targets: hard strict endpoint rows `151:7` and `151:8`, open connector-pair
   row `151:5`, and three relation-sufficient rows that still need row-forcing
   arguments.
   The hard strict-endpoint subpacket in
   `docs/bootstrap-t12-hard-strict-endpoints.md` isolates rows `151:7` and
   `151:8`, where strict-edge endpoint sets are still incomplete after closure
   and singleton-support checks.
   The open connector-pair subpacket in
   `docs/bootstrap-t12-open-connector-pair.md` isolates row `151:5`, where the
   connector pair `[7,8]` is still split across singleton support and partial
   closure evidence.
   The relation-sufficient row subpacket in
   `docs/bootstrap-t12-relation-sufficient-rows.md` isolates rows `81:3`,
   `81:8`, and `151:6`, where connector relation evidence is already present
   but row/rich-class forcing remains open.
   The focused `81:3` closure-target packet in
   `docs/bootstrap-t12-81-3-closure-target.md` is the first target in this
   loop: full-row closure exposure and relation sufficiency meet there, and
   the row supplies the final `T12/F16` connector only if a future bridge
   proves genuine row/rich-class forcing.
   The follow-up `81:3` rich-triple connector contract in
   `docs/bootstrap-t12-81-3-rich-triple-contract.md` reduces the next target:
   the stored T12 connector only needs witnesses `0` and `1` in one genuine
   rich class at center `3`.
   The order-resolved fixed-row escape audit in
   `docs/bootstrap-t12-81-3-order-escape.md` shows the current singleton-rich
   closure does not expose label `6` first: center `3` is the only initial
   activation from `[0,1,4]`, and label `6` is added later by trigger
   `[0,3,4]`. It now also records the same-center disjointness guard: if the
   source-`81` center-`6` fixed row `[0,3,4,7]` is preserved as a genuine
   class, no additional center-`6` class can contain the seed triple
   `[0,1,4]`. The next useful PR should leave fixed selected-row preservation
   and attack the genuine rich-class question directly: either exhibit a
   pre-`3` rich-class supply of label `6` that avoids the connector without
   preserving that center-`6` row, or prove no such supply can satisfy the
   minimal/rich-class hypotheses.
5. Classify Kalmanson inverse-pair templates from the C13/C19 all-order
   certificates and emit verifier-backed template records.
6. Audit `n=8` class `14` or the review-pending `n=9` vertex-circle checker
   with an independent input-data replay.

## Task CB-N9-T01 - Extract Vertex-Circle Self-Edge Template

Issue: none yet.

Read first:

- `docs/codex-strategy-instructions.md`
- `docs/n9-vertex-circle-template-lemma-catalog.md`
- `docs/n9-vertex-circle-t01-self-edge-lemma.md`
- `data/certificates/n9_vertex_circle_t01_self_edge_lemma_packet.json`
- `docs/n9-vertex-circle-exhaustive.md`

Commands:

```bash
python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
```

Expected artifacts:

- a proof-facing lemma note or update that states the exact incidence and
  cyclic-order hypotheses for the T01/F09 self-edge template;
- a minimal checker or checker update that verifies the compact template
  packet independently of the full exhaustive search;
- documentation that distinguishes the local template from any `n=9`
  completeness or global Erdos #97 claim.

Acceptance criteria:

- The lemma candidate does not enumerate all `n=9` selected-witness systems.
- The proof-facing text identifies the selected-distance quotienting and
  vertex-circle monotonicity used to force a self-edge.
- The checker treats the packet as input data and reports explicit uncertainty
  rather than silently accepting unsupported fields.
- The result remains review-pending unless independently reviewed.

Trust delta: may produce a reusable local obstruction template. It may not
promote the full `n=9` selected-witness result or alter global status.

Forbidden overclaiming text:

- "n=9 is proved"
- "the vertex-circle checker is independently reviewed"
- "this proves Erdos #97"

## Task CB-N9-T10 - Extract Vertex-Circle Strict-Cycle Template

Issue: none yet.

Read first:

- `docs/codex-strategy-instructions.md`
- `docs/n9-vertex-circle-template-lemma-catalog.md`
- `docs/n9-vertex-circle-t10-strict-cycle-lemma.md`
- `data/certificates/n9_vertex_circle_t10_strict_cycle_lemma_packet.json`
- `docs/n9-vertex-circle-exhaustive.md`

Commands:

```bash
python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_strict_cycle_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
```

Expected artifacts:

- a proof-facing lemma note or update that states the exact incidence and
  cyclic-order hypotheses for the T10/F12 strict-cycle template;
- a compact verifier that replays the quotient strict-cycle certificate from
  stored data;
- documentation that keeps local-core strict-cycle counts separate from
  full-assignment obstruction-shape counts.

Acceptance criteria:

- The lemma candidate states the directed quotient cycle and the exact local
  hypotheses that force it.
- The verifier is independent of the full exhaustive brancher.
- The result is scoped as a reusable obstruction template, not an `n=9`
  completeness proof.

Trust delta: may produce a reusable local strict-cycle obstruction template. It
may not promote the full `n=9` selected-witness result or alter global status.

Forbidden overclaiming text:

- "all strict cycles are classified" without the review-pending qualifier
- "n=9 is proved"
- "this proves Erdos #97"

## Task CB-FRAGILE-GEO - Add One Geometric Fragile-Cover Condition

Issue: none yet.

Read first:

- `docs/codex-strategy-instructions.md`
- `docs/minimal-fragile-cover-bridge.md`
- `src/erdos97/fragile_hypergraph.py`
- `scripts/check_fragile_hypergraph.py`
- `docs/stuck-set-miner.md`
- `docs/bootstrap-core-bridge.md`
- `src/erdos97/bootstrap_cores.py`

Commands:

```bash
python scripts/check_fragile_hypergraph.py --json
python scripts/check_fragile_hypergraph.py --blocks 2 --assert-ok --json
python scripts/check_bootstrap_core_bridge.py --assert-expected
python -m pytest tests/test_fragile_hypergraph.py -q
```

Expected artifacts:

- one documented geometric necessary condition for minimal counterexamples;
- checker support that can be run against the block-6 family, two disjoint
  block-6 families, and any current full-row extension survivors;
- a short report explaining which abstract family is newly rejected and why the
  condition is geometric rather than an arbitrary SAT filter.

Acceptance criteria:

- The condition is proved necessary for a minimal geometric counterexample.
- It rejects at least one abstract fragile-cover family that currently passes
  the pairwise/crossing checks.
- It remains labeled as a partial bridge unless it proves more.

Trust delta: may strengthen the minimal-counterexample bridge. It may not prove
Erdos #97 unless paired with a complete reduction and exact obstruction.

Forbidden overclaiming text:

- "fragile covers prove the theorem"
- "block-6 is impossible geometrically" without the stated new hypothesis
- "minimal counterexamples are ruled out"

## Task CB-83 - Decompose C19 Kalmanson Certificate

Issue: <https://github.com/davidiach/erdos97/issues/83>

Read first:

- `docs/round2/round2_merged_report.md`
- `docs/round2/kalmanson_distance_filter.md`
- `docs/kalmanson-two-order-search.md`
- `docs/kalmanson-certificate-diagnostics.md`
- `reports/c19_kalmanson_diagnostics.json`
- `data/certificates/round2/c19_kalmanson_known_order_unsat.json`
- `data/certificates/round2/c19_kalmanson_known_order_two_unsat.json`
- `data/certificates/c19_skew_all_orders_kalmanson_z3.json`

Commands:

```bash
python scripts/check_round2_certificates.py
python scripts/check_kalmanson_certificate.py data/certificates/round2/c19_kalmanson_known_order_two_unsat.json --summary-json
python scripts/check_kalmanson_two_order_z3.py --certificate data/certificates/c19_skew_all_orders_kalmanson_z3.json --assert-unsat
python scripts/analyze_kalmanson_certificates.py
```

Expected artifacts:

- a reproducible diagnostic script or update to an existing report generator;
- a checked JSON or Markdown report summarizing support groups, smaller
  dependencies, or negative results.
- optional all-order Z3 clause-template diagnostics such as
  `reports/c19_kalmanson_z3_clause_diagnostics.json`, kept separate from the
  underlying SMT replay certificate.

Acceptance criteria:

- The compact fixed-order two-inequality certificate, the earlier
  94-inequality certificate, and the all-order Z3 refinement certificate all
  remain valid.
- Any structural decomposition is reproducible without notebooks.
- Documentation keeps the fixed-order certificate, the all-order fixed-pattern
  obstruction, and the global Erdos #97 status separate.

Trust delta: may improve C19 certificate understanding. The all-order
fixed-pattern obstruction is already exact if the stored Z3 certificate
replays, but this may not promote any `n >= 9` finite case or Erdos
Problem #97.

Forbidden overclaiming text:

- "C19_skew proves Erdos #97"
- "all C19-like patterns are impossible"
- "this closes the frontier"

## Task CB-82 - Attack n=9 Base-Apex Low-Excess Ledgers

Issue: <https://github.com/davidiach/erdos97/issues/82>

Read first:

- `docs/n9-base-apex-frontier.md`
- `src/erdos97/n9_base_apex.py`
- `scripts/explore_n9_base_apex.py`
- `data/certificates/n9_vertex_circle_exhaustive.json`
- `docs/n9-vertex-circle-exhaustive.md`

Commands:

```bash
python scripts/explore_n9_base_apex.py
python scripts/check_n9_base_apex_low_excess_ledgers.py --check --json
python scripts/check_n9_base_apex_escape_budget.py --check --json
python scripts/check_n9_selected_baseline_d3_escape_class_crosswalk.py --check --json
python scripts/check_n9_base_apex_d3_escape_frontier_packet.py --check --json
python scripts/check_n9_base_apex_low_excess_escape_crosswalk.py --check --json
python scripts/check_n9_base_apex_d3_p19_incidence_capacity_pilot.py --check --json
python scripts/check_n9_base_apex_d3_incidence_capacity_packet.py --check --json
python scripts/check_n9_base_apex_d3_artifact_join.py --check --json
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
```

Expected artifacts:

- `data/certificates/n9_base_apex_low_excess_ledgers.json`, or an updated
  successor JSON/Markdown report listing which low-excess ledgers remain;
- optional successor diagnostics such as
  `data/certificates/n9_base_apex_escape_budget_report.json` that keep escape
  placement counts separate from geometric realizability;
- optional selected-baseline overlays such as
  `data/certificates/n9_selected_baseline_escape_budget_overlay.json` that
  compare the escape-budget motif map with the 184 pre-vertex-circle
  selected-witness assignments without treating selected-baseline empty slots
  as actual geometric capacity deficits;
- optional selected-baseline D=3 escape-class crosswalks such as
  `data/certificates/n9_selected_baseline_d3_escape_class_crosswalk.json`
  that count assignment/slot-choice landings by selected-baseline class and
  escape class without treating those landings as realizability counts or as
  comparable to common-dihedral profile/escape classes;
- optional sharp low-excess slices such as
  `data/certificates/n9_base_apex_d3_escape_slice.json` that couple the
  `E=6, D=3, r=3` profile/escape bookkeeping under common dihedral symmetry
  without claiming the slice is impossible or realizable;
- optional D=3 representative packets such as
  `data/certificates/n9_base_apex_d3_escape_frontier_packet.json` that expose
  compact profile-multiset by escape-class targets without certifying
  realizability or impossibility;
- optional P19 incidence-capacity pilots such as
  `data/certificates/n9_base_apex_d3_p19_incidence_capacity_pilot.json` that
  record the first D=3 packet band as capacity bookkeeping only, with
  realizability and incidence states left `UNKNOWN`;
- optional all-row D=3 incidence-capacity packets such as
  `data/certificates/n9_base_apex_d3_incidence_capacity_packet.json` that
  extend the same bookkeeping to all 88 D=3 packet rows while keeping
  realizability and incidence states `UNKNOWN`;
- optional cross-artifact D=3 consistency checkers such as
  `scripts/check_n9_base_apex_d3_artifact_join.py` that join the D=3 slice,
  representative packet, low-excess crosswalk, P19 pilot, and all-row
  incidence-capacity packet without claiming proof, counterexample,
  incidence-completeness, geometric realizability, or global status movement;
- optional low-excess profile/escape crosswalks such as
  `data/certificates/n9_base_apex_low_excess_escape_crosswalk.json` that keep
  ledger-to-escape bookkeeping separate from proof, counterexample, and
  geometric-realizability claims;
- checker updates that independently replay generated ledger arithmetic and
  motif counts from stored JSON.

Acceptance criteria:

- Remaining `E <= 6` / `D >= 3` or related low-excess cases are enumerated
  explicitly.
- Any new obstruction states exact incidence/order hypotheses.
- Any n=9 promotion remains review-pending and cannot update the
  source-of-truth or global status without a broader review decision.

Trust delta: may promote a conditional ledger obstruction or a review-pending
n=9 subcase. It may not promote the full n=9 selected-witness case without a
complete checked pipeline and independent review path.

Forbidden overclaiming text:

- "n=9 is proved"
- "the vertex-circle checker is independently reviewed"
- "this updates the official Erdos #97 status"

## Task CB-N10 - Audit n=10 Singleton Slices

Issue: none yet.

Read first:

- `docs/n10-vertex-circle-singleton-slices.md`
- `src/erdos97/generic_vertex_search.py`
- `src/erdos97/n10_vertex_circle_singletons.py`
- `scripts/check_n10_vertex_circle_singletons.py`
- `data/certificates/n10_vertex_circle_singleton_slices.json`

Commands:

```bash
python scripts/check_n10_vertex_circle_singletons.py --assert-expected --spot-check-row0 0 --spot-check-row0 63 --spot-check-row0 125
python -m pytest tests/test_n10_vertex_circle_singletons.py -q -m "artifact"
```

Expected artifacts:

- independent review notes for the generic checker and the imported singleton rows;
- selected repo-native spot checks for row0 singletons `0`, `63`, and `125`;
- optional second-implementation counts or a replayable terminal-conflict certificate.

Acceptance criteria:

- Row0 singleton coverage is exactly `[0,126)` with no hidden symmetry quotient.
- Partial vertex-circle pruning is verified to use only fixed rows/equalities.
- A second implementation or certificate replay checks all 126 slices.
- The result remains scoped as a draft review-pending n=10 finite-case artifact.

Trust delta: may promote the n=10 package from draft to review-pending finite
case artifact. It may not update the official/global status or the repo
source-of-truth strongest result by itself.

Forbidden overclaiming text:

- "n=10 is proved"
- "no bad decagon exists" without the review qualifier
- "this updates the official Erdos #97 status"

## Task CB-81 - Pilot Kalmanson Cyclic-Order CSP On C13

Issue: <https://github.com/davidiach/erdos97/issues/81>

Read first:

- `docs/kalmanson-two-order-search.md`
- `docs/c13-kalmanson-order-pilot.md`
- `docs/c13-kalmanson-prefix-branch-pilot.md`
- `scripts/check_kalmanson_two_order_search.py`
- `data/certificates/c13_sidon_all_orders_kalmanson_two_search.json`

Commands:

```bash
python scripts/check_kalmanson_certificate.py data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json --summary-json
python scripts/check_kalmanson_two_order_search.py --name C13_sidon_1_2_4_10 --n 13 --offsets 1,2,4,10 --assert-obstructed --assert-c13-expected --json
```

Expected artifacts:

- deterministic branch/pruning counts;
- exact certificates for closed branches when new branches are added;
- documentation separating fixed-order, all-order-for-one-pattern, and
  heuristic diagnostics.

Acceptance criteria:

- Rotation fixing is justified only by circulant translation symmetry.
- The all-order statement remains scoped to the fixed abstract
  `C13_sidon_1_2_4_10` selected-witness pattern.
- The C13 pilot is used only as a benchmark for larger sparse frontiers.

Trust delta: may improve or reproduce
`EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN` for C13. It may not prove
anything about abstract `C19_skew` or Erdos Problem #97.

Forbidden overclaiming text:

- "C13 proves the method works for C19"
- "Kalmanson closes the sparse frontier"
- "this is evidence of a general proof"

## Task CB-5 - Add Interval-Arithmetic Verifier

Issue: <https://github.com/davidiach/erdos97/issues/5>

Read first:

- `scripts/verify_candidate.py`
- `src/erdos97/search.py`
- `data/runs/best_B12_slsqp_m1e-6.json`
- `certificates/best_B12_certificate_template.json`
- `docs/exactification-plan.md`
- `docs/verification-contract.md`

Commands:

```bash
erdos97-search --verify data/runs/best_B12_slsqp_m1e-6.json --tol 1e-6
python scripts/verify_candidate.py data/runs/best_B12_slsqp_m1e-6.json
python -m pytest tests/test_search_hygiene.py -q
```

Expected artifacts:

- `src/erdos97/interval_verify.py` or an equivalent module;
- `scripts/interval_verify_candidate.py` or an equivalent CLI;
- tests that reject the saved B12 near-miss as a counterexample.

Current entrypoint:

```bash
python scripts/interval_verify_candidate.py data/runs/best_B12_slsqp_m1e-6.json
```

The current entrypoint certifies interval bounds only. It deliberately rejects
the saved B12 near-miss and reserves exact acceptance for rational-coordinate
inputs under `coordinates_exact`.

Acceptance criteria:

- The verifier distinguishes malformed input, floating near-miss,
  interval-certified strict convexity with uncertified equality, and exact or
  algebraic acceptance.
- JSON output includes validation errors, residual bounds, claim strength, and
  failure mode.
- No floating candidate is promoted to a counterexample.

Trust delta: may promote selected candidate checks from numerical evidence to
interval-certified validation only when interval hypotheses are actually met.
It may not certify exact distance equalities from floating residuals alone.

Forbidden overclaiming text:

- "B12 is a counterexample"
- "near miss"
- "intervals prove exact equality" unless the interval certificate really does

## Cross-Cutting Rules

- Run `make verify-fast` or the raw fast tier after code or documentation
  changes.
- Run `make verify-artifacts` or `make audit-artifacts` before finite-case,
  certificate, or public theorem-style updates.
- Update `README.md`, `STATE.md`, `RESULTS.md`, and `metadata/erdos97.yaml`
  together only when a task changes source-of-truth status.
- Keep archived/provenance statements marked when superseded.
- Do not prepare OEIS submissions from AI-generated output.
