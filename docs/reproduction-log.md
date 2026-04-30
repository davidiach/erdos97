# Reproduction Log

Status: operational guide, not a mathematical certificate.

This repository separates fast checks, artifact/certificate checks, and fresh
exhaustive enumeration. The split is intentional: a reviewer should be able to
run the default suite quickly without accidentally starting the full `n=8`
incidence search.

## Current Environment Note

The metadata file records the known-good local snapshot:

```text
Python: 3.12.2
Dependencies: requirements-lock.txt
Snapshot date: 2026-04-29
```

The lock file is a local dependency snapshot. It does not make the repository
offline-reproducible by itself, and it is not a proof certificate.

## Fast Checks

Plain pytest now runs the fast suite:

```bash
pytest -q
```

The repository hygiene checks are:

```bash
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
git diff --check
```

## Artifact Checks

Run checked-in artifact and certificate validators explicitly:

```bash
pytest -q -m artifact
python scripts/independent_check_n8_incidence_json.py --json
python scripts/analyze_n8_exact_survivors.py --check --json
python scripts/analyze_n8_exact_survivors.py --check --json \
  --check-compatible-orders-data data/incidence/n8_compatible_orders.json \
  --check-exact-analysis-data certificates/n8_exact_analysis.json
```

The independent incidence JSON checker validates the 15 stored survivor
representatives and brute-force canonical forms. It does not prove the
completeness of the enumeration.

## Slow Or Exhaustive Checks

Run fresh enumeration separately:

```bash
pytest -q -m "slow or exhaustive"
python scripts/enumerate_n8_incidence.py --summary
python scripts/enumerate_n8_incidence.py --summary \
  --check-data data/incidence/n8_incidence_completeness.json
```

The `n=8` incidence enumeration is the expensive part of the current local
pipeline. Its checked-in result should eventually be supplemented with a compact
branch-count or independent completeness certificate.
