# Deep review — Erdős Problem #97 research log

Date: 2026-06-28
Reviewer: senior-reviewer pass (adversarial, read-only)
Scope: repository at `davidiach/erdos97`, branch `claude/erdos-97-deep-review-h8u8go`
Method: Phase-0 orientation → parallel fan-out across 7 review dimensions →
adversarial re-check of load-bearing findings → re-sweep of the two highest-risk
dimensions (verification-pipeline soundness, claim integrity).

---

## Executive summary (claim-neutral)

This is a disciplined research-log and reproducibility workspace, not a
solved-proof repo. Its non-overclaiming posture holds: every source-of-truth
file agrees the official/global status is **falsifiable/open**, that no general
proof and no counterexample are claimed, that the strongest **local** result is
the repo-local machine-checked `n <= 8` selected-witness artifact, and that the
`n=9`/`n=10` artifacts are review-pending/draft and are **not** promoted. The
verification infrastructure on the load-bearing paths is genuinely sound: the
`n<=8` exact-obstruction pipeline uses exact arithmetic throughout (SymPy over
ℚ, z3 NRA, `Fraction`) with no float equality; the Kalmanson/Farkas certificate
verifier performs a real exact-integer `0 > 0` check and rebuilds the distance
classes and inequality coefficients itself rather than trusting stored fields;
the `n=9` certificate verifiers recompute from rows with exact integer
arithmetic and provably raise on tampered input; the "independent replay"
checkers genuinely import no package module and re-derive their results. The
fast tier (`check_text_clean`, `check_status_consistency`,
`check_artifact_provenance`, `git diff --check`, `ruff`) passes, and the default
test suite is green (1458 passed, 0 failures). **No Critical and no High
findings were found.** The actionable findings are guardrail-hardening and
hygiene items — most prominently that the automated overclaim detector is a
partial tripwire with several confirmed bypasses, that it only scans 3 of the
designated source-of-truth files, that the Lean pilot is never compiled (and
currently would not compile), and that the certificate/artifact test tier is
excluded from the default/PR suite.

Counts: **Critical 0, High 0, Medium 6, Low (notable) ~12.** All findings below
were re-checked; the load-bearing ones were independently reproduced by the
reviewer (commands in the verification log).

---

## Findings

### Critical

None. No checker on a load-bearing path was found unsound or vacuous; no
certificate was found to certify something other than what it claims; no two
source-of-truth files contradict each other on a claim's status; and no
repo-authored statement overclaims a proof of Erdős #97 or a counterexample.

### High

None.

### Medium

#### M1 — The automated overclaim detector is a partial tripwire with multiple confirmed evasion paths
- Location: `scripts/check_status_consistency.py:48-75` (`BANNED_OVERCLAIM_RE_LIST`),
  `:82-84` (`CLAIM_CONTEXT_BOUNDARY_RE`), `:188-211` (`find_forbidden_overclaim_lines`),
  `:215-218` (`line_continues_wrapped_sentence`), `:221-232` (`local_claim_context`).
- Evidence (reviewer-reproduced by importing the module and calling
  `find_forbidden_overclaim_lines`):
  - **Negation-in-clause bypass.** The detector suppresses a banned match if any
    allow-word (`no/not/never/cannot/...`) appears in the surrounding "clause",
    but `local_claim_context` only splits clauses on `.`, `;`, `|`, and
    but/however/although/though — **not** on `:`, `,`, or dashes
    (`CLAIM_CONTEXT_BOUNDARY_RE.search('a : b' / 'a , b' / 'a - b')` all return
    `False`). Result: `"Summary - no longer open: we have proven Erdos Problem
    #97"` and `"Cannot stress enough, we have proven Erdos Problem #97 today"`
    both **PASS**, while the bare forms are correctly **BLOCKED**.
  - **Missing synonym verbs.** The verb set is closed; `"We resolved Erdos
    Problem #97."` and `"We exhibited a counterexample."` both **PASS**.
  - **Multi-line wrap.** `find_forbidden_overclaim_lines` only joins a wrapped
    sentence when the continuation begins lowercase/digit/`([{`; an
    uppercase-led continuation or a blank-line reset evades it (agent-verified).
- Why it matters: `check_status_consistency.py` runs in `make verify-fast` and
  in PR CI (`.github/workflows/tests.yml`) and is the primary automated guard of
  the repo's own non-overclaiming policy. The tree is clean today, so this is a
  guardrail-evasion weakness, not a current overclaim — but a human or AI could
  land an actual overclaim into a source-of-truth file with incidental phrasing
  and the gate would stay green.
- Recommended action: add `:`, `,`, and en/em dashes to
  `CLAIM_CONTEXT_BOUNDARY_RE`; require the negation token to directly govern the
  matched verb (small token window) rather than appear anywhere in the clause;
  extend the verb set (resolve/refute/demonstrate/exhibit/obtain/establish,
  "counterexample … exists"); and scan a blank-line-delimited paragraph join
  rather than a line-pair heuristic. Document explicitly that the list is a
  best-effort tripwire so reviewers do not over-trust a green result.

#### M2 — Overclaim/status enforcement covers only 3 of the source-of-truth files; `docs/` and `docs/claims.md` are never overclaim-scanned
- Location: `scripts/check_status_consistency.py:20` (`REQUIRED_STATUS_FILES =
  ["README.md", "STATE.md", "RESULTS.md"]`), `:405-413` (`validate_top_level_status`),
  `:419-429` (`validate_archived_synthesis`).
- Evidence: `require_no_forbidden_overclaims` runs only on those three files plus
  the `metadata local_repo.overall_claim` YAML field. `docs/canonical-synthesis.md`
  is scanned only for stale n=8 "Open" wording, not overclaims. `AGENTS.md:28-29`
  lists `docs/claims.md` as required reading before changing mathematical claims
  (its source-of-truth alignment rule at `AGENTS.md:21` names
  `metadata/erdos97.yaml` against `README.md`/`STATE.md`/`RESULTS.md`), yet this
  proof-facing claims ledger is not in `REQUIRED_STATUS_FILES` and is never
  overclaim-scanned; nor are the ~300 `docs/*.md` files (including the large
  `bootstrap-t12-*` corpus) are never overclaim-scanned. `check_text_clean.py`
  scans all files but only for hidden Unicode/CRLF, not overclaims.
- Why it matters: the policy is described as repo-wide but enforced on a narrow
  surface; a docs page could assert a proof of #97 and the gate would not catch
  it.
- Recommended action: extend `require_no_forbidden_overclaims` to all tracked
  Markdown (with the existing `OVERCLAIM_LINE_ALLOW_RE` allowlist for legitimate
  "forbidden overclaiming text" samples), or explicitly document the scan as
  limited to three files so reviewers calibrate trust accordingly. At minimum,
  add `docs/claims.md`.

#### M3 — The Lean pilot is never compiled in CI and currently would not compile (duplicate declarations)
- Location: `scripts/check_lean_files.py:22-24` (skips on missing `lake`);
  `lean/Erdos97/Basic.lean:31-61` vs `lean/Erdos97/WitnessLemmas.lean:20-45`;
  import chain `WitnessLemmas.lean:1` → `SelectedWitness.lean:1` → `Basic.lean`.
- Evidence (reviewer-reproduced): `check_lean_files.py` prints `"lake not found;
  skipped Lean compilation"` and returns success when `lake` is absent (the
  default; `make verify-lean` does not pass the opt-in `--require-lean` flag); no CI
  workflow installs Lean/lake. Independently, `Basic.lean` declares
  `lemma Witness4.b_ne_a … d_ne_c` (6 lemmas) and `WitnessLemmas.lean` declares
  `theorem Witness4.b_ne_a … d_ne_c` (same 6 fully-qualified names in namespace
  `Erdos97`); since `WitnessLemmas` transitively imports `Basic`, a real
  `lake build` of the `@[default_target] lean_lib Erdos97` would raise
  duplicate-declaration errors.
- Why it matters: the "verify-lean" tier gives a green signal without ever
  compiling anything, and the library as committed would not build. Impact is
  contained: the Lean files are explicitly a "first Lean pilot," are
  dependency-free sketches that honestly carry `sorry` ("STATED, NOT PROVED"),
  and are not load-bearing for any repo claim.
- Recommended action: remove the duplicated `Witness4.*` lemmas from one of the
  two files (or have one re-export the other), and either wire a real `lake
  build` into CI or document that the Lean tier is text-lint-only and the library
  is not currently expected to compile.

#### M4 — Templated `n=9` self-edge lemma packets dropped a self-check present in the T01 original
- Location: `scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py`
  (defines/calls `validate_strict_inequality_support`, 2 refs) vs
  `scripts/check_n9_vertex_circle_t0{2,3,4,5,...}_self_edge_lemma_packet.py`
  (0 refs).
- Evidence (reviewer-reproduced via grep count across the `t0*` packet family):
  only the T01 packet contains `validate_strict_inequality_support`; the sibling
  templated packets omit it.
- Why it matters: classic copy-paste divergence in a ~12-file templated family —
  the T01 packet performs an extra strict-inequality-support self-check that its
  siblings do not, so the sibling packets verify slightly less than T01 claims to
  for the analogous templates. These are review-pending proof-mining packets, so
  the live impact is low, but the divergence is a maintainability and
  audit-consistency risk.
- Recommended action: factor the shared packet logic (including
  `validate_strict_inequality_support`) into one module imported by all `t0*`
  packets, or restore the check to the siblings; add a meta-test asserting the
  packets share a common validation surface.

#### M5 — The certificate/artifact test tier is excluded from the default/PR test suite, and the certificate test family is largely snapshot/regression-style
- Location: `pytest.ini` (`addopts = -m "not artifact and not slow and not
  exhaustive"`); the `artifact`-marked test family (e.g. the c19/c13/archive
  certificate tests).
- Evidence (reviewer-reproduced): default collection is 1458 tests with 678
  deselected; `pytest --co -q -m "artifact"` shows **537 artifact-marked tests**
  exist but are deselected by default. These validate checked-in certificates and
  run only in the separate `make verify-artifacts` / `audit-artifacts` path
  (CI `.github/workflows/artifact-audit.yml`), not in the PR-default `tests.yml`.
  A sampled portion of the certificate test family is snapshot/regression-style
  (asserts stored artifact counts and that `replay == stored artifact`).
- Why it matters: a green PR-default run does not exercise certificate
  validation; the most security-relevant tests (does a certificate still certify
  its claim) live in a tier that is not the default gate. Snapshot tests guard
  against drift but cannot, by themselves, catch a certificate that was wrong
  when first stored.
- Recommended action: run the `artifact` tier in PR CI (it need not be in the
  fast local loop), or document clearly that PR-green excludes certificate
  validation and that `make verify-artifacts` is the gate for certificate
  changes. Where feasible, add at least one from-scratch (non-snapshot)
  re-derivation test per certificate family.

#### M6 — Provenance guardrail misses space-separated shell-redirection writes
- Location: `scripts/check_artifact_provenance.py:293-324` (`command_outputs_path`),
  used by `:350-381` (`validate_check_command_for_generated_write`).
- Evidence (reviewer-reproduced by importing the module): for a manifest
  `command` of the form `python gen.py > data/certificates/foo.json` (space
  before the path), `command_outputs_path(...)` returns **False** (the early
  `token_matches_path` return at `:301-302` fires before the
  redirect-via-previous-token branch at `:315-320` is reached), whereas the
  attached form `>data/...json` and `--out data/...json` are correctly detected
  as `True`. `| tee path` is also not detected.
- Why it matters: a "generated" artifact whose manifest command used
  space-separated redirection would not trigger the
  `check_command must replay …` requirement, weakening the provenance guard. This
  is latent — no current manifest entry uses that form, and the manifest check
  passes today — but it is a real detection gap.
- Recommended action: treat a path token whose previous token matches
  `\d?>{1,2}` as an output unconditionally (move that branch before the
  generic `token_matches_path` return), and consider handling `tee`.

### Low (notable; the long tail of cosmetic items is omitted)

- **B12 near-miss label drift.** `README.md:291` and `STATE.md:1085` print
  `max squared-distance spread: 0.006806368780585714`; `RESULTS.md:1839` prints
  the identical value as `max selected-distance spread`. The proof-facing
  canonical term (`docs/verification-contract.md`) is "selected-distance spread."
  Same number, inconsistent label. Action: relabel README/STATE to match.
- **`CHANGELOG.md` is stale.** Audit/reviewability commits from 2026-06-19…06-27
  have no CHANGELOG entry. Action: backfill or note the cadence.
- **`docs/formalization.md` Lean enumeration omits `WitnessLemmas.lean` and
  `TwoCircleCap.lean`.** Action: sync the file list.
- **Manifest "generator" semantics for the n8 entries.** Some
  `metadata/generated_artifacts.yaml` entries name a `generator` that is actually
  a checker/re-deriver with no file-write path; and `n10_secondary` writes to a
  hardcoded `/tmp` path rather than the tracked artifact path. Both are
  consistent with the manifest schema but make "generator" mean two things.
  Action: distinguish "writes the artifact" from "re-derives/checks it."
- **Lean sketch-integrity axiom check is literal-only.** `check_lean_sketch_integrity.py`
  flags a literal `axiom` declaration; `constant`/`opaque`/imported axioms would
  not be caught. Low because none are present. Action: broaden the pattern.
- **`verify-only` audit mode skips preflight.** `run_artifact_audit.py
  --verify-only` skips the status-freshness and provenance preflight that the
  full `audit-artifacts`/CI path runs. Action: run preflight in both modes.
- **Quotient-soundness "three independent ways" share one rule.**
  `check_n9_vertex_circle_quotient_soundness.py` recomputes status three ways,
  but all three implement the same nested-chord rule, so they catch
  implementation drift, not a wrong rule — honestly disclaimed in its
  `CLAIM_SCOPE`. Likewise the strict-edge-geometry audit is a self-consistency
  check. Action: none required; keep the disclaimers.
- **Integrity (sha256) tracking covers only `data/certificates/` and
  `certificates/`.** `reports/*.json` diagnostics and docs-embedded JSON are not
  hash-tracked. Action: decide whether report artifacts need provenance too.
- **C13 all-order obstruction has no compact replayable certificate.** Unlike the
  C19 all-order Z3 certificate, the C13 all-order check re-runs the full
  ~1.5M-node order search each time (`verify-kalmanson`). Action: store a
  replayable certificate for cheaper/independent audit.
- **Partial vertex-circle pruning relies on an unasserted monotonicity property**
  in the exhaustive `n=9` search (`src/erdos97/...`); correct in practice but the
  invariant is implicit. Action: add an assertion or comment documenting it.

### Positive confirmations (not findings; recorded so a maintainer knows what was actively checked and held)

- `n<=8` exact-obstruction path: exact arithmetic everywhere (SymPy/ℚ, z3 NRA,
  `Fraction`); all 15 survivor classes killed non-vacuously (mechanisms cover
  classes 0–14 with no gap); the SymPy-free recheck and the z3 SMT second source
  are genuinely independent decision procedures (z3 finds class 14 SAT without
  the convexity constraint, so it discriminates).
- Kalmanson/Farkas verifier (`check_kalmanson_certificate.py`): real exact-integer
  `0 > 0` Farkas check; rebuilds distance classes (DSU) and inequality
  coefficients from `kind`+`quad`; raises unless the weighted coefficient vector
  is exactly zero. The C19/C13 fixed-order certs verify (`zero_sum_verified:
  true`). The all-orders Z3 verifier genuinely replays stored clauses to UNSAT
  and validates each pair is a real inverse Kalmanson pair.
- `n=9` certificate verifiers (Kalmanson self-edge, turn-inequality Farkas dual,
  turn-indexing, quotient-soundness, strict-edge geometry): recompute from rows;
  no trusted stored boolean; `--assert-expected` provably raises on tampered
  input; no circular-sha "verification"; no float on exact steps.
- "Independent replay" checkers (e.g. `check_n9_kalmanson_selfedge_frontier_replay.py`):
  import no `erdos97` module, regenerate from scratch, assert hardcoded expected
  counts, and `--check` compares the regeneration to the stored artifact (catches
  tampering).
- Core `src/erdos97` lemma encoders match their documented lemmas; no soundness
  bug found. `scripts/`+`src/` are free of bare-except swallowing, `eval`/`exec`,
  `pickle`-on-repo-data, and mutable default arguments. The 12 ruff B023 warnings
  are immediate-consumption false positives.
- Cross-file consistency holds: official status falsifiable/open (and 59 days
  fresh, under the 90-day audit gate); strongest-local = `n<=8` everywhere;
  n=8 = 15 classes (1 cyclic-order + 14 PB/ED); the three distinct n=9 objects
  (184→158+26 frontier; 90→70+20 `{0,1,2,3}` packet; 1358→1164+194 shape sweep)
  are never conflated; the sorted row-set digest `dc28b32d…213d5` matches across
  files; node counts 100817 vs 100818 are different branchers, not drift.
- No claim-scope leakage: only `C19_skew` and `C13_sidon_1_2_4_10` carry all-order
  claims (correctly scoped); C25/C29 stay fixed-order; n=9/n=10 are never
  promoted; `contradictions.md` C-002 (abandoned unconditional `n>=13` count) is a
  genuinely different argument from the active edge-sensitive rich-support lemma
  (conditional, size-five-richness-only) — no live contradiction.
- Lean core files state the problem faithfully and smuggle no conclusion as an
  axiom; sketches honestly carry `sorry`; `check_lean_sketch_integrity.py` bans
  miracle-lemma declaration names.

---

## Verification log

Commands the reviewer actually ran, with results:

| Command | Result |
| --- | --- |
| `python scripts/check_text_clean.py` | PASS — "tracked text files are clean" (exit 0) |
| `python scripts/check_status_consistency.py` | PASS (exit 0) |
| `python scripts/check_artifact_provenance.py` | PASS — "manifest is valid" (validates sha256 + size_bytes + path existence + tracked-artifact coverage) |
| `git diff --check` | clean (exit 0) |
| `python -m ruff check .` | "All checks passed!" (exit 0) |
| `python -m pytest -q` (default markers) | **1458 passed, 678 deselected, 0 failed** in 595s |
| `python -m pytest --co -q -m "artifact"` | 537 artifact-marked tests exist (deselected by default) |
| `python scripts/independent_check_n8_artifacts.py --check --json` | `verified: true` (exit 0) |
| `python scripts/analyze_n8_exact_survivors.py --check --json` | 15 survivor classes, `exact_obstruction_artifact_pending_independent_review` (exit 0) |
| `python scripts/check_n8_class14_certificate.py --check --json` | `verified: true` (exit 0) |
| `python scripts/check_kalmanson_certificate.py <c19 compact> --summary-json` | `zero_sum_verified: true`, status `EXACT_OBSTRUCTION_FOR_FIXED_PATTERN_AND_FIXED_CYCLIC_ORDER` |
| `python scripts/check_kalmanson_certificate.py <c13 survivor> --summary-json` | `zero_sum_verified: true` |
| import + run `find_forbidden_overclaim_lines` on crafted strings | reproduced M1 bypasses (negation-clause + missing-verb PASS; bare forms BLOCKED) |
| import + run `command_outputs_path` on redirect forms | reproduced M6 (space-separated `>` → False; attached `>`/`--out` → True) |
| grep `validate_strict_inequality_support` across `t0*` packets | reproduced M4 (only T01 has it) |
| grep lean `Witness4.*` decls in Basic vs WitnessLemmas + import chain | reproduced M3 duplicate-declaration collision |
| `python -c` on `check_lean_files.py` path / grep `.github/workflows` | reproduced M3 (lake-absent silent skip; no Lean build in CI) |

What I could **not** verify (and why):
- The **artifact / certificate tier** (`make verify-artifacts`, `audit-artifacts`)
  and the **exhaustive checkers** (`check_n9_vertex_circle_exhaustive`,
  the n10 singleton search, the all-order Kalmanson order search,
  `verify-bridge-frontier`, `verify-n9-review`) were **not** run — out of the
  cheap-and-safe budget. The 537 `artifact`-marked tests and the
  `slow`/`exhaustive` tests were likewise not executed. The certificate verifiers
  themselves were read and found sound, and the default suite is green, but the
  fresh from-scratch enumerations were not reproduced this pass.
- **Lean was not built** (no `lake`/mathlib). M3's "would not compile" is inferred
  from source + the import graph, not from a build.
- The **`cpp/` second-source replay** was not compiled/run.
- The **mathematical correctness** of the geometry/proofs (the vertex-circle and
  turn geometric rules, the n8 survivor obstruction algebra, the bridge program,
  the Kalmanson inequalities' geometric validity) was treated as **out of scope** —
  see "Limits" below.

---

## Fix these first (ranked)

1. **Harden the overclaim detector (M1).** Add `:`/`,`/dash clause boundaries,
   require the negation to govern the verb, add synonym verbs, scan paragraph
   joins. Effort: ~1–2h. Highest leverage: it is the primary policy guard.
2. **Widen overclaim/status scanning to `docs/**/*.md` and add `docs/claims.md`
   to the source-of-truth set (M2).** Effort: ~2–3h (needs the quoted-sample
   allowlist).
3. **Run the `artifact`/certificate test tier in PR CI, or document its
   exclusion (M5).** Effort: ~1–2h CI wiring. This is the gate that actually
   validates certificates.
4. **Fix the Lean pilot (M3):** dedupe `Witness4.*` between `Basic.lean` and
   `WitnessLemmas.lean`; decide whether to enforce `lake build` in CI or mark the
   tier text-lint-only. Effort: ~1–2h to dedupe; more to wire a Lean toolchain.
5. **Restore/factor the dropped `validate_strict_inequality_support` self-check
   across the `t0*` packets (M4).** Effort: ~1h.
6. **Close the provenance redirection-detection gap (M6).** Effort: ~30m; latent
   but cheap.
7. **Low cleanups:** relabel the B12 spread in README/STATE; backfill
   `CHANGELOG.md`; sync `docs/formalization.md` Lean enumeration. Effort: <1h
   total.

---

## Limits of this review

- **This pass audited the verification infrastructure, not the mathematics.** It
  checked that "exact" paths use exact arithmetic, that checkers assert real
  properties and are not vacuous/circular, that certificates verify what they
  claim mechanically, and that the source-of-truth files are mutually consistent
  and non-overclaiming. It did **not** check whether the underlying lemmas and
  geometric rules are mathematically correct. Per `docs/review-priorities.md`,
  the following still require a human geometry/proof reviewer and are out of scope
  here: the octagon proof note and base-apex lemma (Priority 1); the `n=8`
  exact-survivor obstruction algebra and class-14 Gröbner branch (Priorities 2–3);
  the review-pending `n=9` vertex-circle checker, its filter necessity, and the
  geometric turn lemma (Priorities 5–6); the `n=10` singleton-slice draft
  (Priority 6b); and the all-order Kalmanson/SMT encoding trust (Priority 7).
- **Coverage was by sampling and targeted adversarial reads, not line-by-line
  over all 344 scripts / 333 test files / ~300 docs / 238 certificates / 12 Lean
  files under `lean/` (plus the root `lakefile.lean`).** The load-bearing paths
  (n≤8, Kalmanson, the guardrail checkers, the
  n9 certificate verifiers, cross-file consistency, scope discipline) were read
  closely; the long tail of `bootstrap-t12-*` micro-packets and per-template
  packets was spot-checked (headers/footers uniformly carry the review-pending +
  "not a proof / not a counterexample" hedges).
- **Directories not examined in depth:** `incoming/` (archive), `notebooks/`,
  `cpp/` (beyond reading the replay claim), `references/`, `papers/`,
  `inventory.json`, `kernels.json`.
- **No expensive or fresh-enumeration command was run** (see the verification
  log); conclusions about those tiers rest on reading the code plus the green
  default suite, not on re-execution.
