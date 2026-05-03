# Codex Goal Log - Erdos Problem #97

Long-running goal: work toward either a complete proof of Erdos Problem #97
under the repository's strictly convex finite-polygon selected-witness
formulation, or an exact independently checkable counterexample satisfying the
repository verification contract.

This log is a research record. It does not claim a general proof or a
counterexample.

## Session 2026-05-03

### Branch and Baseline Status

- Required branch: `codex/goal-erdos97-proof-or-counterexample`.
- Initial branch found: `main`.
- Initial working tree status: one unstaged pre-existing edit in
  `tests/test_metric_order_lp.py`.
- Branch action: created and switched to
  `codex/goal-erdos97-proof-or-counterexample`, preserving the working tree.
- Remote sync: `git fetch origin` completed after elevated permission was
  needed to write `.git/FETCH_HEAD`.
- Current branch after setup: `codex/goal-erdos97-proof-or-counterexample`.
- `reports/codex_goal_erdos97_log.md` did not exist at session start.
- Recent checkout head: `f4b30cd add C13 Kalmanson pilot certificate`.

### Files Read

Required orientation files:

- `AGENTS.md`
- `README.md`
- `STATE.md`
- `RESULTS.md`
- `docs/index.md`
- `docs/claims.md`
- `docs/failed-ideas.md`
- `docs/canonical-synthesis.md`
- `docs/verification-contract.md`
- `docs/candidate-patterns.md`
- `docs/exactification-plan.md`
- `docs/reviewer-guide.md`
- `docs/review-priorities.md`
- `docs/upstream-alignment.md`
- `metadata/erdos97.yaml`

Round-two and Kalmanson-focused files:

- `docs/round2/round2_merged_report.md`
- `docs/round2/kalmanson_distance_filter.md`
- `docs/round2/do_not_repeat_round3.md`
- `docs/round2/ptolemy_log_method_note.md`
- `docs/kalmanson-c13-pilot.md` was identified as relevant for follow-up.
- `data/certificates/c13_sidon_order_survivor_kalmanson_unsat.json`
- `reports/c19_kalmanson_diagnostics.json`
- `reports/check_round2_certificates_summary.json`

Relevant scripts, source, and tests:

- `pyproject.toml`
- `scripts/find_kalmanson_certificate.py`
- `scripts/check_kalmanson_certificate.py`
- `scripts/check_round2_certificates.py`
- `scripts/check_sparse_order_survivors.py`
- `scripts/check_metric_order_lp.py`
- `src/erdos97/search.py`
- `src/erdos97/pattern_io.py`
- `src/erdos97/altman_diagonal_sums.py`
- `src/erdos97/vertex_circle_order_filter.py`
- `src/erdos97/metric_order_lp.py`
- `tests/test_kalmanson_certificate.py`
- `tests/test_round2_package.py`
- `tests/test_sparse_order_survivors.py`
- `tests/test_sidon_patterns.py`
- `tests/test_metric_order_lp.py`

GitHub issue context, via the GitHub connector:

- Open issue #5: interval-arithmetic verifier for convexity and distance
  equations.
- Open issue #81: pilot Kalmanson cyclic-order CSP on C13.
- Open issue #82: attack n=9 base-apex low-excess ledgers.
- Open issue #83: decompose C19 Kalmanson certificate and plan abstract-order
  search.

### Current Known Exact Results

- No general proof and no counterexample are claimed.
- Official/global status is falsifiable/open; metadata records last official
  status check as 2026-04-30.
- The selected-witness method rules out `n <= 8` in a repo-local,
  machine-checked finite-case sense, pending independent review before
  paper-style claims.
- The `n=7` equality case is reproduced by Fano enumeration and odd
  perpendicularity cycles.
- The `n=8` pipeline reduces necessary incidence survivors to 15 canonical
  classes and kills them by exact cyclic-order or algebraic obstructions.
- Fixed-pattern exact filters kill several registered patterns, including
  `B12_3x4_danzer_lift`, `B20_4x5_FR_lift`, `C17_skew`, `P18_parity_balanced`,
  and `P24_parity_balanced`.
- `C19_skew` is killed in natural order by Altman sums and in one registered
  non-natural cyclic order by an exact 94-inequality Kalmanson/Farkas
  certificate. This is fixed-order only.
- `C13_sidon_1_2_4_10` is killed in natural order by Altman linear
  certificates and in one registered non-natural cyclic order by an exact
  34-inequality Kalmanson/Farkas certificate. This is fixed-order only.

### Current Numerical or Heuristic Evidence

- Historical `B12_3x4_danzer_lift` near-miss remains numerical evidence only
  and is attached to a fixed selected pattern now killed exactly.
- `C13_sidon_1_2_4_10` SLSQP runs plateau at large residuals under strict
  convexity margins; this is NUMERICAL_EVIDENCE, not an obstruction proof.
- Metric-order LP and Ptolemy/NLP diagnostics on registered sparse orders are
  diagnostics only unless exactified.

### Failed Approaches Not to Repeat

- Weak witness definitions that do not require one common circle.
- Forced double regularity outside the saturated small cases.
- Generic Jacobian rank as a nonexistence proof.
- Circumcenter-inside-witness-hull arguments.
- Middle-neighbor forest arguments.
- Uniform-radius shortcuts using `2n-7` as if it were an upper bound.
- Treating fixed-order Kalmanson certificates, random order kills, or numerical
  residual plateaus as all-order obstructions.
- Reusing phi4, mutual-rhombus, or vertex-circle filters as a new round-three
  idea without a new exact ingredient.

### Baseline Commands

- `git status` on initial `main`: one unstaged edit in
  `tests/test_metric_order_lp.py`.
- `git branch --show-current` on initial checkout: `main`.
- `git fetch origin`: first attempt failed with `Operation not permitted` on
  `.git/FETCH_HEAD`; elevated retry succeeded.
- `git switch -c codex/goal-erdos97-proof-or-counterexample`: succeeded.
- `python -m pytest`: unavailable because `python` is not on PATH.
- `python3 -m pytest`: failed during collection in the system Python 3.9.6
  because SciPy is missing.
- `.venv/bin/python -m pytest`: passed, `172 passed, 8 deselected` in 25.93s.

### Verification Commands After This Checkpoint

- `.venv/bin/python scripts/analyze_kalmanson_certificates.py --assert-expected`:
  passed.
- `.venv/bin/python -m pytest tests/test_kalmanson_certificate_diagnostics.py tests/test_kalmanson_certificate.py tests/test_round2_package.py`:
  passed, `8 passed`.
- `.venv/bin/python scripts/check_text_clean.py`: passed.
- `.venv/bin/python scripts/check_status_consistency.py`: passed.
- `git diff --check`: passed.
- `.venv/bin/python -m pytest -q`: passed, `173 passed, 8 deselected`.

### Publish / PR Checkpoint

- Local commit: `d2a64e7 research: add kalmanson certificate diagnostics`.
- `gh --version`: available, `gh version 2.87.3`.
- `gh auth status`: failed because the stored token for account `oskarasi` is
  invalid.
- `git push -u origin codex/goal-erdos97-proof-or-counterexample`: failed with
  GitHub `403` permission denial for account `oskarasi`.
- Fallback publication used the GitHub connector:
  - created remote branch `codex/goal-erdos97-proof-or-counterexample` from
    `origin/main` at `f4b30cd722ceadd36a864feafcb37cb600e655d6`;
  - wrote the checkpoint files to that branch;
  - opened draft PR #86:
    `https://github.com/davidiach/erdos97/pull/86`.
- Remote PR head after connector publication:
  `2cc8ceb3a4224871dcb1910aa552e154b591f53a`.
- Note: because local `git push` was blocked and the GitHub connector created
  commits through the API, the local branch commit SHA and the remote PR head
  SHA differ even though the intended file diff is the same.

### Chosen Research Direction

Checkpoint direction: exact Kalmanson certificate diagnostics supporting open
issues #81 and #83.

Rationale:

- The all-order C13/C19 problem is too large for an unfocused first step.
- The repo already has exact fixed-order Kalmanson certificates but only a
  C19-specific static diagnostic artifact.
- A deterministic analyzer that validates certificates and summarizes support
  structure, gap patterns, distance-class cancellations, and rank data gives a
  reproducible base for later C13 cyclic-order search and C19 decomposition.
- This is a checkpoint artifact only. It does not change the global status and
  does not claim an abstract all-order obstruction.

### Iteration History

1. Enforced branch safety and moved off `main`.
2. Completed orientation over state, claim, failed-route, round-two, script,
   source, test, and GitHub issue context.
3. Established the test baseline in the existing `.venv`.
4. Selected exact Kalmanson certificate diagnostics as the focused checkpoint.
5. Added `scripts/analyze_kalmanson_certificates.py`, which rechecks the
   registered fixed-order C13 and C19 Kalmanson/Farkas certificates and emits
   deterministic support diagnostics.
6. Generated `reports/kalmanson_certificate_diagnostics.json`.
7. Added `tests/test_kalmanson_certificate_diagnostics.py`.
8. Added `docs/kalmanson-certificate-diagnostics.md` and linked it from
   `docs/index.md`; also noted the generalized diagnostic in
   `docs/round2/round2_merged_report.md`.

### Artifacts Produced

- This running log.
- `scripts/analyze_kalmanson_certificates.py`
- `reports/kalmanson_certificate_diagnostics.json`
- `tests/test_kalmanson_certificate_diagnostics.py`
- `docs/kalmanson-certificate-diagnostics.md`

### Open Risks and Next Steps

- Keep the pre-existing `tests/test_metric_order_lp.py` edit separate unless it
  is intentionally adopted after review.
- The local branch is not tracking the connector-published remote branch state;
  reconcile carefully before the next local push attempt.
- Next mathematical iteration: use the support diagnostics to guide a bounded
  C13 cyclic-order pilot with exact certificates for closed branches.
