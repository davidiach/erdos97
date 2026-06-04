# GPT-5.5 Pro Zip 4 Triage, 2026-06-04

Status: provenance and task-selection guidance only; not mathematical
evidence.

This note triages the fourth GPT-5.5 Pro zip supplied on 2026-06-04. It does
not promote any finite-case result, alter the source-of-truth status, or
replace the checked repository artifacts. The repository still claims no
general proof and no counterexample for Erdos Problem #97.

## Input

Local archive reviewed:

```text
C:\Users\User\Desktop\code\erd archive\04.06.2026\4.zip
sha256: 54f97577facd40573f18c95186e4bcf13139ae587ebaa7cbbe07df0202d4a465
```

The extracted `MANIFEST.sha256` listed `6` files and verified byte-for-byte
with zero SHA-256 mismatches.

## Contents

The packet contains:

- `scripts/independent_n9_vertex_circle_replay.py`: self-contained Python
  replay of the `n=9` selected-witness vertex-circle finite-case pipeline;
- `data/certificates/independent_n9_vertex_circle_replay.json`: saved replay
  output with the `184` classified frontier assignments;
- `docs/independent-n9-vertex-circle-replay.md`: proof-facing note for the
  replay;
- `PATCH_NOTES.md`, `README.md`, `run.log`, and `MANIFEST.sha256`.

The useful wrinkle is that the replay deliberately does not enforce the
selected-indegree cap while branching. It uses row-pair crossing and
witness-pair capacity filters before replaying the vertex-circle quotient
obstruction.

## Checks Run

The packet's Python file compiles with `py_compile`.

The replay was rerun from scratch with:

```text
python .codex-work\zip4-review\erdos97_progress_2026_06_03\scripts\independent_n9_vertex_circle_replay.py --assert-expected --write .codex-work\zip4-review\rerun_independent_n9_vertex_circle_replay.json
```

The rerun reproduced the expected summary:

```text
row0 choices:                                70
search nodes without vertex-circle pruning: 100,817
frontier assignments before vertex-circle:  184
vertex-circle status split:                 158 self-edge, 26 strict-cycle
selected-indegree cap enforced:             false
all frontier indegrees:                     (4,4,4,4,4,4,4,4,4)
frontier sha256:                            d7807b69b9de27da17fa851b3325b1e26cfa0b6d86277abeda4bc4e3454b8e01
```

The regenerated JSON and the archived JSON differ byte-for-byte because of
line-ending or formatting details, but their parsed JSON objects match.

The summary agrees with the checked-in
`data/certificates/n9_vertex_circle_exhaustive.json` no-vertex-circle
cross-check:

```text
repo no-vertex-circle nodes:          100,817
repo no-vertex-circle full frontier:  184
repo no-vertex-circle status split:   158 self-edge, 26 strict-cycle
```

The frontier digest also matches the digest already recorded by existing
frontier crosswalk artifacts.

## Decision

Do not import the raw packet as a tracked source artifact in this pass.

Reasons:

- The count and digest content corroborates existing review-pending `n=9`
  vertex-circle artifacts rather than changing the source-of-truth status.
- The cap-free brancher is a useful independent audit shape, but it overlaps
  existing frontier coverage, stored-frontier assignment, and mixed-rich
  frontier crosswalk diagnostics.
- The raw proof note contains theorem-facing phrasing that should be rewritten
  into the repository's normal trust-taxonomy language before import.
- A maintained import should use a repo-native `check_...` script name,
  compact summary output by default, generated-artifact provenance metadata,
  and an explicit crosswalk against the stored frontier artifact.
- The zip does not provide exact coordinates, an exact algebraic certificate,
  an interval certificate, an SMT certificate, or a formal proof.

This packet is useful provenance for the fact that the selected-indegree cap is
not needed to reach the stored `n=9` pre-vertex-circle frontier, but it is not a
source-of-truth status update.

## Follow-Up

The worthwhile follow-up is to turn the cap-free replay into a maintained
artifact-tier checker. The checker should regenerate the `184` frontier without
selected-indegree pruning, compare the ordered rows and status labels to the
stored frontier artifact, and record a compact generated JSON summary.

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this packet.
