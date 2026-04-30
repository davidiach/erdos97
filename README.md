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
- For a compact human-readable proof-note draft excluding bad convex octagons,
  read [`docs/n8-geometric-proof.md`](docs/n8-geometric-proof.md).
- For an interactive visualization of that proof idea, open
  [`docs/octagon-trap.html`](docs/octagon-trap.html).
- For the crossing-bisector, mutual-rhombus, and vertex-circle fixed-pattern
  filters, read [`docs/mutual-rhombus-filter.md`](docs/mutual-rhombus-filter.md)
  and [`docs/vertex-circle-order-filter.md`](docs/vertex-circle-order-filter.md).
- For the weak exact minimum-radius short-chord filter, read
  [`docs/minimum-radius-filter.md`](docs/minimum-radius-filter.md).
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
- For current work items, see [Issues #1-#7](https://github.com/davidiach/erdos97/issues).

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

The crossing-bisector, mutual-rhombus, cyclic crossing-CSP, and vertex-circle
order filters now exactly kill several previously live fixed selected-witness
patterns, including
`B12_3x4_danzer_lift`, `B20_4x5_FR_lift`, `C17_skew`, `C20_pm_4_9`,
`C16_pm_1_6`, `C13_pm_3_5`, `C9_pm_2_4`, `P18_parity_balanced`, and
`P24_parity_balanced`. These are fixed-pattern obstructions, not a general
proof of the problem.

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

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
pytest -q
python scripts/enumerate_n8_incidence.py --summary
python scripts/analyze_n8_exact_survivors.py --check --json
erdos97-search --list-patterns
erdos97-search --verify data/runs/best_B12_slsqp_m1e-6.json --tol 1e-6
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

- Run `pytest -q`.
- Run `python scripts/check_text_clean.py`.
- Run `python scripts/check_status_consistency.py`.
- Confirm this README still says no general proof and no counterexample are claimed.
- Create labels matching `.github/labels.yml`.
- Open the seed issues listed in `docs/initial-issues.md`.
