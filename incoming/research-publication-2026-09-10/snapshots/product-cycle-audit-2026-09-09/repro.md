# Reproduction

Use Python 3.10 or newer. The exact replay uses only the standard library and
can run with `-S` (no third-party site packages). Do not use `-O`.

From this directory:

```sh
python -S replay.py --output fresh-validation.json
```

This copies the packet to a temporary directory, runs all exact fixed-system
certificates, the positive rational relaxations, four exact geometry controls,
the incidence-only guardrail, 35 defensive tests and 12 publication-core tests.
It does not run an optimizer, regenerate a search frontier, or modify inputs/.
Two test suites contain 47 distinct tests in total; individual replays inside
tests are repeated checks, not additional independent mathematical reviews.

Important standalone checks:

```sh
python -S verify/check_combined.py reports/all_fixed_system_certificates.json
python -S verify/check_positive_relaxations.py reports/angle_survivor_preflight.json reports/full_metric_preflight.json
python -S verify/check_geometry.py candidate_counterexamples/c3_maximum_root_rich_neighborhood_21.json
python -S verify/check_geometry.py candidate_counterexamples/supplier_arc_positive_12.json
python -S verify/check_six_cycle.py candidate_counterexamples/upper_six_cycle_exact_nonconvex_18.json
python -S -m unittest -v test_product_cycle_audit_20260909.py
```

Optional NEW numerical search (requires NumPy and SciPy; not exact proof):

```sh
python search/max_root_local_probe.py --help
python search/lattice_milp.py --help
python search/realize_nine.py --restarts 30 --nfev 1500 --seed 9709093 --output fresh-realization.json
```

The last command reruns a now-obstructed benchmark. Its current role is regression
for collapse detection, not a live counterexample search. Do not call its small
residuals exact equalities. Existing command-line options and recorded output
files state their actual finite pools, parameters, and termination conditions.

Optional bounded C3 enumeration, preserving the specified 9-orbit model:

```sh
c++ -O3 -std=c++17 search/nine_with_supplier_arc.cpp -o /tmp/erdos97-nine-arc
/tmp/erdos97-nine-arc --all --limit 2000000 --output fresh-arc-rows.jsonl
```

Exit code 3 denotes the node guard, not a mathematical exclusion. That run has
not integrated the later diamond-phase equalities; frontier.md identifies that
next modification. The full nine-orbit universe was NOT exhausted in this packet.

The historical inputs remain byte-bound by manifest.json. Reports are either
stored exact certificates/outputs or explicitly classified numerical records.
No historical source bytes should be overwritten when reproducing searches.
Repository-wide `make verify-fast`, `make verify-artifacts`, root Ruff, and
Python 3.10/3.11 compatibility gates were not run here because the environment
contains a scoped export rather than a full checkout, lacks Ruff, and provides
Python 3.13.5. No Lean changes were made. These are unrun gates, not passes.


## Phase-filter continuation

```sh
python -S verify/check_phase_filter.py
c++ -O3 -std=c++17 -Wall -Wextra -Wpedantic search/nine_with_phase.cpp -o /tmp/nine-phase
python search/run_phase_search.py --binary /tmp/nine-phase --limit 2000000 --seconds 30 --name fresh-phase
```

The saved run uses the two-million-node guard and is not exhaustive. The exact
Python replay checks the retained C++ decision batch and produces certified
one/two-diamond contradictions; it does not rerun the entire search.
`search/add_phase_filter.py` regenerates the C++ adaptation from its retained
predecessor and records source hashes. The full phase-equation span is not yet
integrated with the chord-angle optimizer.
