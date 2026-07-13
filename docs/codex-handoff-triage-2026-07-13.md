# Codex handoff triage (2026-07-13)

Status: provenance and import decision record. No general proof or
counterexample is claimed.

## Source

The reviewed pasted research handoff had SHA-256

```text
205b468cf9dce4af5c20a04d3d5537c2d2e70fd90c8ad97ac4ce9b231f9f1a2c
```

The source text is not checked in verbatim. Its useful material is represented
by the smaller proof-facing note and managed exact artifact below; its
remaining contents are either duplicate provenance or unfinished research.

## Verification performed

- Reconstructed all ten proposed points with `fractions.Fraction`.
- Recomputed all `80` strict-convexity half-plane determinants exactly.
- Enumerated the complete squared-distance partitions at centers `0` and `1`.
- Compared all six witness-chord lengths in each rich class by exact rational
  ordering.
- Checked endpoint alternation of the two selected chords in the stated cyclic
  order.
- Compared the structural lemmas and research leads with the current
  repository notes and artifacts.
- Rechecked the cited Barany--Roldan-Pensado paper's continuous-boundary claim;
  the repository already records the boundary-to-vertex gap and a dedicated
  vertexization probe.

## Imported material

### Exact canonical-chord crossing control

The rational decagon is imported as
`docs/canonical-shortest-chord-crossing-control.md`,
`scripts/check_canonical_shortest_chord_crossing.py`, and
`data/certificates/canonical_shortest_chord_crossing_control.json`.

It shows exactly that two locally bad centers can have crossing chords under
the deterministic rule "smallest rich radius, then unique shortest witness
chord." Exactly those two centers are bad; the checker proves that every distance at
the other eight centers is distinct. The result is a negative
control for a proof route, not a counterexample to Erdos Problem #97.

### Good-deletion closure from every nonempty seed

The minimality observation is added to `docs/minimal-fragile-cover-bridge.md`.
For every nonempty proper deleted set `A` in a vertex-minimal counterexample,
some surviving center is good among the remaining vertices and can be deleted
next. Iteration produces a full good-deletion order after any nonempty seed.

This is deliberately kept separate from rich-triple closure. It does not imply
ear-orderability or force a selected row.

## Material not imported

### Strong-connectivity lemma

This is already represented by the row-closure consequence recorded in
`docs/codex-handoff-triage-2026-07-12.md`: every actual selected-witness
digraph of a vertex-minimal counterexample is strongly connected. No duplicate
theorem note is needed.

### Danzer double-lift lead

The first-order normal condition and proposed cycle cover do not establish a
nonzero exact nonlinear branch, an exact doubled configuration, or even a
certified numerical realization. The repository already records Danzer-style
lift obstructions and degeneration diagnostics. The proposed cycle cover is
therefore retained only in this triage decision, not promoted to a live
counterexample candidate or a theorem artifact.

### Continuous-boundary discussion

The Barany--Roldan-Pensado 15-gon concerns centered intersections with the
polygon boundary, including edge interiors. The existing
`docs/brp-boundary-vertexization-probe.md` already records why this does not
give four equidistant polygon vertices and keeps the route at diagnostic grade.

### General ledger and outcome summary

The broad status summary duplicates the repository source-of-truth surfaces.
It is not imported as a replacement for `README.md`, `STATE.md`, `RESULTS.md`,
`docs/claims.md`, or `metadata/erdos97.yaml`.

## Claim boundary

This triage adds one exact local negative control and one elementary
minimality lemma. It does not promote `n=9`, change the repo-local strongest
result `n <= 8`, update the official/global falsifiable/open status, prove
Erdos Problem #97, or produce a counterexample.
