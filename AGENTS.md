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

Run these after documentation or code changes:

```bash
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
pytest -q
```

For finite-case artifacts, also run:

```bash
python scripts/enumerate_n8_incidence.py --summary
python scripts/analyze_n8_exact_survivors.py --check --json
```

## Research hygiene

- Separate exact proofs from heuristics and numerical evidence.
- Label claims using the repo trust taxonomy.
- Prefer small reproducible JSON artifacts over screenshots or prose-only
  claims.
- Record failed approaches clearly enough that future work avoids repeating
  them.
- Do not prepare OEIS submissions from AI-generated output.
