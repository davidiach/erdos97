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

Run checked-in artifact and certificate validators explicitly. The current
audit command set is maintained in `Makefile` and
`scripts/run_artifact_audit.py`; the block below records commonly used
validators and should be cross-checked against those files before a release or
review packet.

```bash
pytest -q -m artifact
python scripts/check_round2_certificates.py
python scripts/check_kalmanson_certificate.py data/certificates/round2/c19_kalmanson_known_order_unsat.json
python scripts/check_ptolemy_log_filter.py --certificate data/certificates/round2/c17_skew_ptolemy_log_certificate.json --summary-json
python scripts/independent_check_n8_incidence_json.py --json
python scripts/analyze_n8_exact_survivors.py --check --json
python scripts/analyze_n8_exact_survivors.py --check --json \
  --check-compatible-orders-data data/incidence/n8_compatible_orders.json \
  --check-exact-analysis-data certificates/n8_exact_analysis.json
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected
python scripts/check_n9_vertex_circle_frontier_motif_classification.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_self_edge_path_join.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_self_edge_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_strict_cycle_path_join.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_strict_cycle_template_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_template_lemma_catalog.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t01_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t02_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t03_self_edge_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_t10_strict_cycle_lemma_packet.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_admissible_gap_replay.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_gap_self_edge_cores.py --check --assert-expected --json
python scripts/check_n10_vertex_circle_singletons.py --assert-expected --spot-check-row0 0 --spot-check-row0 63 --spot-check-row0 125
python scripts/check_n10_secondary_singleton_replay.py --check --assert-expected --json
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
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --write
```

The `n=8` incidence enumeration is the expensive part of the current local
pipeline. Its checked-in result should eventually be supplemented with a compact
branch-count or independent completeness certificate.

The `n=9` vertex-circle exhaustive checker is review-pending. It is faster than
the fresh `n=8` incidence enumeration on the current machine, but it is still a
full replay and should be reviewed before it changes the source-of-truth local
finite-case status.

The `n=10` singleton-slice checker is a draft review-pending artifact check.
The command above validates the imported counts and reruns row0 singleton IDs
`0`, `63`, and `125` with the repo-native generic checker; it is not a full
repo-native replay of all 126 singleton slices and does not promote `n=10`.
