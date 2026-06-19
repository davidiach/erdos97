# n=10 Vertex-circle Singleton-slice Reviewer Packet

Status: `REVIEW_PACKET_ONLY`.

Claim scope: repo-local `n=10` selected-witness finite-case draft candidate.

Source of truth: `README.md`, `STATE.md`, `RESULTS.md`, `docs/claims.md`,
`docs/n10-vertex-circle-singleton-slices.md`, and
`metadata/erdos97.yaml`.

Last assembled: 2026-06-19.

## Non-claims

- This packet does not prove Erdos Problem #97.
- This packet does not claim a counterexample.
- This packet does not update the official/global status.
- This packet does not promote the n=10 singleton artifact beyond draft.
- Passing every command below is not a substitute for independent mathematical
  review of the pruning lemmas, brancher implementation, and certificate path.

## Candidate being reviewed

The scoped draft candidate is:

```text
No strictly convex 10-gon has a selected 4-witness row at every vertex,
provided the checked pair/crossing/count and vertex-circle filters are sound.
```

The checked-in primary artifact reports that all `126` singleton choices for
row `0` close under the current vertex-circle selected-row search and that no
full selected-witness assignment survives. This is evidence for a finite-case
draft only. The current review packet is mainly a map of what has been
checked, what has been cross-checked, and what is still missing.

## Main files to inspect

- `docs/n10-vertex-circle-singleton-slices.md`
- `data/certificates/n10_vertex_circle_singleton_slices.json`
- `data/certificates/n10_fast_cpp_singleton_replay.json`
- `data/certificates/2026-05-05/n10_secondary.json`
- `cpp/n_vertex_search_fast.cpp`
- `src/erdos97/generic_vertex_search.py`
- `src/erdos97/n10_vertex_circle_singletons.py`
- `src/erdos97/n10_secondary_singleton_replay.py`
- `scripts/check_n10_vertex_circle_singletons.py`
- `scripts/check_n10_singleton_input_audit.py`
- `scripts/check_n10_fast_cpp_singleton_replay.py`
- `scripts/check_n10_secondary_singleton_replay.py`
- `tests/test_n10_vertex_circle_singletons.py`

## Evidence layers

### Layer A: primary singleton artifact

Primary artifact:
`data/certificates/n10_vertex_circle_singleton_slices.json`.

The artifact stores one explicit row for each singleton slice of row `0` in
the repo-native row-option order. Expected aggregate invariants:

```text
row0 choices covered:      126 / 126
aborted slices:            0
full assignments:          0
nodes visited:             4,142,738
partial self-edge prunes:  4,467,592
partial strict cycles:     5,318,250
```

Reviewer burden: check that the recorded row0 split is genuinely a singleton
split of all `4`-subsets of labels `1..9`, not a hidden symmetry quotient, and
that aggregating independent singleton runs is equivalent to the unsplit
row-0 search.

### Layer B: input-data audit

The input audit treats the primary JSON as stored data. It recomputes row0
choices directly as lexicographic `4`-subsets of labels `1..9`, then checks
row indices, singleton ranges, witness masks, witness lists, and aggregate
count arithmetic. It deliberately does not rerun the search, import
`GenericVertexSearch`, replay terminal conflicts, or prove the n=10 candidate.

Run:

```bash
python scripts/check_n10_singleton_input_audit.py --check --assert-expected --json
```

Acceptance outcome: this layer can accept row0 coverage and stored arithmetic
only. It cannot accept pruning soundness or terminal closure.

### Layer C: repo-native spot replay

The generic Python checker can rerun selected singleton slices against the
primary artifact. Current reviewer spot checks use the first, middle, and last
row0 slices:

```bash
python scripts/check_n10_vertex_circle_singletons.py \
  --assert-expected \
  --spot-check-row0 0 \
  --spot-check-row0 63 \
  --spot-check-row0 125
```

Acceptance outcome: this layer can detect disagreement between the imported
artifact and the repo-native checker at the sampled rows. It does not replace
the all-slice second-source replay layer below.

### Layer D: portable C++ all-slice replay

Second-source artifact:
`data/certificates/n10_fast_cpp_singleton_replay.json`.

This artifact records a portable C++17 replay from
`cpp/n_vertex_search_fast.cpp`. It replays all 126 row0 singleton slices,
records an n=9 calibration run, and compares every n=10 row summary against
the primary artifact.

Expected aggregate invariants:

```text
row0 choices covered:      126 / 126
full assignments:          0
nodes visited:             4,142,738
partial self-edge prunes:  4,467,592
partial strict cycles:     5,318,250
row digest:                64ebe12406c8777bcc7d7e2c5f1db3adb7703cbdba3898bb069bf964091b2fbb
```

Run the stored-artifact check:

```bash
python scripts/check_n10_fast_cpp_singleton_replay.py --check --json
```

When a C++17 compiler is available, rerun the C++ source:

```bash
python scripts/check_n10_fast_cpp_singleton_replay.py --check --run-cpp --json
```

Acceptance outcome: this layer can accept all-slice second-implementation
agreement with the primary artifact. It is still not an independent written
review of the pruning lemmas or either implementation.

### Layer E: secondary first-five replay

Secondary artifact:
`data/certificates/2026-05-05/n10_secondary.json`.

This archived replay covers row0 singletons `0..4` only. It uses the same
pair/crossing/indegree/vertex-circle filters and an additional
triple-intersection necessary filter. The replay verifies exact agreement with
the primary artifact for witness lists, node counts, full counts, and prune
counts on those first five rows.

Expected aggregate invariants:

```text
row0 choices covered:      5 / 126
full assignments:          0
nodes visited:             114,144
partial self-edge prunes:  106,827
partial strict cycles:     120,823
```

Run:

```bash
python scripts/check_n10_secondary_singleton_replay.py --check --assert-expected --json
```

Acceptance outcome: this layer can accept prefix agreement only. Because it
covers `5 / 126` row0 slices and adds an extra necessary filter, it cannot
promote the primary artifact by itself.

## Missing promotion evidence

The current packet is intentionally incomplete. Before the n=10 candidate can
move beyond draft, it still needs:

- independent review of the primary Python checker, the portable C++ replay,
  and the geometric necessity of the filters;
- a replayable terminal-conflict certificate for every terminal branch, with a
  verifier that does not trust the brancher search history, or a smaller exact
  mathematical lemma that subsumes the singleton search and has independently
  reviewed hypotheses.

Any of those routes would still remain a repo-local finite-case review result,
not a general proof of Erdos Problem #97.

## Review checklist

- Verify the geometric necessity of the pair/crossing, witness-pair capacity,
  selected-indegree, and vertex-circle strict-edge filters.
- Check that minimum-remaining-options branching changes only search order.
- Check that partial vertex-circle pruning uses only already-fixed selected
  rows and selected-distance equalities.
- Confirm that the primary artifact has exact row0 singleton coverage
  `[0,126)` with no symmetry quotient.
- Confirm that the input-data audit, selected spot replay, portable C++ replay,
  and secondary first-five replay are described with their actual scopes.
- Require independent implementation/filter review plus either terminal-conflict
  certificates or an independently reviewed replacement lemma before promoting
  the n=10 package.

## Safe acceptance outcomes

- `accepted_input_coverage`: row0 singleton coverage and stored aggregate
  arithmetic are accepted.
- `accepted_selected_spot_replay`: sampled rows match the repo-native checker.
- `accepted_cpp_all_slice_replay`: all `126` rows match the portable C++
  replay artifact and optional live C++ rerun where available.
- `accepted_secondary_prefix`: rows `0..4` match the archived secondary replay.
- `blocked_on_independent_review`: promotion is blocked until the finite
  encoding, pruning rules, and replay implementations receive independent
  review or are replaced by an independently reviewed certificate/lemma route.
- `gap_found`: any mismatch or unsound pruning rule keeps the artifact as
  diagnostic input only.
