# AGENTS.md

## Repository role

This repository preserves the research log and reproducibility work for
Erdos Problem #97. An external negative resolution was released on
13 September 2026 by Liam Kruer, Jensen Kohlmeyer, and Liam Price.
Read `docs/external-resolution-2026-09-14.md` and
`metadata/external-resolution-2026-09-14.json` before interpreting older status
or task documents. This repository does not claim authorship of that result.

## Current research scope

- Do not start further affirmative-proof attempts for the unrestricted target.
- Older bridge queues, solver prompts, and open-problem descriptions are
  historical material, not current task authorization. This section controls
  conflicting historical instructions elsewhere in the repository.
- Preserve existing proofs, exact verifiers, failed routes, artifacts, and
  published paths. A negative global outcome does not automatically invalidate
  a correctly scoped local result or validate a pending one.
- Further reproduction, smaller explicit constructions, or other mathematical
  work require an explicitly selected scope. Do not start them automatically.

## Non-overclaiming rules

- Preserve the currently accepted claim scope until an explicit, evidence-backed
  status transition is reviewed and approved. Do not claim a proof or a
  counterexample without the required exact evidence and independent review.
  No original or independently replayed global result is currently claimed
  by this repository; the externally attributed result is recorded separately.
- Use the reviewed transition contract in `docs/status-transitions.md` for a
  stronger accepted result. Pending candidates must not silently replace it.
- Separate the external mathematical outcome from the canonical website's
  last retrieved label. The latter remains a dated record, not a live status.
  Never advance its successful-check date after a failed retrieval.
- The local `n <= 8` result is repo-local and machine-checked; public
  theorem-style claims require independent review.
- Numerical near-misses are not counterexamples.
- Exact coordinates, algebraic certificates, interval certificates, SMT
  certificates, or formal proofs are required for exact claims.

## Source-of-truth discipline

- Keep `README.md`, `STATE.md`, `RESULTS.md`, and `docs/claims.md` aligned
  with both metadata sources: `metadata/erdos97.yaml` for accepted local claims
  and the dated canonical-page record, and the source-pinned
  `metadata/external-resolution-2026-09-14.json` for the external result.
  Do not silently turn an external report into an accepted local transition.
- Do not edit generated artifacts if a generator exists.
- Keep archived/provenance statements clearly marked when superseded.

## Verification and repository layout

Follow [CONTRIBUTING.md](CONTRIBUTING.md) for the canonical setup, verification,
artifact, and Lean commands. Run the fast tier after changes and the artifact
tier for finite-case or public theorem-style artifact changes; report any
command that cannot be run and why.

Before changing mathematical claims, read `README.md`, `STATE.md`, `RESULTS.md`,
`metadata/erdos97.yaml`, `docs/claims.md`, and `docs/review-priorities.md`.
For task selection, also read `docs/codex-backlog.md`.

Preserve published paths, historical source snapshots, and independent
mathematical implementations. New reusable code belongs in `src/erdos97/`;
command scripts should call it. Use the shared JSON/path helpers for plumbing.
See `docs/repository-maintenance.md` for topic grouping and generated navigation.

## Research hygiene

- Separate exact proofs from heuristics and numerical evidence.
- Run exact preflight before numerical search. `--allow-obstructed` is only for
  deliberately impossible benchmarks, never for claiming a viable pattern.
  See `docs/research-engine-audit-fixes.md` for objective and scope controls.
- Label claims using the repo trust taxonomy.
- Keep fixed-pattern, fixed-order, all-order-for-one-pattern, `n <= 8`
  repo-local, and review-pending `n=9` artifacts in separate claim scopes.
- Prefer small reproducible JSON artifacts over screenshots or prose-only
  claims.
- Record failed approaches clearly enough that future work avoids repeating
  them.
- Do not prepare OEIS submissions from AI-generated output.
