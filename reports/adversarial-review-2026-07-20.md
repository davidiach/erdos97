# Adversarial review — merge wave PRs #877–#884

Date: 2026-07-20
Reviewer: Claude Code adversarial review pass (read-only; no source files were
modified during the review)
Scope: commit range `14ffc19..9aa67a5` (PRs #877–#884, merged 2026-07-17 to
2026-07-19): near-saturation and linear-slack support obstructions, exact
bounded two-mode cyclic certificate, signed-zero portable-compare fix,
external frontier audits, Kalmanson primary-route registration and independent
recheck, Kalmanson equilateral-hinge extraction, n=9 hinge forcing, and the
associated status/metadata/release-packet changes.
Method: six parallel adversarial review lanes (one per component family), each
instructed to break the mathematics, hunt for circular or vacuous
verification, and flag overclaims; every HIGH and load-bearing MEDIUM finding
was then independently re-reproduced by the coordinating reviewer before
inclusion here. Predecessor report: `reports/deep-review-2026-06-28.md`
(covers the tree as of 2026-06-28).

This report is AI-generated. The parallel lanes and coordinating replay are
internal cross-checks from one Claude Code review session; they do not
constitute independent external review, satisfy any repository review gate, or
promote any mathematical claim. The finding counts below describe the pinned
snapshot at `9aa67a5`, not the state of later `main`.

---

## Executive summary (claim-neutral)

The mathematics of this wave survived adversarial attack. In particular:

- The Kalmanson inequality convention underlying all 184 n=9 self-edge kills
  was re-derived from scratch and stress-tested numerically (20,000 random
  strictly convex quadrilaterals plus degenerate controls); every code site
  emits only the two sides-vs-diagonals comparisons, for which strictness is
  justified, and the sign-indefinite side-vs-side comparison is never emitted.
- The n=9 hinge-forcing UNSAT result was reproduced with a structurally
  different independent implementation (fixed-order DFS, set-based, fresh
  hinge recognizer): same 184-terminal frontier, byte-identical digest
  `dc28b32d...`, zero hinge-free terminals, identical hinge histogram.
- The two-mode certificate's quantifier structure is correct: the code uses
  only the genuine period-`d` subgroup symmetry (`d = n/gcd(n, k-1)`), not the
  false full rotation symmetry; convexity is only ever refuted, never assumed;
  no float arithmetic exists on any decision path; conversion seams
  (rational-to-Arb, decimal outward rounding) were fuzzed without violation.
- The near-saturation and linear-slack proofs were re-derived step by step,
  including the five checklist items in `docs/review-priorities.md`; the
  escape-deficit sequence 2,3,3,4,4 was reproduced by a third from-scratch
  implementation; all published integer consequences (decagon/hendecagon
  exact-four floors, budget tables, boundary profiles) were recomputed and
  agree.
- No silent status promotion occurred: all 10 review gates remain
  `still_open: true`, every "primary route" mention is coupled with
  still-open-gates caveats, and every recomputable number that appears in more
  than one changed file agrees across README/STATE/RESULTS/claims/metadata.
- The repo's own fast tier passes (`check_text_clean`,
  `check_status_consistency`, `check_artifact_provenance`, `git diff --check`,
  `ruff`, default pytest: 1604 passed, 0 failures), and the release-packet
  SHA256SUMS, manifest, and dependency pins are internally consistent.

At the reviewed snapshot, the remaining findings were reproducibility,
review-contract, and verification-theater defects, not mathematical ones. The
single HIGH finding
is that the two 2026-07-18 external audits pin CRLF-rendered SHA-256 hashes,
so their documented `--assert-expected` reproduction fails on any standard
POSIX checkout of the pinned commit — the failure is fail-closed (false
alarm, not false pass), but the commit that introduced them is titled
"reproducible external frontier audits" and they are not reproducible as
documented.

Counts: **Critical 0, High 1, Medium 11, Low (notable) 17.**

---

## Findings

### Critical

None. No checker on a load-bearing path is unsound or vacuous in a way that
could produce a false positive result; no certificate certifies something
other than what it claims; no source-of-truth files contradict each other; no
repo-authored statement overclaims a proof or counterexample.

### High

#### H1 — The 2026-07-18 external audits pin CRLF hashes; their documented reproduction fails on any standard checkout

- Location: `src/erdos97/external_frontier_audit.py:18-23`
  (`EXPECTED_SOURCE_SHA256`, `EXPECTED_README_SHA256`),
  `src/erdos97/external_exact_five_contract.py:16,32-45`;
  docs `docs/external-removable-vertex-frontier-audit-2026-07-18.md` and
  `docs/external-exact-five-occurrence-contract-2026-07-18.md` (both instruct
  running with `--assert-expected`).
- Reviewer-reproduced evidence (fresh Linux checkouts of
  `mysticflounder/erdos-97-96-formalization` at the pinned commits):
  - `audit_external_removable_vertex_frontier.py <checkout-at-5e43baeb>
    --assert-expected` → `expected_snapshot_match: False`, **exit 1**. The
    commit matches and the sorry census (12 declarations / 32 holes)
    reproduces; only the byte hashes fail.
  - The pinned hash `d2aaf3c9...` is exactly the SHA-256 of the pinned
    commit's `U1LargeCapRouteBTail.lean` after LF→CRLF substitution (actual
    checkout bytes hash to `03478c4b...`); likewise `9601dfa1...` vs
    `66256413...` for the external README. The external repo has no
    `.gitattributes`, so POSIX checkouts are LF; the pins can only have been
    produced on a Windows checkout with `autocrlf=true`.
  - `audit_external_exact_five_contract.py` exits 1 against **all three**
    available external commits, including its own pinned commit `5e43baeb`.
  - Control: the two later audits (`exact_six`, 2026-07-18 and
    `exact_seven_l0`, 2026-07-19) hash LF-normalized bytes (`_lf_sha256`) and
    exit 0 at their pinned commits — the exact-six doc even explains why LF
    normalization is needed. The earlier two audits were never retrofitted.
- Why it matters: these are provenance pins for an external Lean formalization
  attempt; the recorded SHA-256 values identify no artifact that exists in the
  external repository as normally checked out, and the audits' only
  documented invocation fails. The defect is fail-closed, so nothing false is
  certified — but the reproducibility promise in the commit title and both
  docs is not met, and a future reviewer hitting exit 1 cannot distinguish
  external tampering from this pinning bug without re-deriving the CRLF
  explanation.
- Suggested fix: switch both audits to the `_lf_sha256` normalization already
  used by the exact-six/exact-seven audits, repin the hashes from a POSIX
  checkout, and re-run all four audits against their pinned commits (see also
  M10 on the missing end-to-end coverage that let this ship).

### Medium

#### M1 — The `frontier_enumeration` review gate was re-scoped without a recorded review decision

- Location: `metadata/n9_review_gate_ledger.yaml:78-99` and
  `docs/n9-review-gate-ledger.md:383` (new), vs
  `git show 14ffc19:metadata/n9_review_gate_ledger.yaml` line 69-80 (old);
  outcome `accepted_kalmanson_route` added at
  `metadata/n9_review_gate_ledger.yaml:294-302` by commit `794e7a2`.
- The gate titled "A6/A7 source frontier enumeration" became "Shared source
  frontier from A6/A7 or D0/D1", and its review question now accepts either
  the legacy A6/A7 brancher or the fresh D0/D1 all-row search introduced by
  the same PR wave. Because the two pre-existing acceptance outcomes
  (`accepted_vertex_circle_route`, `accepted_turn_route`) require only
  `frontier_enumeration`, a reviewer could now nominally satisfy their
  frontier prerequisite via the D0/D1 path while those routes' obstruction
  gates (A10, B3) replay against the A-route enumeration; the D=A frontier
  identification is a blocker only conditionally. This is in tension with the
  wave's own new sentence at `docs/n9-reduction-chain.md:237-238`: "Those
  review intake contracts should change only with an explicit review
  decision."
- Mitigations verified: no gate status changed (all 10 remain
  `still_open: true`), the per-path blockers are spelled out, every dependent
  file was updated consistently, the cross-path frontier set equality is
  machine-checked (digests match, reviewer-reproduced), and the route
  decision request lists both new gates as requested-not-reviewed. So this is
  a unilateral review-contract change, not a silent promotion.

#### M2 — Tautological "template orbits: 1" statistic in the hinge crosswalk

- Location: `scripts/check_kalmanson_equilateral_hinge_crosswalk.py:132-141`
  (`_template_signature`); `docs/kalmanson-equilateral-hinge.md:74-93`.
- `_template_signature` maps `hinge.a/b/c/d` to the fixed letters
  `"A"/"B"/"C"/"D"` before hashing, so the signature is a constant for every
  possible input and `generic_pair_membership_template_orbits` can never be
  anything but 1. The doc reports "stored dihedral core signatures: 56 /
  equilateral-hinge template orbits: 1" as a measured result and calls the
  56→1 collapse "the proof-facing gain". The genuine computed content of the
  crosswalk — 184/184 core-orientation coverage with exactly one matching
  orientation per record — is real (independently reproduced); the orbit
  metric adds zero information and could never flag a recognizer bug.

#### M3 — Tautological satisfaction-table half of the hinge-forcing "compiled semantics audit"

- Location: `src/erdos97/n9_hinge_forcing.py:437-459`
  (`audit_compiled_hinge_semantics`) vs `:355-369` (`SATISFIED_HINGES`
  builder); presented as review assurance in `docs/n9-hinge-forcing.md:90-92`.
- The audit's `expected` tuple is the character-for-character identical
  comprehension used to build `SATISFIED_HINGES`, evaluated against the same
  in-memory `HINGE_REQUIREMENTS`. It can only fail on post-import mutation,
  never on a compilation bug. `SATISFIED_HINGES` is the load-bearing pruning
  structure for the headline zero-terminal UNSAT search (at which no terminal
  recognizer replay ever fires), so a bug in the shared expression would
  over-prune and silently produce a false UNSAT while this audit passes.
  Mitigation: this review independently re-implemented the search and
  recognizer and confirmed the result (184 terminals, digest match, 0
  hinge-free terminals), so the current tables are correct — the finding is
  that the shipped audit provides no protection, not that the result is
  wrong.

#### M4 — The hinge results are absent from the claims ledger and all dashboards

- Location: `docs/claims.md`, `STATE.md`, `RESULTS.md`,
  `metadata/erdos97.yaml`, `metadata/n9_review_evidence_matrix.yaml` — zero
  occurrences of "hinge" in any of them (reviewer-verified by grep), while
  `docs/kalmanson-equilateral-hinge.md:3` carries a `LEMMA`-labeled claim and
  `docs/n9-reduction-chain.md` records Chain E. Sibling PRs in the same wave
  registered their new lemmas in `docs/claims.md` (near-saturation, two-mode).
- The gate-ledger omission is disclosed in `docs/n9-reduction-chain.md:236-238`,
  and the direction of the error is under-claiming, not inflation — but a
  reviewer auditing the proof-facing claims ledger will not find the hinge
  route at all, which defeats the ledger's purpose as the claim inventory.

#### M5 — CHANGELOG omits the entire 2026-07-19 half of the wave

- Location: `CHANGELOG.md:10` (latest entry `## 2026-07-17`) vs six merges
  dated 2026-07-19 (PRs #879, #881–#884 plus the external-audit commit):
  linear-slack lemma, Kalmanson primary-route registration with two new
  review gates and a new acceptance outcome, equilateral-hinge lemma, hinge
  forcing, external audits, signed-zero fix. `CHANGELOG.md:5-7` states the
  file records changes "that affect how an external reader should interpret
  the repository"; the gate-ledger re-scoping (M1) is exactly such a change.
  The entries that are present (2026-07-16/17) were verified accurate and
  non-inflated.

#### M6 — Corrupted claim-scope prose retained in the two-mode notes

Post-review disposition: **resolved after the reviewed snapshot by PR #885**.
The finding and snapshot count are retained here as historical review evidence.

- Location: `docs/two-mode-cyclic-exact-n80.md:179-181` ("Scope boundary": the
  sentence "It converts the" is followed by a stray literal `+` line, then
  "the real two-mode family and finite range stated above.");
  `docs/two-mode-exact-packet-triage-2026-07-17.md:36-38` (same defect class).
  Reviewer-verified with `cat -A` (literal `+$` lines — surviving patch
  fragments).
- The corrupted paragraph is the one that was supposed to state the scope
  conversion of the headline result, in the primary proof note of the wave's
  largest certificate; and the triage note containing the second fragment
  itself asserts "No damaged prose was retained verbatim." No mathematical
  content is wrong (the scope is stated correctly elsewhere in the same doc
  and in README/STATE/RESULTS), but a claim-bearing sentence is unreadable.

#### M7 — The linear-slack doc misattributes its finite cross-check's provenance

- Location: `docs/linear-slack-support-obstruction.md:138-141` says the n=9
  base-apex diagnostic's "exhaustive escape search for n=8,...,12 reports
  minimum deficits 2,3,3,4,4". No prior repo record contains that sequence:
  `docs/n9-base-apex-frontier.md:349-351` and
  `data/certificates/n9_base_apex_escape_budget_report.json` record only n=9.
  The n=8..12 sequence is computed for the first time by the new test
  (`tests/test_linear_slack_support_obstruction.py:59-68`) calling the
  pre-existing `minimum_capacity_deficit_to_escape_turn_cover`.
- The cross-check itself is real and the sequence is correct (reproduced in
  this review by a third from-scratch implementation), and the two
  implementations do differ (one predates the lemma) — but they encode the
  identical clause abstraction, so their agreement tests the cyclic
  bookkeeping, not the geometric clause derivation, and the doc presents a
  new computation as an already-reported result.

#### M8 — The exact-seven "independent contract" is a transcription of the audited enumerator

- Location: `src/erdos97/external_exact_seven_l0_audit.py:145-206`
  (`_expected_schema`) vs the external repo's `enumerate_l0.py:86-120`
  (`build_schema`): identical structure, identical variable names, identical
  id format string. `docs/external-exact-seven-l0-audit-2026-07-19.md:41-56`
  says the local checker "independently reconstructs every expected schema".
- Comparing a port of X against X detects only drift, which the SHA pin
  already covers; a logic bug shared by both survives the flagship
  `every_schema_matches_independent_contract` check. The audit's remaining
  value (hash pins, digest pinning, uniqueness, census — the 11:8..16:81
  point-count distribution was independently verified as combinatorially
  forced — and determinism) is real but weaker than the prose suggests.

#### M9 — Headline external replay claims are off-repo and unreproducible from committed tooling

- Location: `docs/external-exact-six-frontier-audit-2026-07-18.md:61-91`
  ("exact vector replays passed 12509", "all minimized cores exact-LRA
  UNSAT", "every single-core deletion exact-LRA SAT") — obtained by running
  the upstream verifier with "an in-memory one-line normalization"; the
  audit JSON itself records
  `external_farkas_replay_checked_by_this_script: false`. Same pattern for
  the exact-seven doc's Z3 smoke-gate replay
  (`live_replay_by_this_audit: false`). `docs/index.md` advertises
  "independent replay of 263 minimized cores and 12,509 weighted cuts".
- The JSON labeling is honest, but the docs record verification results that
  no committed script in either repository can re-run, and the index headline
  does not carry the qualification.

#### M10 — The four external audit entry points have zero end-to-end coverage

- Location: `tests/test_external_*.py` import only helper functions
  (`_missing_markers`, `_lf_bytes`, `strip_lean_comments_and_strings`,
  `_expected_schema`, ...); the four `audit_external_*` entry points are
  called nowhere in-repo, and none is registered in
  `scripts/run_artifact_audit.py`, the Makefile, or CI (they require an
  external checkout path). This is exactly how H1 shipped: the audits passed
  on the author's CRLF checkout and were never executed on a POSIX checkout
  before merge. Even a smoke test against a small committed fixture tree
  would have caught H1.

#### M11 — The released n=8 bundle mutates in place under a frozen release date

- Location: `scripts/build_n8_release_packet.py:44,48` hardcode
  `RELEASE_DATE = "2026-07-09"` and a fixed zip timestamp;
  `papers/release/n8-artifact-bundle.zip` was regenerated three times in and
  around this range (`7195aed`, `f559e16`, `b4ae76b`) with changed content
  (new dependency pins, metadata wording, README source-commit pin) while
  `release_date` stays 2026-07-09, `CITATION.cff` stays 0.1.0, and superseded
  digests are overwritten in place with no regeneration log and no CHANGELOG
  entry for the 07-19 refresh.
- A reviewer holding an earlier "2026-07-09" bundle now hash-mismatches
  against the published sums with no discriminator except the manifest's
  source commit. No written rule is violated (`docs/public-provenance.md` is
  silent on release bundles, and the packet README's model is
  regenerate-and-repin), and the current sums/manifest are internally
  consistent (reviewer-verified: outer SHA256SUMS all OK, inner bundle sums
  0 mismatches, `build_n8_release_packet.py --check` passes) — this is a
  provenance-policy gap, not broken provenance.

### Low (notable)

- **L1** — The "fresh D0/D1" Kalmanson frontier search
  (`scripts/check_n9_kalmanson_selfedge_frontier_replay.py:64`,
  `nodes_visited = 100_818`) makes the same MRV branching decisions as the
  legacy brancher (`src/erdos97/n9_kalmanson_selfedge.py:20`); its
  independence claims (no `erdos97` imports, no stored certificate as search
  input) are literally true (verified), but as an alternative enumeration for
  gate purposes it is a re-implementation, not a different algorithm. The
  genuinely different enumeration is the fixed-order
  `scripts/independent_n9_vertex_circle_recheck.py` search (verified: 184,
  digest match).
- **L2** — `docs/n9-kalmanson-independent-recheck.md:88-91`: the "150 + 34
  split also matches" line is not independent evidence — both
  implementations scan quadruples in identical lexicographic order and test
  K1 before K2, so given equal frontiers the split is forced. Only the
  frontier-set/digest agreement carries information.
- **L3** — `src/erdos97/kalmanson_equilateral_hinge.py:249-280`:
  `find_core_hinge_instances` never validates that `quadruple` is cyclically
  ordered; a scrambled quadruple would yield K1/K2 labels whose geometric
  reading is false. Currently harmless (all 184 stored quadruples verified
  ascending; the internal search path derives quadruples safely from
  `combinations(order, 4)`).
- **L4** — Every test asserting the hinge-forcing mathematical outcome
  (0 terminals, pinned digests) is `@pytest.mark.artifact` and deselected by
  the default tier (`pytest.ini:2`); meanwhile the unmarked
  `test_pair_capacity_and_indegree_are_derived_not_assumed` pays the full
  UNSAT search cost via the module fixture but asserts only config metadata.
  A green default `pytest -q` gives zero assurance about the
  theorem-strength search.
- **L5** — `scripts/check_n9_hinge_forcing.py:100-101`: the comment that the
  hardcoded `DROP_WITNESSES` were "found independently of the production
  DFS" is unverifiable provenance prose (their mathematical validity was
  re-verified). Similarly, the cross-artifact digest agreement with the
  Kalmanson frontier replay is enforced only through hand-copied constants
  in each script; no single run compares the two regenerated digests.
- **L6** — `src/erdos97/n9_hinge_forcing.py:469-472`:
  `public_exact_match_count` always equals `requirement_count` by
  construction (any mismatch raises before the record is appended), so the
  certificate field reads like a measurement but carries no information.
- **L7** — `docs/near-saturation-support-obstruction.md:306-307` claims exact
  brute force of "all cycle-minus-0/1/2-edge covers for n = 3..12"; the code
  verifies 0/1-edge removals for n=3..12 but 2-edge removals only for
  n=8..12, with full two-edge cover enumeration only at n=8
  (`scripts/check_near_saturation_support_obstruction.py:159-170,396-401`).
  The mathematical claims need only n >= 8.
- **L8** — `scripts/check_linear_slack_support_obstruction.py:103-111`:
  `forces_turn_contradiction` — the function whose name suggests it embodies
  the headline test — is dead code, never called by the script or tests.
- **L9** — `docs/linear-slack-support-obstruction.md:100-101` reuses the
  index `i` for both the bad gap-2 index and the clause index (wording
  only; the checker implements the intended meaning);
  `docs/localized-rich-support-counting.md:96-101` credits the linear-slack
  strengthening with the n=10/n=11 exact-four floors of six and four,
  which already follow from the earlier two-unit budget (as the linear-slack
  doc itself states) — the minimal review-pending dependency is
  misidentified. All arithmetic itself verified correct both ways.
- **L10** — `src/erdos97/two_mode_cyclic_exact.py:559-567,632`: the
  `root_isolation`/`unexpected_zero` unresolved paths append records without
  incrementing `real_roots`, so the closing conservation assert would crash
  the run instead of emitting the designed
  `incomplete_exact_bounded_family_diagnostic` artifact. Fail-loud, so
  soundness is unaffected; the graceful-incomplete path works only for the
  other two failure kinds.
- **L11** — The elliptical two-mode member `k = n-1` (`z_i = w^i + t*w^-i`)
  is outside the sweep; every claim statement does carry `2 <= k <= n-2`
  adjacently, but "rules out the real two-mode cyclic family" headlines can
  be read as all `k`, and for `k = n-1` the inradius certificate could never
  fire (`gcd(n, n-2) <= 2`), so that member would need different machinery.
- **L12** — The two-mode artifact stores per-case counts plus SHA-256 witness
  digests, not per-root decisions; auditing any single classification of the
  1,865,543 root occurrences requires re-executing its case. The doc is
  honest about this and replay was verified deterministic (byte-identical
  digests for all of n=9..16 and sampled n=79/80 cases, reproduced even on
  CPython 3.11).
- **L13** — After the (correct) signed-zero fix, `portable_compare` also
  rejects stored=1e-18 vs current=-1e-18 even when both are within
  `abs_tol` — a semantic-sign hard-fail on values whose sign is libm
  jitter. Documented intent; noted because this module is on the
  quarter-cell replay path.
- **L14** — `two_mode_cyclic_exact_n80` is a registered audit command whose
  module imports `flint` at `src/erdos97/two_mode_cyclic_exact.py:44`, but
  `python-flint` lives only in the `[dev]` extra: a base `pip install`
  cannot run a registered artifact audit.
- **L15** — `src/erdos97/external_exact_seven_l0_audit.py:136-143,311-312`
  `exec_module`s the external checkout's `enumerate_l0.py`. Execution is
  gated on the pinned SHA (verified: skips as
  `execution_skipped_unpinned_source` otherwise), but a one-line
  hash-constant edit silently changes what third-party code executes; worth
  an explicit policy note.
- **L16** — Trust-label taxonomy sprawl: `N9_CROSSWALK_REVIEW_PENDING`,
  `EXTERNAL_L0_ENUMERATOR_PROVENANCE_AUDIT_ONLY`,
  `EXTERNAL_PROVENANCE_AUDIT_ONLY`,
  `INDEPENDENT_IMPLEMENTATION_RECHECK_REVIEW_PENDING` are ad-hoc labels
  outside the taxonomy in `docs/claims.md`/README. All are deflationary, so
  no inflation occurred, but the taxonomy no longer covers the labels in
  use.
- **L17** — `STATE.md:324` "A follow-up to the sharpened counting lemma
  above, the mixed rich-support reduction..." now directly follows the newly
  inserted linear-slack paragraph, inviting a misreading of which lemma the
  126^9 reduction follows up (it predates linear-slack and does not depend
  on it).

---

## What was attacked and held (verification log)

- **Kalmanson convention** (all n=9 self-edge kills): re-derived from
  scratch; for cyclic a<b<c<d strictly convex, D(a,c)+D(b,d) > D(a,b)+D(c,d)
  and > D(a,d)+D(b,c), strict via the interior diagonal crossing; 20,000
  random strictly convex quadrilaterals, degenerate and wrong-order
  controls; every emitting code site checked
  (`n9_kalmanson_selfedge.py:252-256`, frontier replay, recheck script,
  hinge module) — only the two valid strict comparisons are ever emitted,
  and dihedral reorientation preserves the side/diagonal partition.
- **Hinge lemma algebra**: for all 1,008 oriented templates, the three row
  equalities collapse the designated strict inequality's sides to equal
  multisets (union-find check); strict positivity confirmed on 200 random
  strictly convex nonagons per orientation class.
- **Hinge-forcing search**: independent re-implementation (fixed center
  order, frozensets, terminal-only hinge scan) reproduced 184 terminals,
  digest `dc28b32d...`, 0 hinge-free terminals, histogram
  {2:36, 3:6, 5:18, 6:54, 8:54, 9:16}; the derived-vs-explicit axiom
  crosscheck, both drop-countermodels, the pair-capacity <= 2 /
  hull-pair <= 1 / indegree = 4 derivations, and the crossing-filter
  geometric necessity were all re-verified.
- **Two-mode certificate**: coverage 2,988 = sum over n of (n-3) confirmed;
  every (n,k) pair present exactly once; period-d symmetry justification
  checked ((k-1)d = 0 mod n); at 96 of 128 sampled row-failure roots vertex
  0 genuinely has a fourfold class and a different poor vertex was correctly
  witnessed; all 17 sampled strictly-convex distinct-root configurations
  closed by genuine row failures; backend confirmed SymPy
  `QQ.algebraic_field` + python-flint Arb with one-sided comparisons and
  counted-unresolved escalation; conversion seams fuzzed (2,000 trials each,
  zero enclosure violations); full decision pipeline replayed for 10 cases
  (391 roots) at 60-digit validation; inradius algebra
  (2+S_d)/4 = cos^2(pi/g) verified symbolically; byte-identical artifact
  replay for n=9..16 plus sampled n=79/80.
- **Support lemmas**: base-apex per-pair capacities re-proved (hull edge 1,
  diagonal 2, endpoints cannot self-serve); near-saturation steps 1-5 and
  the linear-slack clause system re-derived, including wrap-around indexing
  and the proved (not asserted) at-most-two-2pi/3-turns step; the
  disconnection concern is moot in the linear proof (never uses global chain
  connectivity); escape minima 2,3,3,4,4 reproduced by a third
  implementation; all budget tables, q-bounds, floors (6/4/1), and boundary
  profiles independently recomputed; both checkers' finite scopes match
  their docs and cannot pass vacuously.
- **Status discipline**: all 10 gates `still_open: true` in both ledger
  files; the two new gates were added open; every "primary route" mention
  across 9 files carries still-open-gates caveats; every recomputable
  number appearing in more than one changed file agrees (184, 150/34,
  158/26, 2,988, 1,865,543 = 1,469,483+395,893+167, 70 = C(8,4), hinge
  1,008/45,360/26,746/1,080, digest `dc28b32d...` in four places,
  ceil((n-4)/2) arithmetic, floors); `official_status_last_checked`
  2026-07-09 within the 90-day bound.
- **Fast tier and artifact commands**: `check_text_clean`,
  `check_status_consistency` (also with `--max-official-status-age-days
  90`), `check_artifact_provenance`, `git diff --check`, `ruff`, default
  pytest (1604 passed, 700 deselected) all pass; the new registered audit
  commands (near-saturation, hinge crosswalk, hinge forcing, Kalmanson
  frontier replay) all run green with expected digests; all 247 registered
  audit script paths exist; release-packet sums/manifest/lock pins
  internally consistent; the signed-zero fix closes a real hole
  (`0.0 == -0.0` short-circuit) and its rejection tests pass.
- **External audits**: the external repo is genuinely external (different
  author); all three pinned commits exist; the exact-six and exact-seven
  audits reproduce exactly (exit 0) at their pinned commits on Linux; the
  period-three partition lemma (203 partitions, 87 pair-free, max
  occurrence-free block 3) was independently re-derived by
  inclusion-exclusion and pigeonhole; the removable-vertex sorry census
  (12/32) reproduces; the Lean comment/string stripper survives nested
  comment and escaped-string controls.

## Scope limits of this review

This review attacked the merge wave `14ffc19..9aa67a5` only; it did not
re-review the pre-existing n<=8 pipeline, the vertex-circle exhaustive
checker, or the C19/C13 certificates beyond their interaction with this
wave (see `reports/deep-review-2026-06-28.md` for the previous full-tree
pass). Sampled verifications (two-mode root decisions, random convex
polygons) are spot checks, not exhaustive replays. Nothing in this report
changes any claim status: the official/global status remains
falsifiable/open, no general proof and no counterexample are claimed, and
the n=9 route remains review-pending under its still-open gates.
