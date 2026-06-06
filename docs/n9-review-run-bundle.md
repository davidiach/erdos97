# n=9 Review Run Bundle

Status: `REVIEW_RUN_BUNDLE_ONLY`.

This note explains `metadata/n9_review_run_bundle.yaml` and
`scripts/check_n9_review_run_bundle.py`. The run bundle is a checked execution
provenance layer for the compact `n=9` review harness. It does not prove Erdos
Problem #97, does not prove `n=9`, does not claim a counterexample, does not
complete independent review, and does not update the official/global status.

## Purpose

The reviewer dossier describes what to inspect. The run bundle records what a
specific checkout actually did when the compact manifest command surface was
executed.

In live mode, the checker:

- executes every compact manifest command in order;
- validates each compact output against `metadata/n9_review_evidence_matrix.yaml`;
- records return codes and durations;
- records SHA-256 digests for stdout and stderr;
- records short stdout/stderr previews for triage;
- writes no generated artifact.

The digest capture is useful for comparing review runs without placing large
command outputs in docs or metadata.

## Commands

Validate the static run-bundle contract:

```bash
python scripts/check_n9_review_run_bundle.py --check --summary-json
```

Capture a live reviewer run:

```bash
python scripts/check_n9_review_run_bundle.py --check --run --summary-json
```

Render the Markdown worksheet to stdout:

```bash
python scripts/check_n9_review_run_bundle.py --markdown
```

Use `--json` with `--run` when the per-command digest records are needed.
Those records still contain only hashes and previews, not full command output.

## Boundary

A passed live capture says the compact `n=9` manifest commands completed in
that checkout and matched the output invariants known to the evidence matrix.
It does not accept any review gate. In particular, all of these remain open
until a written independent review accepts or rejects them:

- A6/A7 source-frontier enumeration;
- A8 vertex-circle strict-edge geometry;
- A10 quotient obstruction replay;
- B1/B2 exterior-turn geometry;
- B3/B4 turn-packing arithmetic replay;
- stored-input Kalmanson corroboration;
- Lean compilation on a machine with Lake installed;
- independent review itself.
