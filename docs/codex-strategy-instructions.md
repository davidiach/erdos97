# Codex strategy instructions

Status: strategic planning guidance only; not mathematical evidence.

This document guides Codex task selection in this repository. If it conflicts
with `AGENTS.md`, `README.md`, `STATE.md`, `RESULTS.md`,
`metadata/erdos97.yaml`, `docs/claims.md`, or
`docs/review-priorities.md`, those files control. In particular, no general
proof and no counterexample are claimed, and the official/global status remains
falsifiable/open unless it is manually rechecked and updated from the official
source.

## Mission

Work on Erdos Problem #97 with one goal: make real progress without
overclaiming.

The repository is already strong at exact obstruction checking for fixed
selected-witness patterns, fixed cyclic orders, finite slices, and review
pending finite-case artifacts. The strategic gap is scope. Erdos #97 requires
ruling out every strictly convex polygon with arbitrary `n`, arbitrary
per-center radii, and arbitrary selected 4-witness choices.

The highest-value work narrows that scope gap.

## Task selection rule

Before starting a task, name the bridge it might strengthen. If no bridge is
strengthened, record why the work is still useful, for example independent
audit, verifier hardening, provenance cleanup, or a negative-control result.

Prefer work that changes this form:

```text
Given this selected-witness pattern, cyclic order, or finite slice,
exact constraints imply contradiction.
```

into this form:

```text
Every hypothetical counterexample must contain or reduce to
one of the forbidden structures.
```

## Scope discipline

Do not claim a general proof of Erdos #97.

Do not claim a counterexample unless there are exact coordinates, exact
algebraic certificates, interval certificates, SMT certificates, or formal
proofs verifying the selected equal-distance equations, strict convexity,
distinct vertices, and selected incidence pattern.

Do not promote `n=9`, `n=10`, C13, C19, C29, B12, P18, P24, or any other
fixed-pattern, fixed-order, sampled-window, or review-pending result into a
global theorem.

When choosing a trust label, use the weakest label compatible with the evidence
and the repository ledgers. Common planning labels include:

- `LEMMA`
- `EXACT_OBSTRUCTION`
- `MACHINE_CHECKED_FINITE_CASE_ARTIFACT`
- `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`
- `MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING`
- `NUMERICAL_EVIDENCE`
- `NUMERICAL_NONLINEAR_DIAGNOSTIC`
- `FIXED_ORDER_DIAGNOSTIC`
- `PROVENANCE`
- `FAILED_ROUTE`

## High-leverage directions

### Reusable vertex-circle lemmas

Treat the `n=9` vertex-circle computation as a source of candidate reusable
templates until independently audited. Do not cite it as established theorem
input without its review-pending label.

Useful work:

- extract one compact self-edge local template into proof-facing hypotheses;
- extract one compact strict-cycle local template into proof-facing hypotheses;
- write minimal independent checkers for each template packet;
- document the exact incidence and cyclic-order hypotheses needed for the
  template, and what the template does not prove.

Good inputs include `docs/n9-vertex-circle-template-lemma-catalog.md`, the
focused T01/T02/T03/T04/T05/T06/T07/T08/T09 self-edge notes, the focused
T10/T11/T12 strict-cycle notes, and their checked JSON packets under
`data/certificates/`.

### Stronger fragile-cover bridges

The minimal fragile-cover bridge is a proved necessary condition for minimal
counterexamples, but pure fragile-cover hypergraph constraints are too weak:
the block-6 abstract family is the standing negative control.

Useful work adds a genuinely geometric necessary condition, such as
critical-radius ordering, dependency-cycle restrictions for the witness map
`pi`, row-circle constraints, vertex-circle monotonicity, crossing constraints
between fragile rows and full selected rows, or interaction with stuck-set /
ear-orderability failures.

Any strengthened condition should be documented as necessary for a minimal
geometric counterexample and tested against an abstract family that currently
passes the fragile-cover checks.

### Removable-vertex descent with retained geometry

The audited external removable-vertex program supplies a useful proof spine,
but its live frontier is not an incidence-only fragile-cover lemma. The current
source retains global four-equal-distance data, minimum-enclosing-circle cap
geometry, and one common source-indexed critical-shell system.

Useful work should target the full retained system and allow the critical
source row to vary. Two weaker targets are recorded negative controls:

- a large cap need not contain an abstractly uncovered vertex; and
- a prescribed critical row need not contribute two common-cap support
  points.

Prefer either a direct contradiction from the full retained live data or an
exact target-faithful countermodel. See
`external-removable-vertex-frontier-audit-2026-07-18.md` for the pinned source
snapshot, crosswalk, and acceptance criteria.

The historical four-hit exact-five reduction and exact-six artifact replay
remain reproducible, but neither is the sharp external target. Upstream closes
the all-reverse exact-six slice and now labels further literal exact-six CEGAR
nonconvergent under its optimized engine. Do not resume broad literal-schema
mining, aggregate cut rounds, anonymous-row adapters, or the equal-radius
escape argument without a new nonlinear Euclidean/MEC, full-fiber, minimality,
or global non-`IsM44` ingredient.

The current external target is source-faithful exact-seven role coverage. The
public L0 enumerator has exactly 1,000 all-fresh schemas, but fresh-role
coincidence/merge cases and L1 first-apex rows are absent. The cited Lean
named-interior normal-form source is also not committed publicly. First require
a reproducible public theorem source, then checked merge/L1 coverage. Any
source-faithful SAT survivor should move to nonlinear Euclidean, MEC,
full-fiber, or minimality analysis; it is not a counterexample. See
`external-exact-seven-l0-audit-2026-07-19.md`.

### Kalmanson/Farkas template extraction

The C13 and C19 all-order Kalmanson certificates are fixed-pattern results,
but their inverse-pair clauses may contain reusable order-search templates.

Useful work classifies repeated ordered-quadrilateral pairs, explains which
selected-distance quotient structures make the inequalities cancel, and emits
human-readable template records with verifiers. The output should cover a
template or family, not merely one more fixed-order certificate.

### Independent trust audits

Audit work is valuable when it treats checked-in JSON and certificates as
inputs rather than generated truth. The best audit targets remain the `n=8`
finite-case artifacts, the delicate `n=8` class `14`, the review-pending
`n=9` vertex-circle checker, and the draft `n=10` singleton-slice package.

## Low-leverage work to avoid

Avoid certificate archaeology unless it produces reusable mathematics.

Examples of low-leverage work:

- making a fixed C29 certificate smaller without extracting a reusable lemma;
- profiling C19 or C29 rows without producing order-search clauses or bridge
  constraints;
- adding numerical near-misses without an exactification plan;
- killing another hand-picked sparse pattern without explaining why arbitrary
  counterexamples reduce to that family.

Certificate simplification is useful only when it yields a reusable local
obstruction lemma, a new exact pruning rule, a bridge condition forced by
arbitrary counterexamples, or an independently checkable compact proof object
for an already important result.

## Failed routes

Before reviving a known failed route, read `docs/failed-ideas.md` and identify
the new ingredient that changes the failure mode. In particular, do not restart
arguments based only on:

- circumcenter-inside-witness-hull contradictions;
- middle-neighbor forest assumptions;
- consecutive-witness assumptions;
- cube-pattern-only `n=8` proofs;
- forced indegree-four regularity outside saturated cases;
- generic Jacobian rank at nonsolutions;
- common-radius or unit-distance shortcuts;
- B12 or C13 numerical near-misses as live candidates;
- pure fragile-cover hypergraph constraints;
- more fixed-pattern killing without a bridge.

## Preferred report shape

Every proof-facing Codex change should answer:

```text
What exact mathematical object is being studied?
Is this a global theorem, finite-case artifact, fixed-pattern obstruction,
fixed-order obstruction, review-pending diagnostic, numerical artifact,
or failed-route record?
What hypotheses are required?
Which arbitrary-counterexample bridge, if any, does this strengthen?
What does this rule out?
What does it not rule out?
What command verifies it?
What files changed?
What trust label applies?
```

## Validation

After code or documentation changes, run `make verify-fast` or the raw fast
tier from `AGENTS.md` / `README.md`. For finite-case, certificate, or public
theorem-style updates, run the relevant artifact checker or record exactly
which command could not be run and why.
