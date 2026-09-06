# Contributing

Contributions should be reproducible, clearly labelled, and modest in claims.
No general proof and no counterexample are currently claimed. Read [STATE.md](STATE.md),
[claims](docs/claims.md), and [review priorities](docs/review-priorities.md) first.
Agent-specific instructions are in [AGENTS.md](AGENTS.md).

## Setup

Use Python 3.10 or newer and an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

The optional Flint backend requires Python 3.11 or newer and is skipped on 3.10
through its package environment marker. For the declared CPython 3.12 snapshot,
install `requirements-lock.txt` before `pip install --no-deps -e .`.
The lock file records direct dependencies, not a fully locked operating system.

## Required verification

After code or documentation changes:

```bash
make verify-fast
```

Without Make, the same tier is:

```bash
python scripts/check_text_clean.py
python scripts/check_status_consistency.py
python scripts/check_artifact_provenance.py
python scripts/generate_navigation.py --check
python scripts/check_docs_index_coverage.py
python scripts/generate_makefile_verify_targets.py --check
git diff --check
python -m ruff check .
python -m pytest -q
```

For finite-case, certificate, or public theorem-style artifact changes, also run:

```bash
make verify-artifacts
```

This runs all commands registered in `scripts/audit_commands.json`.
`make audit-artifacts` runs that registry with per-command evidence capture.
Use `python scripts/run_artifact_audit.py --verify-only` without Make.
If a required command cannot run, report its exact command and reason;
do not describe a partial run as a full pass.

After changing Lean sources or root Lean build files, also run:

```bash
make verify-lean
```

Local Lean compilation is skipped if the toolchain is absent; report that skip.
The hosted Lean workflow requires the pinned toolchain. See [formalization](docs/formalization.md).

## Focused checks and CI

`make verify-lint` runs the non-pytest fast checks. Topic maps link to focused
review targets. `make verify-pytest-artifacts` selects artifact-marked tests;
`make verify-pytest-all` includes all markers. Focused checks aid iteration and
do not replace the required tiers above.

Every PR reports fast, artifact, and compatibility-collection gate results.
Artifact pytest runs for artifact-sensitive changes, including incoming packets;
dependency/workflow changes also collect tests on Python 3.10 and 3.11.
Documentation-only changes can skip expensive lanes while still reporting
successful gate results. Scope-detection errors fail closed.
Full compatibility tests and the broader artifact audit remain scheduled/manual
or post-merge checks as defined in `.github/workflows/`.

## Changing or adding research material

- State hypotheses, claim scope, review status, and what remains open.
- Record generation commands, seeds, inputs, and exact evidence.
- Edit generators, not generated certificates, manifests, or release archives.
- Use [shared maintenance conventions](docs/repository-maintenance.md).
- Regenerate navigation with `python scripts/generate_navigation.py --write`.
- Change the audit registry before regenerating its Make targets with
  `python scripts/generate_makefile_verify_targets.py --write`.
- Use the [incoming lifecycle](incoming/README.md) for imported research packets.
- Keep failed approaches and independently implemented verifiers available.

When changing an input included in the n=8 release bundle, commit the source
changes first, then run `python scripts/build_n8_release_packet.py --source-ref HEAD`
from that clean commit and commit the generated outputs separately. Preserve
that source commit in merge history. `--check` verifies reproducibility.

## Before merging

Review the final diff and exact head; resolve review findings and pass the
applicable checks. Preserve the source-of-truth scope across README, STATE,
RESULTS, claims, and metadata. A stronger mathematical result requires the
[reviewed status-transition contract](docs/status-transitions.md); CI success
alone is not independent mathematical review. Do not prepare OEIS submissions
from AI-generated output.
