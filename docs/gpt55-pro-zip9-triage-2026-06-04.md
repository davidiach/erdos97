# GPT-5.5 Pro Zip 9 Triage, 2026-06-04

Status: provenance and task-selection guidance only; not mathematical
evidence.

This note triages the ninth GPT-5.5 Pro zip supplied on 2026-06-04. It does
not promote any finite-case result, alter the source-of-truth status, or
replace the checked repository artifacts. The repository still claims no
general proof and no counterexample for Erdos Problem #97.

## Input

Local archive reviewed:

```text
C:\Users\User\Desktop\code\erd archive\04.06.2026\9.zip
sha256: 393c38d6132c428957af9e924297d895095e17af9f6c3a3f02a7ba5be02644c2
```

The extracted `MANIFEST.json` lists `19` files. The accompanying
`checksums.txt` verified byte-for-byte with zero SHA-256 mismatches, including
the manifest itself.

## Contents

The packet contains:

- `scripts/independent_n9_turn_replay.py`: self-contained fixed-order `n=9`
  selected-witness incidence enumerator plus turn-capacity certificate finder;
- `scripts/independent_vertex_circle_replay.py`: self-contained exact
  selected-witness / vertex-circle replay;
- `data/n9_turn_independent_replay.json`: saved turn-capacity certificate
  artifact for the `184` `n=9` incidence-frontier assignments;
- `data/n9_exact4_independent_replay.json`: saved `n=9` vertex-circle replay;
- `data/n10_exact4_*.json`: sampled `n=10` row0 spot/chunk replays;
- rebuilt JSON outputs, two small pytest files, `run_all.sh`, and proof-facing
  notes under `docs/`.

## Checks Run

The packet's Python scripts compile with `py_compile`.

The packet's tests passed:

```text
3 passed
```

Rerunning the main turn replay into scratch passed the packet's expected-count
assertions:

```text
frontier assignments:             184
enumerator nodes:                 104,399
turn inequalities per assignment: 108
missing certificates:             0
lambda histogram:                 {"1": 180, "2": 4}
term-count histogram:             {"5": 180, "9": 4}
frontier sha256:                  dc28b32d93e721838a592d1f010f92720869191594dbcc40df2a00f96f213d55
```

Rerunning the packet's `n=9` vertex-circle replay also closed its selected
scope:

```text
row0 slices checked:       70
full assignments:          0
nodes:                     11,066
dead ends:                 15,663
vertex-circle prunes:      12,305
partial self-edge prunes:  5,371
partial strict-cycle prunes: 6,934
maximum depth reached:     6
```

The repo-native turn-inequality artifact check also passed:

```text
python scripts/check_n9_turn_inequality_frontier.py --check --assert-expected --summary-json
```

## Repo Comparison

The packet substantially overlaps the already tracked review-pending artifact:

```text
data/certificates/n9_turn_inequality_frontier.json
scripts/check_n9_turn_inequality_frontier.py
docs/n9-turn-inequality-frontier.md
docs/turn-inequality-lemma.md
```

The headline turn-capacity data match the repo artifact:

```text
frontier assignment count: 184
turn inequalities:         108 per assignment
certificate missing count: 0
lambda histogram:          {"1": 180, "2": 4}
term-count histogram:      {"5": 180, "9": 4}
```

The packet's frontier SHA-256 differs from the repo artifact's
`d7807b69b9de27da17fa851b3325b1e26cfa0b6d86277abeda4bc4e3454b8e01`, but this
is due to ordering/canonicalization. After normalizing both frontiers to
center-to-witness tuples, the two assignment sets are exactly equal:

```text
repo assignment count: 184
zip assignment count:  184
same order:            false
same set:              true
repo minus zip:        0
zip minus repo:        0
```

The packet's selected turn-capacity certificate rows are not byte-for-byte the
same as the repo's stored `farkas_certificates`; they use different selected
interval indices and coverage vectors while reaching the same certificate
histograms. This makes the packet useful as independent implementation
provenance, but not a replacement for the repo-native registered artifact.

The packet's secondary `n=9` vertex-circle replay closes the same selected
case, but its node and prune counters differ from the repo-native checker. Treat
those counters as implementation-specific audit data, not as replacement
totals.

The packet's `n=10` files cover only row0 indices `[0,10)`, `0`, `63`, and
`125`. They report zero full assignments in those sampled scopes but do not
match the repo singleton-slice counters and do not prove `n=10`.

## Decision

Do not import the raw packet as a tracked source artifact in this pass.

Reasons:

- The main `n=9` turn route is already represented by a repo-native generated
  artifact, checker, tests, and documentation.
- The packet is a useful independent-code replay, but not an independent human
  review of the turn lemma or source frontier.
- The proof-facing notes use stronger language than the repo should promote
  while the turn lemma remains review-pending.
- The `n=10` material is explicitly spot/chunk audit data only.
- The zip does not provide exact coordinates, an exact algebraic certificate,
  an interval certificate, an SMT certificate, or a formal proof.

This packet is useful corroborating provenance for the review-pending `n=9`
turn-inequality frontier route. It is not a source-of-truth status update.

## Follow-Up

The alternate certificate selection may be worth comparing against
`data/certificates/n9_turn_inequality_frontier.json` if reviewers want a second
stored certificate family. That should be done through a repo-native generator
or explicit appendix with generated-artifact provenance, not by importing the
zip payload directly.

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this packet.
