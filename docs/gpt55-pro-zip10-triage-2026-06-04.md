# GPT-5.5 Pro Zip 10 Triage, 2026-06-04

Status: provenance and task-selection guidance only; not mathematical
evidence.

This note triages the tenth GPT-5.5 Pro zip supplied on 2026-06-04. It does
not promote any finite-case result, alter the source-of-truth status, or
replace the checked repository artifacts. The repository still claims no
general proof and no counterexample for Erdos Problem #97.

## Input

Local archive reviewed:

```text
C:\Users\User\Desktop\code\erd archive\04.06.2026\10.zip
sha256: b4082078083befa824a7974764cf607edc9fdaeeb2f691255146399b94c98e48
```

The extracted `manifest.sha256` verified byte-for-byte with zero SHA-256
mismatches.

## Contents

The packet contains:

- `src/localized_vertex_search.cpp`: standalone C++17 selected-witness /
  vertex-circle replay with an optional localized edge-sensitive selected
  indegree cap;
- `src/localized_vertex_search`: compiled executable from the source packet;
- `src/run_slices_range.py` and `src/run_n10_localized_slices.py`: helpers to
  rerun `n=10` row0 slices;
- `src/check_results.py`: expected-count validator for the saved outputs;
- `results/n9_coarse_no_vc.json`: saved `n=9` no-vertex-circle frontier replay;
- `results/n9_coarse_full.json`: saved `n=9` vertex-circle-pruned replay;
- `results/n10_localized_slices.jsonl`: one saved JSON object per `n=10` row0
  slice;
- `results/n10_localized_summary.json`: aggregate `n=10` summary;
- `docs/proof_note.md`, `README.md`, and `manifest.sha256`.

## Checks Run

The packet's Python files compile with `py_compile`.

The packet's own validator passed:

```text
OK: packet outputs match expected n=9/n=10 finite-case counts
```

The saved `n=9` outputs match the known review-pending counts:

```text
n=9 without vertex-circle pruning:
  nodes visited:       100,817
  full assignments:    184
  terminal split:      158 self-edge, 26 strict-cycle

n=9 with vertex-circle pruning:
  nodes visited:       16,752
  full assignments:    0
  partial split:       11,271 self-edge, 11,011 strict-cycle
```

The saved `n=10` output covers all row0 slices with the localized cap
`floor((2n-4)/3)=5`:

```text
row0 slices covered:        126
aborted slices:             0
total nodes visited:        4,142,738
full assignments:           0
partial self-edge prunes:   4,467,592
partial strict-cycle prunes: 5,318,250
rows_sha256:                1e466efafff385d9e83cc111993114d809dc5ea2a8c3adb0d5b3378eb6b4bab1
```

Static comparison against
`data/certificates/n10_vertex_circle_singleton_slices.json` found exact
row-level agreement:

```text
zip rows:        126
repo rows:       126
row mismatches:  0
```

The C++ source was not locally rebuilt or rerun in this pass: no `g++`,
`clang++`, or `cl` compiler was available on the Windows path. The bundled
compiled executable was not imported or treated as a maintained artifact.

## Decision

Do not import the raw packet as a tracked source artifact in this pass.

Reasons:

- The `n=9` and `n=10` numeric content duplicates checked-in review-pending
  artifacts and previous June 4 GPT-5.5 Pro replay packets.
- The localized edge-sensitive cap is useful audit context, but the relevant
  counting idea is already represented in repo-native localized-counting
  documentation and checks.
- The packet includes a compiled binary, which should not be committed as a
  research source-of-truth artifact.
- The C++ source has not been locally rebuilt in this environment.
- The zip does not provide exact coordinates, an exact algebraic certificate,
  an interval certificate, an SMT certificate, or a formal proof.

This packet is useful corroborating provenance for the review-pending `n=9`
and draft `n=10` vertex-circle audit trails. It is not a source-of-truth status
update.

## Follow-Up

If a maintained C++ replay is added later, this localized-cap implementation is
a reasonable comparison target against the prior June 4 C++ replay packets. A
repo-native version should be source-only, compile in CI or a documented local
toolchain, emit generated JSON, and compare generated `n=9`/`n=10` summaries
against the checked-in artifacts.

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this packet.
