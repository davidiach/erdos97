# Documentation review - Erdos Problem #97 research log

Date: 2026-09-05
Reviewer: read-only documentation pass
Scope: repository documentation surface at `davidiach/erdos97`, branch
`claude/documentation-review-orh86q`, at commit `b86a573`
Method: run the documented documentation gates; mechanically cross-check every
Markdown link and repo-path reference; compare the source-of-truth files against
`metadata/erdos97.yaml` and the checked artifacts; inventory the trust-label
vocabulary actually in use; re-check the open findings of the two prior reviews.

Status: reviewability aid only; not mathematical evidence. This report makes no
mathematical claim. No general proof and no counterexample are claimed, the
official/global status remains falsifiable/open, and nothing here promotes any
review-pending artifact.

---

## Executive summary

The documentation surface is in good shape on the things that matter most for
this repository. Every documented fast-tier documentation gate passes, all 534
tracked Markdown files resolve every relative link, the source-of-truth files do
not contradict each other, and the headline figures they quote match the checked
artifacts. The non-overclaiming posture holds throughout: `README.md`,
`STATE.md`, `RESULTS.md`, and `docs/claims.md` all state the falsifiable/open
official status, the repo-local `n <= 8` scope, and the review-pending status of
the `n=9`/`n=10` material. Two findings from earlier reviews are now fixed
(`docs/claims.md` is overclaim-scanned; the Lean pilot is compiled in CI).

The findings below are consistency, coverage, and staleness items. None of them
is a claim-integrity defect, and none of them requires a status change.

Counts: **Critical 0, High 0, Medium 3, Low 6, Informational 3.** All three
Medium findings and five of the six Low ones have since been fixed on this
branch. D5 (the length of `STATE.md`) and the three informational items
remain open.

---

## Verified healthy

- Documentation gates pass: `scripts/check_text_clean.py`,
  `scripts/check_status_consistency.py`, `scripts/check_artifact_provenance.py`,
  `scripts/generate_makefile_verify_targets.py --check`, `git diff --check`.
- 0 broken relative Markdown links across 534 tracked Markdown files.
- 0 dangling repo-path references from `README.md`, `STATE.md`, `RESULTS.md`,
  `AGENTS.md`, `CONTRIBUTING.md`, `docs/claims.md`, `docs/index.md`,
  `docs/reviewer-guide.md`, `docs/review-priorities.md`, `docs/codex-backlog.md`.
- Every `make` target named in the docs exists in the `Makefile`. The
  registry-backed target list quoted in `README.md` matches
  `scripts/audit_commands.json` exactly, and the generated Makefile block is in
  sync with the registry.
- Headline figures agree across `README.md`, `STATE.md`, `RESULTS.md`, and
  `docs/claims.md`: the `184` frontier assignments, `15` canonical `n=8`
  classes, `8097` chord graphs, `310,320` covers, `2,988` `(n,k)` cases,
  `1,865,543` collision-root occurrences, `126` singleton rows. The `184` figure
  was checked directly against
  `data/certificates/n9_vertex_circle_exhaustive.json`
  (`cross_check_without_vertex_circle_pruning.full_assignments = 184`,
  `main_search.full_assignments = 0`).
- `metadata/erdos97.yaml` is aligned with the prose: the equilateral-nonagon
  restricted theorem, the review-pending `n=9` artifact list, and the strongest
  local result all match what `README.md` and `STATE.md` say.
- `unclassified.md` self-reports "11 of 138 inventoried files are SCRATCH
  (8.0%)"; `inventory.json` holds 138 entries with exactly 11 `SCRATCH`
  `tentative_label` values.
- The published landing page `docs/index.html` carries the correct
  non-overclaim wording and its only relative link resolves.
- Fixed since prior reviews: `docs/claims.md` is now overclaim-scanned
  (`scripts/check_status_consistency.py:29`), closing deep-review-2026-06-28 M2;
  `.github/workflows/lean.yml` now compiles every Lean source with the pinned
  toolchain via `scripts/check_lean_files.py --require-lean`, closing
  deep-review-2026-06-28 M3.

---

## Findings

### Medium

#### D1 - `docs/index.md` omits 76 of 412 documentation files

- Location: `docs/index.md`; `README.md:63`, `README.md:226`.
- `README.md` routes readers to `docs/index.md` for "the full documentation
  map" and for "the complete packet inventory". The index mentions 336 of the
  412 files under `docs/`; 76 are absent (not linked and not named anywhere in
  the file).
- Among the omissions are six documents that `README.md` and `AGENTS.md`
  themselves point to: `docs/codex-backlog.md`, `docs/public-provenance.md`,
  `docs/status-transitions.md`, `docs/research-engine-audit-fixes.md`,
  `docs/artifact-provenance-policy.md`, `docs/n9-groebner-decoders.md`.
- The gap is not only historical: 11 of the 47 documents added since
  2026-07-24 are unindexed, including `docs/sparse-minimum-distance-forest.md`,
  `docs/triple-fanin-radius-descent.md`, `docs/radius-level-linear-forest.md`,
  `docs/radius-level-return-locality.md`,
  `docs/orbit66-exact-partial-construction.md`,
  `docs/alternate-vertex-perimeter-obstruction.md`, and
  `docs/minimum-radius-component-injectivity.md`.
- Effect: a reviewer who takes `docs/index.md` at its documented word will miss
  roughly a fifth of the packet inventory, including the reviewed
  status-transition contract and the artifact provenance policy.
- Suggested fix: add the missing entries, or soften the two `README.md`
  descriptions to say the index is curated rather than complete. A coverage
  test over `docs/*.md` would keep whichever contract is chosen honest.

**Resolved in `596582a`** on this branch: `scripts/check_docs_index_coverage.py`
now enforces the documented contract in the fast tier, and all 76 entries were
backfilled. The finding is kept here as the record of why the gate exists.

#### D2 - Three incompatible trust-label vocabularies, none of which maps to the others

- Location: `README.md:292-306` ("Trust labels");
  `scripts/check_artifact_provenance.py:37-50` (`KNOWN_TRUST_CLASSES`);
  `docs/artifact-provenance-policy.md:14`; per-note `Status:` headers
  throughout `docs/`.
- `README.md` presents six reader-facing label families: `THEOREM`/`LEMMA`,
  `MACHINE_CHECKED_FINITE_CASE_ARTIFACT`, `EXACT_OBSTRUCTION`,
  `NUMERICAL_EVIDENCE`, `HEURISTIC`/`CONJECTURE`, `COUNTEREXAMPLE_CANDIDATE`.
- `scripts/check_artifact_provenance.py` enforces a different, closed set of 12
  canonical `trust_class` values across the 245 managed artifacts in
  `metadata/generated_artifacts.yaml`. The most common by far,
  `REVIEW_PENDING_DIAGNOSTIC` (154 artifacts, 63%), does not appear in the
  `README.md` taxonomy at all. (Corrected: the first version of this report
  said 274 artifacts and 163, which counted `trust_class` occurrences in the
  YAML, including the 29 inside `native_trust_policy` overrides.)
- The prose notes use a third vocabulary: of the 390 documents under `docs/`
  that carry a `Status:`/`Trust labels:` header, the headers contain 79 distinct
  label tokens. 53 of those are used exactly once, and 67 appear in neither the
  `README.md` taxonomy nor `KNOWN_TRUST_CLASSES` - for example
  `REVIEW_PENDING_RESTRICTED_THEOREM`, `PAPER_PROOF_CANDIDATE / REVIEW_PENDING`,
  `REVIEW_PENDING_DIAGNOSTIC_ONLY`, `INTERNAL_REVIEW_NOTE`, `REVIEW_PACKET_ONLY`.
- Only `EXACT_OBSTRUCTION` is common to all three vocabularies.
- `docs/artifact-provenance-policy.md` calls `trust_class` "the repository's
  canonical review category" but never enumerates the permitted values, so the
  canonical vocabulary exists only in code - and that policy note is itself one
  of the 76 files missing from `docs/index.md` (D1).
- Effect: the trust taxonomy is the repository's central non-overclaiming
  device, and a reader currently cannot map an artifact's label, a note's
  header, and the `README.md` list onto each other.
- Suggested fix: enumerate the 12 canonical `trust_class` values in
  `docs/artifact-provenance-policy.md`, state in `README.md` that the
  reader-facing labels are a coarsening of that set, and say explicitly whether
  per-note `Status:` headers are free-form prose or are meant to be drawn from
  the canonical set.

**Resolved in `9bb4ad4`** on this branch, except for one deliberately open
question. The canonical set is now enumerated and glossed in
`docs/artifact-provenance-policy.md`, `README.md` records how the three
vocabularies relate, and `scripts/check_artifact_provenance.py` fails if the
documented set and `KNOWN_TRUST_CLASSES` ever diverge. Whether per-note
`Status:` headers should stay free-form or be constrained to the canonical set
is a maintainer decision and is left open in both the note and the policy.

#### D3 - `CHANGELOG.md` is six weeks and 123 commits stale, and omits a new restricted local theorem

- Location: `CHANGELOG.md:10` (newest entry, 2026-07-23).
- `CHANGELOG.md:5-8` states its purpose: "claim-scope changes, demotions, audit
  additions, and reviewability fixes that affect how an external reader should
  interpret the repository."
- 123 commits and 47 new `docs/` files have landed since the last entry.
  Several are squarely within that stated purpose - notably
  `docs/status-transitions.md` (the reviewed status-transition contract) and
  `docs/research-engine-audit-fixes.md`, both added by
  `b86a573`.
- The clearest omission is the restricted local theorem "No bad strictly convex
  equilateral nonagon exists", added 2026-07-24 in `adf16fe`
  (`docs/n9-equilateral-chord-obstruction.md`). It appears in `README.md`'s
  "Status at a glance" and in `metadata/erdos97.yaml`
  `local_repo.restricted_repo_local_theorems`, but has no changelog entry.
- This is a recurrence: adversarial-review-2026-07-20 M5 already recorded that
  the changelog had omitted a wave of work, and the gap has since widened.
- Suggested fix: backfill entries for the claim-scope-relevant changes since
  2026-07-23, starting with the equilateral-nonagon theorem and the
  status-transition contract.

**Resolved in `d76368a`** on this branch: nine dated entries now cover the
window, written from the merged notes and certificates rather than from commit
subjects. The changelog remains hand-maintained, so unlike D1 and D2 no gate
prevents it drifting again.

### Low

#### D4 - The documented `ruff` gate is not reproducible from the documented dev extras

- Location: `README.md:334-352`, `AGENTS.md` ("Test commands"), `Makefile:11`,
  `pyproject.toml:36-43`.
- `README.md`, `AGENTS.md`, and `make verify-lint` all specify
  `python -m ruff check .` as a required fast-tier gate. `pyproject.toml` has a
  `[tool.ruff]` table with `target-version` and `extend-exclude` but no
  `[tool.ruff.lint] select`, and the dev extra pins only `ruff>=0.15` with no
  upper bound.
- Installing the documented dev extras in this environment produced ruff
  0.16.6, whose default rule selection is far broader than the classic
  `E4,E7,E9,F`. The documented command then reports 3,918 errors, dominated by
  rules the repository has clearly never linted against (1,161 `TRY004`, 571
  `RUF100`, 538 `I001`, 431 `EXE001`).
- The repository source itself is clean: `python -m ruff check . --select
  E4,E7,E9,F` passes with no findings.
- Effect: the documented gate is version-dependent rather than pinned, so a new
  contributor following `README.md`'s quick start (`pip install -e .[dev]`,
  which resolves `ruff>=0.15` to the current release) sees thousands of
  failures on an unmodified checkout.
- CI is not affected, and deliberately so. The lint lane installs
  `requirements-lock.txt`, which pins `ruff==0.15.11`, and the compatibility
  lane that does install an unbounded `ruff>=0.15`
  (`.github/workflows/tests.yml:100`) runs only pytest, under an explicit
  comment declining to treat "a floating Ruff version as the repository's lint
  authority" (`.github/workflows/tests.yml:106-108`). So this is a contributor
  and reproducibility defect, not a live CI exposure. (Corrected: the first
  version of this report said CI was exposed to the same drift.)
- Suggested fix: record the intended rule set explicitly in `pyproject.toml`
  (`[tool.ruff.lint] select = ["E4", "E7", "E9", "F"]`), or bound the dev-extra
  version. Either makes the documented command mean what the docs say it means.

**Resolved in `1207ee9`**: `pyproject.toml` now pins
`[tool.ruff.lint] select = ["E4", "E7", "E9", "F"]`, and `python -m ruff check .`
passes on ruff 0.16.6. `E402` was confirmed load-bearing before pinning, and
the pinned set is the one the lock file's `ruff==0.15.11` already enforced, so
the fix makes the documented contributor command agree with CI rather than
changing what CI checks.

#### D5 - `STATE.md` has outgrown the role every doc assigns it

- Location: `STATE.md:5`; `README.md:60`; `README.md:317`; `docs/index.md:3`;
  `docs/index.md:8`.
- Five places call `STATE.md` "the short working dashboard", and
  `docs/index.md:3` instructs: "Keep `STATE.md` short; put detailed
  reconciliation in the canonical synthesis."
- `STATE.md` is 1,454 lines - 22% longer than
  `docs/canonical-synthesis.md` (1,191 lines), the long-form document it defers
  to. A single section, `## Strongest proved state` (lines 22-812), accounts for
  790 lines, more than half the file.
- Effect: the dashboard no longer serves the fast-orientation role the docs
  promise, and detailed reconciliation now lives in the file that is supposed to
  point away from it.
- Suggested fix: move the accumulated per-pattern detail out of
  `## Strongest proved state` into the topic notes it already cites, or restate
  the documented role of `STATE.md` to match what it has become.

#### D6 - A superseded run memo is not marked superseded

- Location: `data/runs/2026-05-05/selection_lemma_progress.md`; refuted by
  `docs/canonical-shortest-chord-crossing-control.md` and recorded in
  `docs/canonical-synthesis.md:311` and
  `docs/selection-lemma-asymmetric-kite-conditional.md:14-16`.
- The memo concludes that the Selection Lemma program is "Likely YES with
  significant additional work", resting on a noncrossing claim it reports as
  "supported by 1,935 tests (zero crossings)".
- That noncrossing claim has since been shown exactly false for the
  deterministic canonical rule: `docs/canonical-shortest-chord-crossing-control.md`
  records an exact rational strictly convex decagon whose canonical shortest
  witness chords cross, and the canonical synthesis and the asymmetric-kite memo
  both record the refutation.
- The memo carries no superseded marker or forward pointer, and is the only
  memo in `data/runs/2026-05-05/` without a date line. `AGENTS.md`
  ("Source-of-truth discipline") requires archived or provenance statements to
  be clearly marked when superseded.
- The memo's own headline is not an overclaim: it is explicitly conditional on
  both injectivity and noncrossing being proven first, and neither is. So this
  is a staleness-marking issue only.
- Suggested fix: add a superseded banner pointing at
  `docs/canonical-shortest-chord-crossing-control.md`.

**Resolved in `1207ee9`**: the memo now carries a dated superseded banner
naming the refutation. The historical body is unaltered.

#### D7 - `unclassified.md` is orphaned from the provenance layer

- Location: `unclassified.md`; `docs/public-provenance.md:132-143`.
- `docs/public-provenance.md` lists `contradictions.md`, `dropped_kernels.md`,
  `inventory.json`, and `kernels.json` as "the public reconciliation layer for
  superseded archive claims, failed routes, dropped kernels, and source
  inventory."
- `unclassified.md` is the fourth output of that same 138-file classification
  pass - it accounts for the 11 `SCRATCH` files - but it is referenced by no
  Markdown, YAML, or Python file in the repository, and it appears in neither
  `README.md` nor `docs/index.md`.
- Suggested fix: add it to the `docs/public-provenance.md` list beside its three
  siblings.

**Resolved in `1207ee9`**.

#### D8 - The Lean subproject is invisible from `README.md` and `AGENTS.md`

- Location: `README.md:314-327` (repository map), `README.md:334-352` (quick
  start), `README.md:421`; `AGENTS.md` ("Test commands"); `Makefile:16-18`.
- The repository ships `lean/` (10+ Lean sources), root `lakefile.lean`,
  `lake-manifest.json`, and `lean-toolchain`, a dedicated
  `.github/workflows/lean.yml`, and a `make verify-lean` target running two
  checkers.
- `README.md`'s repository map lists none of it, the quick start and artifact
  sections never mention `make verify-lean`, and `AGENTS.md`'s test-command
  contract omits it too - yet `README.md:421` already refers to "Lean-only pull
  requests" using "their dedicated ... Lean workflows".
- Effect: an agent or contributor following `AGENTS.md` who edits `lean/` has no
  documented verification step; the Lean route is documented only in
  `docs/formalization.md:35`.
- Suggested fix: add `make verify-lean` to the `AGENTS.md` test commands and
  name `lean/` in the `README.md` repository map.

**Resolved in `1207ee9`**: both done, with a note that the compile step skips
rather than fails when no Lean toolchain is on `PATH`.

#### D9 - `LICENSE.md`'s code clause omits `cpp/` and `lean/`

- Location: `LICENSE.md:5-6`; `README.md:483-485`.
- MIT is granted to "Source code in `src/`, `scripts/`, `tests/`, and
  `.github/workflows/`"; CC-BY-4.0 covers "Research notes, documentation, data
  artifacts, issue templates, and certificate templates".
- `cpp/` (`n10_kalmanson_pair_filter_probe.cpp`, `n_vertex_search_fast.cpp`) and
  `lean/` (plus the root `lakefile.lean`, `lake-manifest.json`,
  `lean-toolchain`) are source code and fall under neither clause. No file in
  either directory carries its own notice, so the `LICENSE.md:8` fallback ("If a
  file states a different license explicitly, that file's notice controls") does
  not resolve it.
- `README.md:483-485` repeats the same split, so the gap is reproduced there.
- Suggested fix: extend the MIT clause to `cpp/` and `lean/`.

**Resolved in `1207ee9`**: the MIT clause now names `cpp/`, `lean/`, and the
root Lean build files, and `README.md` matches.

### Informational

#### D10 - The published landing page is a status surface with no gate

- Location: `docs/index.html`; `scripts/check_status_consistency.py:28-29`.
- `.github/workflows/pages.yml` publishes all of `docs/`, making
  `docs/index.html` the public entry point. Its body currently carries the
  correct wording ("Repository status: no general proof and no counterexample
  are claimed", scoped to "at most eight vertices").
- The status/overclaim checker reads only `README.md`, `STATE.md`, `RESULTS.md`,
  and `docs/claims.md`, all Markdown, so nothing would catch that sentence being
  weakened or dropped from the published HTML.

#### D11 - Freshness watch on the two dated metadata fields

- Location: `metadata/erdos97.yaml:12`, `metadata/erdos97.yaml:28`;
  `scripts/check_status_consistency.py:474-481`;
  `scripts/audit_commands.json` (`official_status_freshness`).
- `problem.official_status_last_checked: "2026-07-09"` is 58 days old as of this
  review. The weekly artifact audit runs the 90-day gate, so it will begin
  failing on or after 2026-10-07 unless the official page is rechecked.
- `nearby_literature.last_swept: "2026-04-30"` is 128 days old. It is validated
  for `YYYY-MM-DD` format only and has no freshness gate at all, so it can go
  stale silently.

#### D12 - A run-log entry records four files that are not in the repository

- Location: `reports/codex_goal_erdos97_log.md:20662-20665`.
- The C13 Kalmanson fourth-pair entry records "Added"
  `scripts/refine_c13_kalmanson_fourth_pair.py`,
  `data/certificates/c13_kalmanson_fourth_pair_refinement.json`,
  `tests/test_c13_kalmanson_fourth_pair_refinement.py`, and
  `docs/c13-kalmanson-fourth-pair-refinement.md`. None exists in the working
  tree, and a search over the full history (1,146 commits, all refs, back to
  2026-04-26) finds no commit that ever added any of them.
- The entry is anomalous rather than typical: the C13 *third*-pair script exists,
  and every file in the parallel C19 sampled-fourth-pair entry
  (`reports/codex_goal_erdos97_log.md:20835-20838`) exists.
- The log is an append-only historical record, so this is a provenance
  discrepancy to annotate rather than a claim defect. Its "Updated" list for the
  same entry also names `docs/index.md` and `metadata/erdos97.yaml`, which makes
  it worth confirming that no dangling C13 fourth-pair reference was left behind
  elsewhere - none was found by this review.

---

## Verification log

Commands run for this review, from the repository root:

```bash
python scripts/check_text_clean.py                            # clean
python scripts/check_status_consistency.py                    # pass
python scripts/check_status_consistency.py --max-official-status-age-days 90
python scripts/check_artifact_provenance.py                   # manifest valid
python scripts/generate_makefile_verify_targets.py --check    # in sync
git diff --check                                              # clean
python -m ruff check . --select E4,E7,E9,F                    # all checks passed
python scripts/check_lean_sketch_integrity.py                 # passed
python scripts/check_lean_files.py                            # lake absent, skipped
```

Not run, and why:

- `python -m pytest -q`: `numpy`/`scipy` are unavailable in this environment, so
  the suite fails at collection with `ModuleNotFoundError` before any test body
  runs. This is an environment limitation, not a repository defect, and no
  finding above depends on the test suite.
- `python -m ruff check .` without `--select`: see D4.
- The artifact tier (`make verify-artifacts`): not required for a
  documentation-only review, and blocked by the same missing dependencies.

Link and reference checks were performed by scanning all 534 tracked Markdown
files for relative Markdown links and for backtick-quoted repository paths, then
resolving each against the working tree.


## Follow-up corrections, 2026-09-06

The findings above describe the original review snapshot, not independent
mathematical validation. Follow-up review found that the initial index checker
counted links in comments and code examples; it now uses CommonMark tokens and
has failure-case tests. The canonical diagnostic gloss now includes existing
bounded-obstruction and construction uses, with each artifact's claim scope
and review qualifications controlling its interpretation. The triple-fan-in
navigation summary now states its boundary hypotheses.

Changing LICENSE.md and pyproject.toml also invalidated the n=8 release bundle's
pinned source snapshot in fresh clones. The release packet is regenerated
through its builder from a clean source commit; the provenance gates are retained.
