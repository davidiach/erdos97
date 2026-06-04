# GPT-5.5 Pro Zip 1 Triage, 2026-06-04

Status: provenance and task-selection guidance only; not mathematical
evidence.

This note triages the first GPT-5.5 Pro zip supplied on 2026-06-04. It does
not promote any finite-case result, alter the source-of-truth status, or
replace the checked repository artifacts. The repository still claims no
general proof and no counterexample for Erdos Problem #97.

## Input

The prompt asked for progress on Erdos #97 and explicitly requested either a
proof or a counterexample. The returned packet did neither. Instead, it
packaged a compact selected-witness vertex-circle replay for the existing
review-pending `n=9` and draft `n=10` finite-case artifacts.

Local archive reviewed:

```text
C:\Users\User\Desktop\code\erd archive\04.06.2026\1.zip
sha256: 692054c2d7e8a35d12ba284b121c176c720733715ad88976915ef746eafc4515
```

The extracted packet manifest verified byte-for-byte.

## Contents

The zip contains:

- `src/fast_vertex_circle_search.cpp`: standalone C++ selected-witness search;
- `src/generic_vertex_circle_search.py`: compact Python reference search;
- `data/n9_replay_fast_cpp.json` and
  `data/n9_replay_fast_cpp_unpruned.json`: `n=9` count replays;
- `data/n10_chunks/*.json`: 26 chunks covering row0 choices `[0,126)`;
- `data/n10_aggregate_replay.json`: aggregate `n=10` replay summary;
- short README/provenance notes.

## Checks Run

The packet's static aggregate checker passed:

```text
row0 coverage: [0,126), exact
chunk count: 26
nodes visited: 4,142,738
full assignments: 0
partial self-edge prunes: 4,467,592
partial strict-cycle prunes: 5,318,250
```

Those chunk totals exactly match the checked-in
`data/certificates/n10_vertex_circle_singleton_slices.json` artifact when its
126 singleton rows are regrouped into the packet's five-row chunks. The
comparison found zero chunk mismatches.

The Python files compile with `py_compile`. This triage did not rerun the C++
verifier: no `g++`, `clang++`, or `cl` compiler was available on the Windows
path, and WSL access was denied in the current sandbox. The full C++ rerun is
therefore not locally reproduced here.

## Decision

Do not import the raw packet as a tracked source artifact.

Reasons:

- The numeric content is already present in the repository as the draft
  `n=10` singleton-slice artifact.
- The Python reference is a compact duplicate of the repo-native generic
  vertex search rather than a new certificate format.
- The C++ verifier is useful provenance, but it is not yet a maintained
  repo-native checker and was not locally rerun during this triage.
- The packet does not provide exact coordinates, an exact algebraic
  certificate, an interval certificate, an SMT certificate, or a formal proof.

This zip is useful as corroborating provenance for the existing draft `n=10`
audit trail, not as a source-of-truth update.

## Follow-Up

If this line of work is continued, the useful next artifact is a maintained
repo-native all-slice replay or a compact terminal-conflict certificate for
the `n=10` singleton slices. That should remain scoped as
`MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING` unless independent review
promotes it.

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this packet.
