# GPT-5.5 Pro Zip 2 Triage, 2026-06-04

Status: provenance and task-selection guidance only; not mathematical
evidence.

This note triages the second GPT-5.5 Pro zip supplied on 2026-06-04. It does
not promote any finite-case result, alter the source-of-truth status, or
replace the checked repository artifacts. The repository still claims no
general proof and no counterexample for Erdos Problem #97.

## Input

Local archive reviewed:

```text
C:\Users\User\Desktop\code\erd archive\04.06.2026\2.zip
sha256: fa5f47466ea8ea6f560d1c9423cee93dd062efaf56d370a2cc001cad6234ae1e
```

The extracted `MANIFEST.json` verified byte-for-byte.

## Contents

The packet contains:

- `src/independent_vertex_search.cpp`: standalone C++17 selected-witness
  searcher for the `n=9` and `n=10` vertex-circle pipeline;
- `scripts/run_n10_full_rerun.py`: C++ compile-and-run wrapper that emits all
  126 row0 singleton slices;
- `scripts/independent_n9_core_certificate.py`: Python support checker that
  regenerates the `n=9` frontier and records minimal obstructed row cores;
- `results/independent_n10_full_rerun_with_slices.json`: per-slice `n=10`
  rerun packet;
- `results/independent_n9_vertex_circle_core_certificate.json`: full `n=9`
  support packet;
- `bin/independent_vertex_search_linux_x86_64`: prebuilt Linux binary, not
  imported or executed during this triage.

## Checks Run

Static `n=10` per-slice comparison against the checked-in
`data/certificates/n10_vertex_circle_singleton_slices.json` artifact found
zero mismatches:

```text
slice count:                 126
matched expected repo counts: true
nodes visited:               4,142,738
full assignments:            0
partial self-edge prunes:    4,467,592
partial strict-cycle prunes: 5,318,250
```

The Python support checker reran successfully with
`--summary-json --assert-expected` and reproduced the expected `n=9` summary:

```text
frontier assignments: 184
frontier status split: 158 self-edge, 26 strict-cycle
minimal core sizes: 182 of size 3, 2 of size 4
minimal core status split: 48 self-edge, 136 strict-cycle
sha256_without_digest: 9145de3c170efab41d8c1ac4d3fc8943f4713872be10bf05405332e733b0ef8b
```

The packet's Python files compile with `py_compile`.

The C++ verifier was not locally rerun in this pass: no `g++`, `clang++`, or
`cl` compiler was available on the Windows path, WSL access was denied in the
current sandbox, and the included binary targets Linux rather than the current
Windows shell.

## Decision

Do not import the raw packet as a tracked source artifact.

Reasons:

- The `n=10` numeric content is already present in the repository's draft
  singleton-slice artifact, and the packet's per-slice JSON matches it exactly.
- The `n=9` Python support packet is useful corroboration, but its counts and
  minimal-core direction overlap existing review-pending `n=9` vertex-circle
  audit artifacts.
- The most useful new item is the standalone C++ source, but it still needs a
  maintained repo-native wrapper, local compilation in the review environment,
  and normal generated-artifact provenance before it should enter the checked
  artifact path.
- The zip does not provide exact coordinates, an exact algebraic certificate,
  an interval certificate, an SMT certificate, or a formal proof.

This packet is stronger corroborating provenance for the existing draft
`n=10` audit trail than the first zip, but it is still not a source-of-truth
status update.

## Follow-Up

The worthwhile follow-up is to convert the C++ searcher into a maintained
artifact-tier verifier, then add a checker that compiles it where available and
compares all 126 generated row0 slices to the checked-in singleton artifact.
That should remain scoped as review-pending finite-case audit support unless
independent review promotes the `n=10` package.

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this packet.
