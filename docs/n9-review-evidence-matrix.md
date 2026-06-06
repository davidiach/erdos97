# n=9 Review Evidence Matrix

Status: `REVIEW_EVIDENCE_MATRIX_ONLY`.

This note explains `metadata/n9_review_evidence_matrix.yaml`, a
machine-readable output contract for the compact `n=9` review harness. The
matrix is review infrastructure only. It does not prove Erdos Problem #97, does
not prove `n=9`, does not claim a counterexample, does not complete independent
review, and does not update the official/global status.

## Purpose

The compact harness now has three checked metadata layers:

```bash
python scripts/check_n9_candidate_review_manifest.py --check --summary-json
python scripts/check_n9_review_gate_ledger.py --check --summary-json
python scripts/check_n9_review_evidence_matrix.py --check --summary-json
```

The route manifest records the command sequence. The gate ledger records which
independent-review gates those commands support. The evidence matrix records
the expected compact output invariants for every command in the harness.
The reviewer dossier in `metadata/n9_review_dossier.yaml` then assembles these
contracts into an on-demand Markdown worksheet.

This makes two kinds of drift visible:

- command drift, when the Makefile, route manifest, and matrix disagree;
- evidence drift, when a command still runs but no longer reports the expected
  reviewer-facing counts or status fields.

## Live Replay

The checker can run in contract-only mode or live replay mode.

Contract-only mode:

```bash
python scripts/check_n9_review_evidence_matrix.py --check --summary-json
```

Live replay mode:

```bash
python scripts/check_n9_review_evidence_matrix.py --check --run --summary-json
```

Live replay mode executes the compact harness commands in manifest order,
using the current Python interpreter for `python ...` commands. It checks JSON
commands against matrix paths such as `validation_status`,
`source_frontier.assignment_count`, and
`frontier_full_assignments_summary.status_counts.self_edge`. It checks text
commands with substring expectations, including the current Lake-missing Lean
compilation skip message.

## Matrix Coverage

The matrix covers all commands in `make verify-n9-candidate`:

- the route manifest checker;
- the review-gate ledger checker;
- the evidence matrix checker itself in contract-only mode;
- the reviewer dossier checker;
- Lean sketch and optional Lean compilation guardrails;
- the compact vertex-circle route commands;
- the compact turn-packing route commands;
- the stored-input Kalmanson corroboration command.

The matrix also checks that every evidence command named by
`metadata/n9_review_gate_ledger.yaml` has a linked matrix record. Metadata-only
commands intentionally have an empty ledger-gate list because they guard the
harness rather than a mathematical review step.

## Boundary

Passing the matrix in live replay mode means the current compact harness
outputs match the expected reviewer-facing invariants. It does not mean:

- the source-frontier enumeration has completed independent review;
- the vertex-circle strict-edge geometry has been accepted;
- the quotient replay has been accepted as theorem-grade;
- the exterior-turn lemma has been proved;
- the Lean pilot has been compile-checked on this machine when Lake is absent;
- any source-of-truth claim or official/global status should change.
