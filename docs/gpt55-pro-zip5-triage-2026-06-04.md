# GPT-5.5 Pro Zip 5 Triage, 2026-06-04

Status: provenance and task-selection guidance only; not mathematical
evidence.

This note triages the fifth GPT-5.5 Pro zip supplied on 2026-06-04. It does
not promote any finite-case result, alter the source-of-truth status, or
replace the checked repository artifacts. The repository still claims no
general proof and no counterexample for Erdos Problem #97.

## Input

Local archive reviewed:

```text
C:\Users\User\Desktop\code\erd archive\04.06.2026\5.zip
sha256: f7675de416869b86c3195071334516a62315aab7eb78cc57352ad2f891615c2a
```

The extracted `checksums.sha256` listed `136` paths. The `135` payload-file
checksums matched after clean extraction. The only mismatch was the
`checksums.sha256` self-entry itself:

```text
expected: 954668307daa83186ebf3b1c5206de716705f04eb08ef503b203f15908449e12
actual:   f4797cfdc7639a409e36057827ceeb650a4e099ed05740be678c6ef314e555b9
```

Treat the checksum file as useful for payload integrity, but not as a
self-authenticating artifact.

## Contents

The packet contains:

- `src/generic_vertex_search_cpp.cpp`: standalone C++17 selected-witness
  replay checker;
- `src/generic_vertex_search_standalone.py`: slower standalone Python port;
- `scripts/run_n10_cpp_replay.sh`: compile-and-rerun wrapper for all
  `n=10` row0 singleton slices;
- `scripts/aggregate_n10_cpp.py`: aggregate checker for the saved slices;
- `scripts/verify_expected_n10_cpp.py`: quick expected-count verifier;
- `data/n10_cpp_slices/slice_000.json` through `slice_125.json`: per-slice
  replay records;
- `data/n10_cpp_aggregate.json`: aggregate result and slice hashes;
- `docs/n10_cpp_replay_proof_note.md`, `REPORT.md`, `MANIFEST.json`, and
  `checksums.sha256`.

## Checks Run

The packet's Python files compile with `py_compile`.

The packet's quick aggregate verifier passed:

```text
OK: n=10 C++ replay aggregate matches expected repo counts.
```

Rerunning the packet's aggregate script over the saved slices reproduced the
expected summary:

```text
completed slices:            126
nodes visited:               4,142,738
full assignments:            0
partial self-edge prunes:    4,467,592
partial strict-cycle prunes: 5,318,250
matches expected counts:     true
```

The static aggregate and row-level comparison against the checked-in
`data/certificates/n10_vertex_circle_singleton_slices.json` artifact found
zero mismatches:

```text
aggregate mismatches: 0
row mismatches:       0
slice count:          126
```

The standalone Python port was run for slice `[0, 1)` and matched the archived
slice and repo artifact:

```text
nodes visited:               9,759
full assignments:            0
partial self-edge prunes:    5,256
partial strict-cycle prunes: 6,031
```

The C++ verifier was not locally rebuilt or rerun in this pass: no `g++`,
`clang++`, or `cl` compiler was available on the Windows path.

## Decision

Do not import the raw packet as a tracked source artifact in this pass.

Reasons:

- The checkable `n=10` row packet exactly duplicates the repository's existing
  review-pending singleton-slice artifact.
- The packet overlaps the earlier June 4 GPT-5.5 Pro C++ replay zips, which
  already recorded the same `n=10` aggregate as corroborating provenance.
- The C++ source may be useful as a future maintained optional verifier, but
  it should enter through a repo-native wrapper, local build verification, and
  generated-artifact provenance metadata.
- The checksum file has a self-hash mismatch, even though the payload hashes
  verified.
- The zip does not provide exact coordinates, an exact algebraic certificate,
  an interval certificate, an SMT certificate, or a formal proof.

This packet is useful corroborating provenance for the existing draft `n=10`
audit trail, but it is not a source-of-truth status update.

## Follow-Up

The worthwhile follow-up is still to convert one of the independent C++ replay
implementations into a maintained artifact-tier verifier that compiles where a
C++17 compiler is available and compares generated `n=10` slices to the
checked-in singleton artifact.

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this packet.
