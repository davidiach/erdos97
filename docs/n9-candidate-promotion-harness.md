# n=9 Candidate Promotion Harness

Status: `REVIEW_HARNESS_ONLY`.

This note records the compact command surface for reviewing the current
repo-local `n=9` selected-witness candidate. It does not prove Erdos Problem
#97, does not claim a counterexample, does not update the official/global
status, and does not promote the review-pending `n=9` artifacts. Independent
mathematical review remains required before any theorem-style use.

## Purpose

The repository now has several independent-looking `n=9` obstruction routes:
the vertex-circle quotient route, the turn-packing route, and algebraic /
Kalmanson corroboration. The useful promotion-grade surface is not the full
artifact audit, which is intentionally broad. It is the shortest command chain
that exercises the current finite-case review bottlenecks and the
formalization-facing turn-packing contract.

The machine-readable route contract is
`metadata/n9_candidate_review.yaml`, checked by:

```bash
python scripts/check_n9_candidate_review_manifest.py --check --summary-json
```

That checker compares the manifest command list with the Makefile target,
verifies referenced docs and Lean files exist, and keeps the review gates
explicitly open. It does not run the mathematical replay commands.

The route contract points to the review-gate ledger
`metadata/n9_review_gate_ledger.yaml`, checked by:

```bash
python scripts/check_n9_review_gate_ledger.py --check --summary-json
```

That checker maps the compact harness to the A6/A7, A8, A10, B1/B3, and
corroborating Kalmanson review gates, then checks those gates against
`docs/n9-reduction-chain.md`, `docs/n9-review-packet.md`, and the route
manifest. It is review bookkeeping only, not mathematical evidence.

The route contract also points to the evidence matrix
`metadata/n9_review_evidence_matrix.yaml`, checked by:

```bash
python scripts/check_n9_review_evidence_matrix.py --check --summary-json
```

That checker validates the expected reviewer-facing output invariants for
every command in this harness. To execute the command chain and check the live
outputs against the matrix, run:

```bash
python scripts/check_n9_review_evidence_matrix.py --check --run --summary-json
```

Live replay is still harness validation, not independent mathematical review.

Finally, the route contract points to the reviewer dossier contract
`metadata/n9_review_dossier.yaml`, checked by:

```bash
python scripts/check_n9_review_dossier.py --check --summary-json
```

To render the on-demand Markdown worksheet, run:

```bash
python scripts/check_n9_review_dossier.py --markdown
```

The worksheet is a review aid only; it does not write a generated artifact and
does not mark any gate accepted.

The run-capture contract is `metadata/n9_review_run_bundle.yaml`, checked by:

```bash
python scripts/check_n9_review_run_bundle.py --check --summary-json
```

To execute the compact command surface and emit digest-level provenance for one
reviewer run, use:

```bash
python scripts/check_n9_review_run_bundle.py --check --run --summary-json
```

The live capture validates compact outputs against the evidence matrix and
records hashes/previews only. It does not write a generated artifact and does
not accept any review gate.

The reviewer-decision intake contract is
`metadata/n9_review_decision_intake.yaml`, checked by:

```bash
python scripts/check_n9_review_decision_intake.py --check --summary-json
```

To print a fillable decision template, run:

```bash
python scripts/check_n9_review_decision_intake.py --template
```

To validate an external written-review record, run:

```bash
python scripts/check_n9_review_decision_intake.py --decision path/to/decision.yaml --check --summary-json
```

The intake checker validates gate partitions and allowed outcomes only. It
does not update source-of-truth status files and does not accept any gate by
itself.

The vertex-circle route decision preflight is checked by:

```bash
python scripts/check_n9_vertex_circle_route_decision_preflight.py --check --summary-json
```

It verifies that the internal A6/A7, A8, and A10 notes are present, that the
vertex-circle route gates remain open, and that a real route decision still
requires written independent review. It is preflight infrastructure only.

The explicit vertex-circle decision-request packet is checked by:

```bash
python scripts/check_n9_vertex_circle_route_decision_request.py --check --summary-json
```

It records the requested gate partition and reviewer workflow for a future
written route decision. It is request infrastructure only: it does not accept
any gate and does not update source-of-truth status files.

Run:

```bash
make verify-n9-candidate
```

Use `PYTHON=.venv/bin/python` if working in the local virtual environment:

```bash
make verify-n9-candidate PYTHON=.venv/bin/python
```

## What It Checks

The target first runs the review-infrastructure checks and Lean pilot
guardrails:

```bash
python scripts/check_n9_candidate_review_manifest.py --check --summary-json
python scripts/check_n9_review_gate_ledger.py --check --summary-json
python scripts/check_n9_review_evidence_matrix.py --check --summary-json
python scripts/check_n9_review_dossier.py --check --summary-json
python scripts/check_n9_review_run_bundle.py --check --summary-json
python scripts/check_n9_review_decision_intake.py --check --summary-json
python scripts/check_n9_vertex_circle_route_decision_preflight.py --check --summary-json
python scripts/check_n9_vertex_circle_route_decision_request.py --check --summary-json
python scripts/check_lean_sketch_integrity.py
python scripts/check_lean_files.py
```

The manifest, gate-ledger, evidence-matrix, dossier, run-bundle,
decision-intake, vertex-circle preflight, and decision-request checkers run
before the Lean pilot guardrails. The Lean layer includes
`lean/Erdos97/TurnPacking.lean`, a dependency-free formal contract for the
turn-packing route. It pins the forward/reverse interval support convention
and proves the small arithmetic kernel behind the stored dual certificates: a
lower bound exceeding the total coefficient budget has no realization. It does
not prove the Euclidean exterior-turn lemma.

The target then runs the compact vertex-circle route checks:

```bash
python scripts/check_n9_vertex_circle_exhaustive.py --assert-expected --json
python scripts/check_n9_vertex_circle_input_audit.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_incidence_filters.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_mro_branching_replay.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_frontier_coverage_crosswalk.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_strict_edge_geometry.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_quotient_soundness.py --check --assert-expected --summary-json
python scripts/check_n9_vertex_circle_local_lemma_audit_path.py --check --assert-expected --summary-json
```

These commands cover row-0/input conventions, incidence filters, branch-order
agreement, frontier coverage, strict-edge geometry, quotient replay, and the
local-lemma handoff path. They are review aids, not an independent review by
themselves.

The target then runs the compact turn-packing route checks:

```bash
python scripts/check_turn_inequality_indexing.py --check --assert-expected --summary-json
python scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --summary-json
```

These commands check the machine indexing convention and the stored integer
dual certificates for all `184` regenerated frontier assignments. They still
depend on independent review of the geometric turn lemma in
`docs/turn-inequality-lemma.md`.

Finally, the target runs the stored-input Kalmanson replay:

```bash
python scripts/check_n9_kalmanson_selfedge_independent_replay.py --check --assert-expected --summary-json
```

This is corroborating stored-certificate audit support. It does not replace
the vertex-circle or turn-packing review routes.

## Promotion Boundary

Passing `make verify-n9-candidate` means the compact review harness is
internally consistent at the current repository revision. It does not mean:

- Erdos Problem #97 is solved;
- the official/global status changed;
- the general problem for larger polygons is proved;
- the `n=9` candidate has completed independent review;
- the exterior-turn lemma has been formally proved in Lean.

The intended next promotion step is a written independent review that accepts
or rejects the specific dependencies listed in `docs/n9-reduction-chain.md`
and `docs/n9-review-packet.md`.
