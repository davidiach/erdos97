# GPT-5.5 Pro Zip 8 Triage, 2026-06-04

Status: provenance and task-selection guidance only; not mathematical
evidence.

This note triages the eighth GPT-5.5 Pro zip supplied on 2026-06-04. It does
not promote any finite-case result, alter the source-of-truth status, or
replace the checked repository artifacts. The repository still claims no
general proof and no counterexample for Erdos Problem #97.

## Input

Local archive reviewed:

```text
C:\Users\User\Desktop\code\erd archive\04.06.2026\8.zip
sha256: e8f2e4a16391f9687718d45f982248298ef3abc8362eb9b227e9bcf67090e1b2
```

The extracted `manifest.json` describes the packet as a standalone finite-case
audit replay for the `n=10` selected-witness exclusion. It records the trust
label `INDEPENDENT_AUDIT_REPLAY_OF_REPO_DRAFT_N10_SINGLETON_SLICES`, but it
does not include per-file SHA-256 payload hashes.

## Contents

The packet contains:

- `src/fast_generic_vertex_search.cpp`: standalone C++17 selected-witness
  search;
- `scripts/run_replays.sh`: compile-and-rerun shell script;
- `scripts/verify_results.py`: aggregate-and-assert validator;
- `results/n9_fast_vertex_pruned_replay.json`: saved `n=9`
  vertex-circle-pruned replay output;
- `results/chunks/n10_rows_*.json`: thirteen saved `n=10` row0 chunk outputs;
- `results/n10_fast_chunked_replay_summary.json`: saved aggregate `n=10`
  summary;
- `notes/geometric_filters.md`, `notes/n10_audit_note.md`, `README.md`, and
  `manifest.json`.

## Checks Run

The packet's Python verifier compiles with `py_compile`.

The verifier passed when run against the extracted packet:

```text
ok: true
n=9 nodes:                  16,752
n=9 full assignments:       0
n=9 split:                  11,271 self-edge, 11,011 strict-cycle
n=10 row0 choices covered:  126
n=10 chunks covered:        13
n=10 total nodes:           4,142,738
n=10 full assignments:      0
n=10 split:                 4,467,592 self-edge, 5,318,250 strict-cycle
n=10 aborted_any:           false
```

Static comparison against checked-in repo artifacts found that the saved
results duplicate existing review-pending vertex-circle replay data:

```text
n=9 compared artifact:       data/certificates/n9_vertex_circle_exhaustive.json
n=9 matching scope:          main_search
n=10 compared artifact:      data/certificates/n10_vertex_circle_singleton_slices.json
n=10 chunk mismatches:       0 across 13 packet chunks
n=10 chunk coverage:         [0,126)
```

For `n=10`, the packet groups the repo's 126 singleton row0 slices into
thirteen larger row ranges. Aggregating the repo rows over those same ranges
matches every packet chunk for visited nodes, full assignments, abort status,
partial self-edge prunes, and partial strict-cycle prunes.

The C++ verifier was not locally rebuilt or rerun in this pass: no `g++`,
`clang++`, or `cl` compiler was available on the Windows path.

## Decision

Do not import the raw packet as a tracked source artifact in this pass.

Reasons:

- The `n=9` and `n=10` numeric content duplicates checked-in review-pending
  artifacts and previous June 4 GPT-5.5 Pro replay packets.
- The packet is useful as an independent audit/replay shape, but its C++ source
  has not been locally rebuilt in this environment.
- The manifest records provenance metadata but no per-file hashes.
- The zip does not provide exact coordinates, an exact algebraic certificate,
  an interval certificate, an SMT certificate, or a formal proof.

This packet is useful corroborating provenance for the existing review-pending
`n=9` and draft `n=10` audit trails, but it is not a source-of-truth status
update.

## Follow-Up

If a maintained C++ replay is added later, this implementation is another
reasonable compact baseline to compare against the prior June 4 replay packets.
The maintained version should compile in CI or a documented local toolchain,
emit generated JSON, and compare generated `n=9`/`n=10` summaries against the
checked-in artifacts.

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this packet.
