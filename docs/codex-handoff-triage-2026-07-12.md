# Codex handoff triage (2026-07-12)

Status: provenance and import decision record. No general proof or
counterexample is claimed.

## Source

The reviewed archive was `erdos97_codex_handoff_2026-07-12.zip`, with
SHA-256

```text
284a090a5980f10d0e4826bc3d7d4186985c4d0405f39332f540fd23fd44f20e
```

It recorded repository commit
`929693a5ce4f3d227bc28b35937ff2703f084d05` as its reference state.
The archive itself is not checked in because its useful source material is
small, reviewable, and represented directly by managed repository artifacts.

## Verification performed

- The top-level manifest matched every packaged regular file.
- Both nested upstream packages matched the duplicated source, note, and JSON
  files in the handoff.
- The S12A and `n=9` standard-library checkers ran successfully.
- Regenerated JSON matched the stored JSON after normalizing platform line
  endings.
- The `n=9` checker regenerated the existing `184`-assignment frontier digest
  `d7807b69b9de27da17fa851b3325b1e26cfa0b6d86277abeda4bc4e3454b8e01`.

## Imported result

The S12A equilateral-ear obstruction was imported as
`scripts/check_s12a_equilateral_ears.py` and
`data/certificates/s12a_equilateral_ear_obstruction.json`. It exactly rejects
the fixed S12A selected-witness pattern in the natural order. The former S12A
frontier artifact remains checked but is explicitly marked as superseded
provenance.

## Material not imported

### n=9 elementary packet

The packet gives a useful proof compression: `144` of the `184` existing
frontier assignments have at least three forced equilateral ears, and the
remaining `40` assignments form four dihedral classes handled by the same
turn-budget certificates already represented in
`data/certificates/n9_turn_inequality_frontier.json`.

No duplicate checker or artifact was imported. The repository already has
self-contained frontier regeneration, integer dual certificates, indexing
audits, and independent vertex-circle/Kalmanson replay paths for the same
frontier. The handoff does not change the review-pending `n=9` status.

One prose statement in the packet also needed correction: the witness-pair
capacity argument gives selected indegree at most `5`, not at most `4`. The
enumeration subsequently finds that all `184` survivors have indegree exactly
`4`; the checker itself used the correct cap `5`.

### Parabola note

The handoff's standard-parabola result is subsumed by
`docs/parabola-model-case.md`, which handles arbitrary nondegenerate affine
parabolas directly.

### Strong-connectivity note

The note is a concise restatement of an existing minimality consequence. The
row-closure statement in `docs/minimal-fragile-cover-bridge.md` says that the
closure of every nonempty seed under any actual selected-row choice is the
whole vertex set. Equivalently, the selected-witness digraph is strongly
connected. No separate duplicate theorem note was imported.

### Outcome and bridge summaries

The packaged summaries were tied to the recorded reference commit and were
already superseded by the repository's current bridge and finite-artifact
ledgers. They are not source-of-truth replacements.

## Claim boundary

This triage adds one exact fixed-pattern, fixed-order obstruction. It does not
promote `n=9`, change the repo-local strongest result `n <= 8`, update the
official/global falsifiable/open status, prove Erdos Problem #97, or produce a
counterexample.
