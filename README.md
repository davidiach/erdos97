# Erdős Problem #97 — counterexample/proof search

![tests](https://github.com/davidiach/erdos97/actions/workflows/tests.yml/badge.svg)

This repository is a public research log and reproducibility workspace for Erdős Problem #97.

**Status:** No general proof and no counterexample are claimed. This repo records reproducible searches, obstruction lemmas, failed approaches, finite-case proofs, and exact-certification attempts.

## Where to start

- For the short working state, read [`STATE.md`](STATE.md).
- For the long-form canonical synthesis and claim reconciliation, read
  [`docs/canonical-synthesis.md`](docs/canonical-synthesis.md) before adding
  new claims, search branches, or proof attempts.
- For upstream alignment with `teorth/erdosproblems`, read
  [`docs/upstream-alignment.md`](docs/upstream-alignment.md).
- For independent audit instructions, read
  [`docs/reviewer-guide.md`](docs/reviewer-guide.md).
- For current review priorities, read
  [`docs/review-priorities.md`](docs/review-priorities.md).
- For canonical status metadata, see
  [`metadata/erdos97.yaml`](metadata/erdos97.yaml).
- For documentation navigation, read [`docs/index.md`](docs/index.md).
- For the compact results ledger, read [`RESULTS.md`](RESULTS.md).
- For proved local facts, read [`docs/claims.md`](docs/claims.md).
- For the reproducible `n=7` Fano enumeration, read [`docs/n7-fano-enumeration.md`](docs/n7-fano-enumeration.md).
- For the reproducible `n=8` incidence-completeness enumeration, read
  [`docs/n8-incidence-enumeration.md`](docs/n8-incidence-enumeration.md).
- For the `n=8` exact survivor obstruction artifact, read
  [`docs/n8-exact-survivors.md`](docs/n8-exact-survivors.md).
- For the review-pending exhaustive `n=9` vertex-circle finite-case checker,
  read [`docs/n9-vertex-circle-exhaustive.md`](docs/n9-vertex-circle-exhaustive.md).
- For the review-pending `n=10` singleton-slice finite-case draft, read
  [`docs/n10-vertex-circle-singleton-slices.md`](docs/n10-vertex-circle-singleton-slices.md).
- For a compact human-readable proof-note draft excluding bad convex octagons,
  read [`docs/n8-geometric-proof.md`](docs/n8-geometric-proof.md).
- For an interactive visualization of that proof idea, open
  [`docs/octagon-trap.html`](docs/octagon-trap.html).
- For the crossing-bisector, mutual-rhombus, phi 4-cycle rectangle-trap, and
  vertex-circle fixed-pattern filters, read
  [`docs/mutual-rhombus-filter.md`](docs/mutual-rhombus-filter.md),
  [`docs/phi4-rectangle-trap.md`](docs/phi4-rectangle-trap.md), and
  [`docs/vertex-circle-order-filter.md`](docs/vertex-circle-order-filter.md).
- For the round-two fixed-order Kalmanson/Farkas certificate, read
  [`docs/round2/round2_merged_report.md`](docs/round2/round2_merged_report.md)
  and [`docs/round2/kalmanson_distance_filter.md`](docs/round2/kalmanson_distance_filter.md).
- For the weak exact minimum-radius short-chord filter, read
  [`docs/minimum-radius-filter.md`](docs/minimum-radius-filter.md).
- For a partial bridge theorem from minimality to fragile-cover witness
  systems, read
  [`docs/minimal-fragile-cover-bridge.md`](docs/minimal-fragile-cover-bridge.md).
- For fixed-selection stuck-set mining around the bridge/peeling program, read
  [`docs/stuck-set-miner.md`](docs/stuck-set-miner.md).
- For search patterns, read [`docs/candidate-patterns.md`](docs/candidate-patterns.md).
- For known bad proof routes, read [`docs/failed-ideas.md`](docs/failed-ideas.md).
- For the verification standard, read [`docs/verification-contract.md`](docs/verification-contract.md).
- For archive synthesis provenance, read [`inventory.json`](inventory.json),
  [`kernels.json`](kernels.json), [`contradictions.md`](contradictions.md),
  and [`dropped_kernels.md`](dropped_kernels.md).
- For formalization alignment, read [`docs/formalization.md`](docs/formalization.md).
- For possible OEIS connections, read
  [`docs/oeis-possibilities.md`](docs/oeis-possibilities.md).
- For repository-level Codex guidance, read [`AGENTS.md`](AGENTS.md).
- For runnable verification, start with [`scripts/verify_candidate.py`](scripts/verify_candidate.py).
- For current work items, see [`docs/review-priorities.md`](docs/review-priorities.md),
  [`docs/codex-backlog.md`](docs/codex-backlog.md), and the live
  [open GitHub issues](https://github.com/davidiach/erdos97/issues).

## Problem

Let `P` be a strictly convex polygon in the Euclidean plane with vertex set `V`, `|V| = n >= 5`. For a vertex `v`, define

```text
E(v) = max_{r > 0} #{ w in V \ {v} : |vw| = r }.
```

The question is whether every convex polygon must have some vertex `v` with `E(v) <= 3`.

Equivalently, can one find a strictly convex polygon whose every vertex has **four** other vertices on a circle centered at that vertex?

A counterexample consists of:

```text
n >= 5
strictly convex points p_0,...,p_{n-1}
4-sets S_i subset {0,...,n-1} \ {i}
```

such that, for each center `i`, all values

```text
|p_i - p_j|^2,  j in S_i
```

are equal. The radius may depend on `i`; the selected set may depend on `i`; the directed incidence graph need not be symmetric.

## Current status in this repo

Official/global status remains falsifiable/open.

No general proof and no counterexample are claimed.

The selected-witness incidence method rules out `n <= 8` in this repo-local,
machine-checked finite-case sense. In the `n=7`
equality case, the 720 pointed Fano patterns fall into 54 cyclic-dihedral
classes; in every case the common-witness chord map has cycle type `7+7+7`,
so the required perpendicularity relation has an odd cycle. See
[`docs/n7-fano-enumeration.md`](docs/n7-fano-enumeration.md).

For `n=8`, [`scripts/enumerate_n8_incidence.py`](scripts/enumerate_n8_incidence.py)
derives indegree regularity from the column-pair cap, enumerates all necessary
incidence survivors, and reduces them to 15 canonical classes. Exact
cyclic-order and perpendicular-bisector/equal-distance checks then leave no
strictly convex realization for those classes. See
[`docs/n8-incidence-enumeration.md`](docs/n8-incidence-enumeration.md) and
[`docs/n8-exact-survivors.md`](docs/n8-exact-survivors.md). External/public
theorem claims should still get independent review of the computer-assisted
artifacts.

The crossing-bisector, mutual-rhombus, phi 4-cycle rectangle-trap, cyclic
crossing-CSP, and vertex-circle order filters now exactly kill several
previously live fixed selected-witness patterns, including
`B12_3x4_danzer_lift`, `B20_4x5_FR_lift`, `C17_skew`, `C20_pm_4_9`,
`C16_pm_1_6`, `C13_pm_3_5`, `C9_pm_2_4`, `P18_parity_balanced`, and
`P24_parity_balanced`. The phi 4-cycle rectangle-trap filter also kills a
registered fixed `n=9` selected-witness pattern containing
`{0,6}->{2,8}->{1,5}->{4,7}->{0,6}`. These are fixed-pattern obstructions, not
a general proof of the problem.

A review-pending exhaustive `n=9` vertex-circle checker now records a candidate
repo-local finite-case extension: the cross-check leaves 184 full
selected-witness assignments after the pair/crossing/count filters, and the
vertex-circle filter kills all 184 by exact self-edge or strict-cycle
obstructions. This is not yet promoted to the source-of-truth strongest local
result; independent review is required before any public theorem-style claim.
See [`docs/n9-vertex-circle-exhaustive.md`](docs/n9-vertex-circle-exhaustive.md).

An incoming `n=10` singleton-slice continuation is now recorded as a
review-pending finite-case draft: all 126 row0 singleton slices report zero
full assignments, with 4,142,738 total visited nodes and no aborted slices.
The artifact is an audit target only and is not promoted to the source-of-truth
strongest local result. See
[`docs/n10-vertex-circle-singleton-slices.md`](docs/n10-vertex-circle-singleton-slices.md).

Round two first added an exact compact Kalmanson/Farkas certificate for one
fixed `C19_skew` selected-witness pattern and one fixed cyclic order:
`[18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1]`. The checked certificate is
`data/certificates/round2/c19_kalmanson_known_order_two_unsat.json`; the earlier
94-inequality certificate remains checked as provenance.

A follow-up SMT refinement now kills the fixed abstract `C19_skew` pattern
across all cyclic orders: every cyclic order contains a two-inequality
Kalmanson inverse-pair obstruction after selected-distance quotienting. The
checked certificate is
`data/certificates/c19_skew_all_orders_kalmanson_z3.json`, and the verifier is
`scripts/check_kalmanson_two_order_z3.py`. This retires the registered sparse
`C19_skew` fixed-pattern lead, but it is still not a proof of Erdos #97.

A C13 Kalmanson pilot kills one registered non-natural
`C13_sidon_1_2_4_10` order `[5,0,10,8,9,7,4,6,2,11,12,3,1]` by the exact
certificate
`data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json`.
The follow-up exact order search now kills this fixed C13 Sidon pattern across
all cyclic orders; see `docs/kalmanson-two-order-search.md`. This does not
settle the larger sparse frontier or prove Erdos #97.

A later sparse-frontier probe tested the larger Sidon entries
`C25_sidon_2_5_9_14` and `C29_sidon_1_3_7_15`. The C25 Kalmanson-filter
survivor is exactly killed by vertex-circle and Altman filters. The recorded
C29 order first survived the lightweight fixed-order exact sweep, the
two-inequality Kalmanson inverse-pair search, the metric LP diagnostic, and a
slow global Ptolemy NLP diagnostic, but it is now exactly killed by the
165-inequality fixed-order Kalmanson/Farkas certificate
`data/certificates/c29_sidon_fixed_order_kalmanson_165_unsat.json`. This is
still only a fixed selected-witness pattern plus fixed cyclic-order
obstruction, not an all-order C29 result and not a counterexample claim. See
[`data/certificates/c25_c29_sparse_frontier_probe.json`](data/certificates/c25_c29_sparse_frontier_probe.json)
and [`docs/sparse-frontier-diagnostic.md`](docs/sparse-frontier-diagnostic.md).

The previous best numerical near-miss was `B12_3x4_danzer_lift`. It remains a
useful degeneration diagnostic, but the fixed selected pattern is now exactly
killed by the mutual-rhombus midpoint filter. The saved numerical artifact is
still retained as provenance for the failed route, **not** as a solution.

The best saved B12 object is **not** a counterexample: its max
selected-distance spread is about `0.0068`, and its convexity margin is about
`1e-6`.

Any claimed counterexample needs exact coordinates, or an exact algebraic
certificate, verifying the distance equalities and strict convexity.

Key diagnostics for the best saved near-miss:

```text
n: 12
pattern: B12_3x4_danzer_lift
max squared-distance spread: 0.006806368780585714
RMS equality residual:       0.0019599509549614457
convexity margin:            9.999999943508973e-07
minimum edge length:         0.0007465865604262556
status: numerical artifact only; fixed selected pattern exactly killed
```

See [`STATE.md`](STATE.md) for the most compact working summary and
[`docs/canonical-synthesis.md`](docs/canonical-synthesis.md) for the full
canonical synthesis.

## Trust levels used here

Use these labels consistently:

- **THEOREM**: fully proved and checked.
- **LEMMA**: fully justified local result, preferably with tests or formalizable proof.
- **CONJECTURE**: plausible but unproved mathematical claim.
- **HEURISTIC**: useful search guidance, not a proof ingredient.
- **NUMERICAL_EVIDENCE**: floating-point result; never a proof of equality.
- **FAILED_APPROACH**: route that currently appears invalid or degenerate.
- **LITERATURE_RISK**: reference or missing reference that could change the project status.
- **INCIDENCE_COMPLETENESS**: exhaustive finite enumeration under proved incidence constraints.
- **EXACT_OBSTRUCTION**: exact arithmetic, algebraic, interval, SMT, or formal certificate killing a pattern.
- **EXACTIFICATION**: algebraic, interval, SMT, or certificate work.
- **SAT_SMT**: finite abstraction or solver encoding.
- **INCIDENCE_PATTERN**: directed 4-neighbor pattern proposal or enumeration.
- **COUNTEREXAMPLE_CANDIDATE**: candidate requiring independent verification; not a counterexample.

## Repository map

```text
.
├── AGENTS.md                         # repository-level Codex guidance
├── README.md
├── RESULTS.md
├── STATE.md
├── metadata/
│   └── erdos97.yaml                  # canonical status metadata snapshot
├── pyproject.toml
├── src/erdos97/search.py              # main search/verification engine
├── src/erdos97/incidence_filters.py   # exact incidence obstruction filters
├── src/erdos97/stuck_sets.py          # fixed-selection stuck-set miner core
├── src/erdos97/motif_fingerprint.py   # cyclic/dihedral motif fingerprints
├── src/erdos97/stuck_motif_search.py  # bounded SMT stuck-motif search
├── src/erdos97/stuck_motif_sweep.py   # motif sweep and geometry smoke tests
├── src/erdos97/n7_fano.py             # exact n=7 Fano enumeration
├── scripts/                           # thin CLI helpers
├── tests/                             # smoke tests and incidence checks
├── docs/
│   ├── index.md                       # documentation navigation
│   ├── upstream-alignment.md          # relation to teorth/erdosproblems
│   ├── reviewer-guide.md              # independent audit instructions
│   ├── formalization.md               # Lean/formalization alignment
│   ├── oeis-possibilities.md          # exploratory OEIS notes
│   ├── canonical-synthesis.md         # long-form canonical project synthesis
│   ├── claims.md                      # proved vs heuristic statements
│   ├── candidate-patterns.md          # ranked incidence patterns
│   ├── failed-ideas.md                # failed arguments to avoid repeating
│   ├── exactification-plan.md         # numerical-to-exact certificate route
│   ├── stuck-set-miner.md             # bridge/peeling obstruction tooling
│   ├── n8-incidence-enumeration.md    # n=8 incidence-completeness proof
│   ├── n8-exact-survivors.md          # n=8 exact survivor obstructions
│   ├── mutual-rhombus-filter.md       # exact fixed-pattern filters
│   ├── vertex-circle-order-filter.md  # exact cyclic-order distance filter
│   ├── sat-smt-plan.md                # finite abstraction plan
│   ├── literature-risk.md             # what has/has not been checked
│   └── verification-contract.md       # candidate acceptance requirements
├── data/
│   ├── incidence/n7_fano_dihedral_representatives.json
│   ├── incidence/n8_incidence_completeness.json
│   ├── incidence/n8_reconstructed_15_survivors.json
│   ├── patterns/candidate_patterns.json
│   └── runs/best_B12_slsqp_m1e-6.json
└── certificates/
    ├── best_B12_certificate_template.json
    ├── n8_exact_analysis.json
    └── n8_polynomial_systems.txt
```

New generated checked certificates should normally live under
`data/certificates/`. The top-level `certificates/` directory is retained for
legacy n=8 artifacts and manual templates whose paths are already referenced by
docs, tests, and manifests.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
make verify-fast
```

`make verify-lint` runs the sub-minute text/status/provenance/ruff tier
without pytest. The default pytest configuration excludes tests marked
`artifact`, `slow`, or `exhaustive`; run `python -m pytest -q -m ""` when you
intentionally want the full marker set.

If `make` is not available, run the fast tier directly:

```bash
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
python scripts/check_artifact_provenance.py
git diff --check
python -m ruff check .
python -m pytest -q
```

Artifact and frontier checks are slower and should be run before finite-case,
certificate, or public theorem-style updates:

```bash
make verify-artifacts
```

The manual/scheduled artifact-audit workflow runs the same artifact commands
with command, commit, Python version, dependency snapshot, elapsed-time, and
output-hash metadata. It also includes the dated official-status consistency
check:

```bash
make audit-artifacts
```

If `make` is unavailable, treat `Makefile` and
`scripts/run_artifact_audit.py` as the source of truth for the current raw
command set. The current raw commands are:

```bash
python scripts/check_status_consistency.py --max-official-status-age-days 90
python scripts/check_artifact_provenance.py
python scripts/independent_check_n8_artifacts.py --check --json
python scripts/enumerate_n8_incidence.py --summary
python scripts/analyze_n8_exact_survivors.py --check --json
python scripts/check_round2_certificates.py
python scripts/check_kalmanson_certificate.py data/certificates/round2/c19_kalmanson_known_order_two_unsat.json --summary-json
python scripts/check_kalmanson_certificate.py data/certificates/c13_sidon_order_survivor_kalmanson_two_unsat.json --summary-json
python scripts/check_kalmanson_two_order_search.py --name C13_sidon_1_2_4_10 --n 13 --offsets 1,2,4,10 --assert-obstructed --assert-c13-expected --json
python scripts/check_kalmanson_two_order_z3.py --certificate data/certificates/c19_skew_all_orders_kalmanson_z3.json --assert-unsat
python scripts/analyze_kalmanson_z3_clauses.py --assert-expected --check-artifact reports/c19_kalmanson_z3_clause_diagnostics.json
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
python scripts/check_n9_vertex_circle_local_core_packet.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_core_templates.py --check --assert-expected --json
python scripts/check_n9_vertex_circle_frontier_motif_classification.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_product_cancellations.py --check --json
python scripts/check_n9_row_ptolemy_family_signatures.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_order_sensitivity.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_order_admissible_census.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_admissible_gap_replay.py --check --assert-expected --json
python scripts/check_n9_row_ptolemy_gap_self_edge_cores.py --check --assert-expected --json
python scripts/check_n9_base_apex_low_excess_ledgers.py --check --json
python scripts/check_n9_base_apex_escape_budget.py --check --json
python scripts/check_n9_selected_baseline_escape_budget_overlay.py --check --json
python scripts/check_n9_d3_escape_slice.py --check --json
python scripts/check_n10_vertex_circle_singletons.py --assert-expected --spot-check-generic
```

Useful exploratory commands:

```bash
erdos97-search --list-patterns
erdos97-search --verify data/runs/best_B12_slsqp_m1e-6.json --tol 1e-6
python scripts/interval_verify_candidate.py data/runs/best_B12_slsqp_m1e-6.json
python scripts/check_mutual_rhombus_filter.py --assert-expected
python scripts/check_vertex_circle_order_filter.py --pattern P18_parity_balanced --search --assert-obstructed
python scripts/check_min_radius_filter.py --pattern C19_skew --assert-pass
```

For a version-matched reproduction environment, install the checked snapshot
before installing this package:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
pip install -e . --no-deps
```

Run a small search:

```bash
erdos97-search --pattern B12_3x4_danzer_lift --mode polar --restarts 10 --max-nfev 1000 --out data/runs/new_attempt.json
```

Optional dependencies:

```bash
pip install sympy z3-solver
```

## Research hygiene

1. Do not present floating-point equalities as exact.
2. Keep optional search heuristics separate from necessary mathematical constraints.
3. Record failed approaches with enough detail that future work can avoid repeating them.
4. Prefer small reproducible JSON artifacts over screenshots or prose-only claims.
5. Any proposed counterexample should include an independent verifier output and then an exactification plan.

## Known nearby examples

The 3-neighbor version is false: Danzer produced a 9-point convex polygon where every vertex has 3 equidistant vertices, and Fishburn--Reeds produced a 20-point convex polygon where every vertex has 3 equidistant vertices at a common radius. These do not automatically extend to the 4-neighbor target.

A 1975 Erdos paper reports an unpublished all-`k` Danzer claim, but the official #97 page says this was not repeated later and was presumably mistaken. This repository treats that statement as unverified literature risk, not as a `k=4` counterexample; see [`docs/literature-risk.md`](docs/literature-risk.md).

## Contribution policy

Contributions are welcome if they are reproducible and clearly labelled. Especially useful contributions:

- new incidence patterns satisfying known necessary filters;
- independent verification scripts;
- exact obstruction lemmas;
- interval/SOS/SMT certificates for restricted classes;
- numerical candidates with robust convexity margins and residual below `1e-10`.

Please avoid presenting numerical near-equalities as counterexamples.

## License and citation

Code is licensed under the MIT License. Research notes, documentation, data artifacts, issue templates, and certificate templates are licensed under CC-BY-4.0. See [`LICENSE.md`](LICENSE.md).

If you use this repository, please cite it using [`CITATION.cff`](CITATION.cff).

## Maintenance checklist

- Run `make verify-fast` or the equivalent raw fast-tier commands.
- Run `make verify-artifacts` before finite-case, certificate, or public
  theorem-style updates, or record why a command could not be run.
- Run `make audit-artifacts` for audit metadata; it includes the dated
  official-status consistency check.
- Run `python scripts/check_text_clean.py`.
- Run `python scripts/check_status_consistency.py`.
- Confirm this README still says no general proof and no counterexample are claimed.
- Create labels matching `.github/labels.yml`.
- Keep current-work pointers aligned with `docs/review-priorities.md`,
  `docs/codex-backlog.md`, and the live GitHub issue list.
