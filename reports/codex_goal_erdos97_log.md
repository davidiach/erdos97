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

## Session 2026-05-03, Iteration 2

### Branch and Local State

- Current branch: `codex/goal-erdos97-proof-or-counterexample`.
- `git fetch origin codex/goal-erdos97-proof-or-counterexample` succeeded.
- Local HEAD tree and `origin/codex/goal-erdos97-proof-or-counterexample` tree
  matched after the fetch, even though commit histories differ.
- The pre-existing unstaged edit in `tests/test_metric_order_lp.py` is still
  present and is still treated as out of scope for this iteration.

### Focus

Bounded C13 Kalmanson cyclic-order pilot.

This is a direct follow-up to open issue #81 and to the previous Kalmanson
certificate diagnostics checkpoint. The goal is not to prove the all-order C13
case, but to make the first small fixed-order pilot reproducible and
independently checkable.

### Work Performed

- Added `scripts/pilot_c13_kalmanson_orders.py`.
- Added `data/certificates/c13_kalmanson_bounded_order_pilot.json`.
- Added `tests/test_c13_kalmanson_order_pilot.py`.
- Added `docs/c13-kalmanson-order-pilot.md`.
- Linked the pilot from `docs/index.md` and `docs/kalmanson-c13-pilot.md`.

The pilot normalizes seven pinned cyclic orders by rotation/reflection and
runs the fixed-order Kalmanson/Farkas certificate finder on each unique order.
All seven unique orders close by exact positive-integer certificates. The
committed artifact stores compact checked summaries; the script can emit the
full certificate objects by omitting `--summary-only`.

### Verification Commands

- `.venv/bin/python scripts/pilot_c13_kalmanson_orders.py --assert-expected --summary-only --out data/certificates/c13_kalmanson_bounded_order_pilot.json`:
  passed.
- `.venv/bin/python scripts/pilot_c13_kalmanson_orders.py --assert-expected`:
  passed and emitted full certificate objects to stdout/table mode.
- `.venv/bin/python scripts/pilot_c13_kalmanson_orders.py --assert-expected --summary-only`:
  passed.
- `.venv/bin/python -m pytest tests/test_c13_kalmanson_order_pilot.py tests/test_kalmanson_certificate.py`:
  passed, `7 passed`.
- `.venv/bin/python scripts/check_text_clean.py`: passed.
- `.venv/bin/python scripts/check_status_consistency.py`: passed.
- `git diff --check`: passed.
- `.venv/bin/python -m pytest -q`: passed, `174 passed, 8 deselected`.

### Claim Boundary

- Trust label: `EXACT_CERTIFICATE_DIAGNOSTIC`.
- This kills only the seven fixed cyclic orders encoded in the artifact.
- No general proof, no counterexample, and no all-order C13 obstruction are
  claimed.

### Publish / PR Checkpoint

- Local commit: `e07a6b1 research: add bounded c13 kalmanson order pilot`.
- `git push -u origin codex/goal-erdos97-proof-or-counterexample`: failed with
  GitHub `403` permission denial for account `oskarasi`.
- Fallback publication used the GitHub connector to update draft PR #86:
  `https://github.com/davidiach/erdos97/pull/86`.
- A connector-side bad script blob was detected by fetching the PR branch and
  comparing tree hashes; the PR branch was repaired through a follow-up
  connector commit before updating the PR body.
- After the repair fetch, the local `HEAD` tree and
  `origin/codex/goal-erdos97-proof-or-counterexample` tree matched.

## Session 2026-05-03, Iteration 3

### Branch and Local State

- Current branch: `codex/goal-erdos97-proof-or-counterexample`.
- `git fetch origin` succeeded.
- Local `HEAD` tree and
  `origin/codex/goal-erdos97-proof-or-counterexample` tree matched before
  starting this iteration.
- The pre-existing unstaged edit in `tests/test_metric_order_lp.py` is still
  present and is still treated as out of scope.

### Focus

Bounded C13 Kalmanson prefix brancher.

This follows open issue #81 more closely than the pinned-order pilot by adding
reflection-prefix pruning before LP/certificate calls. It is still a bounded
pilot, not an all-order C13 search.

### Work Performed

- Added `scripts/branch_c13_kalmanson_prefix_pilot.py`.
- Added `data/certificates/c13_kalmanson_prefix_branch_pilot.json`.
- Added `tests/test_c13_kalmanson_prefix_branch_pilot.py`.
- Added `docs/c13-kalmanson-prefix-branch-pilot.md`.
- Linked the brancher from `docs/index.md`, `docs/c13-kalmanson-order-pilot.md`,
  and `docs/kalmanson-c13-pilot.md`.

The brancher fixes label `0`, branches on two labels from each side of the
cyclic order, prunes reflection duplicates as soon as the boundary prefix is
decided, and then runs a deterministic budget of twelve fixed-order
Kalmanson/Farkas certificate searches on ascending completions. The default
run has 11,880 raw boundary states, 5,940 canonical states after reflection
pruning, 66 prefix extensions pruned before LP, and 12/12 sampled completions
closed by exact positive-integer certificates.

### Verification Commands

- `.venv/bin/python scripts/branch_c13_kalmanson_prefix_pilot.py --assert-expected --out data/certificates/c13_kalmanson_prefix_branch_pilot.json`:
  passed.
- `.venv/bin/python scripts/branch_c13_kalmanson_prefix_pilot.py --assert-expected --include-certificates --out /tmp/c13_prefix_branch_full_certificates.json`:
  passed.
- `.venv/bin/python -m pytest tests/test_c13_kalmanson_prefix_branch_pilot.py tests/test_c13_kalmanson_order_pilot.py tests/test_kalmanson_certificate.py`:
  passed, `8 passed`.
- `.venv/bin/python scripts/check_text_clean.py`: passed.
- `.venv/bin/python scripts/check_status_consistency.py`: passed.
- `git diff --check`: passed.
- `.venv/bin/python -m pytest -q`: passed, `175 passed, 8 deselected`.

### Claim Boundary

- Trust label: `EXACT_CERTIFICATE_DIAGNOSTIC`.
- Reflection pruning is search accounting, not a geometric obstruction.
- Exact obstructions apply only to the twelve sampled fixed cyclic orders in
  the artifact.
- No general proof, no counterexample, and no all-order C13 obstruction are
  claimed.

### Publish / PR Checkpoint

- Local commit: `96400f9 research: add c13 kalmanson prefix branch pilot`.
- `git push -u origin codex/goal-erdos97-proof-or-counterexample`: failed with
  GitHub `403` permission denial for account `oskarasi`.
- Fallback publication used the GitHub connector to update draft PR #86:
  `https://github.com/davidiach/erdos97/pull/86`.
- Connector-side commit:
  `83154407c7ffabed38d0018a2fa4fb5c34a54091`.
- After fetching the PR branch, local `HEAD` tree and
  `origin/codex/goal-erdos97-proof-or-counterexample` tree both resolved to
  `5ea9cacb9e71cc53edf900068f6fcacddf22d475`; `git diff --stat
  HEAD..origin/codex/goal-erdos97-proof-or-counterexample` was empty.
- PR title/body updated to cover the prefix-branch pilot and its claim
  boundary.

## Session 2026-05-03, Iteration 4

### Branch and Local State

- Current branch: `codex/goal-erdos97-proof-or-counterexample`.
- `git fetch origin` succeeded before this iteration.
- The pre-existing unstaged edit in `tests/test_metric_order_lp.py` is still
  present and is still treated as out of scope.

### Focus

Partial-branch C13 Kalmanson closures.

This strengthens the previous prefix-branch pilot by replacing sampled full
cyclic-order completions with certificates that use only Kalmanson
inequalities forced by a two-sided boundary prefix. A closed prefix branch is
therefore killed for every completion of that prefix.

### Work Performed

- Added `scripts/certify_c13_kalmanson_partial_branches.py`.
- Added `data/certificates/c13_kalmanson_partial_branch_closures.json`.
- Added `tests/test_c13_kalmanson_partial_branches.py`.
- Added `docs/c13-kalmanson-partial-branch-closures.md`.
- Linked the partial-branch pass from `docs/index.md`,
  `docs/c13-kalmanson-prefix-branch-pilot.md`,
  `docs/c13-kalmanson-order-pilot.md`, and `docs/kalmanson-c13-pilot.md`.

The scan uses the 5,940 canonical two-boundary-pair states. For each branch,
it keeps only the 170 Kalmanson inequalities whose quadrilateral order is
forced by the prefix. Exact positive-integer Farkas certificates close 5,108
branches; 832 two-boundary-pair prefixes remain unclosed by this pass. The
compact artifact records closure counts, support-size histograms, twelve
checked certificate examples, and a digest plus first/last windows for the
832 unclosed branch labels.

### Verification Commands

- `.venv/bin/python scripts/certify_c13_kalmanson_partial_branches.py --assert-expected --out data/certificates/c13_kalmanson_partial_branch_closures.json`:
  passed.
- `.venv/bin/python -m pytest tests/test_c13_kalmanson_partial_branches.py`:
  passed, `2 passed`.
- `.venv/bin/python -m pytest tests/test_c13_kalmanson_partial_branches.py tests/test_c13_kalmanson_prefix_branch_pilot.py tests/test_c13_kalmanson_order_pilot.py tests/test_kalmanson_certificate.py`:
  passed, `10 passed`.
- `.venv/bin/python scripts/check_text_clean.py`: passed.
- `.venv/bin/python scripts/check_status_consistency.py`: passed.
- `git diff --check`: passed.
- `.venv/bin/python -m pytest -q`: passed, `177 passed, 8 deselected`.

### Claim Boundary

- Trust label: `EXACT_OBSTRUCTION` for the 5,108 certified partial branches.
- Each closure applies only to one fixed two-sided boundary prefix and all its
  completions.
- The remaining 832 prefixes are not counterexamples and are not evidence of
  realizability.
- No general proof, no counterexample, and no all-order C13 obstruction are
  claimed.

### Publish / PR Checkpoint

- Local commit: `6fd42a2 research: certify c13 partial prefix branches`.
- `git push -u origin codex/goal-erdos97-proof-or-counterexample`: failed with
  GitHub `403` permission denial for account `oskarasi`.
- Fallback publication used the GitHub connector to update draft PR #86:
  `https://github.com/davidiach/erdos97/pull/86`.
- Connector-side commit:
  `d3cdec5a0d72147dfbf06eb9579d282c1c475d22`.
- After fetching the PR branch, local `HEAD` tree and
  `origin/codex/goal-erdos97-proof-or-counterexample` tree both resolved to
  `4976f20a5d6da0cd4bbc8634aa5f36063a806ef1`; `git diff --stat
  HEAD..origin/codex/goal-erdos97-proof-or-counterexample` was empty.
- PR title/body updated to cover the partial-branch closures and remaining
  832-prefix risk.
