# AGENTS.md

## Repository role

This repository is a public research log and reproducibility workspace for
Erdos Problem #97. It is not a solved-proof repository.

## Non-overclaiming rules

- Always preserve: no general proof and no counterexample are claimed.
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

## Test commands

Before changing mathematical claims, read `README.md`, `STATE.md`,
`RESULTS.md`, `metadata/erdos97.yaml`, `docs/claims.md`, and
`docs/review-priorities.md`. For task selection, also read
`docs/codex-backlog.md`.

Run the fast tier after documentation or code changes:

```bash
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
python scripts/check_artifact_provenance.py
git diff --check
python -m ruff check .
python -m pytest -q
```

The same fast tier is available as:

```bash
make verify-fast
```

For finite-case or public theorem-style artifact changes, also run the
artifact tier or explain exactly which command could not be run and why:

```bash
python scripts/independent_check_n8_artifacts.py --check --json
python scripts/enumerate_n8_incidence.py --summary
python scripts/analyze_n8_exact_survivors.py --check --json
python scripts/check_round2_certificates.py
python scripts/check_kalmanson_certificate.py data/certificates/round2/c19_kalmanson_known_order_two_unsat.json --summary-json
python scripts/check_kalmanson_two_order_search.py --name C13_sidon_1_2_4_10 --n 13 --offsets 1,2,4,10 --assert-obstructed --assert-c13-expected --json
python scripts/check_kalmanson_two_order_z3.py --certificate data/certificates/c19_skew_all_orders_kalmanson_z3.json --assert-unsat
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
```

The artifact tier is available as:

```bash
make verify-artifacts
```

The scheduled/manual GitHub artifact audit runs the same artifact commands with
metadata capture. Locally, use:

```bash
python scripts/check_status_consistency.py --max-official-status-age-days 90
make audit-artifacts
```

## Research hygiene

- Separate exact proofs from heuristics and numerical evidence.
- Label claims using the repo trust taxonomy.
- Keep fixed-pattern, fixed-order, all-order-for-one-pattern, `n <= 8`
  repo-local, and review-pending `n=9` artifacts in separate claim scopes.
- Prefer small reproducible JSON artifacts over screenshots or prose-only
  claims.
- Record failed approaches clearly enough that future work avoids repeating
  them.
- Do not prepare OEIS submissions from AI-generated output.
