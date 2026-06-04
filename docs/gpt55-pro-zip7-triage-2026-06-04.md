# GPT-5.5 Pro Zip 7 Triage, 2026-06-04

Status: provenance and task-selection guidance only; not mathematical
evidence.

This note triages the seventh GPT-5.5 Pro zip supplied on 2026-06-04. It does
not promote any finite-case result, alter the source-of-truth status, or
replace the checked repository artifacts. The repository still claims no
general proof and no counterexample for Erdos Problem #97.

## Input

Local archive reviewed:

```text
C:\Users\User\Desktop\code\erd archive\04.06.2026\7.zip
sha256: 5adb4402cc858ac85f4b8ff18a484d775a612c826e27153336d5ceb2a04f78b6
```

The extracted `MANIFEST.json` listed `12` files and verified byte-for-byte
with zero SHA-256 mismatches.

## Contents

The packet contains:

- `src/compact_vertex_circle_replay.cpp`: standalone C++17 selected-witness
  replay checker;
- `scripts/run_replays.sh`: compile-and-rerun script;
- `scripts/check_results.py`: expected-count validator for saved outputs;
- `scripts/aggregate_n10_slices.py`: row0-slice aggregator and stable digest
  calculator;
- `results/n8_exact_four_compact.json`: compact `n=8` replay output;
- `results/n9_exact_four_vertex_circle.json`: vertex-circle-pruned `n=9`
  replay output;
- `results/n9_pre_vertex_frontier.json`: `n=9` no-vertex-circle frontier
  output plus terminal classification counts;
- `results/n10_exact_four_row0_slices.jsonl`: one JSON object per `n=10`
  row0 slice;
- `results/n10_exact_four_row0_slices_summary.json`: aggregate `n=10`
  summary and stable slice digest;
- `docs/proof_note.md`, `docs/transcript.md`, `README.md`, and
  `MANIFEST.json`.

## Checks Run

The packet's Python files compile with `py_compile`.

The packet's expected-count validator passed:

```text
OK: compact replay result files match expected counts
```

Rerunning the `n=10` aggregator over the saved JSONL produced a passed
summary:

```text
row0 slices:                 126
row0 coverage:               [0,126)
aborted slices:              0
total nodes:                 4,142,738
full assignments:            0
partial self-edge prunes:    4,467,592
partial strict-cycle prunes: 5,318,250
slice digest sha256:         27116780a8808b5bf565a116b6f61439b4e5f9a6364bef18270e74a8279b41e8
```

Static comparison against checked-in repo artifacts found zero mismatches for
the matching `n=9` and `n=10` scopes:

```text
n=9 vertex-circle nodes:       16,752
n=9 vertex-circle full:        0
n=9 vertex-circle split:       11,271 self-edge, 11,011 strict-cycle
n=9 pre-vertex nodes:          100,817
n=9 pre-vertex full frontier:  184
n=9 pre-vertex status split:   158 self-edge, 26 strict-cycle
n=10 row-level mismatches:     0 across 126 slices
```

The bundle's `n=8` compact replay was not treated as a replacement for the
repo's `n <= 8` source-of-truth pipeline, which is the existing incidence and
exact-obstruction artifact chain rather than this compact counter stream.

The C++ verifier was not locally rebuilt or rerun in this pass: no `g++`,
`clang++`, or `cl` compiler was available on the Windows path.

## Decision

Do not import the raw packet as a tracked source artifact in this pass.

Reasons:

- The `n=9` and `n=10` numeric content duplicates checked-in review-pending
  artifacts and previous June 4 GPT-5.5 Pro replay packets.
- The `n=8` compact replay is not the repo's source-of-truth `n <= 8`
  artifact path.
- The C++ source may still be useful as a compact optional verifier, but it
  should enter through a repo-native wrapper, local build verification, and
  generated-artifact provenance metadata.
- The zip does not provide exact coordinates, an exact algebraic certificate,
  an interval certificate, an SMT certificate, or a formal proof.

This packet is useful corroborating provenance for the existing `n=9` and
draft `n=10` audit trails, but it is not a source-of-truth status update.

## Follow-Up

If a maintained C++ replay is added later, this compact implementation is a
reasonable candidate to compare against the other June 4 C++ packets. The
maintained version should compile where available, emit compact generated JSON,
and compare generated `n=9`/`n=10` summaries against the checked-in artifacts.

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this packet.
