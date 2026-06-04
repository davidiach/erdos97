# GPT-5.5 Pro Zip 6 Triage, 2026-06-04

Status: provenance and follow-up candidate only; not mathematical evidence.

This note triages the sixth GPT-5.5 Pro zip supplied on 2026-06-04. It does
not promote any finite-case result, alter the source-of-truth status, or
replace the checked repository artifacts. The repository still claims no
general proof and no counterexample for Erdos Problem #97.

## Input

Local archive reviewed:

```text
C:\Users\User\Desktop\code\erd archive\04.06.2026\6.zip
sha256: 63872100c8adb8e2ed4ca8402dc6eba0a8e2c0613c4cfc1a6dab79b7a4799209
```

The packet does not include a payload checksum manifest, so this note records
only the archive-level SHA-256 plus local consistency checks.

## Contents

The packet contains:

- `src/enhanced_search.cpp`: standalone C++17 selected-witness brancher;
- `scripts/run_enhanced_checks.sh`: compile-and-run script for the enhanced
  checks;
- `scripts/summarize_json_objects.py`: JSON-object stream aggregator;
- `results/n5_n9_enhanced_summary.json`: saved enhanced runs for `n=5..9`;
- `results/n10_enhanced_chunks.jsonl`: raw chunk outputs for the `n=10` run;
- `results/n10_enhanced_summary.json`: aggregate enhanced `n=10` run;
- `results/n11_probe_summary.json`: diagnostic `n=11` probe;
- `CLAIM.json`, `README.md`, `docs/proof_note.md`, and
  `docs/limitations.md`.

The reported new ingredient is a Kalmanson one-cancellation strict-edge filter:
after quotienting selected-distance equalities, strict Kalmanson quadrilateral
inequalities that share one quotient class on both sides are converted into a
single strict directed edge between the remaining distance classes. The branch
is pruned on strict self-edges or directed strict cycles, together with the
existing vertex-circle quotient pruning.

## Checks Run

The packet's Python summarizer compiles with `py_compile`.

Rerunning the summarizer over `results/n10_enhanced_chunks.jsonl` reproduced
the saved aggregate fields exactly:

```text
chunk count:                  10
row0 coverage:                [0,126), no gaps
nodes visited:                250,568
full assignments:             0
aborted any:                  false
partial self-edge prunes:     599,372
partial strict-cycle prunes:  939,395
```

The saved `n=5..9` summary is internally consistent as a completed enhanced
run for each listed `n`:

```text
n=5 nodes: 1, full: 0
n=6 nodes: 5, full: 0
n=7 nodes: 33, full: 0
n=8 nodes: 291, full: 0
n=9 nodes: 6,213, full: 0
```

The saved `n=11` probe is explicitly incomplete: row0 slice `[0,1)` closed,
while slice `[5,6)` aborted at `10,000` nodes. It is diagnostic only.

The C++ verifier was not locally rebuilt or rerun in this pass: no `g++`,
`clang++`, or `cl` compiler was available on the Windows path.

## Decision

Do not import the raw packet as a tracked source artifact in this pass.

Reasons:

- Importing the reported `n <= 10` closure directly would promote a
  review-pending finite claim beyond the repository's current source-of-truth
  status.
- The main result depends on a new pruning layer whose geometric inequality
  direction, quotient cancellation logic, monotonicity under partial
  assignments, and C++ implementation still need repo-native review.
- The C++ checker could not be locally rebuilt in this environment.
- The packet provides summary JSON, but not compact independent certificates
  for the pruned branches.
- The `n=11` probe is intentionally incomplete.
- The zip does not provide exact coordinates, an exact algebraic certificate,
  an interval certificate, an SMT certificate, or a formal proof.

This packet is more interesting than the duplicate `n=10` replay packets: the
Kalmanson one-cancellation strict-edge filter is a plausible reviewer-facing
follow-up. It is still not a source-of-truth status update.

## Follow-Up

The worthwhile follow-up is to implement the Kalmanson one-cancellation
strict-edge filter as an optional repo-native checker, preferably first in
Python for auditability. A maintained version should:

- state the strict Kalmanson inequalities and cancellation rule in the repo
  trust taxonomy;
- cross-check the new strict edges against existing Kalmanson/Farkas tooling;
- compare enhanced `n=9` and `n=10` runs against existing vertex-circle
  artifacts;
- emit compact generated JSON with provenance metadata; and
- keep `n=10` review-pending unless independent review promotes the full
  finite-case package.

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this packet.
