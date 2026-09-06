# AGENTS.md

## Repository role

This repository is a public research log and reproducibility workspace for
Erdos Problem #97. It is not a solved-proof repository.

## Non-overclaiming rules

- Preserve the currently accepted claim scope until an explicit, evidence-backed
  status transition is reviewed and approved. Do not claim a proof or a
  counterexample without the required exact evidence and independent review.
  The current snapshot claims neither; this is a status, not a permanent outcome.
- Use the reviewed transition contract in `docs/status-transitions.md` for a
  stronger accepted result. Pending candidates must not silently replace it.
- The official/global status is falsifiable/open unless manually rechecked and
  updated from the official page.
- The local `n <= 8` result is repo-local and machine-checked; public
  theorem-style claims require independent review.
- Numerical near-misses are not counterexamples.
- Exact coordinates, algebraic certificates, interval certificates, SMT
  certificates, or formal proofs are required for exact claims.

## Source-of-truth discipline

- Keep `metadata/erdos97.yaml` aligned with `README.md`, `STATE.md`, and
  `RESULTS.md`.
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
