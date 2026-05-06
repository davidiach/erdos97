# Codex Backlog

Status: operational planning guidance only; not mathematical evidence.

Live open issues were checked through GitHub on 2026-05-04. This backlog is a
Codex-facing companion to `docs/review-priorities.md`; it does not change the
repository claims. No general proof and no counterexample are claimed, and the
official/global status remains falsifiable/open unless manually rechecked and
updated from the official source.

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

Acceptance criteria:

- The compact fixed-order two-inequality certificate, the earlier
  94-inequality certificate, and the all-order Z3 refinement certificate all
  remain valid.
- Any structural decomposition is reproducible without notebooks.
- Documentation keeps the fixed-order certificate, the all-order fixed-pattern
  obstruction, and the global Erdos #97 status separate.

Trust delta: may improve C19 certificate understanding. The all-order
fixed-pattern obstruction is already exact if the stored Z3 certificate
replays, but this may not promote any `n >= 9` finite case or Erdos Problem
#97.

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
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
```

Expected artifacts:

- `data/certificates/n9_base_apex_low_excess_ledgers.json`, or an updated
  successor JSON/Markdown report listing which low-excess ledgers remain;
- checker updates that independently replay generated ledger arithmetic and
  motif counts from stored JSON.

Acceptance criteria:

- Remaining `E <= 6` / `D >= 3` or related low-excess cases are enumerated
  explicitly.
- Any new obstruction states exact incidence/order hypotheses.
- The n=9 status is not promoted unless every required case is certified.

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
python scripts/check_n10_vertex_circle_singletons.py --assert-expected --spot-check-generic
python -m pytest tests/test_n10_vertex_circle_singletons.py -q -m "artifact"
```

Expected artifacts:

- independent review notes for the generic checker and the imported singleton rows;
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
