# Affine-Circuit Rank-Rigidity Loop

Status: `EXACT_CHECKER_DIAGNOSTIC` / bounded research-loop note.

No general proof of Erdos Problem #97 is claimed. No counterexample is
claimed. The checks below are exact diagnostics for fixed coordinates and fixed
selected four-cohorts only. They do not prove rank rigidity, do not rule out
all exotic syzygies, and do not alter the repo source-of-truth status.

## Scope

Task bridge: continue the affine-circuit/rank-rigidity program by turning
possible quotient-kernel defects into small checker experiments for exotic
syzygies and cofactor certificates.

Exact object studied:

- points `p_j = (x_j,y_j)` with lifted rows
  `(1, x_j, y_j, x_j^2 + y_j^2)`;
- signed affine-circuit matrix `L` from fixed selected four-cohorts;
- quotient matrix `L_N` after choosing a nonsingular lifted base `B`;
- singleton-peeled weighted two-core;
- minimal-support cofactor certificates and pure pair-gain components.

Inputs read first:

- `AGENTS.md`
- `README.md`, `STATE.md`, `RESULTS.md`, `metadata/erdos97.yaml`
- `docs/claims.md`, `docs/review-priorities.md`, `docs/codex-backlog.md`
- `docs/codex-strategy-instructions.md`
- `docs/exactification-plan.md`
- `docs/prompt-roadmap.md`
- `docs/failed-ideas.md`
- `incoming/prompt2-runs/audit.md`
- `incoming/prompt2-runs/run-02.md`
- `src/erdos97/affine_circuit_certificates.py`
- `scripts/check_affine_circuit_certificates.py`
- `tests/test_affine_circuit_certificates.py`

Verifier commands run during this loop:

```bash
python scripts/check_affine_circuit_certificates.py --example single-circle-row --assert-expected --json
python scripts/check_affine_circuit_certificates.py --example golden-decagon --assert-expected --json
python -m pytest tests/test_affine_circuit_certificates.py -q
```

Focused results:

- `single-circle-row`: `rank_z = 4`, `LZ = 0`, `kernel_dim_l = 5`,
  `kernel_dim_quotient = 1`, singleton peeling removes quotient column `3`,
  and the remaining isolated quotient column `5` yields the cofactor
  certificate `support = [5]`, `cofactors = [1]`.
- `golden-decagon`: `rank_z = 4`, `LZ = 0`, `kernel_dim_l = 6`,
  `kernel_dim_quotient = 2`, no singleton peeling for the default base
  `[0,1,2,3]`, three reported cofactor certificates, and one balanced
  pair-gain component. This is a nonconvex negative-control example, not a
  counterexample candidate.
- Focused tests: `5 passed`.

One exploratory base-sweep command was attempted and timed out:

```bash
@' ... golden_decagon valid-base sweep ... '@ | python -
```

It timed out after about 21 minutes. Before timeout it printed a useful
diagnostic summary, but this is not a completed artifact:

```text
valid_bases 180
kernel_dims {2: 180}
core_size_counts {6: 60, 4: 120}
peeled_counts {0: 60, 2: 120}
cert_count_counts {3: 60, 2: 120}
pair_component_counts {1: 60, 2: 120}
```

The working tree already contained unrelated edits before this report was
written. They were not reverted or modified.

## Cycle 1 - Existing Checker Baseline

Propose:

Use the existing fixed-coordinate checker as the first bounded continuation.
The goal is not to prove rank rigidity, but to confirm that the implemented
Prompt 2 reductions expose the three expected quotient-defect mechanisms:
isolated quotient columns, pair-gain components, and cofactor circuits.

Audit:

The baseline examples do expose those mechanisms. The single-circle example is
the clean isolated-column case. The golden-decagon negative control has an
exotic quotient kernel of dimension `2` and reports nontrivial cofactor and
pair-gain data. The checker also records `status:
exact_checker_not_a_proof`, which is the right scope.

The baseline is still too narrow for any proof-facing claim. Both examples are
fixed coordinate systems, and the golden-decagon example is explicitly
nonconvex. The output says that defects can be represented exactly in this
framework; it does not say such defects exist or fail for strictly convex
counterexample candidates.

Refine:

Treat the golden-decagon example as a regression benchmark for exotic syzygy
classification, not as evidence about Erdos #97. The next useful checker
experiment should focus on base dependence: quotient columns and individual
minimal supports can vary with the lifted base even though
`dim ker L_N = dim ker L - 4` is base-independent.

## Cycle 2 - Base-Dependence Probe

Propose:

Run a small exact sweep over valid lifted bases for the golden-decagon negative
control, recording only quotient dimension, two-core size, peel count,
certificate count, and pair-component count. This tests whether the defect
mechanism is stable enough to summarize in a future report or checker mode.

Audit:

The attempted sweep timed out, so it should not be cited as a verified
artifact. The partial printed summary is still suggestive:

- all printed valid bases had quotient kernel dimension `2`;
- two-core sizes split between `6` and `4`;
- bases with core size `4` appeared to peel two columns;
- printed certificate counts split between `3` and `2`;
- printed pair-component counts split between `1` and `2`.

This matches the audit warning from `incoming/prompt2-runs/audit.md`: quotient
dimension is base-independent for nonsingular lifted bases, while immediate
certificates and isolated-column visibility can be base-dependent.

Refine:

Do not add a heavy all-base symbolic sweep as a default test. The next
experiment should be bounded, cheap, and explicitly a diagnostic.

## Cycle 3 - Concrete Next Experiment

Recommended next checker experiment:

Add a bounded "base-certificate profile" diagnostic for the existing
`golden-decagon` negative control. The checker should enumerate valid lifted
bases only under an explicit cap, for example `--max-bases`, and for each base
record:

- `base`;
- `kernel_dim_quotient`;
- `core_columns`;
- `peeled_columns`;
- number of minimal cofactor certificates found with
  `max_support_size <= 2` or another documented small bound;
- pure pair-gain component summaries.

Acceptance standard for that experiment:

- it verifies `kernel_dim_quotient = 2` for every visited valid base;
- it records, but does not overinterpret, which bases expose pair-support
  cofactor certificates or balanced pair-gain components;
- it exits quickly under the cap and reports if the cap prevents full coverage;
- it labels the result as a negative-control exact checker diagnostic.

Why this is the right next experiment:

The existing code already verifies the quotient reduction and minimal
cofactor machinery on hand examples. The unresolved risk is explanatory:
certificate visibility depends on base choice, and a future rank-rigidity
workflow needs to distinguish invariant data from base-local witnesses. A
bounded base-certificate profile directly tests that interface without
claiming a general obstruction and without touching finite-case source-of-truth
artifacts.

What it would not prove:

- It would not prove `ker L = U` for any general family.
- It would not rule out exotic syzygies in strictly convex polygons.
- It would not promote `n = 9`, `n = 10`, or any fixed sparse pattern.
- It would not produce a counterexample.

Trust label for this loop: `EXACT_CHECKER_DIAGNOSTIC`.

## Commands Not Run

The full fast tier was not run after writing this report because the checkpoint
request asked to stop heavy/full-test work and finalize with the bounded-loop
report. In particular, these were not run in this loop:

```bash
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
python scripts/check_artifact_provenance.py
git diff --check
python -m ruff check .
python -m pytest -q
make verify-fast
make verify-artifacts
```

No code change or finite-case/certificate artifact change was made.
