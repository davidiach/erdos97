# GPT-5.5 Pro Zip 3 Triage, 2026-06-04

Status: provenance and task-selection guidance only; not mathematical
evidence.

This note triages the third GPT-5.5 Pro zip supplied on 2026-06-04. It does
not promote any finite-case result, alter the source-of-truth status, or
replace the checked repository artifacts. The repository still claims no
general proof and no counterexample for Erdos Problem #97.

## Input

Local archive reviewed:

```text
C:\Users\User\Desktop\code\erd archive\04.06.2026\3.zip
sha256: 2c23d6801737c1be131e50dde7faa4c455186d66c88e2d4a49c6e22d52a45e99
```

The extracted `MANIFEST.json` listed `138` files and verified byte-for-byte
with zero SHA-256 mismatches.

## Contents

The packet contains:

- `src/independent_vertex_replay.cpp`: standalone C++17 selected-witness
  replay engine for the vertex-circle finite-case pipeline;
- `scripts/run_n10_cpp_singletons.py`: runner that invokes the C++ binary on
  all `126` `n=10` row0 singleton slices and aggregates the results;
- `scripts/validate_reports.py`: report validator for the saved `n=9`,
  `n=10`, and bounded `n=11` outputs;
- `reports/n10_cpp_replay_aggregated.json` plus
  `reports/n10_rows/row_000.json` through `row_125.json`: per-row `n=10`
  audit trail;
- `reports/n9_cpp_replay_summary.json` and
  `reports/n9_cpp_no_vc_crosscheck.json`: independent `n=9` replay summaries;
- `reports/n11_row0_limit1m.json`: node-limited `n=11` row0 scout;
- `reports/proof_note_n10_selected_witness.md`, `reports/REPORT.md`, and
  `reports/verification_transcript.txt`: prose summary and command transcript;
- `bin/independent_vertex_replay_linux_x86_64`: prebuilt Linux binary, not
  imported or executed during this triage.

## Checks Run

The packet's own report validator passed:

```text
validated reports: n9 replay, n9 no-VC cross-check, n10 singleton aggregate, n11 scout
```

The packet's Python files compile with `py_compile`.

The static `n=10` aggregate and row-level comparison against the checked-in
`data/certificates/n10_vertex_circle_singleton_slices.json` artifact found
zero mismatches:

```text
row count:                    126
aggregate mismatches:         0
row mismatches:               0
nodes visited:                4,142,738
full assignments:             0
partial self-edge prunes:     4,467,592
partial strict-cycle prunes:  5,318,250
matches repo expected totals: true
```

The static `n=9` summary comparison against
`data/certificates/n9_vertex_circle_exhaustive.json` also found zero
mismatches:

```text
vertex-circle replay nodes:       16,752
vertex-circle replay full:        0
partial self-edge prunes:         11,271
partial strict-cycle prunes:      11,011
no-vertex-circle replay nodes:    100,817
no-vertex-circle full frontier:   184
no-vertex-circle status split:    158 self-edge, 26 strict-cycle
```

The bounded `n=11` scout is diagnostic only. It covers row0 slice `[0, 1)`,
hits the `1,000,000` node limit, reports `aborted: true`, and proves nothing
about `n=11`.

The C++ verifier was not locally rerun in this pass: no `g++`, `clang++`, or
`cl` compiler was available on the Windows path, and the included binary
targets Linux rather than the current Windows shell.

## Decision

Do not import the raw packet as a tracked source artifact.

Reasons:

- The checkable `n=10` row packet exactly duplicates the repository's existing
  review-pending singleton-slice artifact.
- The `n=9` summaries exactly duplicate the repository's existing
  review-pending exhaustive vertex-circle artifact.
- The `n=11` scout is intentionally incomplete and should not be used as
  evidence.
- The standalone C++ source is the interesting part, but it still needs a
  maintained repo-native wrapper, local compilation in the review environment,
  and generated-artifact provenance before it should enter the checked artifact
  path.
- The zip does not provide exact coordinates, an exact algebraic certificate,
  an interval certificate, an SMT certificate, or a formal proof.

This packet is useful corroborating provenance for the existing review-pending
`n=9` and draft `n=10` audit trails, but it is not a source-of-truth status
update.

## Follow-Up

The worthwhile follow-up is to convert the independent C++ replay engine into
a maintained artifact-tier verifier, then add a checker that compiles it where
available and compares its generated `n=9` and `n=10` summaries to the
checked-in JSON artifacts.

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this packet.
