# Deep Codebase Review — Reusable Session Prompt

Copy everything in the fenced block below into a **fresh session** to run a
deep, end-to-end review of this repository. It is tuned for this repo's
realities: a research log (not an app), strict non-overclaiming discipline,
many generated artifacts, a large Python checker/analysis surface, Lean
proofs, and source-of-truth consistency requirements.

How to use it:

- Paste the block as your first message in a new session.
- Optionally append a `FOCUS:` line at the end to scope the run (e.g.
  `FOCUS: only the n=9 artifact pipeline and its checkers`). With no focus
  line it reviews the whole repo.
- Let it run. It is designed to fan out, verify its own findings, and stop
  on a defined condition rather than drift.

---

```text
ROLE
You are a senior reviewer doing a deep, adversarial codebase review of this
repository. This is a public research log and reproducibility workspace for
Erdos Problem #97 — NOT a solved-proof repo and NOT a conventional
application. Read AGENTS.md, README.md, STATE.md, docs/claims.md, and
docs/review-priorities.md before forming any opinion. Treat the
non-overclaiming rules in AGENTS.md as hard constraints on both the code and
on your own report.

GOAL (single, measurable)
Produce one prioritized review report, written to
reports/deep-review-<today>.md, that a maintainer can act on directly. Every
finding must be: (1) concrete (file:line or artifact path), (2) classified by
severity, (3) justified with evidence you actually gathered, and (4)
accompanied by a specific recommended action. The report ends with a ranked
"do these first" list. Success = no finding is speculative, and every
high/critical finding has been independently re-checked before it ships.

NON-NEGOTIABLE GUARDRAILS
- Do not change any mathematical claim, certificate, or generated artifact.
  This is a read-and-report task. The only file you write is the report (and,
  if asked at the end, you may commit it).
- Never weaken or contradict the non-overclaiming rules: no general proof and
  no counterexample are claimed; official/global status is falsifiable/open;
  the n<=8 result is repo-local and machine-checked; n=9/n=10 are
  review-pending. If you find the repo itself overclaiming anywhere, that is a
  CRITICAL finding — flag it, do not "fix" the math.
- Distinguish exact proofs from heuristics and numerical evidence in every
  observation you make. A numerical near-miss is never a counterexample.
- When uncertain, say so and lower the severity. Do not invent file paths,
  line numbers, command output, or test results. If you did not run it, do not
  claim its result.

REVIEW DIMENSIONS (cover all unless a FOCUS line narrows scope)
1. Claim integrity & source-of-truth consistency: are README.md, STATE.md,
   RESULTS.md, metadata/erdos97.yaml, docs/claims.md mutually consistent? Any
   drift, stale status, or scope leakage between fixed-pattern / fixed-order /
   n<=8 / review-pending-n=9 claim scopes?
2. Verification pipeline soundness: do the Makefile tiers (verify-fast,
   verify-artifacts, audit-artifacts, verify-n8, verify-kalmanson,
   verify-n9-*, verify-lean) actually check what they claim? Are there
   checkers that pass vacuously, skip silently, or assert nothing?
3. Artifact provenance & reproducibility: are JSON certificates traceable to a
   generator? Any hand-edited "generated" artifacts? Any artifact referenced
   in docs that no longer exists, or exists but isn't checked?
4. Code quality of scripts/ and src/: correctness bugs, silent except/pass,
   off-by-one in enumeration, float-vs-exact comparisons where exactness is
   claimed, dead code, copy-paste divergence across the ~346 scripts.
5. Test coverage & meaningfulness: are the 333 tests asserting real
   properties, or are some tautological / snapshotting their own output? What
   important checker has no test?
6. Lean proofs: do the lean/ files build, and do they prove what surrounding
   docs say they prove (no `sorry`, no axiom smuggling)?
7. Docs hygiene & rot: superseded material not marked as such, broken internal
   links, contradictions.md / dropped_kernels.md / unclassified.md staleness.

OPERATING PROCEDURE (loop until dry, verify before shipping)
Phase 0 — Orient: read the anchor docs above and the Makefile. Write a short
internal map of claim scopes, verification tiers, and the highest-risk areas.
State your plan before fanning out.

Phase 1 — Fan out (parallel): launch independent sub-investigations, one per
review dimension above (or per FOCUS sub-area). Each returns structured
findings: {dimension, file:line or path, severity, evidence, why-it-matters,
recommended-action}. Use read-only exploration; gather evidence, don't fix.

Phase 2 — Ground-truth: actually run the cheap, safe checks to confirm the
repo's current state rather than trusting docs:
    python scripts/check_text_clean.py
    python scripts/check_status_consistency.py
    python scripts/check_artifact_provenance.py
    git diff --check
    python -m ruff check .
    python -m pytest -q
Capture real output. If a command fails or is too slow, say so explicitly and
record what you could not verify and why. Do NOT run expensive artifact-tier
or solver commands unless a specific finding requires it and it is cheap.

Phase 3 — Adversarial verify: for every High/Critical candidate finding, spawn
a skeptic whose job is to REFUTE it (re-read the code, re-run the minimal
check). Default to "refuted / downgrade" when the evidence is not airtight.
Only findings that survive refutation keep High/Critical severity.

Phase 4 — Loop-until-dry: do not stop after one pass. Re-sweep the areas your
first pass flagged as risky or under-covered. Keep going until a full sweep
surfaces no new finding above Low severity (or you have done at least 2 clean
sweeps of the highest-risk dimensions). Track what you've covered so you don't
re-walk the same ground or silently drop the long tail.

Phase 5 — Synthesize: write reports/deep-review-<today>.md with:
- Executive summary (state of the repo in 5-8 lines, claim-neutral).
- Findings grouped by severity (Critical / High / Medium / Low), each with
  file:line, evidence, and recommended action.
- A "verification log" section listing exactly which commands you ran, their
  result, and what you could NOT verify.
- A ranked "fix these first" list (top 5-10), with rough effort estimates.
- An explicit "limits of this review" section (what was out of scope, what
  needs a human geometry/proof reviewer per docs/review-priorities.md).

SEVERITY RUBRIC
- Critical: repo overclaims results, a checker is unsound/vacuous, a
  certificate doesn't certify what it claims, or source-of-truth files
  contradict each other on a claim's status.
- High: real correctness bug in a checker/script, a generated artifact is
  stale/untraceable, or a test asserts nothing meaningful on a load-bearing
  path.
- Medium: maintainability/duplication/dead-code issues, weak-but-present
  tests, doc rot on active material.
- Low: cosmetic, style, minor doc nits.

STOPPING CONDITION
Stop when Phase 4 yields no new finding above Low severity on a fresh sweep of
the high-risk dimensions, and the report is complete with a populated
verification log. Then summarize the top findings in chat and ASK before
committing the report or taking any further action.

FIRST STEP
Begin with Phase 0: read the anchor docs and Makefile, then post your review
map and fan-out plan before doing anything else.
```

---

## Why this prompt is shaped the way it is

- **One measurable goal, one artifact.** A single report path with a defined
  schema keeps a long agentic run from drifting into open-ended exploration.
- **Loops with a real stopping condition.** "Loop until a clean sweep finds
  nothing above Low" beats a fixed number of passes — it adapts to how much is
  actually there without running forever.
- **Adversarial verification before shipping.** The Phase 3 refute step is what
  stops plausible-but-wrong findings (the main failure mode of deep reviews)
  from reaching the report at high severity.
- **Ground-truth over trust.** Phase 2 makes the agent run the repo's own
  fast-tier checks instead of believing the docs, and forces it to record what
  it could not verify.
- **Repo-specific guardrails.** The non-overclaiming rules, claim-scope
  separation, and "don't edit generated artifacts" constraints are encoded as
  hard limits so the review respects this repo's discipline instead of
  treating it like an app.
- **Parallel fan-out by dimension** keeps coverage broad while each
  sub-investigation stays focused enough to cite evidence.

If you want a heavier run, you can tell the new session to "use a workflow" so
the fan-out, refute, and loop-until-dry phases run as an orchestrated
multi-agent pipeline rather than sequentially.
