# Reviewer guide for Erdos Problem #97 finite-case artifacts

## What this repo claims

- No general proof and no counterexample are claimed.
- The selected-witness method rules out `n <= 8` in a repo-local,
  machine-checked finite-case sense.

## What this repo does not claim

- It does not claim to solve Erdos Problem #97.
- It does not claim that numerical near-misses are counterexamples.
- It does not claim the `n=8` artifact has had independent external review.
- It does not claim that the round-two `C19_skew` Kalmanson certificate kills
  all cyclic orders of the abstract pattern.
- It records a separate Z3 certificate that kills all cyclic orders for the
  fixed abstract `C19_skew` pattern, but this still is not a proof of Erdos
  Problem #97.
- It does not claim that the exact all-order C13 result proves Erdos Problem
  #97; that result is only for one fixed abstract selected-witness pattern.

## Fast reproduction commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
make verify-fast
```

If `make` is not available, run:

```bash
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
python scripts/check_artifact_provenance.py
git diff --check
python -m ruff check .
python -m pytest -q
```

## Artifact audit commands

Run these before finite-case, certificate, or public theorem-style updates:

```bash
make verify-artifacts
```

For CI-style audit metadata, run:

```bash
make audit-artifacts
```

The `audit-artifacts` target includes the dated official-status consistency
check, so this audit path is stricter than the default fast tier.

If `make` is unavailable, treat `Makefile` and
`scripts/run_artifact_audit.py` as the source of truth for the current raw
command set. To print the registered artifact-audit command list without
running the audit, including the two `audit-artifacts` preflight checks, use:

```bash
python scripts/run_artifact_audit.py --list-commands
```

The following hand-maintained command excerpt is retained for reviewer
orientation:

```bash
python scripts/check_status_consistency.py --max-official-status-age-days 90
python scripts/check_artifact_provenance.py
python scripts/independent_check_n8_artifacts.py --check --json
python scripts/enumerate_n8_incidence.py --summary
python scripts/analyze_n8_exact_survivors.py --check --json
python scripts/check_round2_certificates.py
python scripts/check_kalmanson_certificate.py data/certificates/round2/c19_kalmanson_known_order_two_unsat.json --summary-json
python scripts/check_kalmanson_certificate.py data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json --summary-json
python scripts/check_kalmanson_two_order_search.py --name C13_sidon_1_2_4_10 --n 13 --offsets 1,2,4,10 --assert-obstructed --assert-c13-expected --json
python scripts/check_kalmanson_two_order_z3.py --certificate data/certificates/c19_skew_all_orders_kalmanson_z3.json --assert-unsat
python scripts/analyze_kalmanson_z3_clauses.py --assert-expected --check-artifact reports/c19_kalmanson_z3_clause_diagnostics.json
python scripts/export_c19_kalmanson_order_cnf.py --assert-expected --check-artifact reports/c19_kalmanson_order_cnf_summary.json
python scripts/probe_c19_proof_tooling.py --check-c19-cnf-summary --json
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
python scripts/independent_n9_vertex_circle_recheck.py --json
python scripts/n9_vertex_circle_minimal_cores.py --check --assert-expected --json
python scripts/analyze_n9_vertex_circle_obstruction_shapes.py --check --assert-expected --json
python scripts/analyze_n9_vertex_circle_motif_families.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_local_core_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_core_templates.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_frontier_motif_classification.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_self_edge_path_join.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_self_edge_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_strict_cycle_path_join.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_strict_cycle_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_local_lemmas.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_focused_minireplay_crosswalk.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_local_lemma_simple_replay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_local_lemma_replay_crosswalk.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_exhaustive_local_lemma_crosswalk.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t01_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t02_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t03_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t04_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t04_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t05_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t05_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t06_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t06_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t07_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t07_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t08_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t08_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t09_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t09_self_edge_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t10_strict_cycle_minireplay.py --check --assert-expected --json
python scripts/check_n9_t10_paired_square_entry.py --check --assert-expected --json
python scripts/check_relation_skeleton_catalog.py --check --assert-expected --json
python scripts/check_relation_skeleton_local_lemma_crosswalk.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_t11_strict_cycle_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t11_strict_cycle_minireplay.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t12_strict_cycle_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_t12_strict_cycle_minireplay.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_product_cancellations.py --check --json
python scripts/check_n9_row_ptolemy_family_signatures.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_order_sensitivity.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_order_admissible_census.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_admissible_gap_replay.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_gap_self_edge_cores.py --check --assert-expected --json
python scripts/check_n9_base_apex_low_excess_ledgers.py --check --json
python scripts/check_n9_base_apex_escape_budget.py --check --json
python scripts/check_n9_selected_baseline_escape_budget_overlay.py --check --json
python scripts/check_n9_d3_escape_slice.py --check --json
python scripts/check_n10_vertex_circle_singletons.py --assert-expected --spot-check-row0 0 --spot-check-row0 63 --spot-check-row0 125
python scripts/check_n10_secondary_singleton_replay.py --check --assert-expected --json
```

The default pytest configuration excludes tests marked `artifact`, `slow`, or
`exhaustive`. Use `python -m pytest -q -m ""` when intentionally replaying the
full marker set.

For a version-matched reproduction run, replace `pip install -e .[dev]` with:

```bash
pip install -r requirements-lock.txt
pip install -e . --no-deps
```

## Expected `n=8` outputs

For `python scripts/enumerate_n8_incidence.py --summary`, expected invariants:

- status is `INCIDENCE_COMPLETENESS`;
- `canonical_survivor_class_count` is `15`;
- `matches_existing_reconstructed_survivors` is `true`;
- all necessary incidence survivors are reduced to the 15 canonical classes in
  `data/incidence/n8_incidence_completeness.json` and
  `data/incidence/n8_reconstructed_15_survivors.json`.

For `python scripts/analyze_n8_exact_survivors.py --check --json`, expected
invariants:

- status is `exact_obstruction_artifact_pending_independent_review`;
- the per-class obstruction status is exact, while the aggregate `n=8`
  exclusion remains a repo-local machine-checked finite-case artifact pending
  independent review;
- `survivor_classes` is `15`;
- `cyclic_order_remaining_count` is `14`, with class `12` killed by cyclic
  order noncrossing;
- classes `3`, `4`, `5`, and `14` report their named exact certificates as
  verified;
- the `pb_y2_span_ids_verified` list contains ten classes;
- the final obstruction pass is exact and does not rely on floating-point
  equality;
- certificate data agrees with `certificates/n8_exact_analysis.json`.

## Files to inspect first

1. `STATE.md`
2. `RESULTS.md`
3. `docs/n7-fano-enumeration.md`
4. `docs/n8-proof-trail.md`
5. `docs/n8-incidence-enumeration.md`
6. `docs/n8-exact-survivors.md`
7. `docs/round2/round2_merged_report.md`
8. `docs/verification-contract.md`
9. `docs/n8-geometric-proof.md`
10. `docs/review-priorities.md`

For the joined `n <= 8` review route, start with
`docs/n8-proof-trail.md`. It separates the geometric octagon trap, the
selected-witness finite artifact, and the literature-backed shortcut while
preserving the repo-local status boundary.

## Review target A - `n=7`

Primary reference: `docs/n7-fano-enumeration.md`.

Check:

- the Fano/equality reduction;
- the enumeration of labelled/pointed families;
- the cyclic-dihedral reduction;
- the odd-cycle perpendicularity obstruction.

## Review target B - `n=8` incidence completeness

Check:

- derivation of indegree regularity from the column-pair cap;
- exhaustive enumeration assumptions;
- canonicalization under relabeling;
- reproducibility of the 15 survivor classes.

## Review target C - `n=8` exact survivor obstruction

Check:

- the class killed by cyclic-order noncrossing;
- the classes killed by perpendicular-bisector algebra;
- the classes requiring full equal-distance algebra;
- the strict-convexity obstruction cases;
- the archived-ID provenance mapping.

## Review target D - `n=8` geometric proof note

Check:

- the base-apex lemma and its strict-convexity hypothesis;
- the isosceles-triangle count and octagon equality saturation;
- the length-2 diagonal argument forcing equal side lengths;
- the length-3 diagonal argument forcing a cover of adjacent turn-angle pairs;
- the exterior-turn contradiction.

## Review target E - round-two fixed-order Kalmanson certificate

Check:

- that `scripts/check_kalmanson_certificate.py` reconstructs the selected
  distance quotient from the declared `C19_skew` offsets;
- that every listed quadrilateral is in the declared cyclic order;
- that the compact two-inequality certificate has positive integer weights and
  zero total coefficient sum;
- that the earlier 94-inequality certificate remains valid as provenance;
- that the weighted coefficient sum is exactly zero;
- that the result is recorded only as a fixed-order obstruction.

## Review target F - fixed-pattern all-order two-certificate searches

Check:

- that `scripts/check_kalmanson_two_order_search.py` fixes label `0` only by
  translation symmetry for the circulant pattern;
- that the search/Z3 results are all-order statements only for their fixed
  abstract selected-witness patterns, such as `C13_sidon_1_2_4_10` and
  `C19_skew`;
- that the result is not described as a general proof of Erdos Problem #97.

## Review target G - `n=9` local-lemma audit path

Primary references:

- `docs/n9-review-packet.md`
- `docs/n9-vertex-circle-local-lemma-review-packet.md`
- `docs/n9-vertex-circle-local-lemmas.md`
- `docs/relation-skeleton-catalog.md`
- `docs/n9-reduction-chain.md`
- `scripts/check_n9_vertex_circle_local_lemma_audit_path.py`

Run:

```bash
python scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --summary-json
```

The compact `--summary-json` output includes the adjacent handoff checks, a
per-layer source-artifact contract summary, and an input-manifest summary. Use
`--json` instead when the full layer and manifest records are needed for
audit.

Check:

- that the focused packet/catalog, focused mini-replay, aggregate/simple
  replay, exhaustive/local-lemma, and relation-skeleton/local-lemma handoffs
  agree on the same 12 templates, 16 families, and 184 frontier assignments;
- that the relation-skeleton/closed-descent companion stays an accounting
  crosswalk, not a replacement for packet soundness review;
- that manifest role, digest, header, provenance, metadata, claim, and
  consistency contracts localize drift to a specific input layer;
- that the audit path is described only as review-pending cross-artifact
  bookkeeping, not as local-lemma completeness, brancher soundness, a proof of
  `n=9`, or an official/global status update.

## Review target H - `n=9` base-apex audit path

Primary references:

- `docs/n9-base-apex-frontier.md`
- `docs/n9-base-apex-d3-p19-degree-obstruction.md`
- `docs/n9-base-apex-d3-p20-residue-obstruction.md`
- `scripts/check_n9_base_apex_audit_path.py`

Run:

```bash
python scripts/check_n9_base_apex_audit_path.py --check --summary-json
```

Check:

- that the low-excess ledger, escape budget, low-excess ladder, D=3 artifact
  stack, selected-baseline D=3 crosswalk, and review-pending vertex-circle
  frontier agree across the named handoff checks;
- that the D=3 packet rows keep realizability and incidence states `UNKNOWN`,
  and that selected-baseline landings are not treated as geometric
  realizability counts;
- that the P19 and P20 finite profile-capacity obstructions remain scoped to
  their exact packet rows, not to all low-excess profiles or all `n=9`
  selected-witness systems;
- that the audit path is described only as finite bookkeeping over existing
  artifacts, not as incidence completeness, geometric realizability,
  a proof of `n=9`, a counterexample, or an official/global status update.

## Review target I - `n=10` singleton-slice draft

Primary references:

- `docs/n10-vertex-circle-singleton-review-packet.md`
- `docs/n10-vertex-circle-singleton-slices.md`
- `scripts/check_n10_singleton_input_audit.py`
- `scripts/check_n10_vertex_circle_singletons.py`
- `scripts/check_n10_secondary_singleton_replay.py`

Run:

```bash
python scripts/check_n10_singleton_input_audit.py --check --assert-expected --json
python scripts/check_n10_vertex_circle_singletons.py --assert-expected --spot-check-row0 0 --spot-check-row0 63 --spot-check-row0 125
python scripts/check_n10_secondary_singleton_replay.py --check --assert-expected --json
```

Check:

- that row0 singleton coverage is exactly `[0,126)` with no hidden symmetry
  quotient;
- that the input-data audit is only stored-data validation, not a terminal
  conflict replay;
- that the selected spot replay covers only rows `0`, `63`, and `125`;
- that the secondary replay covers only rows `0..4` and uses an extra
  necessary filter;
- that all-slice independent replay, terminal-conflict certificates, or an
  independently reviewed replacement lemma are still required before the n=10
  package can move beyond draft.

## Known weak points / independent review requests

- Independent audit of `scripts/enumerate_n8_incidence.py`.
- Independent audit of exact certificates, especially classes `3`, `4`, and
  `14` if those remain singled out in `RESULTS.md`.
- A minimal standalone class `14` checker would be especially valuable because
  that obstruction combines Groebner reasoning with a strict-interior
  conclusion.
- A Z3-independent replay path for the C19 all-order Kalmanson order UNSAT
  certificate would reduce single-solver trust. A checkable SAT/SMT proof or a
  pure finite-order checker is preferred over an UNSAT core alone.
- Independent review of the `n=9` local-lemma audit path should check packet
  soundness, mini-replay soundness, local-lemma completeness, strict-edge
  geometry, selected-distance quotient soundness, and brancher coverage before
  any `n=9` promotion.
- Independent review of the `n=9` base-apex audit path should check the
  low-excess ledger arithmetic, D=3 handoffs, selected-baseline crosswalk, and
  vertex-circle frontier connection before using it as bridge evidence.
- Independent review of the `n=10` singleton-slice draft should check the
  primary search implementation, row0 singleton split, partial vertex-circle
  pruning, and all-slice replay gap before any n=10 promotion.
- Independent reproduction of `certificates/n8_exact_analysis.json`.
- A Lean, SMT, interval, or algebraic certificate checker would be high value.

## Reporting review findings

Open an issue or PR that states:

- which artifact was reviewed;
- exact command run;
- environment details;
- whether the result reproduced;
- any mathematical or implementation gap found.
